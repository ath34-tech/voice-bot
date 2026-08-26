import os
from typing import List, Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    # App & Environment
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "*"

    # LiveKit Credentials
    LIVEKIT_URL: str = "ws://127.0.0.1:8880"
    LIVEKIT_API_KEY: str = "devkey"
    LIVEKIT_API_SECRET: str = "secret"
    LIVEKIT_ROOM: str = "test-room"
    BOT_NAME: str = "AI Assistant"

    # Database & Transcripts
    DATABASE_URL: str = "sqlite+aiosqlite:///./survey_bot.db"
    TRANSCRIPT_STORAGE: str = "database"  # 'database' | 'file' | 'both'

    # LLM Credentials & Models
    GOOGLE_API_KEY: Optional[str] = None
    DEEPGRAM_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    SARVAM_API_KEY: Optional[str] = None

    LLM_PROVIDER: str = "gemini"
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    EXTRACTOR_MODEL: str = "gemini-3.5-flash-lite"

    # Audio Provider Options: 'deepgram' | 'sarvam'
    STT_PROVIDER: str = "deepgram"
    TTS_PROVIDER: str = "deepgram"

    # Deepgram Settings
    DEEPGRAM_STT_ENDPOINTING_MS: str = "2000"
    DEEPGRAM_STT_LANGUAGE: str = "hi"
    DEEPGRAM_TTS_VOICE: str = "aura-stella-en"

    # Sarvam AI Settings
    SARVAM_STT_MODEL: str = "saarika:v2"
    SARVAM_STT_LANGUAGE: str = "hi-IN"
    SARVAM_TTS_MODEL: str = "bulbul:v2"
    SARVAM_TTS_SPEAKER: str = "anushka"
    SARVAM_TTS_LANGUAGE: str = "hi-IN"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origin_list(self) -> List[str]:
        if not self.CORS_ORIGINS or self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
