# Questionnaire v1 — Memory Assessment & Study Profile

## 1. Purpose

This questionnaire is designed to collect structured and qualitative information from students, primarily Grades 7–8, about:

1. Study Pattern
2. Learning & Memory
3. Subject Comprehension, Teaching Style & Learning Effectiveness
4. Examination & Stress

The interviewer must preserve the intended meaning of the original questionnaire while converting written questions into natural spoken questions.

The questionnaire is a **survey**, not an examination.

The student must not feel that there is a correct or incorrect answer unless the question explicitly requires a factual response.

---

# 2. Questionnaire Rules

## 2.1 One Primary Question at a Time

Ask one primary question and wait for the student's response.

Do not combine multiple questions into one spoken turn.

## 2.2 Preserve Meaning

Questions may be simplified for spoken conversation, but their meaning must not change.

Example:

Original:

> Do you have a fixed timetable for studying at home?

Natural spoken version:

> Do you usually have a fixed timetable for studying at home?

Both have the same intent.

## 2.3 Do Not Suggest Answers

Do not lead the student toward an option.

Bad:

> "You probably study in short sessions, right?"

Good:

> "How do you usually study?"

## 2.4 Preserve Raw Responses

Every answer must preserve:

* Original transcription
* Normalized answer, when applicable
* Question ID
* Timestamp
* Session ID

## 2.5 Options

When a question has predefined options, the interviewer may read the options naturally.

Example:

> "Would you say you study continuously for a long time, or in shorter sessions with breaks?"

Do not alter the underlying options.

## 2.6 Unclear Responses

If the answer does not map confidently to the expected answer type, ask a short clarification.

Do not guess.

Maximum clarification attempts should normally be 2 unless application configuration specifies otherwise.

---

# 3. Section A — Student Information

These fields are collected before or at the beginning of the survey.

## A01 — Student Name

Field:

`student_name`

Prompt:

> "What is your name?"

Type:

`free_text`

---

## A02 — Previous Class

Field:

`previous_class`

Prompt:

> "Which class were you in previously?"

Type:

`free_text / categorical`

---

## A03 — Present Class

Field:

`present_class`

Prompt:

> "Which class are you currently studying in?"

Type:

`categorical`

Expected target:

Grades 7–8.

---

## A04 — Previous Percentage

Field:

`previous_percentage`

Prompt:

> "What percentage did you get in your previous class?"

Type:

`numeric`

If the student does not know:

> "That's okay. We can skip that."

Do not invent a value.

---

# 4. Section B — Subject Comprehension & Teaching Style

Purpose:

Assess how well students understand topics taught by teachers, how comfortable they are interacting with teachers, and which teaching methods help them understand, stay interested, and remember.

---

## SC01 — Understanding Teacher's Topics

Question:

> "Do you usually understand the topics taught by your teacher in class?"

Expected answers:

* Yes
* No

Type:

`single_choice`

Normalization:

```text
yes → yes
yeah → yes
usually → clarify
no → no
not really → no / clarify
```

If unclear:

> "Do you usually understand what the teacher explains in class?"

---

## SC02 — Teacher Clarity

Question:

> "Do your teachers explain subjects in a simple and clear way?"

Expected answers:

* Yes
* No
* Sometimes

Type:

`single_choice`

---

## SC03 — Teacher Interaction

Question:

> "How comfortable do you feel asking questions or talking to your teacher in class?"

Expected answers:

* Comfortable
* Uncomfortable

Type:

`single_choice`

Do not assume that silence means discomfort.

If the student says:

> "Sometimes."

Record the raw response and clarify if necessary:

> "Would you say you are mostly comfortable or mostly uncomfortable?"

---

## SC04 — Teaching Methods

Question:

> "Which things help you understand, stay interested, and remember a topic the most?"

Expected options:

* Lecture only
* Examples and real-life stories
* Charts and mind maps
* Models and hands-on activities
* Storytelling

Type:

`multi_choice`

The student may select more than one.

Do not force the student to select only one.

Example:

> "Examples and charts."

Store both.

---

## SC05 — One-Day Retention

Question:

> "If you study a topic today, about what percentage of it do you remember the next day?"

