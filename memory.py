import os
import json
from typing import List
from schemas import TranscriptTurn, SurveyState, Question

class MemoryManager:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.transcript: List[TranscriptTurn] = []
        self.turn_counter = 0

    def add_student_turn(self, text: str) -> int:
        self.turn_counter += 1
        self.transcript.append(TranscriptTurn(
            session_id=self.session_id,
            turn_id=self.turn_counter,
            speaker="student",
            text=text
        ))
        self.save_transcript()
        return self.turn_counter

    def add_ai_turn(self, text: str):
        self.turn_counter += 1
        self.transcript.append(TranscriptTurn(
            session_id=self.session_id,
            turn_id=self.turn_counter,
            speaker="assistant",
            text=text
        ))
        self.save_transcript()

    def save_transcript(self):
        os.makedirs("data", exist_ok=True)
        file_path = f"data/{self.session_id}_conversation.json"
        
        # Pydantic v2 support; fallback to dict() if needed
        data = []
        for turn in self.transcript:
            if hasattr(turn, "model_dump"):
                data.append(turn.model_dump())
            else:
                data.append(turn.dict())
                
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_recent_turns(self, count: int = 6) -> str:
        recent = self.transcript[-count:] if self.transcript else []
        lines = []
        for turn in recent:
            lines.append(f"{turn.speaker.upper()}: {turn.text}")
        return "\n".join(lines)

    def build_llm_prompt(self, state: SurveyState, current_question: Question) -> str:
        prompt = "SYSTEM RULES\n"
        prompt += "You are an AI-powered voice survey interviewer conducting a survey with a Grade 7-8 student.\n"
        prompt += "Ask one question at a time. Do not answer for the student. Be friendly and conversational.\n\n"
        
        prompt += "CURRENT SURVEY STATE\n"
        prompt += f"Status: {state.status}\n"
        prompt += f"Completed Questions: {', '.join(state.completed_questions)}\n\n"
        
        if current_question:
            prompt += "CURRENT QUESTION TO ASK OR CLARIFY\n"
            prompt += f"Question ID: {current_question.id}\n"
            prompt += f"Text: {current_question.text}\n"
            if current_question.options:
                prompt += f"Options: {', '.join(current_question.options)}\n"
            prompt += "\n"
        
        prompt += "RECENT CONVERSATION\n"
        prompt += self.get_recent_turns(8) + "\n\n"
        
        prompt += """INSTRUCTIONS FOR YOUR RESPONSE:
You MUST output ONLY a valid JSON object. No markdown blocks, no other text.
The JSON must follow this exact schema:
{
  "action": "NEXT_QUESTION" | "ASK" | "CLARIFY" | "REPEAT" | "SKIP" | "COMPLETE",
  "answer_status": "answered" | "ambiguous" | "unknown" | "refused" | "pending",
  "answer": {
    "value": "normalized answer string",
    "confidence": 0.95
  } or null,
  "response": "The exact natural spoken response you will say to the student."
}
"""
        return prompt
