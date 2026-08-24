import asyncio
import logging
import os
import sys
from livekit import api
from config import settings
from rooms import LiveKitClient
from pipeline import Pipeline
import database

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger("bodh_agent")


async def start_health_server():
    """Lightweight HTTP health check server with auto-heartbeat to keep Render service awake 24/7."""
    port = int(os.getenv("PORT", "10000"))
    try:
        from aiohttp import web, ClientSession
        async def handle_health(request):
            return web.Response(text="OK - Bodh Agent Live")
        app = web.Application()
        app.router.add_get("/", handle_health)
        app.router.add_get("/health", handle_health)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        logger.info(f"Health check HTTP server listening on port {port}")

        # Self-ping heartbeat loop every 3 minutes to keep Render Free Tier 100% active
        async def heartbeat_loop():
            await asyncio.sleep(15)
            while True:
                try:
                    async with ClientSession() as session:
                        await session.get(f"http://127.0.0.1:{port}/", timeout=5)
                except Exception:
                    pass
                await asyncio.sleep(180)

        asyncio.create_task(heartbeat_loop())
    except Exception as e:
        logger.debug(f"Health server notice: {e}")


class MultiRoomAgentManager:
    """
    Production Multi-Room Manager:
    Monitors LiveKit Cloud for active student rooms and spawns an AI Voice Bot for each room automatically!
    Supports UNLIMITED concurrent students simultaneously.
    """
    def __init__(self):
        self.active_bots = {}

    async def run(self):
        logger.info(f"🚀 Starting Bodh Multi-Room Agent Worker connected to {settings.LIVEKIT_URL}...")
        await database.init_db()
        asyncio.create_task(start_health_server())

        # Convert wss:// or ws:// to https:// or http:// for LiveKit Server REST API
        api_url = settings.LIVEKIT_URL
        if api_url.startswith("wss://"):
            api_url = api_url.replace("wss://", "https://", 1)
        elif api_url.startswith("ws://"):
            api_url = api_url.replace("ws://", "http://", 1)

        lk_api = api.LiveKitAPI(
            api_url,
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET
        )

        logger.info("✅ Multi-Room Manager active! Monitoring rooms on LiveKit Cloud...")

        while True:
            try:
                api_url = settings.LIVEKIT_URL
                if api_url.startswith("wss://"):
                    api_url = api_url.replace("wss://", "https://", 1)
                elif api_url.startswith("ws://"):
                    api_url = api_url.replace("ws://", "http://", 1)

                lk_api = api.LiveKitAPI(
                    api_url,
                    settings.LIVEKIT_API_KEY,
                    settings.LIVEKIT_API_SECRET
                )
                try:
                    res = await lk_api.room.list_rooms(api.ListRoomsRequest())
                    # Detect any active student survey room (chat-xxxx)
                    active_room_names = [r.name for r in res.rooms if r.name.startswith("chat-")]

                    # 1. Spawn AI Bot for any newly detected active student room
                    for r_name in active_room_names:
                        if r_name not in self.active_bots:
                            logger.info(f"⚡ New student room detected: '{r_name}'! Spawning AI Voice Bot...")
                            try:
                                client = LiveKitClient()
                                client.pipeline = Pipeline(client.room, session_id=r_name)
                                await client.pipeline.start()
                                await client.connect(r_name)
                                await client.pipeline.publish_bot_track()
                                self.active_bots[r_name] = client
                                logger.info(f"✅ AI Voice Bot successfully joined room: '{r_name}'")
                                # Trigger greeting if student is already in the room
                                if len(client.room.remote_participants) > 0 and not getattr(client.pipeline, "_has_greeted", False):
                                    client.pipeline._has_greeted = True
                                    logger.info(f"🔊 Student present! Triggering opening greeting for room '{r_name}'...")
                                    asyncio.create_task(client.pipeline.trigger_first_message())
                            except Exception as spawn_err:
                                logger.error(f"Error spawning bot for room '{r_name}': {spawn_err}")

                    # 2. Cleanup AI Bot when room closes
                    dead_rooms = [r for r in self.active_bots if r not in active_room_names]
                    for r_name in dead_rooms:
                        logger.info(f"🧹 Room '{r_name}' ended. Cleaning up AI Bot...")
                        bot = self.active_bots.pop(r_name, None)
                        if bot:
                            await bot.shutdown()
                finally:
                    await lk_api.aclose()

            except Exception as loop_err:
                logger.error(f"Room monitor loop notice: {loop_err}")

            await asyncio.sleep(2)


if __name__ == "__main__":
    manager = MultiRoomAgentManager()
    try:
        asyncio.run(manager.run())
    except KeyboardInterrupt:
        logger.info("Shutting down Bodh Multi-Room Agent Manager...")