Type:

`numeric / approximate`

The student may answer:

> "Around 70 percent."

Store:

```text
raw = "Around 70 percent."
normalized = 70
```

If the student cannot estimate:

> "Just give me your best estimate."

Do not imply that any particular percentage is expected.

---

## SC06 — One-Week Retention

Question:

> "And after one week, about what percentage of that topic do you still remember?"

Type:

`numeric / approximate`

The answer is independent from SC05.

---

## SC07 — Definitions and Formulas

Question:

> "Do you find it difficult to remember definitions or formulas?"

Expected:

* Yes
* No

Type:

`single_choice`

---

# 5. Section C — Memorizing & Memory

Purpose:

Assess the student's experience of memorization, relationship between understanding and remembering, support systems, revision behavior, memory strategies, and attitudes toward rote learning.

---

## LM01 — Feeling About Memorization

Question:

> "How does memorizing a subject usually feel to you?"

Options:

* Easy
* Difficult
* Boring
* Other

Type:

`single_choice`

If Other:

> "What does it feel like for you?"

Store the student's description.

---

## LM02 — Understanding and Memory

Question:

> "After you understand a topic properly, does it become easier to remember?"

Options:

* Yes
* No
* Somewhat

Type:

`single_choice`

---

## LM03 — Who Helps You Remember

Question:

> "Who usually helps you learn and remember a topic?"

Options:

* Teacher
* Tutor
* Parent
* Self-learning

Type:

`multi_choice`

The student may select more than one.

If the student says:

> "My brother."

Preserve the raw answer.

If the questionnaire requires categorization, record it as an additional qualitative response rather than incorrectly mapping it to Parent/Tutor.

---

## LM04 — Help With Learning

Question:

> "Do you feel that you can do better when someone helps you while learning?"

Options:

* Yes
* No

Type:

`single_choice`

---

## LM05 — Written Revision

Question:

> "After memorizing a topic, do you practise it by writing?"

Options:

* Yes
* No
* Sometimes

Type:

`single_choice`

---

## LM06 — Revision Frequency

Question:

> "After memorizing a topic, after how many days do you usually revise it?"

Type:

`numeric / free_text`

Examples:

> "Two days."

> "About a week."

> "I don't usually revise."

Preserve the raw response.

Normalize when possible.

---

## LM07 — Self-Questioning

Question:

> "Do you practise asking yourself questions and answering them to remember things?"

Options:

* Yes
* No
* Sometimes

Type:

`single_choice`

---

## LM08 — Confidence and Memory

Question:

> "Do you think lack of confidence or fear affects your memory?"

Options:

* Yes
* No

Type:

`single_choice`

Do not diagnose the student.

This records the student's own perception.

---

## LM09 — Note Taking

Question:

> "Do you make notes while studying?"

Options:

* Yes
* No

Type:

`single_choice`

---

## LM10 — Lesson Plans

Question:

> "Do you use lesson plans to help remember subject topics?"

Options:

* Yes
* No

Type:

`single_choice`

If the student does not understand "lesson plans", clarify without suggesting an answer.

---

## LM11 — Difficult Subject

Question:

> "Which subject is the most difficult for you to remember?"

Type:

`free_text`

Do not restrict the student to predefined subjects.

---

## LM12 — Favourite Subject

Question:

> "What is your favourite subject?"

Type:

`free_text`

---

## LM13 — Rote Learning

Question:

> "Do you think repeating or rewriting something again and again is the only effective way to remember it?"

Options:

* Yes
* No

Type:

`single_choice`

Do not imply whether rote learning is good or bad.

---

## LM14 — Special Memory Technique

Question:

> "Do you use any special trick or memory technique to remember something?"

Expected:

* Yes
* No

If Yes:

> "Can you tell me how you use it?"

Type:

`yes_no + qualitative_followup`

The follow-up is important because the original questionnaire explicitly asks the student to explain the technique in detail.

Examples of possible student responses:

> "I make a story."

> "I use short forms."

> "I draw pictures."

Do not classify the strategy unless the extraction system can do so reliably.

Always retain the original response.

---

## LM15 — Memory Strategies From Teacher/Tutor

Question:

