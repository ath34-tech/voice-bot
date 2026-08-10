from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://127.0.0.1:8880")
    LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
    LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")

    LIVEKIT_ROOM = os.getenv("LIVEKIT_ROOM", "test-room")
    BOT_NAME = os.getenv("BOT_NAME", "AI Assistant")

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")


settings = Settings()
