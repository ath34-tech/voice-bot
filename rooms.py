import asyncio

from livekit import rtc, api
from config import settings


class LiveKitClient:
    def __init__(self):
        self.room = rtc.Room()
        self.pipeline = None
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

        @self.room.on("participant_disconnected")
        def on_participant_disconnected(participant: rtc.RemoteParticipant):
            print(f"Participant left: {participant.identity}")
            # Automatically self-destruct the bot if the human leaves the room!
            if len(self.room.remote_participants) == 0:
                print(f"Room empty. Shutting down bot for room {self.room.name}...")
                asyncio.create_task(self.shutdown())

        @self.room.on("track_published")
        def on_track_published(publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
            print(f"Track published: {publication.sid} by {participant.identity}")

        @self.room.on("track_subscribed")
        def on_track_subscribed(track: rtc.Track, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
            print(f"Track subscribed: {track.sid}")
            if track.kind == rtc.TrackKind.KIND_AUDIO:
                print("Subscribed to remote microphone track.")
                self._start_audio_stream(track)

    def _start_audio_stream(self, track: rtc.RemoteAudioTrack):
        # We MUST force the AudioStream to resample the audio to 48kHz / 1 channel!
        # If the browser negotiates a different sample rate, Deepgram will fail to recognize the audio!
        audio_stream = rtc.AudioStream(track, sample_rate=48000, num_channels=1)
        
        async def _read_audio():
            async for event in audio_stream:
                if self.pipeline:
                    await self.pipeline.handle_audio_frame(event.frame)
                    
        asyncio.create_task(_read_audio())

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

    async def shutdown(self):
        """Cleanly stops the AI pipeline and disconnects the bot from the room."""
        if self.pipeline:
            await self.pipeline.stop()
        await self.room.disconnect()
        print(f"Bot disconnected from {self.room.name}.")