> "Do your school teacher or tutor teach you any memory techniques or strategies?"

Options:

* Yes
* No

Type:

`single_choice`

---

## LM16 — Teacher Pressure to Memorize

Question:

> "When your subject teacher puts pressure on you to memorize a topic, how do you usually take it?"

Options:

* Seriously
* Normally
* I ignore it

Type:

`single_choice`

Do not judge the response.

---

## LM17 — Method of Memorization

Question:

> "When you memorize something, do you usually do it silently in your mind or say it out loud?"

Options:

* In the mind
* By speaking aloud

Type:

`single_choice`

If the student uses both:

> "Which one do you use more often?"

---

# 6. Section D — Examination & Stress

Purpose:

Assess the student's perception of examinations, relationship between exams and learning, response to marks, motivation, and perception of pressure.

---

## ES01 — Exams and Learning

Question:

> "Do you think examinations help improve your understanding, learning, and knowledge?"

Options:

* Yes
* No
* Sometimes

Type:

`single_choice`

---

## ES02 — Exam Results and Expectations

Question:

> "Do your exam results usually match what you expect from yourself?"

Options:

* Yes
* No
* Sometimes

Type:

`single_choice`

The original questionnaire frames this around whether the exam result reflects hard work and mindset.

Do not reinterpret the student's answer beyond the intended question.

---

## ES03 — Attitude Toward Exams

Question:

> "How do you usually feel about exams?"

Options:

* I take them very seriously and work hard.
* They are a normal event that happens every year.
* I think, 'whatever happens, we'll see.'

Type:

`single_choice`

Preserve the student's chosen attitude.

---

## ES04 — Reaction to Low Marks

Question:

> "What do you usually think when you don't get good marks in an exam?"

Options:

* It's okay.
* It's about what I expected.
* I'll do better next time.

Type:

`single_choice`

If the student gives a different answer, preserve it as a qualitative response.

---

## ES05 — Motivation After Lower Marks

Question:

> "Do marks that are lower than you expected motivate you to do better next time?"

Options:

* Yes
* No

Type:

`single_choice`

---

## ES06 — Effort and Results

Question:

> "When you work harder for better results, do you usually get the result you expect?"

Options:

* Yes
* No
* Sometimes

Type:

`single_choice`

---

## ES07 — Marks and Actual Ability

Question:

> "Do you think it is right to judge a student's actual ability only by the percentage or marks they get in exams?"

Options:

* Yes
* No
* Not sure

Type:

`single_choice`

The question is about the student's opinion.

Do not explain the concept of "actual ability" unless clarification is necessary.

---

# 7. Section E — Study Pattern Strategy

Purpose:

Assess study scheduling, session structure, concentration, incomplete work, and the student's primary difficulty during studying.

---

## SP01 — Fixed Timetable

Question:

> "Do you have a fixed timetable for studying at home?"

Options:

* Yes
* No
* Sometimes

Type:

`single_choice`

If Yes, the original questionnaire contains additional timetable-related information about duration and learning/revision activities.

Where enabled by the survey configuration, ask:

> "About how much time do you usually spend studying each day?"

Record the student's response.

---

## SP02 — Usual Study Pattern

Question:

> "How do you usually study?"

Options:

* Continuously for long periods
* In short sessions with breaks

Type:

`single_choice`

If the student describes another pattern, preserve the response and map only when appropriate.

---

## SP03 — Perceived Better Method

Question:

> "From your experience, which way gives you better results?"

Options:

* Studying continuously for long periods
* Studying in short sessions with breaks

Type:

`single_choice`

This is the student's perception.

Do not substitute the system's opinion.

---

## SP04 — Thirty-Minute Concentration

Question:

> "Can you study with full concentration continuously for about thirty minutes?"

Options:

* Yes
* No

Type:

`single_choice`

---

## SP05 — Incomplete Work

Question:

> "If you know that your learning or written work is incomplete, do you sometimes still leave it unfinished?"

Options:

* Yes
* No
* Sometimes

Type:

`single_choice`

The question concerns the student's behavior, not whether incomplete work is good or bad.

---

## SP06 — Difficult Stage of Studying

Question:

