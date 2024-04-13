import asyncio
import json
import logging
import nextcord
from nextcord.ext import commands
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)

class SimpleDiscordKafkaService:
    def __init__(self, token, channel_id, openai_key):
        self.bot = commands.Bot(command_prefix='!', intents=nextcord.Intents.all(), help_command=None)
        self.token = token
        self.channel_id = channel_id
        self.openai_key = openai_key

        # Setup LangChain with OpenAI
        self.chat_api = ChatOpenAI(api_key=openai_key, model="gpt-3.5-turbo")

        # Kafka Producer setup
        self.producer = AIOKafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda m: json.dumps(m).encode('utf-8'),
            loop=asyncio.get_event_loop()
        )

        # Kafka Consumer setup (if needed for consuming history elsewhere in the app)
        # self.consumer = AIOKafkaConsumer(
        #     'discord_history',
        #     bootstrap_servers='kafka:9092',
        #     value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        #     loop=asyncio.get_event_loop()
        # )

        self.setup_bot_events()

    def setup_bot_events(self):
        @self.bot.event
        async def on_ready():
            logger.info(f'Logged in as {self.bot.user}')
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                await channel.send("Hello! I am your Roman history teacher. Ask me anything about Roman history.")
            else:
                logger.warning(f"Channel with ID {self.channel_id} not found.")

        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user:
                return
            
            if not isinstance(message.channel, nextcord.abc.GuildChannel):
                return

            if message.content.startswith("!"):
                await self.bot.process_commands(message)
                return

            # Process and store the message to Kafka
            await self.process_message(message)

    async def process_message(self, message):
        # Store user message in Kafka
        await self.producer.send('discord_history', {
            'type': 'user_message',
            'content': message.content,
            'user_id': message.author.id,
            'channel_id': message.channel.id,
            'timestamp': message.created_at.isoformat()
        })

        # Handle conversation
        response = await self.handle_conversation(message.content)

        # Store system response in Kafka
        await self.producer.send('discord_history', {
            'type': 'system_response',
            'content': response,
            'user_id': message.author.id,
            'channel_id': message.channel.id,
            'timestamp': message.created_at.isoformat()
        })

        await message.channel.send(response)

    async def handle_conversation(self, user_input):
        era = "ancient Rome"
        prompt_text = f"Imagine you are a history teacher specializing in {era}. Your task is to educate a student about {era}. Respond to the student's inquiry: '{user_input}'"
        prompt = ChatPromptTemplate.from_messages([("system", prompt_text)])

        output_parser = StrOutputParser()
        chain = prompt | self.chat_api | output_parser

        try:
            response = chain.invoke({"input": user_input})  # Ensure await is correctly used here
            return f"Roman History Teacher: {response}"
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return "Sorry, I encountered an error. Please try asking something else."

    async def start(self):
        await self.producer.start()
        logger.info("Kafka producer started")
        await self.bot.start(self.token)

    async def stop(self):
        await self.producer.stop()
        await self.bot.close()
        logger.info("Services stopped")
