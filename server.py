import uuid
import logging
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from livekit import api

from config import settings
from questionnaire import get_questionnaire_for_school
import database

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger("bodh_api")

app = FastAPI(
    title="Bodh AI Voice Survey API",
    description="FastAPI Web Service for session management and LiveKit token generation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


_lk_api: Optional[api.LiveKitAPI] = None

def get_lk_api() -> Optional[api.LiveKitAPI]:
    global _lk_api
    if _lk_api is None:
        try:
            api_url = settings.LIVEKIT_URL
            if api_url.startswith("wss://"):
                api_url = api_url.replace("wss://", "https://", 1)
            elif api_url.startswith("ws://"):
                api_url = api_url.replace("ws://", "http://", 1)
            _lk_api = api.LiveKitAPI(api_url, settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET)
        except Exception as e:
            logger.warning(f"LiveKitAPI client init notice: {e}")
    return _lk_api


@app.on_event("startup")
async def on_startup():
    logger.info("Initializing database connection...")
    await database.init_db()
    key_snippet = (settings.LIVEKIT_API_KEY[:6] + "...") if settings.LIVEKIT_API_KEY else "NONE"
    logger.info(f"🔑 Bodh API Server started! LiveKit URL={settings.LIVEKIT_URL}, Key={key_snippet}")


@app.on_event("shutdown")
async def on_shutdown():
    global _lk_api
    if _lk_api is not None:
        try:
            await _lk_api.aclose()
        except Exception:
            pass
        _lk_api = None


class StartCallRequest(BaseModel):
    school_code: Optional[str] = Field(default="DEFAULT", description="Unique school identification code")
    student_id: Optional[str] = Field(default=None, description="Optional unique student ID")
    name: Optional[str] = Field(default="Student", description="Student's name")
    grade: Optional[str] = Field(default="Grade 8", description="Student's grade or class level")


class CallResponse(BaseModel):
    room_name: str
    token: str
    ws_url: str
    user_token: str
    livekit_url: str


async def _notify_agent_to_spawn(room_name: str):
    """Notifies agent worker to spawn a bot for room_name, avoiding self-looping on the API port."""
    import os, aiohttp
    my_port = os.getenv("PORT", "8000")
    urls_to_try = [
        os.getenv("AGENT_URL"),
        "http://bodh-agent:10000",
        "http://bodh-agent:8000",
        "http://127.0.0.1:10001",
    ]
    # Filter out empty entries and any loopback URL pointing to self (same port as API)
    target_urls = []
    for u in urls_to_try:
        if u:
            clean_u = u.rstrip("/")
            if f":{my_port}" in clean_u and ("127.0.0.1" in clean_u or "localhost" in clean_u):
                continue  # Skip self-looping call to API server port
            if clean_u not in target_urls:
                target_urls.append(clean_u)

    for base_url in target_urls:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{base_url}/spawn_bot", json={"room_name": room_name}, timeout=2.0) as resp:
                    if resp.status == 200:
                        logger.info(f"⚡ Dispatched direct spawn signal for room '{room_name}' to {base_url}")
                        return
        except Exception:
            pass
    logger.debug(f"Direct agent notification attempted ({target_urls}) — falling back to LiveKit Cloud polling.")


@app.post("/spawn_bot")
async def spawn_bot_proxy(payload: Dict[str, Any]):
    """Proxies direct spawn requests to the background agent worker service."""
    room_name = payload.get("room_name")
    if not room_name:
        raise HTTPException(status_code=400, detail="Missing room_name parameter")

    agent_url = os.getenv("AGENT_URL", "http://bodh-agent:10000").rstrip("/")
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{agent_url}/spawn_bot", json={"room_name": room_name}, timeout=3.0) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
                else:
                    err_txt = await resp.text()
                    logger.warning(f"Agent worker returned {resp.status}: {err_txt}")
                    return {"status": "error", "detail": err_txt}
    except Exception as e:
        logger.error(f"Error forwarding /spawn_bot to agent worker at {agent_url}: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to reach agent worker: {str(e)}")


def generate_user_token(room_name: str, identity: str = "human-user") -> str:
    """Generates a secure LiveKit JWT Access Token for the client."""
    if not settings.LIVEKIT_API_KEY or not settings.LIVEKIT_API_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LiveKit API key or secret is not configured on the server."
        )

    return (
        api.AccessToken(
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET,
        )
        .with_identity(identity)
        .with_name("Human")
        .with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True
        ))
        .to_jwt()
    )


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Liveness health check endpoint for Render monitoring."""
    return {"status": "ok", "app": "bodh-api", "environment": settings.APP_ENV}


@app.post("/start_call", response_model=CallResponse, status_code=status.HTTP_201_CREATED)
async def start_call(req: Optional[StartCallRequest] = None):
    """
    Creates a new survey interview session:
    1. Validates student and school information.
    2. Persists student & session records in PostgreSQL / SQLite.
    3. Generates a unique LiveKit room name on LiveKit Cloud.
    4. Generates a secure LiveKit JWT access token for the client.
    """
    try:
        body = req if req is not None else StartCallRequest()
        school_code = (body.school_code or "DEFAULT").strip().upper()
        student_id = (body.student_id or f"STU-{uuid.uuid4().hex[:6].upper()}").strip()
        name = (body.name or "Student").strip()
        grade = (body.grade or "Grade 8").strip()

        # 1. Save Student and Survey Session in Database
        await database.save_or_update_student_async(student_id, school_code, name, grade)

        import uuid
        room_name = f"chat-{uuid.uuid4().hex[:8]}"
        q_engine = get_questionnaire_for_school(school_code)
        first_q = q_engine.get_first_question()

        await database.create_survey_session_async(
            session_id=room_name,
            student_id=student_id,
            school_code=school_code,
            current_question_id=first_q.id if first_q else None
        )

        # 2. Explicitly create room on LiveKit Cloud
        try:
            lk_client = get_lk_api()
            if lk_client:
                await lk_client.room.create_room(api.CreateRoomRequest(name=room_name))
        except Exception as room_err:
            logger.debug(f"LiveKit room creation notice: {room_err}")

        # 3. Notify Agent Worker to spawn bot instance immediately
        await _notify_agent_to_spawn(room_name)

        # 4. Generate Client LiveKit Access Token
        user_token = generate_user_token(room_name)

        logger.info(
            f"Session created: room={room_name}, student_id={student_id}, "
            f"school={school_code}, student_name='{name}'"
        )

        return CallResponse(
            room_name=room_name,
            token=user_token,
            ws_url=settings.LIVEKIT_URL,
            user_token=user_token,
            livekit_url=settings.LIVEKIT_URL
        )



    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating session in /start_call: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start call session: {str(e)}"
        )


@app.get("/api/questionnaire/{school_code}")
async def get_school_questionnaire(school_code: str):
    """
    Returns question bank & category schema for a given school code.
    """
    code = school_code.strip().upper()
    q_engine = get_questionnaire_for_school(code)
    return {
        "school_code": code,
        "questionnaire": q_engine.export_schema_for_frontend()
    }


@app.get("/api/session/{session_id}")
async def get_session_details(session_id: str):
    """
    Returns full live survey session data from the database.
    """
    session_data = await database.get_survey_session_async(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Survey session '{session_id}' not found."
        )
    return session_data
