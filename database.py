import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import Column, String, DateTime, Text, JSON, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from config import settings

logger = logging.getLogger(__name__)

# Normalize DATABASE_URL for SQLAlchemy async drivers
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif db_url.startswith("sqlite://") and not db_url.startswith("sqlite+aiosqlite://"):
    db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

engine = create_async_engine(
    db_url,
    echo=False,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


class Student(Base):
    __tablename__ = "students"

    student_id = Column(String(64), primary_key=True, index=True)
    school_code = Column(String(32), index=True, nullable=False)
    name = Column(String(128), nullable=False)
    grade = Column(String(32), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SurveySession(Base):
    __tablename__ = "survey_sessions"

    session_id = Column(String(64), primary_key=True, index=True)
    student_id = Column(String(64), index=True, nullable=False)
    school_code = Column(String(32), index=True, nullable=False)
    status = Column(String(32), default="in_progress")  # 'in_progress' | 'completed'
    current_question_id = Column(String(32), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    extracted_answers = Column(JSON, default=dict)
    transcript = Column(JSON, default=list)


async def init_db():
    """Creates database tables if they do not exist."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)


async def save_or_update_student_async(student_id: str, school_code: str, name: str, grade: str):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Student).where(Student.student_id == student_id))
            student = result.scalar_one_or_none()
            if student:
                student.school_code = school_code
                student.name = name
                student.grade = grade
            else:
                student = Student(
                    student_id=student_id,
                    school_code=school_code,
                    name=name,
                    grade=grade
                )
                session.add(student)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Error saving student {student_id}: {e}")


async def create_survey_session_async(session_id: str, student_id: str, school_code: str, current_question_id: Optional[str] = None):
    async with AsyncSessionLocal() as session:
        try:
            survey = SurveySession(
                session_id=session_id,
                student_id=student_id,
                school_code=school_code,
                status="in_progress",
                current_question_id=current_question_id,
                started_at=datetime.utcnow(),
                extracted_answers={},
                transcript=[]
            )
            session.add(survey)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating survey session {session_id}: {e}")


async def save_session_state_async(session_id: str, extracted_answers: Dict[str, Any], status: str = "in_progress", current_question_id: Optional[str] = None):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(SurveySession).where(SurveySession.session_id == session_id))
            survey = result.scalar_one_or_none()
            if survey:
                survey.extracted_answers = extracted_answers
                survey.status = status
                if current_question_id:
                    survey.current_question_id = current_question_id
                if status == "completed":
                    survey.completed_at = datetime.utcnow()
                await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating session state for {session_id}: {e}")


async def append_transcript_turn_async(session_id: str, sender: str, text: str):
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(SurveySession).where(SurveySession.session_id == session_id))
            survey = result.scalar_one_or_none()
            if survey:
                current_transcript = list(survey.transcript or [])
                current_transcript.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "sender": sender,
                    "text": text
                })
                survey.transcript = current_transcript
                await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Error appending transcript to session {session_id}: {e}")


async def get_survey_session_async(session_id: str) -> Optional[Dict[str, Any]]:
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(SurveySession).where(SurveySession.session_id == session_id))
            survey = result.scalar_one_or_none()
            if not survey:
                return None

            student_res = await session.execute(select(Student).where(Student.student_id == survey.student_id))
            student = student_res.scalar_one_or_none()

            return {
                "session_id": survey.session_id,
                "student_id": survey.student_id,
                "student_name": student.name if student else "Student",
                "student_grade": student.grade if student else "Grade 8",
                "school_code": survey.school_code,
                "status": survey.status,
                "current_question_id": survey.current_question_id,
                "started_at": survey.started_at.isoformat() if survey.started_at else None,
                "completed_at": survey.completed_at.isoformat() if survey.completed_at else None,
                "extracted_answers": survey.extracted_answers or {},
                "transcript": survey.transcript or []
            }
        except Exception as e:
            logger.error(f"Error getting survey session {session_id}: {e}")
            return None


# Sync wrappers for synchronous callers
def save_or_update_student(student_id: str, school_code: str, name: str, grade: str):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(save_or_update_student_async(student_id, school_code, name, grade))
        else:
            loop.run_until_complete(save_or_update_student_async(student_id, school_code, name, grade))
    except Exception:
        pass


def create_survey_session(session_id: str, student_id: str, school_code: str, current_question_id: Optional[str] = None):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(create_survey_session_async(session_id, student_id, school_code, current_question_id))
        else:
            loop.run_until_complete(create_survey_session_async(session_id, student_id, school_code, current_question_id))
    except Exception:
        pass


def get_survey_session(session_id: str):
    try:
        return asyncio.run(get_survey_session_async(session_id))
    except Exception:
        return None
