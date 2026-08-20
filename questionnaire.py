from typing import List, Optional
from schemas import Question

# Hardcoded survey questions based on questionnaire.v1.md & psychological profile
QUESTIONS: List[Question] = [
    # ==========================================
    # Section A: Student Information
    # ==========================================
    Question(
        id="A01",
        text="What is your name?",
        type="free_text",
        allow_followup=False,
    ),
    Question(
        id="A03",
        text="Which class are you currently studying in?",
        type="categorical",
        expected_target="Grades 7–8",
        allow_followup=False,
    ),
    Question(
        id="A04",
        text="What percentage did you get in your last exams?",
        type="numeric",
        allow_followup=False,
    ),

    # ==========================================
    # Section B: Subject Comprehension & Teaching Style
    # ==========================================
    Question(
        id="SC01",
        text="Do you usually understand the topics taught by your teacher in class?",
        type="single_choice",
        options=["Yes", "No"],
        allow_followup=True,
    ),
    Question(
        id="SC02",
        text="Do your teachers explain subjects in a simple and clear way?",
        type="single_choice",
        options=["Yes", "No", "Sometimes"],
        allow_followup=True,
    ),
    Question(
        id="SC03",
        text="How comfortable do you feel asking questions or talking to your teacher in class?",
        type="single_choice",
        options=["Comfortable", "Uncomfortable"],
        allow_followup=True,
    ),
    Question(
        id="SC04",
        text="Which things help you understand, stay interested, and remember a topic the most?",
        type="multi_choice",
        options=[
            "Lecture only",
            "Examples and real-life stories",
            "Charts and mind maps",
            "Models and hands-on activities",
            "Storytelling",
        ],
        allow_followup=True,
    ),
    Question(
        id="SC05",
        text="If you study a topic today, how much of it do you usually remember the next day?",
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
        text="And after a whole week, how much of that topic do you usually still remember?",
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
        text="Do you find it difficult to remember definitions or formulas?",
        type="single_choice",
        options=["Yes", "No"],
        allow_followup=True,
    ),

    # ==========================================
    # Section C: Memorizing & Learning Psychology
    # ==========================================
    Question(
        id="LM01",
        text="How does memorizing a subject usually feel to you?",
        type="single_choice",
        options=["Easy", "Difficult", "Boring", "Other"],
        allow_followup=True,
    ),
    Question(
        id="LM02",
        text="After you understand a topic properly, does it become easier to remember?",
        type="single_choice",
        options=["Yes", "No", "Somewhat"],
        allow_followup=True,
    ),
    Question(
        id="LM03",
        text="Who usually helps you learn and remember a topic?",
        type="multi_choice",
        options=["Teacher", "Tutor", "Parent", "Self-learning"],
        allow_followup=False,
    ),
    Question(
        id="LM04",
        text="Do you feel that you can do better when someone helps you while learning?",
        type="single_choice",
        options=["Yes", "No"],
        allow_followup=False,
    ),
    Question(
        id="LM05",
        text="After memorizing a topic, do you practise it by writing?",
        type="single_choice",
        options=["Yes", "No", "Sometimes"],
        allow_followup=False,
    ),
    Question(
        id="LM06",
        text="After memorizing a topic, after how many days do you usually revise it?",
        type="numeric / free_text",
        allow_followup=True,
    ),
    Question(
        id="LM07",
        text="Do you practise asking yourself questions and answering them to remember things?",
        type="single_choice",
        options=["Yes", "No", "Sometimes"],
        allow_followup=True,
    ),
    Question(
        id="LM08",
        text="Do you think lack of confidence or fear affects your memory?",
        type="single_choice",
        options=["Yes", "No"],
        allow_followup=True,
    ),
    Question(
        id="LM09",
        text="Do you make notes while studying?",
        type="single_choice",
        options=["Yes", "No"],
        allow_followup=True,
    ),
    Question(
        id="LM10",
        text="Do you use lesson plans to help remember subject topics?",
        type="single_choice",
        options=["Yes", "No"],
        allow_followup=True,
    ),
    Question(
        id="LM11",
        text="Which subject is the most difficult for you to remember?",
        type="free_text",
        allow_followup=True,
    ),
    Question(
        id="LM12",
        text="What is your favourite subject?",
        type="free_text",
        allow_followup=True,
    ),
    Question(
        id="LM13",
        text="Do you think repeating or rewriting something again and again is the only effective way to remember it?",
        type="single_choice",
        options=["Yes", "No"],
        allow_followup=False,
    ),
    Question(
        id="LM14",
        text="Do you use any special trick or memory technique to remember something?",
        type="yes_no + qualitative_followup",
        options=["Yes", "No"],
        allow_followup=True,
    ),
    Question(
        id="LM15",
        text="Do your school teacher or tutor teach you any memory techniques or strategies?",
        type="single_choice",
        options=["Yes", "No"],
        allow_followup=False,
    ),
    Question(
        id="LM16",
        text="When your subject teacher puts pressure on you to memorize a topic, how do you usually take it?",
        type="single_choice",
        options=["Seriously", "Normally", "I ignore it"],
        allow_followup=False,
    ),
    Question(
        id="LM17",
        text="When you memorize something, do you usually do it silently in your mind or say it out loud?",
        type="single_choice",
        options=["In the mind", "By speaking aloud"],
        allow_followup=False,
    ),

    # ==========================================
    # Section D: Examination & Stress Psychology
    # ==========================================
    Question(
        id="ES01",
        text="Do you think examinations help improve your understanding, learning, and knowledge?",
        type="single_choice",
        options=["Yes", "No", "Sometimes"],
        allow_followup=False,
    ),
    Question(
        id="ES02",
        text="Do your exam results usually match what you expect from yourself?",
        type="single_choice",
        options=["Yes", "No", "Sometimes"],
        allow_followup=True,
    ),
    Question(
        id="ES03",
        text="How do you usually feel about exams?",
        type="single_choice",
        options=[
            "I take them very seriously and work hard.",
            "They are a normal event that happens every year.",
            "I think, 'whatever happens, we'll see.'",
        ],
        allow_followup=True,
    ),
    Question(
        id="ES04",
        text="What do you usually think when you don't get good marks in an exam?",
        type="single_choice",
        options=[
            "It's okay.",
            "It's about what I expected.",
            "I'll do better next time.",
        ],
        allow_followup=False,
    ),
    Question(
        id="ES05",
        text="Do marks that are lower than you expected motivate you to do better next time?",
        type="single_choice",
        options=["Yes", "No"],
        allow_followup=True,
    ),
    Question(
        id="ES06",
        text="When you work harder for better results, do you usually get the result you expect?",
        type="single_choice",
        options=["Yes", "No", "Sometimes"],
        allow_followup=False,
    ),

    # ==========================================
    # Section E: Study Pattern & Cognitive Habits
    # ==========================================
    Question(
        id="SP01",
        text="Do you have a fixed timetable for studying at home?",
        type="single_choice",
        options=["Yes", "No", "Sometimes"],
        allow_followup=False,
    ),
    Question(
        id="SP02",
        text="What is your usual way of studying?",
        type="single_choice",
        options=[
            "Continuously for long periods",
            "In short sessions with breaks",
        ],
        allow_followup=True,
    ),
    Question(
        id="SP03",
        text="In your experience, which method gives better results?",
        type="single_choice",
        options=[
            "Continuously for long periods",
            "In short sessions with breaks",
        ],
        allow_followup=True,
    ),
    Question(
        id="SP04",
        text="Are you able to study with full concentration for 30 minutes?",
        type="single_choice",
        options=["Yes", "No"],
        allow_followup=True,
    ),
    Question(
        id="SP05",
        text="When you know your learning or written work is incomplete, do you sometimes still leave it unfinished?",
        type="single_choice",
        options=["Yes", "No", "Sometimes"],
        allow_followup=False,
    ),
    Question(
        id="SP06",
        text="At which stage do you face the most difficulty in studying?",
        type="single_choice",
        options=[
            "Understanding the topic",
            "Memorizing it",
            "Retaining it long-term",
        ],
        allow_followup=True,
    ),
    Question(
        id="SP07",
        text="According to you, what is the biggest problem in studies: understanding, memorizing or retaining?",
        type="free_text",
        allow_followup=True,
    ),
    Question(
        id="SP08",
        text="If you were taught a memory technique that makes it easy to memorize a subject and retain it for a long time, would you like to learn it?",
        type="single_choice",
        options=["Yes", "No"],
        allow_followup=True,
    ),
    Question(
        id="SP09",
        text="Do you have any suggestions or thoughts you'd like to share about studying, learning, or memory?",
        type="free_text",
        allow_followup=True,
    ),

    # ==========================================
    # Section F: Qualitative Reflections
    # ==========================================
    Question(
        id="FQ01",
        text="If you could design the perfect learning environment, what would it look like?",
        type="free_text",
        allow_followup=True,
    ),
    Question(
        id="FQ02",
        text="When you are completely free from schoolwork, what is your favorite way to spend your time?",
        type="free_text",
        allow_followup=True,
    ),
    Question(
        id="FQ03",
        text="Looking ahead, what is a personal goal or dream you are most excited to achieve in the next few years?",
        type="free_text",
        allow_followup=False,
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
