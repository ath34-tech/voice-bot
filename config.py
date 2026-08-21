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
    
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    EXTRACTOR_MODEL = os.getenv("EXTRACTOR_MODEL", "gemini-2.5-flash-lite")

    # STT & TTS Audio Settings
    DEEPGRAM_STT_ENDPOINTING_MS = os.getenv("DEEPGRAM_STT_ENDPOINTING_MS", "3500")  # 3.5s silence threshold
    DEEPGRAM_TTS_VOICE = os.getenv("DEEPGRAM_TTS_VOICE", "aura-stella-en")  # Warm, rich, non-robotic female voice


settings = Settings()
