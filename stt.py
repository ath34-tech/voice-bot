import asyncio
import logging
import os
import json
import io
import wave
import aiohttp
import websockets
from websockets.exceptions import ConnectionClosed, ConnectionClosedError

from config import settings

logger = logging.getLogger(__name__)

# Deepgram connection URL with 3.5s silence threshold (3500ms endpointing)
_ENDPOINT_MS = getattr(settings, 'DEEPGRAM_STT_ENDPOINTING_MS', '3500')
_STT_LANG = getattr(settings, 'DEEPGRAM_STT_LANGUAGE', 'hi')
_DEEPGRAM_URL = (
    "wss://api.deepgram.com/v1/listen?"
    "model=nova-2&"
    f"language={_STT_LANG}&"
    "smart_format=true&"
    "encoding=linear16&"
    "channels=1&"
    "sample_rate=48000&"
    "interim_results=true&"
    f"endpointing={_ENDPOINT_MS}&"
    f"utterance_end_ms={_ENDPOINT_MS}&"
    "vad_events=true"
)


class DeepgramSTT:
    def __init__(self):
        self.api_key = os.getenv("DEEPGRAM_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPGRAM_API_KEY is not set in environment variables.")

        self.connection = None
        self.transcript_queue: asyncio.Queue[str] = asyncio.Queue()
        self._recv_task = None
        self._keepalive_task = None
        self._reconnect_task = None
        self._running = False          # Master flag — False = stop all loops

        self._utterance_parts = []
        self.on_speech_started = None  # Barge-in callback: fn(transcript_text)

    async def connect(self):
        """Establish initial WebSocket connection to Deepgram."""
        logger.info("Connecting to Deepgram STT...")
        self._running = True
        await self._do_connect()
        logger.info("Deepgram STT connected successfully.")

    async def send_audio(self, audio_data: bytes):
        """Send raw PCM audio bytes to Deepgram."""
        if self.connection is None or not self._running:
            return
        try:
            await self.connection.send(audio_data)
        except (ConnectionClosed, ConnectionClosedError):
            pass
        except Exception:
            pass

    async def receive_transcript(self) -> str:
        """Block until the next finalised transcript is available."""
        while self._running:
            try:
                return await asyncio.wait_for(
                    self.transcript_queue.get(),
                    timeout=25.0
                )
            except asyncio.TimeoutError:
                if not self._running:
                    return ""
                if self.connection is None:
                    logger.warning("⚡ Deepgram STT queue timeout with no connection — forcing reconnect...")
                    asyncio.create_task(self._reconnect())
        return ""

    async def disconnect(self):
        """Shut down all tasks and close the WebSocket."""
        self._running = False
        self._cancel_tasks()
        if self.connection:
            try:
                await self.connection.close()
            except Exception:
                pass
            self.connection = None
        logger.info("Disconnected from Deepgram STT.")

    async def _do_connect(self):
        self._cancel_tasks()

        self.connection = await websockets.connect(
            _DEEPGRAM_URL,
            additional_headers={"Authorization": f"Token {self.api_key}"},
            ping_interval=None,
            ping_timeout=None,
            close_timeout=5,
        )

        self._recv_task      = asyncio.create_task(self._receive_loop())
        self._keepalive_task = asyncio.create_task(self._keepalive_loop())

    def _cancel_tasks(self):
        for task in (self._recv_task, self._keepalive_task):
            if task and not task.done():
                task.cancel()
        self._recv_task = None
        self._keepalive_task = None

    async def _reconnect(self):
        if not self._running:
            return
        logger.warning("⚡ Deepgram connection lost — attempting reconnect...")

        delay = 1.0
        for attempt in range(1, 8):
            await asyncio.sleep(delay)
            if not self._running:
                return
            try:
                await self._do_connect()
                logger.info(f"✅ Deepgram reconnected (attempt {attempt}).")
                return
            except Exception as e:
                logger.warning(f"Reconnect attempt {attempt} failed: {e}")
                delay = min(delay * 2, 30)

        logger.error("❌ Deepgram reconnect failed after all attempts. STT unavailable.")

    async def _keepalive_loop(self):
        try:
            while self._running and self.connection:
                await asyncio.sleep(8)
                if not self._running or self.connection is None:
                    break
                try:
                    await self.connection.send(json.dumps({"type": "KeepAlive"}))
                except (ConnectionClosed, ConnectionClosedError):
                    break
                except Exception as e:
                    logger.warning(f"KeepAlive send failed: {e}")
                    break
        except asyncio.CancelledError:
            pass

    async def _receive_loop(self):
        try:
            async for message in self.connection:
                if not self._running:
                    break

                if not isinstance(message, str):
                    continue

                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    continue

                msg_type = data.get("type")

                if msg_type == "Error":
                    logger.error(f"🚨 Deepgram error message: {message}")

                elif msg_type == "UtteranceEnd":
                    if self._utterance_parts:
                        full_text = " ".join(self._utterance_parts).strip()
                        self._utterance_parts.clear()
                        if full_text and len(full_text) >= 2:
                            logger.info(f"🎤 Deepgram UtteranceEnd (3.5s Silence Reached): '{full_text}'")
                            await self.transcript_queue.put(full_text)

                elif msg_type == "Results":
                    channel = data.get("channel", {})
                    alts = channel.get("alternatives", [])
                    if not alts:
                        continue
                    transcript = alts[0].get("transcript", "").strip()
                    if not transcript:
                        continue

                    is_final = data.get("is_final", False)
                    speech_final = data.get("speech_final", False)

                    # Trigger barge-in notification if bot is speaking
                    if self.on_speech_started and len(transcript) >= 3:
                        self.on_speech_started(transcript)

                    logger.info(f"🎙️ Deepgram STT Stream: '{transcript}' (is_final={is_final}, speech_final={speech_final})")

                    # Accumulate sub-phrases
                    if is_final or speech_final:
                        if transcript not in self._utterance_parts:
                            self._utterance_parts.append(transcript)

        except asyncio.CancelledError:
            pass
        except (ConnectionClosed, ConnectionClosedError) as e:
            if self._running:
                logger.error(f"Deepgram connection closed unexpectedly: {e}")
                asyncio.create_task(self._reconnect())
        except Exception as e:
            if self._running:
                logger.error(f"Deepgram receive error: {e}", exc_info=True)
                asyncio.create_task(self._reconnect())


