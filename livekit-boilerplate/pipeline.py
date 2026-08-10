import asyncio
import logging
from livekit import rtc
from stt import DeepgramSTT
from groq_client import GroqClient
from tts import DeepgramTTS

logger = logging.getLogger(__name__)

class Pipeline:
    def __init__(self, room: rtc.Room):
        self.room = room
        self.stt = DeepgramSTT()
        self.llm = GroqClient()
        self.tts = DeepgramTTS()

        self.sample_rate = 48000
        self.num_channels = 1
        self.audio_source = rtc.AudioSource(self.sample_rate, self.num_channels)
        self.audio_track = rtc.LocalAudioTrack.create_audio_track("bot-audio", self.audio_source)

        self.bot_publication = None
        self._main_task = None
        self._is_interrupted = False
        self.stt.on_speech_started = self._handle_interruption

    def _handle_interruption(self):
        if not self._is_interrupted:
            logger.info("🛑 User interrupted! Stopping bot speech...")
            self._is_interrupted = True

    async def start(self):
        logger.info("Connecting to STT...")
        await self.stt.connect()
        self._main_task = asyncio.create_task(self._process_loop())
        logger.info("Pipeline started.")

    async def publish_bot_track(self):
        logger.info("Publishing bot audio track...")
        options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
        self.bot_publication = await self.room.local_participant.publish_track(self.audio_track, options)

    async def stop(self):
        if self._main_task:
            self._main_task.cancel()
        await self.stt.disconnect()
        if self.bot_publication:
            await self.room.local_participant.unpublish_track(self.bot_publication.sid)
        logger.info("Pipeline stopped.")

    async def handle_audio_frame(self, frame: rtc.AudioFrame):
        audio_data = bytes(frame.data)
        await self.stt.send_audio(audio_data)

    async def _process_loop(self):
        try:
            while True:
                transcript = await self.stt.receive_transcript()
                if not transcript:
                    continue

                clean_transcript = transcript.strip().rstrip(".").strip()
                if len(clean_transcript.split()) <= 2:
                    self._is_interrupted = False
                    continue

                logger.info(f"🎤 User: {transcript}")
                await self.send_text_to_frontend(transcript, "User")

                was_interrupted = self._is_interrupted
                self._is_interrupted = False

                response_stream = self.llm.stream_chat(transcript, was_interrupted=was_interrupted)
                await self.send_text_to_frontend("", "AI", is_stream=False)

                buffer = ""
                async for chunk in response_stream:
                    if self._is_interrupted:
                        logger.info("Cancelling LLM generation due to interruption.")
                        break

                    await self.send_text_to_frontend(chunk, "AI", is_stream=True)
                    buffer += chunk

                    if any(punc in buffer for punc in [". ", "? ", "! ", "\n"]):
                        temp = buffer.replace("? ", "?|").replace("! ", "!|").replace(". ", ".|").replace("\n", "\n|")
                        sentences = temp.split("|")
                        for sentence in sentences[:-1]:
                            clean = sentence.strip()
                            if clean:
                                await self._speak(clean)
                        buffer = sentences[-1]

                if buffer.strip():
                    await self._speak(buffer.strip())

        except asyncio.CancelledError:
            logger.info("Pipeline loop cancelled.")
        except Exception as e:
            logger.error(f"Error in pipeline loop: {e}", exc_info=True)

    async def _speak(self, text: str):
        logger.info(f"🔊 Bot speaking: {text}")
        try:
            SAMPLES_PER_FRAME = 960
            BYTES_PER_FRAME = SAMPLES_PER_FRAME * 2
            audio_buffer = b""

            import time
            start_time = time.time()
            frames_sent = 0

            async for chunk in self.tts.stream_synthesize(text):
                if self._is_interrupted:
                    logger.info("Cancelling TTS playback due to interruption.")
                    break

                audio_buffer += chunk
                while len(audio_buffer) >= BYTES_PER_FRAME:
                    frame_data = audio_buffer[:BYTES_PER_FRAME]
                    audio_buffer = audio_buffer[BYTES_PER_FRAME:]
                    frame = rtc.AudioFrame(
                        data=frame_data,
                        sample_rate=self.sample_rate,
                        num_channels=self.num_channels,
                        samples_per_channel=SAMPLES_PER_FRAME
                    )
                    await self.audio_source.capture_frame(frame)
                    frames_sent += 1

                    target_time = start_time + (frames_sent * 0.020)
                    sleep_time = target_time - time.time()
                    if sleep_time > 0:
                        await asyncio.sleep(sleep_time)

            if audio_buffer and not self._is_interrupted:
                audio_buffer += b'\x00' * (BYTES_PER_FRAME - len(audio_buffer) % BYTES_PER_FRAME)
                frame = rtc.AudioFrame(
                    data=audio_buffer[:BYTES_PER_FRAME],
                    sample_rate=self.sample_rate,
                    num_channels=self.num_channels,
                    samples_per_channel=SAMPLES_PER_FRAME
                )
                await self.audio_source.capture_frame(frame)

        except Exception as e:
            logger.error(f"TTS error: {e}", exc_info=True)

    async def send_text_to_frontend(self, text: str, sender: str, is_stream: bool = False):
        import json
        payload = json.dumps({"sender": sender, "text": text, "is_stream": is_stream}).encode("utf-8")
        await self.room.local_participant.publish_data(payload)

    async def trigger_first_message(self):
        try:
            response_stream = self.llm.stream_opening_message()
            buffer = ""
            await self.send_text_to_frontend("", "AI", is_stream=False)

            async for chunk in response_stream:
                await self.send_text_to_frontend(chunk, "AI", is_stream=True)
                buffer += chunk

                if any(punc in buffer for punc in [". ", "? ", "! ", "\n"]):
                    temp = buffer.replace("? ", "?|").replace("! ", "!|").replace(". ", ".|").replace("\n", "\n|")
                    sentences = temp.split("|")
                    for sentence in sentences[:-1]:
                        clean = sentence.strip()
                        if clean:
                            await self._speak(clean)
                    buffer = sentences[-1]

            if buffer.strip():
                await self._speak(buffer.strip())

        except Exception as e:
            logger.error(f"Error during first message: {e}")
