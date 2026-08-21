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
        text="क्या आपको class में teacher के पढ़ाए हुए topics समझ में आते हैं? (Do you usually understand the topics taught by your teacher in class?)",
        type="single_choice",
        options=["Yes", "No"],
        allow_followup=True,
    ),
    Question(
        id="SC02",
        text="क्या आपके teachers subjects को simple और clear तरीक़े से समझाते हैं? (Do your teachers explain subjects in a simple and clear way?)",
        type="single_choice",
        options=["Yes", "No", "Sometimes"],
        allow_followup=True,
    ),
    Question(
        id="SC03",
        text="Class में अपने teacher से questions पूछने में आप कितना comfortable महसूस करते हो? (How comfortable do you feel asking questions to your teacher in class?)",
        type="single_choice",
        options=["Comfortable", "Uncomfortable"],
        allow_followup=True,
    ),
    Question(
        id="SC04",
        text="Subjects को समझने और याद रखने में आपको सबसे ज्यादा किस चीज़ से help मिलती है? (Which things help you understand and remember a topic the most?)",
        type="multi_choice",
        options=[
            "Only lectures",
            "Real-life examples and stories",
            "Charts and mind maps",
            "Models and practical activities",
        ],
        allow_followup=True,
    ),
    Question(
        id="SC05",
        text="अगर आप आज कोई topic पढ़ते हो, तो अगले दिन उसमें से कितना याद रहता है? (If you study a topic today, how much of it do you remember the next day?)",
        type="single_choice",
        options=[
            "Almost everything",
            "Most of it",
            "About half of it",
            "Only a little bit",
            "Almost nothing",
        ],
        allow_followup=True,
        max_followups=1,
    ),
    Question(
        id="SC06",
        text="और पूरे एक week के बाद, उस topic का कितना हिस्सा याद रहता है? (And after a whole week, how much of that topic do you still remember?)",
        type="single_choice",
        options=[
            "Almost everything",
            "Most of it",
            "About half of it",
            "Only a little bit",
            "Almost nothing",
        ],
        allow_followup=True,
        max_followups=1,
    ),
    Question(
        id="SC07",
        text="क्या आपको definitions या formulas याद रखने में difficulty होती है? (Do you find it difficult to remember definitions or formulas?)",
        type="single_choice",
        options=["Yes", "No"],
        allow_followup=True,
    ),

    # ==========================================
    # Section C: Memorizing & Learning Psychology
    # ==========================================
    Question(
        id="LM01",
        text="किसी topic को memorize या रटना आपको कैसा लगता है? (How does memorizing a subject usually feel to you?)",
        type="single_choice",
        options=["Easy", "Difficult", "Boring", "Other"],
        allow_followup=True,
    ),
    Question(
        id="LM02",
        text="जब आप किसी topic को अच्छी तरह समझ लेते हो, तो क्या उसे memorize करना easy हो जाता है? (After you understand a topic properly, does it become easier to remember?)",
        type="single_choice",
        options=["Yes", "No", "Somewhat"],
        allow_followup=True,
    ),
    Question(
        id="LM11",
        text="कौन सा subject आपको याद रखने में सबसे difficult लगता है? (Which subject is the most difficult for you to remember?)",
        type="free_text",
        allow_followup=True,
    ),
    Question(
        id="LM12",
        text="आपका favorite subject कौन सा है? (What is your favorite subject?)",
        type="free_text",
        allow_followup=True,
    ),

    # ==========================================
    # Section D: Examination & Stress Psychology
    # ==========================================
    Question(
        id="ES03",
        text="आप exams के बारे में कैसा महसूस करते हो? (How do you usually feel about exams?)",
        type="single_choice",
        options=[
            "Seriously लेता हूँ और hard work करता हूँ",
            "Normal बात है हर साल होती है",
            "जो होगा देखा जाएगा",
        ],
        allow_followup=True,
    ),
    Question(
        id="ES05",
        text="क्या उम्मीद से कम marks मिलने पर आपको अगली बार better करने की motivation मिलती है? (Do lower marks motivate you to do better next time?)",
        type="single_choice",
        options=["Yes", "No"],
        allow_followup=True,
    ),

    # ==========================================
    # Section E: Study Pattern & Cognitive Habits
    # ==========================================
    Question(
        id="SP01",
        text="क्या आपका घर पर study करने का कोई fixed timetable है? (Do you have a fixed timetable for studying at home?)",
        type="single_choice",
        options=["Yes", "No", "Sometimes"],
        allow_followup=False,
    ),
    Question(
        id="SP02",
        text="घर पर study करने का आपका तरीक़ा क्या है? (What is your usual way of studying at home?)",
        type="single_choice",
        options=[
            "Continuously लंबे समय तक",
            "Short sessions में breaks लेकर",
        ],
        allow_followup=True,
    ),
    Question(
        id="SP08",
        text="अगर आपको एक ऐसी memory technique सिखाई जाए जिससे subjects को memorize करना और याद रखना easy हो जाए, तो क्या आप उसे सीखना चाहोगे? (Would you like to learn memory techniques?)",
        type="single_choice",
        options=["Yes", "No"],
        allow_followup=True,
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
