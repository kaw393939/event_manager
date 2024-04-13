import logging
from fastapi import FastAPI
from app.dependencies import get_settings
from app.routers import oauth, user_routes
from app.services.gutenberg_service import SimpleDiscordKafkaService
from app.utils.common import setup_logging

setup_logging()
settings = get_settings()

app = FastAPI(
    title="Event Management",
    description="An application for managing events, integrating with Discord via Kafka, and using OpenAI for interactions.",
    version="0.0.1"
)

app.include_router(oauth.router)
app.include_router(user_routes.router)

discord_kafka_service = SimpleDiscordKafkaService(
    token=settings.discord_bot_token,
    channel_id=settings.discord_channel_id,
    openai_key=settings.openai_api_key
)

@app.on_event("startup")
async def start_services():
    logging.info("Starting application services")
    await discord_kafka_service.start()

@app.on_event("shutdown")
async def stop_services():
    logging.info("Stopping application services")
    await discord_kafka_service.stop()

logging.info("FastAPI application setup completed")
