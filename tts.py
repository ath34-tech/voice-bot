import logging
import os
import aiohttp
import io
import wave
from config import settings

logger = logging.getLogger(__name__)


class DeepgramTTS:
    def __init__(self):
        self.api_key = os.getenv("DEEPGRAM_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPGRAM_API_KEY is not set.")

    async def stream_synthesize(self, text: str):
        """
        Streams text to PCM 16-bit 48kHz audio using Deepgram Aura, yielding chunks instantly.
        """
        logger.info(f"Synthesizing TTS: {text[:50]}...")
        
        # We MUST specify container=none to get raw PCM, otherwise it might send MP3 or WAV headers!
        url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en&encoding=linear16&sample_rate=48000&container=none"
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {"text": text}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"Deepgram TTS Error: {response.status} - {error_text}")
                
                # Because we specified container=none, there is NO header! 
                # We can instantly stream pure PCM sound data.
                while True:
                    chunk = await response.content.read(1920)
                    if not chunk:
                        break
                    yield chunk
