import asyncio

from livekit import rtc, api
from config import settings


class LiveKitClient:
    def __init__(self):
        self.room = rtc.Room()
        self.pipeline = None
        self._audio_stream = None
        self._audio_task = None
        self._setup_event_listeners()

    def _setup_event_listeners(self):
        @self.room.on("connected")
        def on_connected():
            print("Room connected event fired!")

        @self.room.on("disconnected")
        def on_disconnected():
            print("Disconnected from LiveKit room.")

        @self.room.on("participant_connected")
        def on_participant_connected(participant: rtc.RemoteParticipant):
            print(f"Participant joined: {participant.identity}")
            if self.pipeline and not getattr(self.pipeline, "_has_greeted", False):
                self.pipeline._has_greeted = True
                asyncio.create_task(self.pipeline.trigger_first_message())

        @self.room.on("participant_disconnected")
        def on_participant_disconnected(participant: rtc.RemoteParticipant):
            print(f"Participant left: {participant.identity}")
            if len(self.room.remote_participants) == 0:
                print(f"Room empty. Resetting bot greeting state for room {self.room.name}...")
                if self.pipeline:
                    self.pipeline._has_greeted = False

        @self.room.on("track_published")
        def on_track_published(publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
            print(f"Track published: {publication.sid} by {participant.identity}")
            try:
                publication.set_subscribed(True)
            except Exception as e:
                print(f"Notice setting subscription: {e}")

        @self.room.on("track_subscribed")
        def on_track_subscribed(track: rtc.Track, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
            print(f"Track subscribed: {track.sid}")
            if track.kind == rtc.TrackKind.KIND_AUDIO:
                print("Subscribed to remote microphone track.")
                self._start_audio_stream(track)
                if self.pipeline and not getattr(self.pipeline, "_has_greeted", False):
                    self.pipeline._has_greeted = True
                    print(f"🔊 Microphone track subscribed! Triggering opening greeting...")
                    asyncio.create_task(self.pipeline.trigger_first_message())

    def _start_audio_stream(self, track: rtc.RemoteAudioTrack):
        # Force AudioStream to resample audio to 48kHz / 1 channel
        self._audio_stream = rtc.AudioStream(track, sample_rate=48000, num_channels=1)
        
        async def _read_audio():
            try:
                async for event in self._audio_stream:
                    if self.pipeline:
                        await self.pipeline.handle_audio_frame(event.frame)
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"Audio stream closed: {e}")

        self._audio_task = asyncio.create_task(_read_audio())

    def _create_token(self, room_name: str) -> str:
        return (
            api.AccessToken(
                settings.LIVEKIT_API_KEY,
                settings.LIVEKIT_API_SECRET,
            )
            .with_identity(f"backend-bot-{room_name}")
            .with_name(settings.BOT_NAME)
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room_name,
                )
            )
            .to_jwt()
        )

    async def connect(self, room_name: str):
        token = self._create_token(room_name)

        print(f"Connecting bot to dynamic room: {room_name}...")

        await self.room.connect(
            settings.LIVEKIT_URL,
            token,
        )

        print(f"Bot successfully connected to {self.room.name}!")

        # Subscribe to any existing remote microphone tracks
        for participant in self.room.remote_participants.values():
            for pub in participant.track_publications.values():
                if pub.track and pub.track.kind == rtc.TrackKind.KIND_AUDIO:
                    print(f"Subscribing to existing microphone track from {participant.identity}...")
                    self._start_audio_stream(pub.track)

    async def shutdown(self):
        """Cleanly stops the AI pipeline and disconnects the bot from the room."""
        if self._audio_task and not self._audio_task.done():
            self._audio_task.cancel()
        if self._audio_stream:
            await self._audio_stream.aclose()
        if self.pipeline:
            await self.pipeline.stop()
        await self.room.disconnect()
        print(f"Bot disconnected from {self.room.name}.")
