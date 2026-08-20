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

    def start_survey(self):
        if not self.state.current_question:
            first_q = self.questionnaire.get_first_question()
            self.state.current_question = first_q.id
            self.state.status = "in_progress"
            logger.info(f"Survey started. First question: {first_q.id}")
            self.save_state()

    def save_state(self):
        os.makedirs("data", exist_ok=True)
        file_path = f"data/{self.session_id}_assessment.json"
        with open(file_path, "w", encoding="utf-8") as f:
            # Pydantic v2 support; fallback to json() if needed
            if hasattr(self.state, "model_dump_json"):
                f.write(self.state.model_dump_json(indent=2))
            else:
                f.write(self.state.json(indent=2))

    def get_current_question(self):
        if not self.state.current_question:
            return None
        return self.questionnaire.get_question(self.state.current_question)

    def apply_llm_response(self, llm_resp: ConversationalResponse):
        """Advances state based on LLM decision."""
        # Intercept FOLLOWUP if depth limit reached (per-question max_followups or default 3)
        current_q = self.get_current_question()
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
            # Similar logic based on your detailed rules...
            # For brevity, basic advancement on skip/complete
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

    def apply_extraction(self, question_id: str, extraction_resp: ExtractionResponse, raw_text: str, turn_id: int):
        if extraction_resp.answer and extraction_resp.answer_status == "answered":
            self.state.answers[question_id] = Answer(
                question_id=question_id,
                raw_response=raw_text,
                normalized_answer=extraction_resp.answer.value,
                confidence=extraction_resp.answer.confidence,
                turn_id=turn_id
            )
            logger.info(f"Background Extraction saved for {question_id}: {extraction_resp.answer.value}")
            self.save_state()
