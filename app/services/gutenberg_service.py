import asyncio
import json
import logging
from ratelimit import limits, sleep_and_retry
import nextcord
from nextcord.ext import commands
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class SimpleDiscordKafkaService:
    def __init__(self, token, channel_id, openai_key):
        self.bot = commands.Bot(command_prefix='!', intents=nextcord.Intents.all(), help_command=None)
        self.token = token
        self.channel_id = channel_id
        self.openai_key = openai_key

        # Setup LangChain with OpenAI
        self.chat_api = ChatOpenAI(api_key=openai_key, model="gpt-3.5-turbo")
        logger.info("Chat API initialized with model gpt-3.5-turbo")

        # Kafka Producer and Consumer setup
        self.producer = AIOKafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda m: json.dumps(m).encode('utf-8'),
            loop=asyncio.get_event_loop(),
            enable_idempotence=True,
            acks='all',
            retry_backoff_ms=500
        )
        self.consumer = AIOKafkaConsumer(
            bootstrap_servers='kafka:9092',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            loop=asyncio.get_event_loop(),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='discord_history_consumer'
        )
        logger.info("Kafka producer and consumer configured")

        self.setup_bot_events()

    def setup_bot_events(self):
        @self.bot.event
        async def on_ready():
            logger.info(f'Logged in as {self.bot.user}')
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                logger.info(f"Sending greeting message to channel {self.channel_id}")
                await channel.send("Hello! I am your Roman history teacher. Ask me anything about Roman history.")
            else:
                logger.warning(f"Channel with ID {self.channel_id} not found.")

        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user:
                return
            logger.info(f"Received message from {message.author}: {message.content}")
            if isinstance(message.channel, nextcord.DMChannel) or isinstance(message.channel, nextcord.abc.GuildChannel):
                await self.process_message(message)

    async def process_message(self, message):
        user_id = message.author.id
        message_content = message.content
        channel_id = message.channel.id
        timestamp = message.created_at.isoformat()

        logger.info(f"Processing message: {message_content} from user: {user_id}")

        # Sending message to Kafka
        await self.producer.send(f'discord_history_{user_id}', {
            'type': 'user_message',
            'content': message_content,
            'user_id': user_id,
            'channel_id': channel_id,
            'timestamp': timestamp
        })
        logger.info(f"Message sent to Kafka topic for user {user_id}")

        # Handling conversation
        response = await self.handle_conversation(message_content)
        await message.channel.send(response)
        logger.info(f"Generated response: {response}")

        # Storing the response in Kafka
        await self.producer.send(f'discord_history_{user_id}', {
            'type': 'system_response',
            'content': response,
            'user_id': user_id,
            'channel_id': channel_id,
            'timestamp': timestamp
        })
        logger.info("Response stored in Kafka")

    @sleep_and_retry
    @limits(calls=5, period=60)
    async def handle_conversation(self, user_input):
        era = "ancient Rome"
        prompt_text = f"Imagine you are a history teacher specializing in {era}. Your task is to educate a student about {era}. Respond to the student's inquiry: '{user_input}'"
        prompt = ChatPromptTemplate.from_messages([("system", prompt_text)])
        logger.info("Generating response using Chat API")

        chain = (
            RunnablePassthrough.assign(
                input=lambda x: x["input"]
            )
            | prompt
            | self.chat_api
            | StrOutputParser()
        )

        try:
            response = await chain.ainvoke({"input": user_input})
            logger.info("Response generated successfully")
            return f"Roman History Teacher: {response}"
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return "Sorry, I encountered an error. Please try asking something else."

    async def start(self):
        try:
            await self.producer.start()
            logger.info("Kafka producer started")
            await self.consumer.start()
            logger.info("Kafka consumer started")
            await self.bot.start(self.token)
        except Exception as e:
            logger.error(f"Failed to start services due to: {e}")
        finally:
            await self.stop()

    async def stop(self):
        try:
            await self.producer.stop()
            logger.info("Kafka producer stopped")
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")
        except Exception as e:
            logger.error(f"Failed to stop services: {e}")
        try:
            await self.bot.close()
            logger.info("Discord bot stopped")
        except Exception as e:
            logger.error(f"Failed to close Discord bot: {e}")