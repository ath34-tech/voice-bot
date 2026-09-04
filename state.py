import os
import json
import logging
from typing import Optional
from schemas import SurveyState, Answer, ConversationalResponse, ExtractionResponse
from questionnaire import Questionnaire

logger = logging.getLogger(__name__)

class StateManager:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = SurveyState(session_id=session_id)
        self.questionnaire = Questionnaire()
        self.start_survey()

    def start_survey(self, student_name: str = None, student_grade: str = None):
        if not self.state.current_question:
            # Auto-fill A01 (Name) and A03 (Class) as they are pre-known from frontend
            if "A01" not in self.state.completed_questions:
                self.state.completed_questions.append("A01")
                self.state.answers["A01"] = Answer(
                    question_id="A01",
                    raw_response=student_name or "Student",
                    normalized_answer=student_name or "Student",
                    confidence=1.0,
                    turn_id=0
                )
            if "A03" not in self.state.completed_questions:
                self.state.completed_questions.append("A03")
                self.state.answers["A03"] = Answer(
                    question_id="A03",
                    raw_response=student_grade or "Grade 8",
                    normalized_answer=student_grade or "Grade 8",
                    confidence=1.0,
                    turn_id=0
                )

            # First question asked to the student is A04 (Percentage marks)
            self.state.current_question = "A04"
            self.state.status = "in_progress"
            logger.info(f"Survey started. Pre-filled A01/A03. First active question: A04")
            self.save_state()

    def save_state(self):
        # 1. Sync session state to database
        try:
            answers_dict = {}
            for q_id, ans in self.state.answers.items():
                if hasattr(ans, "model_dump"):
                    answers_dict[q_id] = ans.model_dump()
                else:
                    answers_dict[q_id] = ans.dict()

            import asyncio
            import database
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(database.save_session_state_async(
                        session_id=self.session_id,
                        extracted_answers=answers_dict,
                        status=self.state.status,
                        current_question_id=self.state.current_question
                    ))
            except Exception:
                pass
        except Exception as e:
            logger.debug(f"Database state sync notice: {e}")

        # 2. Sync to file
        try:
            os.makedirs("data", exist_ok=True)
            file_path = f"data/{self.session_id}_assessment.json"
            with open(file_path, "w", encoding="utf-8") as f:
                if hasattr(self.state, "model_dump_json"):
                    f.write(self.state.model_dump_json(indent=2))
                else:
                    f.write(self.state.json(indent=2))
        except Exception:
            pass

    def get_current_question(self):
        if not self.state.current_question:
            return None
        return self.questionnaire.get_question(self.state.current_question)

    def apply_llm_response(self, llm_resp: ConversationalResponse):
        """Advances state based on LLM decision, enforcing answer locking before question progression."""
        current_q = self.get_current_question()

        # Safety Guard: Do not allow premature NEXT_QUESTION if answer is not locked and clarification limit not reached
        if llm_resp.action == "NEXT_QUESTION" and current_q:
            q_id = current_q.id
            if q_id not in self.state.answers and self.state.clarification_attempts < 2:
                logger.warning(
                    f"⚠️ Preventing premature NEXT_QUESTION for {q_id}: Answer is not locked in state "
                    f"and clarification attempts ({self.state.clarification_attempts}) < 2. Overriding action to CLARIFY."
                )
                llm_resp.action = "CLARIFY"
                self.state.clarification_attempts += 1
                if not llm_resp.response or "next" in llm_resp.response.lower() or "अगला" in llm_resp.response:
                    llm_resp.response = f"माफ़ कीजिये, मुझे आपका उत्तर समझ नहीं आया। {current_q.text}"
                self.save_state()
                return

        # Intercept FOLLOWUP if depth limit reached (per-question max_followups or default 3)
        max_depth = (current_q.max_followups if current_q and current_q.max_followups is not None else 3)
        if llm_resp.action == "FOLLOWUP":
            if self.state.followup_depth >= max_depth:
                logger.info(f"Max followup depth ({max_depth}) reached for {self.state.current_question}. Forcing NEXT_QUESTION.")
                llm_resp.action = "NEXT_QUESTION"

        if llm_resp.action == "NEXT_QUESTION":
            # Reset followup state
            self.state.is_in_followup = False
            self.state.followup_depth = 0
            
            if self.state.current_question:
                if self.state.current_question not in self.state.completed_questions:
                    self.state.completed_questions.append(self.state.current_question)
            
            # Advance to next question
            next_q = self.questionnaire.get_next_question(self.state.current_question)
            if next_q:
                self.state.current_question = next_q.id
                self.state.clarification_attempts = 0
                logger.info(f"Advanced to next question: {next_q.id}")
            else:
                self.state.current_question = None
                self.state.status = "completed"
                logger.info("Survey completed.")

        elif llm_resp.action == "ASK":
            logger.info(f"LLM asked/re-asked the current question: {self.state.current_question}")

        elif llm_resp.action == "FOLLOWUP":
            self.state.is_in_followup = True
            self.state.followup_depth += 1
            logger.info(f"Diverging to FOLLOWUP branch (Depth: {self.state.followup_depth})")

        elif llm_resp.action == "CLARIFY":
            self.state.clarification_attempts += 1
            logger.info(f"Clarification attempt {self.state.clarification_attempts}")
            if self.state.clarification_attempts >= 2:
                logger.info("Max clarification reached. Skipping question.")
                # Force next question
                next_q = self.questionnaire.get_next_question(self.state.current_question)
                if next_q:
                    self.state.current_question = next_q.id
                    self.state.clarification_attempts = 0
                else:
                    self.state.current_question = None
                    self.state.status = "completed"

        elif llm_resp.action == "SKIP" or llm_resp.action == "ERROR" or llm_resp.action == "COMPLETE":
            if llm_resp.action == "SKIP":
                next_q = self.questionnaire.get_next_question(self.state.current_question)
                if next_q:
                    self.state.current_question = next_q.id
                    self.state.clarification_attempts = 0
                else:
                    self.state.current_question = None
                    self.state.status = "completed"
            elif llm_resp.action == "COMPLETE":
                self.state.current_question = None
                self.state.status = "completed"

        # "REPEAT" does nothing to the state.
        self.save_state()

    def apply_extraction(self, question_id: str, extraction_resp: ExtractionResponse, raw_text: str, turn_id: int) -> bool:
        if not extraction_resp:
            return False

        if extraction_resp.answer and extraction_resp.answer_status == "answered" and extraction_resp.answer.value:
            val = str(extraction_resp.answer.value).strip()
            if val:
                if question_id in self.state.answers and self.state.is_in_followup:
                    existing = self.state.answers[question_id]
                    existing.raw_response += f" | Followup: {raw_text}"
                    existing.normalized_answer = f"{existing.normalized_answer} (Followup: {val})"
                else:
                    self.state.answers[question_id] = Answer(
                        question_id=question_id,
                        raw_response=raw_text,
                        normalized_answer=val,
                        confidence=extraction_resp.answer.confidence or 0.95,
                        turn_id=turn_id
                    )
                logger.info(f"✅ Answer LOCKED for {question_id}: {self.state.answers[question_id].normalized_answer}")
                self.save_state()
                return True

        logger.warning(f"⚠️ Extraction for {question_id} not locked (Status: {extraction_resp.answer_status if extraction_resp else 'None'})")
        return False

