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

    # Audio Engine Provider Options: 'deepgram' | 'sarvam'
    STT_PROVIDER = os.getenv("STT_PROVIDER", "deepgram").lower()
    TTS_PROVIDER = os.getenv("TTS_PROVIDER", "deepgram").lower()

    # Deepgram Settings
    DEEPGRAM_STT_ENDPOINTING_MS = os.getenv("DEEPGRAM_STT_ENDPOINTING_MS", "3500")  # 3.5s silence threshold
    DEEPGRAM_STT_LANGUAGE = os.getenv("DEEPGRAM_STT_LANGUAGE", "hi")  # 'hi' (Hindi/Hinglish) or 'en-US'
    DEEPGRAM_TTS_VOICE = os.getenv("DEEPGRAM_TTS_VOICE", "aura-stella-en")  # Warm, rich female voice

    # Sarvam AI Settings (Hindi & Hinglish STT/TTS)
    SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
    SARVAM_STT_MODEL = os.getenv("SARVAM_STT_MODEL", "saarika:v2")  # 'saarika:v2' or 'saaras:v1'
    SARVAM_STT_LANGUAGE = os.getenv("SARVAM_STT_LANGUAGE", "hi-IN")  # 'hi-IN' (Hindi) or 'en-IN' (Hinglish)
    SARVAM_TTS_MODEL = os.getenv("SARVAM_TTS_MODEL", "bulbul:v2")  # Sarvam Bulbul v2
    SARVAM_TTS_SPEAKER = os.getenv("SARVAM_TTS_SPEAKER", "anushka")  # Options: 'anushka', 'priya', 'kavya', 'shreya', 'ratan', 'aditya'
    SARVAM_TTS_LANGUAGE = os.getenv("SARVAM_TTS_LANGUAGE", "hi-IN")  # 'hi-IN' (Hindi) or 'en-IN' (Hinglish)


settings = Settings()
