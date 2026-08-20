from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal


class Question(BaseModel):
    id: str
    text: str
    type: Literal["free_text", "single_choice", "multi_choice", "numeric", "numeric / approximate", "numeric / free_text", "yes_no + qualitative_followup", "categorical", "free_text / categorical"]
    options: Optional[List[str]] = None
    expected_target: Optional[str] = None
    allow_followup: bool = True
    max_followups: Optional[int] = None


class AnswerData(BaseModel):
    value: Optional[str] = None
    confidence: Optional[float] = None


class Answer(BaseModel):
    question_id: str
    raw_response: str
    normalized_answer: Optional[str] = None
    confidence: Optional[float] = None
    turn_id: int


class TranscriptTurn(BaseModel):
    session_id: str
    turn_id: int
    speaker: Literal["student", "assistant"]
    text: str


class SurveyState(BaseModel):
    session_id: str
    survey_version: str = "v1"
    status: Literal["created", "in_progress", "completed", "failed"] = "created"
    current_question: Optional[str] = None
    completed_questions: List[str] = Field(default_factory=list)
    answers: Dict[str, Answer] = Field(default_factory=dict)
    clarification_attempts: int = 0
    is_in_followup: bool = False
    followup_depth: int = 0


class ConversationalResponse(BaseModel):
    action: Literal["NEXT_QUESTION", "ASK", "CLARIFY", "FOLLOWUP", "REPEAT", "SKIP", "COMPLETE", "ERROR"]
    response: str  # The text to be spoken

class ExtractionResponse(BaseModel):
    answer_status: Literal["answered", "ambiguous", "unknown", "refused", "pending"]
    answer: Optional[AnswerData] = None
