from typing import List, Optional
from schemas import Question

# Survey questions in natural, friendly Hinglish with everyday English vocabulary
QUESTIONS: List[Question] = [
    # ==========================================
    # Section A: Student Information
    # ==========================================
    Question(
        id="A01",
        text="आपका नाम क्या है? (What is your name?)",
        type="free_text",
        allow_followup=False,
    ),
    Question(
        id="A03",
        text="आप अभी कौन सी class में पढ़ रहे हो? (Which class are you currently studying in?)",
        type="categorical",
        expected_target="Grades 7–8",
        allow_followup=False,
    ),
    Question(
        id="A04",
        text="आपके पिछले exams में कितने percentage marks आए थे? (What percentage did you get in your last exams?)",
        type="numeric",
        allow_followup=False,
    ),

    # ==========================================
    # Section B: Subject Comprehension & Teaching Style
    # ==========================================
    Question(
        id="SC01",
        text="क्या आपको class में teacher के पढ़ाए हुए topics आसानी से समझ में आते हैं? (बस 'हाँ' या 'नहीं' में जवाब दें)",
        type="single_choice",
        options=["Yes", "No"],
        allow_followup=True,
        max_followups=1,
    ),
    Question(
        id="SC02",
        text="क्या आपके teachers subjects को simple और clear तरीक़े से समझाते हैं? (हाँ, नहीं या कभी-कभी में जवाब दें)",
        type="single_choice",
        options=["Yes", "No", "Sometimes"],
        allow_followup=True,
        max_followups=1,
    ),
    Question(
        id="SC03",
        text="Class में अपने teacher से questions पूछने में आप कितना comfortable महसूस करते हो? (Comfortable या Uncomfortable)",
        type="single_choice",
        options=["Comfortable", "Uncomfortable"],
        allow_followup=True,
        max_followups=1,
    ),
    Question(
        id="SC04",
        text="Subjects को समझने और याद रखने में आपको सबसे ज्यादा किस चीज़ से help मिलती है?",
        type="multi_choice",
        options=[
            "Only lectures",
            "Real-life examples and stories",
            "Charts and mind maps",
            "Models and practical activities",
        ],
        allow_followup=True,
        max_followups=1,
    ),
    Question(
        id="SC05",
        text="अगर आप आज कोई topic पढ़ते हो, तो अगले दिन उसमें से कितना याद रहता है?",
        type="single_choice",
        options=[
            "Almost everything",
            "Most of it",
            "About half of it",
            "Only a little bit",
            "Almost nothing",
        ],
        allow_followup=False,
    ),
    Question(
        id="SC06",
        text="और पूरे एक week के बाद, उस topic का कितना हिस्सा याद रहता है?",
        type="single_choice",
        options=[
            "Almost everything",
            "Most of it",
            "About half of it",
            "Only a little bit",
            "Almost nothing",
        ],
        allow_followup=False,
    ),
    Question(
        id="SC07",
        text="क्या आपको definitions या formulas याद रखने में difficulty होती है? (बस 'हाँ' या 'नहीं' में जवाब दें)",
        type="single_choice",
        options=["Yes", "No"],
        allow_followup=True,
        max_followups=1,
    ),

    # ==========================================
    # Section C: Memorizing & Learning Psychology
    # ==========================================
    Question(
        id="LM01",
        text="किसी topic को memorize या रटना आपको कैसा लगता है?",
        type="single_choice",
        options=["Easy", "Difficult", "Boring", "Other"],
        allow_followup=False,
    ),
    Question(
        id="LM02",
        text="जब आप किसी topic को अच्छी तरह समझ लेते हो, तो क्या उसे memorize करना easy हो जाता है? (बस 'हाँ' या 'नहीं' में बताइए)",
        type="single_choice",
        options=["Yes", "No", "Somewhat"],
        allow_followup=True,
        max_followups=1,
    ),
    Question(
        id="LM11",
        text="कौन सा subject आपको याद रखने में सबसे difficult लगता है?",
        type="free_text",
        allow_followup=True,
        max_followups=1,
    ),
    Question(
        id="LM12",
        text="आपका favorite subject कौन सा है?",
        type="free_text",
        allow_followup=True,
        max_followups=1,
    ),

    # ==========================================
    # Section D: Examination & Stress Psychology
    # ==========================================
    Question(
        id="ES03",
        text="आप exams के बारे में कैसा महसूस करते हो?",
        type="single_choice",
        options=[
            "Seriously लेता हूँ और hard work करता हूँ",
            "Normal बात है हर साल होती है",
            "जो होगा देखा जाएगा",
        ],
        allow_followup=False,
    ),
    Question(
        id="ES05",
        text="क्या उम्मीद से कम marks मिलने पर आपको अगली बार better करने की motivation मिलती है? (बस 'हाँ' या 'नहीं' में जवाब दें)",
        type="single_choice",
        options=["Yes", "No"],
        allow_followup=True,
        max_followups=1,
    ),

    # ==========================================
    # Section E: Study Pattern & Cognitive Habits
    # ==========================================
    Question(
        id="SP01",
        text="क्या आपका घर पर study करने का कोई fixed timetable है? (बस 'हाँ' या 'नहीं' में बताइए)",
        type="single_choice",
        options=["Yes", "No", "Sometimes"],
        allow_followup=True,
        max_followups=1,
    ),
    Question(
        id="SP02",
        text="घर पर study करने का आपका तरीक़ा क्या है?",
        type="single_choice",
        options=[
            "Continuously लंबे समय तक",
            "Short sessions में breaks लेकर",
        ],
        allow_followup=False,
    ),
    Question(
        id="SP08",
        text="अगर आपको memory techniques सिखाई जाएं, तो क्या आप सीखना चाहोगे? (बस 'हाँ' या 'नहीं' में जवाब दें)",
        type="single_choice",
        options=["Yes", "No"],
        allow_followup=True,
        max_followups=1,
    ),
]


class Questionnaire:
    def __init__(self):
        self.questions = QUESTIONS
        self.question_map = {q.id: q for q in self.questions}
        self.question_order = [q.id for q in self.questions]

    def get_first_question(self) -> Question:
        return self.questions[0]

    def get_question(self, q_id: str) -> Optional[Question]:
        return self.question_map.get(q_id)

    def get_next_question(self, current_q_id: str) -> Optional[Question]:
        try:
            idx = self.question_order.index(current_q_id)
            if idx + 1 < len(self.question_order):
                return self.question_map[self.question_order[idx + 1]]
        except ValueError:
            pass
        return None

    def export_schema_for_frontend(self):
        return [
            {
                "id": q.id,
                "text": q.text,
                "type": getattr(q, "type", "free_text"),
                "options": getattr(q, "options", []) or [],
                "allow_followup": getattr(q, "allow_followup", True)
            }
            for q in self.questions
        ]


def get_questionnaire_for_school(school_code: str = "DEFAULT") -> Questionnaire:
    return Questionnaire()

