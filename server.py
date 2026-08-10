import asyncio
import uuid
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from livekit import api

from config import settings
from rooms import LiveKitClient
from pipeline import Pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Agent Orchestrator")

# Allow the frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Keep track of active bots in memory
active_bots = {}

class CallResponse(BaseModel):
    room_name: str
    user_token: str
    livekit_url: str


def generate_user_token(room_name: str, identity: str = "human-user") -> str:
    """Generates a token for the frontend client to join the room."""
    return (
        api.AccessToken(
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET,
        )
        .with_identity(identity)
        .with_name("Human")
        .with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
        ))
        .to_jwt()
    )


async def spawn_bot_in_background(room_name: str):
    """Dynamically spins up a completely new Pipeline and LiveKit client for a specific room."""
    logger.info(f"Spawning new bot instance for room {room_name}...")
    
    client = LiveKitClient()
    
    # Initialize and start the AI Pipeline FIRST (connects to Deepgram)
    client.pipeline = Pipeline(client.room)
    await client.pipeline.start()
    
    # NOW connect to LiveKit so we are ready to process incoming audio
    await client.connect(room_name)
    
    # Finally, publish the bot's speaker track to the room
    await client.pipeline.publish_bot_track()
    
    # Force the bot to say hello first!
    await client.pipeline.trigger_first_message()
    
    active_bots[room_name] = client


@app.post("/start_call", response_model=CallResponse)
async def start_call():
    """
    Endpoint called by the Frontend.
    1. Generates a unique private room.
    2. Spawns a dedicated AI Bot into that room.
    3. Returns the token so the Human can join the room.
    """
    # 1. Generate a completely unique, private room ID
    room_name = f"chat-{uuid.uuid4().hex[:8]}"
    
    # 2. Spawn the bot into this room in the background
    asyncio.create_task(spawn_bot_in_background(room_name))
    
    # 3. Generate the token for the human to join
    user_token = generate_user_token(room_name)
    
    logger.info(f"Created private room {room_name}. Sending token to user.")
    
    return CallResponse(
        room_name=room_name,
        user_token=user_token,
        livekit_url=settings.LIVEKIT_URL
    )
