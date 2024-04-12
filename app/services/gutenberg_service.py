import asyncio
import nextcord
from nextcord.ext import commands
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import json
import logging

from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.memory import ChatMessageHistory

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

class DiscordMessage(BaseModel):
    author: str
    content: str
    channel_id: int

class SimpleDiscordKafkaService:
    def __init__(self, token, channel_id, openai_key):
        self.bot = commands.Bot(command_prefix='!', intents=nextcord.Intents.all(), help_command=None)
        self.token = token
        self.channel_id = channel_id
        self.openai_key = openai_key

        # Setup LangChain with OpenAI
        self.chat_api = ChatOpenAI(api_key=openai_key, model="gpt-3.5-turbo")
        self.chat_history = ChatMessageHistory()

        # Kafka setup
        self.producer = AIOKafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda m: json.dumps(m).encode('utf-8'),
            loop=asyncio.get_event_loop()
        )
        self.consumer = AIOKafkaConsumer(
            'discord_messages',
            bootstrap_servers='kafka:9092',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            loop=asyncio.get_event_loop()
        )

        self.setup_bot_events()

    def setup_bot_events(self):
        @self.bot.event
        async def on_ready():
            logger.info(f'Logged in as {self.bot.user}')
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                await channel.send("Hello! I am a simple Discord bot connected to Kafka and OpenAI.")
                logger.info(f"Bot announced in channel: {channel.name}")
            else:
                logger.warning(f"Channel with ID {self.channel_id} not found.")

        @self.bot.event
        async def on_message(message: nextcord.Message):
            if message.author == self.bot.user:
                return

            self.chat_history.add_user_message(message.content)
            
            # Generate a response using LangChain
            response = self.chat_api.generate_response(self.chat_history.get_last_messages())
            self.chat_history.add_ai_message(response)

            # Send message to Kafka
            discord_message = DiscordMessage(
                author=str(message.author),
                content=message.content,
                channel_id=message.channel.id
            ).dict()
            await self.producer.send('discord_messages', discord_message)
            logger.info(f"Message sent to Kafka topic 'discord_messages': {discord_message}")

            # Send response to Discord
            await message.channel.send(f"AI Response: {response}")
            logger.info(f"Sent AI response to channel")

            # Process commands if any
            await self.bot.process_commands(message)

    async def start(self):
        await self.producer.start()
        await self.consumer.start()
        logger.info("Kafka consumer and producer started along with OpenAI integration")
        await self.bot.start(self.token)

    async def stop(self):
        logger.info("Stopping services")
        await self.consumer.stop()
        await self.producer.stop()
        await self.bot.close()
        logger.info("All services stopped")