class SarvamSTT:
    def __init__(self):
        self.api_key = getattr(settings, 'SARVAM_API_KEY', None) or os.getenv("SARVAM_API_KEY")
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY is not set in environment variables.")

        self.model = getattr(settings, 'SARVAM_STT_MODEL', 'saarika:v2')
        self.language_code = getattr(settings, 'SARVAM_STT_LANGUAGE', 'hi-IN')
        self.transcript_queue: asyncio.Queue[str] = asyncio.Queue()
        self.on_speech_started = None
        self._running = False
        self._audio_chunks = []

    async def connect(self):
        logger.info(f"Connected Sarvam STT ({self.model}, language={self.language_code}).")
        self._running = True

    async def send_audio(self, audio_data: bytes):
        if not self._running:
            return
        self._audio_chunks.append(audio_data)

    async def receive_transcript(self) -> str:
        """
        Processes accumulated PCM audio chunks using Sarvam AI saarika:v2 Hindi/Hinglish STT API.
        """
        while self._running:
            await asyncio.sleep(3.5)  # 3.5 seconds silence endpointing
            if not self._audio_chunks:
                continue

            # Build WAV file in memory from 48kHz mono 16-bit PCM chunks
            pcm_bytes = b"".join(self._audio_chunks)
            self._audio_chunks.clear()

            if len(pcm_bytes) < 9600:  # Skip tiny audio (<100ms)
                continue

            try:
                wav_buffer = io.BytesIO()
                with wave.open(wav_buffer, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(48000)
                    wav_file.writeframes(pcm_bytes)

                wav_bytes = wav_buffer.getvalue()

                # Call Sarvam Speech-to-Text API
                url = "https://api.sarvam.ai/speech-to-text"
                headers = {"api-subscription-key": self.api_key}

                data = aiohttp.FormData()
                data.add_field('file', wav_bytes, filename='audio.wav', content_type='audio/wav')
                data.add_field('model', self.model)
                data.add_field('language_code', self.language_code)

                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, data=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            transcript = result.get("transcript", "").strip()
                            if transcript:
                                logger.info(f"Sarvam STT Transcript: {transcript}")
                                return transcript
                        else:
                            err_msg = await response.text()
                            logger.error(f"Sarvam STT error ({response.status}): {err_msg}")
            except Exception as e:
                logger.error(f"Error calling Sarvam STT: {e}")

        return ""

    async def disconnect(self):
        self._running = False
        self._audio_chunks.clear()
        logger.info("Disconnected from Sarvam STT.")


# Provider Switcher: Select DeepgramSTT or SarvamSTT based on STT_PROVIDER
if getattr(settings, 'STT_PROVIDER', 'deepgram').lower() == 'sarvam':
    DeepgramSTT = SarvamSTT  # Drop-in replacement for Pipeline
