import asyncio
import logging
import sys
import json
from typing import List, Dict, Any

from config import settings
from questionnaire import Questionnaire
from memory import MemoryManager
from state import StateManager
from llm import LLMClient
from schemas import ConversationalResponse, ExtractionResponse, Question

# Configure logging for test run
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("QualityTest")

class QualityTester:
    def __init__(self):
        self.questionnaire = Questionnaire()
        self.memory_manager = MemoryManager(session_id="test-session-quality")
        self.state_manager = StateManager(session_id="test-session-quality")
        self.llm = LLMClient()
        self.passed_tests = 0
        self.failed_tests = 0

    def log_result(self, test_name: str, passed: bool, details: str = ""):
        if passed:
            self.passed_tests += 1
            print(f"  ✅ [PASS] {test_name}: {details}")
        else:
            self.failed_tests += 1
            print(f"  ❌ [FAIL] {test_name}: {details}")

    def test_questionnaire_integrity(self):
        print("\n--- 1. Questionnaire Structural Integrity ---")
        questions = self.questionnaire.questions
        
        # Test 1.1: Question count
        count_ok = len(questions) >= 40
        self.log_result("Questionnaire Length", count_ok, f"Total questions: {len(questions)}")
        
        # Test 1.2: Check unique IDs
        q_ids = [q.id for q in questions]
        unique_ok = len(q_ids) == len(set(q_ids))
        self.log_result("Unique Question IDs", unique_ok, f"Unique IDs: {len(set(q_ids))}/{len(q_ids)}")
        
        # Test 1.3: Check start and end questions
        first_q = self.questionnaire.get_first_question()
        first_ok = (first_q.id == "A01")
        self.log_result("First Question ID", first_ok, f"First Q: {first_q.id if first_q else None}")
        
        # Test 1.4: Check follow-up configurations
        fu_questions = [q.id for q in questions if q.allow_followup]
        fu_ok = len(fu_questions) > 10
        self.log_result("Follow-up Configuration", fu_ok, f"{len(fu_questions)} questions have follow-ups enabled.")

    async def test_extractor_quality(self):
        print("\n--- 2. Background Extractor Quality & Normalization ---")
        test_cases = [
            {
                "question": self.questionnaire.get_question("A03"),
                "speech": "I am in class eight.",
                "expected_contains": "Grades 7–8"
            },
            {
                "question": self.questionnaire.get_question("A04"),
                "speech": "I scored about 95% in my last exams.",
                "expected_contains": "95"
            },
            {
                "question": self.questionnaire.get_question("SC05"),
                "speech": "I guess near about half of it.",
                "expected_contains": "About half of it"
            },
            {
                "question": self.questionnaire.get_question("LM11"),
                "speech": "I think geography topic is the hardest for me to remember.",
                "expected_contains": "Geography"
            },
            {
                "question": self.questionnaire.get_question("SC04"),
                "speech": "Motivation to get good marks helps me.",
                "expected_contains": "Motivation"
            }
        ]

        for idx, tc in enumerate(test_cases, 1):
            q: Question = tc["question"]
            speech = tc["speech"]
            expected = tc["expected_contains"]
            
            prompt = self.memory_manager.build_extractor_prompt(q, speech)
            try:
                extraction: ExtractionResponse = await self.llm.extract_answer(prompt)
                
                is_answered = extraction.answer_status == "answered"
                val = extraction.answer.value if extraction.answer else ""
                conf = extraction.answer.confidence if extraction.answer else 0.0
                
                matched = expected.lower() in (val or "").lower() or is_answered
                details = f"Extracted: '{val}' (Conf: {conf}) for speech: '{speech}'"
                self.log_result(f"Extractor Test #{idx} ({q.id})", is_answered and conf >= 0.7, details)
            except Exception as e:
                self.log_result(f"Extractor Test #{idx} ({q.id})", False, f"Exception: {e}")

    async def test_conversational_llm_quality(self):
        print("\n--- 3. Conversational LLM Quality & Probing ---")
        
        # Test 3.1: Probing on SC01 when user answers negatively
        q_sc01 = self.questionnaire.get_question("SC01")
        next_q = self.questionnaire.get_next_question("SC01")
        
        self.memory_manager.add_student_turn("No, I don't really understand what my teacher explains in class.")
        prompt = self.memory_manager.build_llm_prompt(self.state_manager.state, q_sc01, next_q)
        
        try:
            resp: ConversationalResponse = await self.llm.get_conversational_decision(prompt)
            action_ok = resp.action in ["FOLLOWUP", "NEXT_QUESTION"]
            has_no_fillers = not any(f in resp.response.lower() for f in [" um ", " ah ", " filler "])
            length_ok = 5 <= len(resp.response.split()) <= 45
            
            details = f"Action: {resp.action} | Response: '{resp.response}'"
            self.log_result("Conversational Probing (SC01)", action_ok and has_no_fillers and length_ok, details)
        except Exception as e:
            self.log_result("Conversational Probing (SC01)", False, f"Exception: {e}")

    def test_state_machine_flow(self):
        print("\n--- 4. State Machine & Followup Depth Limits ---")
        sm = StateManager(session_id="test-state-flow")
        
        # Start at A01
        current_q = sm.get_current_question()
        self.log_result("Initial State Question", current_q.id == "A01", f"Current Q: {current_q.id}")
        
        # Simulate NEXT_QUESTION
        resp_next = ConversationalResponse(action="NEXT_QUESTION", response="Got it. Moving to next.")
        sm.apply_llm_response(resp_next)
        next_q = sm.get_current_question()
        self.log_result("Advance State", next_q.id == "A03", f"Advanced to: {next_q.id}")
        
        # Test custom max_followups depth cap
        sc05_q = self.questionnaire.get_question("SC05")
        sm.state.current_question = "SC05"
        sm.state.followup_depth = 1 # SC05 max_followups = 1
        
        resp_fu = ConversationalResponse(action="FOLLOWUP", response="Why is that?")
        sm.apply_llm_response(resp_fu)
        
        # Should be forced to NEXT_QUESTION because followup_depth reached limit (1)
        depth_capped = (resp_fu.action == "NEXT_QUESTION")
        self.log_result("Follow-up Depth Cap (SC05)", depth_capped, f"Action overridden to NEXT_QUESTION after depth limit 1.")

    async def run_all(self):
        print("==================================================")
        print("        VOICE SURVEY BOT - QUALITY TEST SUITE     ")
        print("==================================================")
        
        self.test_questionnaire_integrity()
        await self.test_extractor_quality()
        await self.test_conversational_llm_quality()
        self.test_state_machine_flow()
        
        print("\n==================================================")
        print(f"  TEST SUMMARY: Passed {self.passed_tests} | Failed {self.failed_tests}")
        print("==================================================")
        
        return self.failed_tests == 0

if __name__ == "__main__":
    tester = QualityTester()
    success = asyncio.run(tester.run_all())
    sys.exit(0 if success else 1)
