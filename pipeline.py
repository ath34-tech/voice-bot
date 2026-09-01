import asyncio
import logging
import time
import re
from livekit import rtc
from config import settings
from stt import DeepgramSTT
from llm import LLMClient
from tts import DeepgramTTS, SarvamTTS

from state import StateManager
from memory import MemoryManager

logger = logging.getLogger(__name__)

class Pipeline:
    def __init__(self, room: rtc.Room, session_id: str):
        self.room = room
        self.stt = DeepgramSTT()
        self.llm = LLMClient()

        if getattr(settings, 'TTS_PROVIDER', 'sarvam').lower() == "sarvam":
            self.sample_rate = 24000
            self.tts = SarvamTTS(sample_rate=self.sample_rate)
        else:
            self.sample_rate = 48000
            self.tts = DeepgramTTS(sample_rate=self.sample_rate)

        self.num_channels = 1
        self.audio_source = rtc.AudioSource(self.sample_rate, self.num_channels)
        self.audio_track = rtc.LocalAudioTrack.create_audio_track("bot-audio", self.audio_source)

        self.bot_publication = None
        self._main_task = None
        self._is_interrupted = False
        self._is_bot_speaking = False
        self._frame_count = 0

        # Register STT speech started callback
        self.stt.on_speech_started = self._handle_interruption

        # Survey Engine State
        self.session_id = session_id
        self.state_manager = StateManager(self.session_id)
        self.memory_manager = MemoryManager(self.session_id)

    def _handle_interruption(self, text: str = ""):
        # Ignore mic speaker echo to prevent false self-interruption
        pass

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
        # Ignore microphone audio while the bot is speaking to prevent speaker echo feedback
        if self._is_bot_speaking:
            return

        self._frame_count += 1
        if self._frame_count % 100 == 1:
            logger.info(f"🎙️ Streaming student microphone audio to STT (frame {self._frame_count})...")
        audio_data = bytes(frame.data)
        await self.stt.send_audio(audio_data)

    async def _process_loop(self):
        try:
            while True:
                transcript = await self.stt.receive_transcript()
                if not transcript:
                    continue

                clean_transcript = transcript.strip().rstrip(".").strip()
                if not clean_transcript or len(clean_transcript) < 2:
                    continue

                logger.info(f"🎤 User (Final 3.5s Endpoint): {transcript}")
                await self.send_text_to_frontend(transcript, "User")
                
                # Add to memory
                turn_id = self.memory_manager.add_student_turn(transcript)

                # Build Context for LLM
                current_question = self.state_manager.get_current_question()
                next_q = self.state_manager.questionnaire.get_next_question(current_question.id) if current_question else None
                prompt = self.memory_manager.build_llm_prompt(self.state_manager.state, current_question, next_q)

                # Call LLM (Gemini / Groq)
                llm_response = await self.llm.get_conversational_decision(prompt)
                
                await self.send_text_to_frontend("", "AI", is_stream=False)
                await self.send_text_to_frontend(llm_response.response, "AI", is_stream=True)

                # Synthesize and speak Gemini's full response
                if llm_response.response:
                    await self._speak(llm_response.response)

                # Add AI response to memory
                self.memory_manager.add_ai_turn(llm_response.response)

                # If moving to next question, trigger extractor in background
                if llm_response.action == "NEXT_QUESTION" and current_question:
                    q_id = current_question.id
                    extractor_prompt = self.memory_manager.build_extractor_prompt(current_question, transcript)
                    asyncio.create_task(self._run_extractor(q_id, extractor_prompt, transcript, turn_id))

                # Update State Machine
                self.state_manager.apply_llm_response(llm_response)

                if self.state_manager.state.status == "completed":
                    logger.info("Survey completed. AI session winding down.")
                    await self._speak("Thank you for completing the survey! Have a great day.")
                    await asyncio.sleep(2.0)
                    await self.stop()
                    await self.room.disconnect()

        except asyncio.CancelledError:
            logger.info("Pipeline loop cancelled.")
        except Exception as e:
            logger.error(f"Error in pipeline loop: {e}", exc_info=True)

    async def _run_extractor(self, q_id: str, prompt: str, raw_text: str, turn_id: int):
        logger.info(f"Triggering background extractor for {q_id}...")
        extraction_resp = await self.llm.extract_answer(prompt)
        self.state_manager.apply_extraction(q_id, extraction_resp, raw_text, turn_id)

    async def _speak(self, text: str):
        if not text or not text.strip():
            return

        logger.info(f"🔊 Bot speaking: {text}")
        self._is_interrupted = False
        self._is_bot_speaking = True

        try:
            SAMPLES_PER_FRAME = int(self.sample_rate * 0.010)  # 240 samples for 24kHz, 480 for 48kHz
            BYTES_PER_FRAME = SAMPLES_PER_FRAME * 2             # 480 bytes for 24kHz, 960 bytes for 48kHz
            audio_buffer = b""

            playback_start = None
            frames_pushed = 0

            async for chunk in self.tts.stream_synthesize(text):
                if self._is_interrupted:
                    logger.info("Cancelling TTS stream due to user interruption.")
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
                    try:
                        await self.audio_source.capture_frame(frame)
                        frames_pushed += 1
                    except Exception as frame_err:
                        logger.debug(f"Audio frame capture notice: {frame_err}")

                    # Smooth 8ms pacing for WebRTC audio queue (prevents buffer underruns & sleep spikes)
                    await asyncio.sleep(0.008)

            # Pad residual bytes cleanly for the final frame
            if audio_buffer and not self._is_interrupted:
                if len(audio_buffer) % 2 != 0:
                    audio_buffer += b'\x00'
                if len(audio_buffer) < BYTES_PER_FRAME:
                    audio_buffer += b'\x00' * (BYTES_PER_FRAME - len(audio_buffer))

                frame_data = audio_buffer[:BYTES_PER_FRAME]
                frame = rtc.AudioFrame(
                    data=frame_data,
                    sample_rate=self.sample_rate,
                    num_channels=self.num_channels,
                    samples_per_channel=SAMPLES_PER_FRAME
                )
                try:
                    await self.audio_source.capture_frame(frame)
                    await asyncio.sleep(0.008)
                except Exception:
                    pass

                frame_data = audio_buffer[:BYTES_PER_FRAME]
                frame = rtc.AudioFrame(
                    data=frame_data,
                    sample_rate=self.sample_rate,
                    num_channels=self.num_channels,
                    samples_per_channel=SAMPLES_PER_FRAME
                )
                try:
                    await self.audio_source.capture_frame(frame)
                    frames_pushed += 1
                except Exception:
                    pass

                target_time = playback_start + (frames_pushed * 0.010)
                sleep_time = target_time - time.time()
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

        except Exception as e:
            logger.error(f"TTS error: {e}", exc_info=True)
        finally:
            self._is_bot_speaking = False

    async def send_text_to_frontend(self, text: str, sender: str, is_stream: bool = False):
        import json
        payload = json.dumps({"sender": sender, "text": text, "is_stream": is_stream}).encode("utf-8")
        if self.room.local_participant:
            await self.room.local_participant.publish_data(payload)

    async def trigger_first_message(self):
        try:
            # Give student browser 1.0s to complete WebRTC audio track subscription
            await asyncio.sleep(1.0)

            student_name = None
            if self.state_manager and self.state_manager.state and "A01" in self.state_manager.state.answers:
                ans = self.state_manager.state.answers["A01"]
                student_name = getattr(ans, 'normalized_answer', None) or getattr(ans, 'raw_response', None)

            await self.send_text_to_frontend("", "AI", is_stream=False)
            full_opening = ""
            async for chunk in self.llm.stream_opening_message(student_name=student_name):
                full_opening += chunk
                await self.send_text_to_frontend(chunk, "AI", is_stream=True)
            
            if full_opening:
                await self._speak(full_opening)
                self.memory_manager.add_ai_turn(full_opening)

        except Exception as e:
            logger.error(f"Error during first message: {e}", exc_info=True)
