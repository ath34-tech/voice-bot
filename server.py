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


@app.on_event("startup")
async def on_startup():
    logger.info("Initializing database connection...")
    await database.init_db()
    logger.info("Bodh API Server started successfully.")


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
    3. Generates a unique LiveKit room name.
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

        # 2. Generate Client LiveKit Token
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
