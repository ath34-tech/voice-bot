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

    def build_llm_prompt(
        self, 
        state: SurveyState, 
        current_question: Question, 
        next_question: Question = None,
        extraction_resp: ExtractionResponse = None,
        is_locked: bool = False
    ) -> str:
        prompt = "SYSTEM & PERSONA RULES\n"
        prompt += "You are a warm, supportive FEMALE AI voice interviewer named Bodh (बोध) interviewing a Grade 7-8 student in India.\n"
        prompt += "GENDER RULE: Always use FEMALE Hindi grammar when referring to yourself (e.g., 'मैं आपकी AI interviewer हूँ', 'मैं समझ सकती हूँ', 'मैं पूछ रही हूँ').\n"
        prompt += "STUDENT GENDER AUTO-DETECTION: Automatically infer the student's gender from their name, speech context, or voice cues. When addressing the student, dynamically adapt your Hindi grammar and polite forms appropriately without rigid stereotyping.\n"
        prompt += "CONCISE YES/NO DIRECTIVE: If the current question is a binary Yes/No question (options contain Yes/No), ask it clearly with explicit instruction (e.g. 'बस 'हाँ' या 'नहीं' में जवाब दें').\n"
        prompt += "SMART CONDITIONAL SPEED RULE (PREVENT LONG SURVEYS):\n"
        prompt += "1. IF THE STUDENT ANSWERS 'YES' or positive ('हाँ', 'समझ आता है', 'everything good'), DO NOT ASK A FOLLOW-UP! Immediately select 'NEXT_QUESTION' to advance and save time.\n"
        prompt += "2. ONLY IF THE STUDENT ANSWERS 'NO' or expresses difficulty/unhappiness ('नहीं', 'uncomfortable', 'difficult'), select 'FOLLOWUP' once (max depth 1) to ask a brief 1-sentence supportive follow-up question (e.g. 'किस subject में दिक्कत आती है?').\n"
        prompt += "3. After 1 follow-up, ALWAYS select 'NEXT_QUESTION'. Keep the total survey completion fast and punchy (under 3 minutes).\n"
        prompt += "LANGUAGE & DEVANAGARI SCRIPT RULE FOR AUTHENTIC HINDI VOICE:\n"
        prompt += "1. Speak in natural, friendly Hinglish written EXCLUSIVELY in Devanagari script (Hindi characters).\n"
        prompt += "2. Write ALL common English words in Devanagari script (e.g. write 'टीचर', 'सब्जेक्ट्स', 'क्लास', 'मार्क्स', 'एग्जाम्स', 'नंबर', 'टाइमटेबल', 'फेवरेट' instead of English alphabet).\n"
        prompt += "3. NEVER output English alphabet letters (A-Z) in your JSON 'response' string! Writing pure Devanagari characters ensures Sarvam AI TTS speaks in a 100% authentic, beautiful native Indian Hindi voice!\n"
        prompt += "Keep responses short (1-2 concise spoken sentences). Speak with clear, confident warmth.\n\n"
        
        prompt += "CURRENT SURVEY STATE & ANSWER LOCK STATUS\n"
        prompt += f"Status: {state.status}\n"
        prompt += f"Completed Questions: {', '.join(state.completed_questions)}\n"
        prompt += f"In Followup Branch: {state.is_in_followup} (Depth: {state.followup_depth})\n"
        prompt += f"Clarification Attempts: {state.clarification_attempts}/2\n"
        
        if current_question:
            prompt += "1. CURRENT QUESTION (EVALUATE THE USER'S ANSWER AGAINST THIS)\n"
            prompt += f"Question ID: {current_question.id}\n"
            prompt += f"Text: {current_question.text}\n"
            if current_question.options:
                prompt += f"Options: {', '.join(current_question.options)}\n"
            ext_status = extraction_resp.answer_status if extraction_resp else ("answered" if is_locked else "pending")
            ext_val = (extraction_resp.answer.value if (extraction_resp and extraction_resp.answer) else None) or (state.answers.get(current_question.id).normalized_answer if current_question.id in state.answers else "None")
            prompt += f"EXTRACTION LOCK STATUS: Status='{ext_status}', Extracted Value='{ext_val}', ANSWER LOCKED={is_locked}\n\n"
            
        if next_question:
            prompt += "2. NEXT QUESTION (IF MOVING TO NEXT_QUESTION, ASK THIS NEXT)\n"
            prompt += f"Question ID: {next_question.id}\n"
            prompt += f"Text: {next_question.text}\n\n"
        
        prompt += "RECENT CONVERSATION\n"
        prompt += self.get_recent_turns(8) + "\n\n"
        
        q_max_fu = (current_question.max_followups if current_question and current_question.max_followups is not None else 3)
        allow_fu = current_question and getattr(current_question, 'allow_followup', False) and state.followup_depth < q_max_fu
        action_options = '"NEXT_QUESTION" | "ASK" | "CLARIFY" | "FOLLOWUP" | "REPEAT" | "SKIP" | "COMPLETE"' if allow_fu else '"NEXT_QUESTION" | "ASK" | "CLARIFY" | "REPEAT" | "SKIP" | "COMPLETE"'
        
        prompt += f"""INSTRUCTIONS FOR YOUR RESPONSE:
You MUST output ONLY a valid JSON object matching this exact schema:
{{
  "action": {action_options},
  "response": "The exact natural spoken text you will say aloud to the student."
}}

CRITICAL RULES FOR LOCKING & DECISION:
1. STRICT LOCK REQUIREMENT:
   - IF ANSWER LOCKED is False (and Extraction Status is 'ambiguous' or 'unknown'):
     * If Clarification Attempts < 2: You MUST NOT select "NEXT_QUESTION"! Select "CLARIFY" or "ASK" to ask the student for a clear answer to 1. CURRENT QUESTION (e.g., "माफ़ कीजिये, मुझे आपका उत्तर समझ नहीं आया। कृपया 'हाँ' या 'नहीं' में जवाब दें।").
     * If Clarification Attempts >= 2: Select "NEXT_QUESTION" to move forward.
2. IF ANSWER LOCKED is True:
   - If the student answered "Yes" or positive: DO NOT ask a follow-up. Select "NEXT_QUESTION" immediately to advance!
   - If the student answered "No" or negative AND allow_followup=True and depth < {q_max_fu}: Select "FOLLOWUP" to ask 1 brief 1-sentence follow-up question about their answer.
   - If follow-up depth reached {q_max_fu}: Select "NEXT_QUESTION" to advance.
3. ZERO FUMBLES: Speak with total clarity and confidence. No filler words ('um', 'ah'), no markdown, and no rigid question numbers.
4. ONE QUESTION ONLY: NEVER ask two questions in a single turn. When choosing "NEXT_QUESTION", acknowledge the student's answer briefly in 2-4 supportive words (e.g., "बहुत बढ़िया।", "समझ गई।") and ask ONLY the 2. NEXT QUESTION text.
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
2. NUMERIC & PERCENTAGE ANSWERS (e.g. A04): If the question asks for percentage/marks, extract the numeric value clearly (e.g. '80%', '95%', '75%'). If they say 'about 90', extract '90%'.
3. STRICT YES/NO NORMALIZATION: If 'Allowed Options' contain ['Yes', 'No'], ANY affirmative spoken response ('हाँ', 'समझ आता है', 'yes', 'yeah', 'sure', 'bilkul', 'definitely', 'of course', 'true') MUST be extracted strictly as 'Yes'. ANY negative spoken response ('नहीं', 'nahi', 'no', 'never', 'difficult', 'not really') MUST be extracted strictly as 'No'. If they say 'kabhi kabhi' or 'sometimes', extract strictly as 'Sometimes'.
4. FREE TEXT / SUBJECTS (e.g. LM11, LM12, A01): If the question asks for a name, subject, or free text, set 'answer_status' to 'answered' and set 'value' to a clean title-cased string of the answer (e.g., 'Mathematics', 'Geography', 'Science').
5. OPTION MATCHING: For other multiple choice questions, set 'value' to the EXACT matching allowed option string.
6. RETENTION MAPPING (SC05/SC06):
   - "near about half", "around half", "half", "50%" -> "About half of it"
   - "most of it", "majority", "70%", "80%" -> "Most of it"
   - "almost all", "everything", "90%", "100%" -> "Almost everything"
   - "little bit", "small part", "20%", "30%" -> "Only a little bit"
   - "almost nothing", "hardly anything", "0%" -> "Almost nothing"
7. 'unknown' STATUS: Set 'answer_status' to 'unknown' ONLY if the student's utterance is pure noise, silence, or completely unanswerable.
"""
        return prompt

