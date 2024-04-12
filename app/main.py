from fastapi import FastAPI
import logging

# Import your simplified DiscordKafkaService here
from app.services.gutenberg_service import SimpleDiscordKafkaService
from app.dependencies import get_settings
from app.utils.common import setup_logging
from app.routers import oauth, user_routes

# Initialize settings and setup logging
settings = get_settings()
setup_logging()

app = FastAPI(
    title="Event Management",
    description="A FastAPI application for event management and integration with Discord.",
    version="0.0.1",
    contact={
        "name": "API Support",
        "url": "http://www.example.com/support",
        "email": "support@example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# Create the Discord service instance globally
service = SimpleDiscordKafkaService(
    token=settings.discord_bot_token,
    channel_id=settings.discord_channel_id,
    openai_key=settings.openai_api_key
)

@app.on_event("startup")
async def start_service():
    logging.info("Starting DiscordKafkaService...")
    await service.start()
    logging.info("DiscordKafkaService started successfully")

@app.on_event("shutdown")
async def stop_service():
    logging.info("Stopping DiscordKafkaService...")
    await service.stop()
    logging.info("DiscordKafkaService stopped successfully")

# Include routers
app.include_router(oauth.router)
app.include_router(user_routes.router)

logging.info("FastAPI application setup completed")