> "Which part of studying is the most difficult for you?"

Options:

* Understanding the topic
* Memorizing it
* Remembering it for a long time

Type:

`single_choice`

---

## SP07 — Biggest Study Problem

Question:

> "According to you, what is the biggest problem you face in studies: understanding, memorizing, or remembering?"

Options:

* Understanding
* Memorizing
* Retaining / remembering for a long time

Type:

`single_choice`

If the student gives a more detailed answer, preserve the raw response.

---

## SP08 — Interest in Memory Techniques

Question:

> "If you were taught a memory technique that made it easier to memorize a subject and remember it for a long time, would you want to learn it?"

Options:

* Yes
* No

Type:

`single_choice`

---

# 8. Section F — Final Open Response

## FR01 — Suggestions

Question:

> "Do you have any suggestions or ideas you'd like to share about studying, learning, or remembering things?"

Type:

`free_text`

Allow the student to speak without interruption.

Do not force the response into predefined categories.

This is an important qualitative field.

---

# 9. Question Progression

The default questionnaire progression is:

```text
Student Information
        ↓
Subject Comprehension & Teaching Style
        ↓
Learning & Memory
        ↓
Examination & Stress
        ↓
Study Pattern Strategy
        ↓
Final Suggestions
        ↓
Complete
```

The application must use the questionnaire version associated with the session.

The LLM must not arbitrarily reorder questions.

---

# 10. Clarification Policy

Clarification should be used only when required.

### Case 1 — Clear answer

Student:

> "Sometimes."

Action:

Record the answer and continue.

### Case 2 — Natural variation

Student:

> "I don't have one every day."

Interpret according to the expected options if confidence is high.

### Case 3 — Ambiguous

Student:

> "It depends."

Action:

Ask a short clarification.

### Case 4 — Off-topic

Student:

> "Why are you asking me this?"

Response:

> "I'm just trying to understand how students study and learn. You can answer based on your own experience."

Then repeat or continue with the question.

### Case 5 — Refusal

Student:

> "I don't want to answer."

Do not pressure the student.

Record according to the application's unanswered/refused state and continue where allowed.

---

# 11. Qualitative Data Rules

Open-ended answers are valuable research data.

For every qualitative response preserve:

```json
{
  "question_id": "LM14",
  "raw_response": "...",
  "normalized_insight": "...",
  "timestamp": "...",
  "confidence": 0.0
}
```

`normalized_insight` is optional.

`raw_response` is mandatory.

Never replace raw speech with an LLM-generated summary.

---

# 12. Answer Normalization

Normalization must not change meaning.

Example:

```text
"Yeah, mostly."
→ yes / high confidence

"Not really."
→ no / medium-high confidence

"Sometimes, depends on exams."
→ sometimes
```

For numerical answers:

```text
"About seventy percent"
→ 70
```

For free-form answers:

```text
"I make diagrams and then explain them to myself."
→ preserve raw response
```

Do not create unsupported conclusions.

---

# 13. Confidence

Every normalized answer may have a confidence value.

Suggested interpretation:

```text
0.90–1.00 → clear
0.70–0.89 → reasonably clear
0.50–0.69 → ambiguous
< 0.50    → clarification required
```

These thresholds are implementation defaults and may be overridden by application configuration.

Confidence must not be shown to the student.

---

# 14. Survey Completion Criteria

The survey is complete when all required questionnaire items have either:

1. A valid recorded answer, or
2. An explicitly recorded skipped/refused/unanswered state according to application policy.

Do not mark a question as answered merely because the LLM generated a plausible interpretation.

---

# 15. Final Output

After completion, the questionnaire engine should produce structured data containing at minimum:

```text
student_information
subject_comprehension
teaching_style
retention
learning_memory
memory_strategies
examination_profile
study_pattern
qualitative_responses
survey_metadata
```

The questionnaire itself does not determine final scoring methodology.

Scoring and analysis should be handled separately from the live interviewer.

---

# 16. Core Questionnaire Principle

The interviewer must collect:

> What the student actually thinks, does, experiences, and remembers.

It must not collect:

> What the interviewer thinks the student should think, do, experience, or remember.

Preserve the student's own voice wherever possible.
