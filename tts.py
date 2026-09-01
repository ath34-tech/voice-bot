import base64
import logging
import os
import aiohttp
from config import settings

logger = logging.getLogger(__name__)


class DeepgramTTSImpl:
    def __init__(self, sample_rate: int = 24000):
        self.sample_rate = sample_rate
        self.api_key = os.getenv("DEEPGRAM_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPGRAM_API_KEY is not set.")

    async def stream_synthesize(self, text: str):
        """
        Streams text to PCM 16-bit audio matching exact pipeline sample_rate.
        """
        logger.info(f"Synthesizing Deepgram TTS ({self.sample_rate}Hz): {text[:50]}...")
        
        voice_model = getattr(settings, 'DEEPGRAM_TTS_VOICE', 'aura-stella-en')
        url = f"https://api.deepgram.com/v1/speak?model={voice_model}&encoding=linear16&sample_rate={self.sample_rate}&container=none"
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
                
                chunk_size = int(self.sample_rate * 0.010 * 2)
                async for chunk in response.content.iter_chunked(chunk_size):
                    if chunk:
                        yield chunk


class SarvamTTS:
    def __init__(self, sample_rate: int = 24000):
        self.sample_rate = sample_rate
        self.api_key = getattr(settings, 'SARVAM_API_KEY', None) or os.getenv("SARVAM_API_KEY") or "sk_mabkyq4l_4pJjpwvbCxhY8JuXAQlfmzk5"
        self.model = "bulbul:v3"
        self.speaker = getattr(settings, 'SARVAM_TTS_SPEAKER', 'anushka')
        self.target_language = getattr(settings, 'SARVAM_TTS_LANGUAGE', 'hi-IN')
        self.fallback = DeepgramTTSImpl(sample_rate=self.sample_rate)

    async def stream_synthesize(self, text: str):
        """
        Synthesizes text using Sarvam AI Bulbul TTS model for Hindi/Hinglish.
        Decodes base64 audio into 16-bit PCM chunks for WebRTC streaming.
        Falls back to Deepgram if Sarvam API key is missing or encounters HTTP error.
        """
        if not self.api_key:
            logger.info("ℹ️ SARVAM_API_KEY not set — using Deepgram TTS for instant speech...")
            async for chunk in self.fallback.stream_synthesize(text):
                yield chunk
            return

        logger.info(f"🔊 Synthesizing Sarvam TTS ({self.target_language}, speaker={self.speaker}, rate={self.sample_rate}Hz): '{text[:60]}...'")
        
        url = "https://api.sarvam.ai/text-to-speech"
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": [text],
            "target_language_code": self.target_language,
            "speaker": self.speaker,
            "pace": 1.0,
            "speech_sample_rate": self.sample_rate,
            "enable_preprocessing": True,
            "model": self.model
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Sarvam TTS HTTP {response.status}: {error_text}. Falling back to Deepgram...")
                        async for chunk in self.fallback.stream_synthesize(text):
                            yield chunk
                        return
                    
                    data = await response.json()
                    audios = data.get("audios", [])
                    if not audios:
                        logger.error("Sarvam TTS returned empty audio list. Falling back to Deepgram...")
                        async for chunk in self.fallback.stream_synthesize(text):
                            yield chunk
                        return

                    # Sarvam returns base64 encoded audio string
                    base64_audio = audios[0]
                    audio_bytes = base64.b64decode(base64_audio)

                    # Extract raw 16-bit PCM samples cleanly by finding the 'data' subchunk
                    if b'data' in audio_bytes[:200]:
                        data_idx = audio_bytes.find(b'data')
                        raw_pcm = audio_bytes[data_idx + 8:]
                    elif audio_bytes.startswith(b'RIFF'):
                        raw_pcm = audio_bytes[44:]
                    else:
                        raw_pcm = audio_bytes

                    # Calculate exact 10ms PCM frame size matching sample_rate (e.g. 480 bytes @ 24kHz mono PCM)
                    chunk_size = int(self.sample_rate * 0.010 * 2)
                    for i in range(0, len(raw_pcm), chunk_size):
                        yield raw_pcm[i:i + chunk_size]
        except Exception as e:
            logger.error(f"Sarvam TTS failed: {e}. Falling back to Deepgram...")
            async for chunk in self.fallback.stream_synthesize(text):
                yield chunk


# Select DeepgramTTS or SarvamTTS based on TTS_PROVIDER ('deepgram' | 'sarvam')
if getattr(settings, 'TTS_PROVIDER', 'sarvam').lower() == 'sarvam':
    DeepgramTTS = SarvamTTS  # Drop-in replacement for Pipeline
else:
    DeepgramTTS = DeepgramTTSImpl
