import os
import json
from typing import List
from config import settings
import database
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
        storage_mode = getattr(settings, 'TRANSCRIPT_STORAGE', 'database').lower()

        # 1. Database Transcript Sync
        if storage_mode in ('database', 'both'):
            if self.transcript:
                latest_turn = self.transcript[-1]
                try:
                    import asyncio
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(database.append_transcript_turn_async(
                            session_id=self.session_id,
                            sender=latest_turn.speaker,
                            text=latest_turn.text
                        ))
                except Exception:
                    pass

        # 2. File Transcript Sync
        if storage_mode in ('file', 'both'):
            try:
                os.makedirs("data", exist_ok=True)
                file_path = f"data/{self.session_id}_conversation.json"
                data = []
                for turn in self.transcript:
                    if hasattr(turn, "model_dump"):
                        data.append(turn.model_dump())
                    else:
                        data.append(turn.dict())
                        
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                pass

    def get_recent_turns(self, count: int = 6) -> str:
        recent = self.transcript[-count:] if self.transcript else []
        lines = []
        for turn in recent:
            lines.append(f"{turn.speaker.upper()}: {turn.text}")
        return "\n".join(lines)

    def build_llm_prompt(self, state: SurveyState, current_question: Question, next_question: Question = None) -> str:
        prompt = "SYSTEM & PERSONA RULES\n"
        prompt += "You are a warm, supportive FEMALE AI voice interviewer named Bodh (बोध) interviewing a Grade 7-8 student in India.\n"
        prompt += "GENDER RULE: Always use FEMALE Hindi grammar when referring to yourself (e.g., 'मैं आपकी AI interviewer हूँ', 'मैं समझ सकती हूँ', 'मैं पूछ रही हूँ').\n"
        prompt += "STUDENT GENDER AUTO-DETECTION: Automatically infer the student's gender from their name, speech context, or voice cues. When addressing the student, dynamically adapt your Hindi grammar and polite forms appropriately without rigid stereotyping.\n"
        prompt += "CONCISE YES/NO DIRECTIVE: If the current question is a binary Yes/No question (options contain Yes/No), ask it clearly with explicit instruction (e.g. 'बस 'हाँ' या 'नहीं' में जवाब दें').\n"
        prompt += "SMART CONDITIONAL SPEED RULE (PREVENT LONG SURVEYS):\n"
        prompt += "1. IF THE STUDENT ANSWERS 'YES' or positive ('हाँ', 'समझ आता है', 'everything good'), DO NOT ASK A FOLLOW-UP! Immediately select 'NEXT_QUESTION' to advance and save time.\n"
        prompt += "2. ONLY IF THE STUDENT ANSWERS 'NO' or expresses difficulty/unhappiness ('नहीं', 'uncomfortable', 'difficult'), select 'FOLLOWUP' once (max depth 1) to ask a brief 1-sentence supportive follow-up question (e.g. 'किस subject में दिक्कत आती है?').\n"
        prompt += "3. After 1 follow-up, ALWAYS select 'NEXT_QUESTION'. Keep the total survey completion fast and punchy (under 3 minutes).\n"
        prompt += "LANGUAGE RULE: Speak in natural, friendly Hinglish (Hindi mixed with common English words like 'class', 'marks', 'subject', 'teacher', 'exams', 'study', 'notes', 'timetable', 'favorite', 'difficult') in Devanagari script for Sarvam AI TTS.\n"
        prompt += "Keep responses short (1-2 concise spoken sentences). Speak with clear, confident warmth.\n\n"
        
        prompt += "CURRENT SURVEY STATE\n"
        prompt += f"Status: {state.status}\n"
        prompt += f"Completed Questions: {', '.join(state.completed_questions)}\n"
        prompt += f"In Followup Branch: {state.is_in_followup} (Depth: {state.followup_depth})\n\n"
        
        if current_question:
            prompt += "1. CURRENT QUESTION (EVALUATE THE USER'S ANSWER AGAINST THIS)\n"
            prompt += f"Question ID: {current_question.id}\n"
            prompt += f"Text: {current_question.text}\n"
            if current_question.options:
                prompt += f"Options: {', '.join(current_question.options)}\n"
            prompt += "\n"
            
        if next_question:
            prompt += "2. NEXT QUESTION (IF MOVING TO NEXT_QUESTION, ASK THIS NEXT)\n"
            prompt += f"Question ID: {next_question.id}\n"
            prompt += f"Text: {next_question.text}\n\n"
        
        prompt += "RECENT CONVERSATION\n"
        prompt += self.get_recent_turns(8) + "\n\n"
        
        q_max_fu = (current_question.max_followups if current_question and current_question.max_followups is not None else 3)
        allow_fu = current_question and getattr(current_question, 'allow_followup', False) and state.followup_depth < q_max_fu
        action_options = '"NEXT_QUESTION" | "ASK" | "CLARIFY" | "FOLLOWUP" | "REPEAT" | "SKIP" | "COMPLETE"' if allow_fu else '"NEXT_QUESTION" | "ASK" | "CLARIFY" | "REPEAT" | "SKIP" | "COMPLETE"'
        
        fu_instruction = ""
        if allow_fu:
            fu_instruction = f"""3. "FOLLOWUP" (PREFERRED WHEN ALLOWED): allow_followup=True for this question ({state.followup_depth}/{q_max_fu} follow-ups used so far).
   - If the student's response is short, negative ("No", "Not comfortable"), custom, or expresses an interesting thought, YOU MUST PREFER "FOLLOWUP".
   - Ask a warm, natural 1-sentence follow-up question (e.g., "What makes you feel uncomfortable?", "Why is that?", "Could you tell me a bit more about that?").
4. "NEXT_QUESTION": Choose "NEXT_QUESTION" ONLY if you have reached the follow-up limit ({q_max_fu} max) OR if the student's answer is already fully comprehensive with nothing left to explore."""
        else:
            fu_instruction = """3. "NEXT_QUESTION": Choose "NEXT_QUESTION" to acknowledge their answer briefly in 2-4 supportive words (e.g., "Got it.", "That makes sense.") and ask 2. NEXT QUESTION."""

        prompt += f"""INSTRUCTIONS FOR YOUR RESPONSE:
You MUST output ONLY a valid JSON object matching this exact schema:
{{
  "action": {action_options},
  "response": "The exact natural spoken text you will say aloud to the student."
}}

CRITICAL RULES FOR DECISION & RESPONSE:
1. EVALUATE USER ANSWER: Evaluate the most recent USER turn against 1. CURRENT QUESTION. If the student gave a reasonable answer, ACCEPT IT!
2. ZERO FUMBLES: Speak with total clarity and confidence. No filler words ('um', 'ah', 'well'), no markdown syntax, no lists, and no rigid question numbers.
{fu_instruction}
5. "CLARIFY" / "ASK": If the user gave an off-topic or completely unclear answer, use "CLARIFY" to ask a brief clarification about 1. CURRENT QUESTION.
6. ONE QUESTION ONLY: NEVER ask two questions in a single turn. When choosing "NEXT_QUESTION", acknowledge the student's answer briefly in 2-4 supportive words and ask ONLY the NEXT QUESTION text.
"""
        return prompt

    def build_extractor_prompt(self, current_question: Question, transcript_turn: str) -> str:
        prompt = "SYSTEM RULES\n"
        prompt += "You are a precise JSON-only Data Extractor. Your job is to extract the student's answer from their raw speech and map it to the expected schema.\n\n"
        
        prompt += "QUESTION DATA\n"
        prompt += f"Question ID: {current_question.id}\n"
        prompt += f"Text: {current_question.text}\n"
        prompt += f"Type: {current_question.type}\n"
        if current_question.options:
            prompt += f"Allowed Options: {', '.join(current_question.options)}\n"
        if current_question.expected_target:
            prompt += f"Expected Target: {current_question.expected_target}\n"
        prompt += "\n"
        
        prompt += f"STUDENT'S RAW RESPONSE\n"
        prompt += f"{transcript_turn}\n\n"
        
        prompt += """INSTRUCTIONS FOR YOUR RESPONSE:
You MUST output ONLY a valid JSON object. No markdown blocks, no other text.
The JSON must follow this exact schema:
{
  "answer_status": "answered" | "ambiguous" | "unknown" | "refused" | "pending",
  "answer": {
    "value": "string (the normalized extracted answer) or null",
    "confidence": 0.95 (float between 0 and 1)
  }
}

CRITICAL EXTRACTION RULES:
1. ALWAYS CAPTURE VALID ANSWERS: If the student gave a relevant response to the question, set 'answer_status' to 'answered'.
2. STRICT YES/NO NORMALIZATION: If 'Allowed Options' contain ['Yes', 'No'], ANY affirmative spoken response ('हाँ', 'समझ आता है', 'yes', 'yeah', 'sure', 'bilkul', 'definitely', 'of course', 'true') MUST be extracted strictly as 'Yes'. ANY negative spoken response ('नहीं', 'nahi', 'no', 'never', 'difficult', 'not really') MUST be extracted strictly as 'No'. If they say 'kabhi kabhi' or 'sometimes', extract strictly as 'Sometimes'. NEVER output conversational text for Yes/No questions!
3. OPTION MATCHING: For other multiple choice questions, set 'value' to the EXACT matching allowed option string.
4. FLEXIBLE / CUSTOM ANSWERS: If the student gave a relevant answer that is NOT in 'Allowed Options' (e.g. saying "good marks", "motivation", "self study"), DO NOT set 'answer_status' to 'unknown'! Set 'answer_status' to 'answered' and set 'value' to a clean summary of their spoken response (e.g., "Motivation for good marks").
4. RETENTION MAPPING (SC05/SC06):
   - "near about half", "around half", "half", "50%" -> "About half of it"
   - "most of it", "majority", "70%", "80%" -> "Most of it"
   - "almost all", "everything", "90%", "100%" -> "Almost everything"
   - "little bit", "small part", "20%", "30%" -> "Only a little bit"
   - "almost nothing", "hardly anything", "0%" -> "Almost nothing"
5. 'unknown' STATUS: Set 'answer_status' to 'unknown' ONLY if the student's utterance is pure noise, off-topic, or completely unanswerable.
"""
        return prompt
