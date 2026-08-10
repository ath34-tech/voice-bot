from typing import List, Optional
from schemas import Question

# Hardcoded survey questions based on questionnaire.v1.md
QUESTIONS: List[Question] = [
    # Section A
    Question(id="A01", text="What is your name?", type="free_text"),
    Question(id="A02", text="Which class were you in previously?", type="free_text / categorical"),
    Question(id="A03", text="Which class are you currently studying in?", type="categorical", expected_target="Grades 7–8"),
    Question(id="A04", text="What percentage did you get in your previous class?", type="numeric"),
    
    # Section B: Subject Comprehension & Teaching Style
    Question(id="SC01", text="Do you usually understand the topics taught by your teacher in class?", type="single_choice", options=["Yes", "No"]),
    Question(id="SC02", text="Do your teachers explain subjects in a simple and clear way?", type="single_choice", options=["Yes", "No", "Sometimes"]),
    Question(id="SC03", text="How comfortable do you feel asking questions or talking to your teacher in class?", type="single_choice", options=["Comfortable", "Uncomfortable"]),
    Question(id="SC04", text="Which things help you understand, stay interested, and remember a topic the most?", type="multi_choice", options=["Lecture only", "Examples and real-life stories", "Charts and mind maps", "Models and hands-on activities", "Storytelling"]),
    Question(id="SC05", text="If you study a topic today, about what percentage of it do you remember the next day?", type="numeric / approximate"),
    Question(id="SC06", text="And after one week, about what percentage of that topic do you still remember?", type="numeric / approximate"),
    Question(id="SC07", text="Do you find it difficult to remember definitions or formulas?", type="single_choice", options=["Yes", "No"]),
    
    # Section C: Memorizing & Memory
    Question(id="LM01", text="How does memorizing a subject usually feel to you?", type="single_choice", options=["Easy", "Difficult", "Boring", "Other"]),
    Question(id="LM02", text="After you understand a topic properly, does it become easier to remember?", type="single_choice", options=["Yes", "No", "Somewhat"]),
    Question(id="LM03", text="Who usually helps you learn and remember a topic?", type="multi_choice", options=["Teacher", "Tutor", "Parent", "Self-learning"]),
    Question(id="LM04", text="Do you feel that you can do better when someone helps you while learning?", type="single_choice", options=["Yes", "No"]),
    Question(id="LM05", text="After memorizing a topic, do you practise it by writing?", type="single_choice", options=["Yes", "No", "Sometimes"]),
    Question(id="LM06", text="After memorizing a topic, after how many days do you usually revise it?", type="numeric / free_text"),
    Question(id="LM07", text="Do you practise asking yourself questions and answering them to remember things?", type="single_choice", options=["Yes", "No", "Sometimes"]),
    Question(id="LM08", text="Do you think lack of confidence or fear affects your memory?", type="single_choice", options=["Yes", "No"]),
    Question(id="LM09", text="Do you make notes while studying?", type="single_choice", options=["Yes", "No"]),
    Question(id="LM10", text="Do you use lesson plans to help remember subject topics?", type="single_choice", options=["Yes", "No"]),
    Question(id="LM11", text="Which subject is the most difficult for you to remember?", type="free_text"),
    Question(id="LM12", text="What is your favourite subject?", type="free_text"),
    Question(id="LM13", text="Do you think repeating or rewriting something again and again is the only effective way to remember it?", type="single_choice", options=["Yes", "No"]),
    Question(id="LM14", text="Do you use any special trick or memory technique to remember something?", type="yes_no + qualitative_followup", options=["Yes", "No"]),
    Question(id="LM15", text="Do your school teacher or tutor teach you any memory techniques or strategies?", type="single_choice", options=["Yes", "No"]),
    Question(id="LM16", text="When your subject teacher puts pressure on you to memorize a topic, how do you usually take it?", type="single_choice", options=["Seriously", "Normally", "I ignore it"]),
    Question(id="LM17", text="When you memorize something, do you usually do it silently in your mind or say it out loud?", type="single_choice", options=["In the mind", "By speaking aloud"]),
    
    # Section D: Examination & Stress
    Question(id="ES01", text="Do you think examinations help improve your understanding, learning, and knowledge?", type="single_choice", options=["Yes", "No", "Sometimes"]),
    Question(id="ES02", text="Do your exam results usually match what you expect from yourself?", type="single_choice", options=["Yes", "No", "Sometimes"]),
    Question(id="ES03", text="How do you usually feel about exams?", type="single_choice", options=["I take them very seriously and work hard.", "They are a normal event that happens every year.", "I think, 'whatever happens, we'll see.'"]),
    Question(id="ES04", text="What do you usually think when you don't get good marks in an exam?", type="single_choice", options=["It's okay.", "It's about what I expected.", "I'll do better next time."]),
    Question(id="ES05", text="Do marks that are lower than you expected motivate you to do better next time?", type="single_choice", options=["Yes", "No"]),
    Question(id="ES06", text="When you work harder for better results, do you usually get the result you expect?", type="single_choice", options=["Yes", "No", "Sometimes"]),
    
    # Additional questions from Page 4 of the book (which are mostly ES or Study Pattern)
    Question(id="SP01", text="Do you have a fixed timetable for studying at home?", type="single_choice", options=["Yes", "No", "Sometimes"]),
    Question(id="SP02", text="What is your usual way of studying?", type="single_choice", options=["Continuously for long periods", "In short sessions with breaks"]),
    Question(id="SP03", text="In your experience, which method gives better results?", type="single_choice", options=["Continuously for long periods", "In short sessions with breaks"]),
    Question(id="SP04", text="Are you able to study with full concentration for 30 minutes?", type="single_choice", options=["Yes", "No"]),
    Question(id="SP05", text="You know that your learning/written part is incomplete, still you ignore it.", type="single_choice", options=["Yes", "No", "Sometimes"]),
    Question(id="SP06", text="At which stage do you face the most difficulty in studying?", type="single_choice", options=["Understanding the topic", "Memorizing it", "Retaining it long-term"]),
    Question(id="SP07", text="According to you, what is the biggest problem in studies: understanding, memorizing or retaining?", type="free_text"),
    Question(id="SP08", text="If you were taught a memory technique that makes it easy to memorize a subject and retain it for a long time, would you like to learn it?", type="single_choice", options=["Yes", "No"]),
    Question(id="SP09", text="Please do share any suggestions or thoughts regarding this subject with us.", type="free_text"),
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
