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
        self.api_key = getattr(settings, 'SARVAM_API_KEY', None) or os.getenv("SARVAM_API_KEY")
        model_name = getattr(settings, 'SARVAM_TTS_MODEL', 'bulbul:v3')
        if model_name in ('bulbul:v2', 'v2', 'bulbul-v2'):
            logger.warning("⚠️ Deprecated Sarvam model 'bulbul:v2' detected. Auto-upgrading to 'bulbul:v3'.")
            model_name = 'bulbul:v3'
        self.model = model_name
        self.speaker = getattr(settings, 'SARVAM_TTS_SPEAKER', 'anushka')
        self.target_language = getattr(settings, 'SARVAM_TTS_LANGUAGE', 'hi-IN')
        self.fallback = None
        
        if not self.api_key:
            logger.error("🚨 SARVAM_API_KEY IS MISSING! Please add SARVAM_API_KEY to Render Environment Variables for native Hindi voice!")
            self.fallback = DeepgramTTSImpl(sample_rate=self.sample_rate)
        else:
            logger.info(f"🔑 SARVAM_API_KEY active. Using Sarvam AI ({self.model}, speaker={self.speaker}, rate={self.sample_rate}Hz).")

    async def stream_synthesize(self, text: str):
        """
        Synthesizes text using Sarvam AI Bulbul TTS model for Hindi/Hinglish.
        Decodes base64 audio into 16-bit PCM chunks for WebRTC streaming.
        """
        if self.fallback:
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
            "pitch": 0,
            "pace": 1.0,
            "loudness": 1.5,
            "speech_sample_rate": self.sample_rate,
            "enable_preprocessing": True,
            "model": self.model
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Sarvam TTS HTTP {response.status}: {error_text}")
                        raise RuntimeError(f"Sarvam TTS Error: {response.status} - {error_text}")
                    
                    data = await response.json()
                    audios = data.get("audios", [])
                    if not audios:
                        logger.error("Sarvam TTS returned empty audio list.")
                        return

                    # Sarvam returns base64 encoded audio string
                    base64_audio = audios[0]
                    audio_bytes = base64.b64decode(base64_audio)

                    # Skip WAV header (44 bytes) if WAV container header is present
                    if audio_bytes.startswith(b'RIFF'):
                        raw_pcm = audio_bytes[44:]
                    else:
                        raw_pcm = audio_bytes

                    # Calculate exact 10ms PCM frame size matching sample_rate
                    chunk_size = int(self.sample_rate * 0.010 * 2)
                    for i in range(0, len(raw_pcm), chunk_size):
                        yield raw_pcm[i:i + chunk_size]
        except Exception as e:
            logger.error(f"Sarvam TTS synthesis failed: {e}. Falling back to Deepgram TTS...")
            fallback_tts = DeepgramTTSImpl(sample_rate=self.sample_rate)
            async for chunk in fallback_tts.stream_synthesize(text):
                yield chunk


# Select DeepgramTTS or SarvamTTS based on TTS_PROVIDER ('deepgram' | 'sarvam')
if getattr(settings, 'TTS_PROVIDER', 'sarvam').lower() == 'sarvam':
    DeepgramTTS = SarvamTTS  # Drop-in replacement for Pipeline
else:
    DeepgramTTS = DeepgramTTSImpl
