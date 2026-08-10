# LLM Calls v1 — Invocation & Processing Policy

## 1. Purpose

This document defines how and when the system uses LLMs during a live voice survey.

The purpose is to:

* Minimize unnecessary LLM calls
* Keep voice latency low
* Separate live interaction from post-survey analysis
* Produce deterministic structured survey state
* Prevent the LLM from becoming the source of truth
* Make LLM behavior observable and reproducible

The LLM is a reasoning and language-processing component.

It is not the survey database or state machine.

---

# 2. Core Principle

The live survey should use the minimum number of LLM calls necessary to produce a reliable response.

Default target:

```text
1 meaningful student turn
        ↓
1 primary LLM call
        ↓
1 AI response
```

Additional calls are allowed only when required by ambiguity, recovery, or a separately defined post-processing task.

---

# 3. Live Conversation Pipeline

The normal live pipeline is:

```text
Student speaks
      ↓
VAD
      ↓
STT
      ↓
Student transcript
      ↓
Survey / Context preparation
      ↓
LLM Call
      ↓
Structured result + response
      ↓
TTS
      ↓
Student hears response
```

The application controls survey state.

The LLM operates inside that state.

---

# 4. Primary Live LLM Call

The primary call handles the normal conversational turn.

Its responsibilities may include:

1. Understanding the student's response.
2. Determining whether the response answers the current question.
3. Extracting the answer.
4. Identifying ambiguity.
5. Determining whether a permitted clarification is required.
6. Generating the next spoken response.

The call should return structured information rather than only plain text.

Example:

```json
{
  "answer": {
    "raw": "Sometimes, especially when exams are close.",
    "normalized": "sometimes",
    "confidence": 0.96
  },
  "action": "NEXT_QUESTION",
  "response": "Got it. How do you usually study?"
}
```

---

# 5. Primary Call Input

The primary LLM call should receive only the context required for the current turn.

Typical input:

```text
SYSTEM RULES
+
QUESTIONNAIRE RULES
+
CURRENT SURVEY STATE
+
CURRENT QUESTION
+
RELEVANT STRUCTURED ANSWERS
+
CONVERSATION SUMMARY
+
RECENT TURNS
+
CURRENT STUDENT TRANSCRIPT
```

Do not send the entire raw transcript by default.

Context construction follows `memory.v1.md`.

---

# 6. Primary Call Output

The LLM should return machine-readable output.

Recommended structure:

```json
{
  "action": "NEXT_QUESTION",
  "answer_status": "answered",
  "answer": {
    "value": "sometimes",
    "confidence": 0.96
  },
  "follow_up": null,
  "response": "Okay, got it. How do you usually study?"
}
```

Possible `action` values:

```text
NEXT_QUESTION
CLARIFY
REPEAT
SKIP
COMPLETE
ERROR
```

The exact enum must be enforced by application code.

---

# 7. Application Validation

Never directly trust an LLM response.

After every LLM call:

```text
LLM output
    ↓
Schema validation
    ↓
Application validation
    ↓
Survey state update
```

Validate:

* Required fields
* Enum values
* Question ID
* Answer type
* Confidence range
* Follow-up limits
* Current survey state

If validation fails, do not update the survey state using the invalid output.

---

# 8. LLM Does Not Choose Arbitrary Questions

The LLM must not generate its own questionnaire progression.

The application provides:

```text
current_question
next_allowed_question
questionnaire_rules
```

The LLM can determine:

```text
answered
clarification_needed
unable_to_answer
```

But the application decides which questionnaire item comes next.

---

# 9. Normal Answer

If the student clearly answers the current question:

```text
Student
 ↓
STT
 ↓
LLM
 ↓
answer_status = answered
 ↓
save answer
 ↓
advance state
 ↓
generate response
```

Example:

Student:

> "Yes, I have a fixed timetable."

LLM:

```json
{
  "answer_status": "answered",
  "answer": {
    "value": "yes",
    "confidence": 0.99
  },
  "action": "NEXT_QUESTION"
}
```

---

# 10. Ambiguous Answer

If the student gives an unclear response:

```text
Student
 ↓
LLM
 ↓
answer_status = ambiguous
 ↓
CLARIFY
```

Example:

Student:

> "It depends."

LLM:

```json
{
  "answer_status": "ambiguous",
  "action": "CLARIFY",
  "response": "Do you have a timetable sometimes, or do you usually not have one?"
}
```

The application should increment the clarification count.

---

# 11. Clarification Limit

Clarification must not become an infinite loop.

Default:

```text
maximum clarification attempts = 2
```

After the limit:

```text
mark answer:
    unclear
    skipped
    refused
```

according to questionnaire/application policy.

Then continue to the next allowed question.

---

# 12. Repeat Request

If the student says:

> "Can you repeat the question?"

Do not unnecessarily invoke a second reasoning process if the application can simply repeat the current question.

The application should replay or regenerate the current question according to the configured behavior.

Example:

```text
Student:
"Sorry, repeat that."

Action:
REPEAT
```

No answer state change should occur.

---

# 13. Student Says "I Don't Know"

Treat this differently from an incorrect answer.

Example:

> "I don't know."

Possible state:

```json
{
  "answer_status": "unknown",
  "action": "NEXT_QUESTION"
}
```

Do not attempt to teach the student the answer.

Do not pressure the student.

---

# 14. Student Refuses

If the student says:

> "I don't want to answer."

Record:

```text
answer_status = refused
```

Do not keep asking the same question unless application policy explicitly requires a retry.

Continue when permitted.

---

# 15. Off-Topic Question

Example:

Student:

> "Are you a real person?"

The LLM may answer briefly:

> "I'm an AI interviewer. Let's continue with the survey."

Then return to the current questionnaire item.

Do not allow unrelated conversation to consume the survey session.

---

# 16. Follow-Up Call

A second LLM call may be used when a permitted qualitative follow-up requires deeper interpretation.

Example:

```text
Question:
"Do you use any special memory technique?"

Student:
"Yeah, I make stories."

Primary call:
answer = yes

Follow-up:
"Can you tell me how you use the stories?"
```

The follow-up question should be generated only when:

* Questionnaire rules permit it
* The information is useful
* The interaction remains within the survey scope

---

# 17. Follow-Up Should Not Become Open Conversation

Maximum follow-up depth should be configurable.

Recommended default:

```text
max_followups_per_question = 1
```

Some questions may explicitly allow more.

Do not recursively generate follow-up questions.

Bad:

```text
Question
 ↓
Follow-up
 ↓
Follow-up
 ↓
Follow-up
 ↓
Conversation never ends
```

---

# 18. Structured Extraction

If the primary LLM call produces structured extraction, save:

```text
raw response
+
normalized answer
+
confidence
+
question ID
+
turn ID
```

Example:

```json
{
  "question_id": "SP02",
  "raw_response": "I usually study for twenty minutes and then take a break.",
  "normalized_answer": "short_sessions_with_breaks",
  "confidence": 0.97
}
```

---

# 19. Do Not Use Separate LLM Calls Unnecessarily

Avoid this architecture for every normal turn:

```text
STT
 ↓
LLM #1 — understand answer
 ↓
LLM #2 — decide next question
 ↓
LLM #3 — generate response
 ↓
TTS
```

This increases:

* Latency
* Cost
* Failure points
* Context synchronization problems

Prefer:

```text
STT
 ↓
LLM #1
 ↓
Structured decision + response
 ↓
TTS
```

---

# 20. When Multiple Calls Are Justified

Multiple calls may be justified for:

### A. Ambiguous interpretation

If the primary call cannot reliably interpret the answer.

### B. Complex qualitative extraction

When a detailed open-ended response requires separate structured analysis.

### C. Recovery

When context/state reconstruction is required after an interruption or agent restart.

### D. Post-survey analysis

When the interview is complete and deeper analysis is required.

### E. Quality assurance

Optional offline evaluation of collected data.

These calls should not unnecessarily block the live voice interaction.

---

# 21. Post-Survey Analysis

Post-survey analysis should be separate from the live interviewer.

After completion:

```text
Survey complete
      ↓
Persist final state
      ↓
Async analysis job
      ↓
LLM analysis
      ↓
Research / analytics output
```

Possible analysis:

* Learning profile
* Study pattern
* Memory strategies
* Teaching preferences
* Retention patterns
* Exam perceptions
* Qualitative themes

The live interviewer should not wait for all of this.

---

# 22. Final Analysis Must Use Stored Data

Post-survey LLM calls should use stored:

```text
structured answers
+
qualitative responses
+
transcript
+
survey metadata
```

Do not rely on the live conversation context still existing in memory.

---

# 23. LLM Call Types

The implementation should distinguish calls by purpose.

Recommended types:

```text
LIVE_INTERVIEW
CLARIFICATION
QUALITATIVE_EXTRACTION
RECOVERY
POST_SURVEY_ANALYSIS
QUALITY_CHECK
```

Each call should have a unique request ID.

---

# 24. LLM Request Logging

Where logging is enabled, record:

```json
{
  "request_id": "llm_123",
  "session_id": "sess_456",
  "call_type": "LIVE_INTERVIEW",
  "model": "model-name",
  "timestamp": "...",
  "input_context_id": "ctx_789",
  "input_tokens": 1234,
  "output_tokens": 180,
  "latency_ms": 820,
  "status": "success"
}
```

The actual prompt/context may also be persisted according to data-retention policy.

---

# 25. Model Configuration

Model configuration must be externalized.

Do not hardcode model names throughout the application.

Example:

```text
LIVE_INTERVIEW_MODEL
QUALITATIVE_MODEL
ANALYSIS_MODEL
```

Different tasks may use different models.

For example:

```text
Live conversation
→ fast / low-latency model

Post-survey analysis
→ stronger reasoning model
```

The exact models are implementation configuration, not questionnaire logic.

---

# 26. Temperature / Generation Configuration

Generation parameters should be configurable.

Live interviewer responses should favor:

* Consistency
* Conciseness
* Predictability
* Low latency

Creative generation should not be prioritized.

The system should avoid unnecessary verbosity.

---

# 27. TTS Separation

LLM output and TTS output are separate layers.

The LLM generates:

```text
spoken_response
```

TTS converts:

```text
spoken_response
        ↓
audio
```

The LLM should not generate SSML or provider-specific audio instructions unless explicitly required by the TTS implementation.

---

# 28. Streaming

Where supported:

```text
LLM streaming
      ↓
sentence/phrase buffering
      ↓
TTS
      ↓
LiveKit
```

Do not wait for the entire LLM response if streaming significantly improves perceived latency.

However, structured state decisions must be validated before they affect survey state.

---

# 29. Interruption During Generation

If the student interrupts while the AI is speaking:

```text
Student starts speaking
        ↓
VAD interruption
        ↓
Stop TTS
        ↓
Cancel unnecessary generation
        ↓
Process student turn
```

Do not continue spending tokens generating a response that the student is no longer listening to.

---

# 30. Failed Calls

If a call fails:

1. Preserve the student transcript.
2. Do not advance survey state unless a valid answer has already been safely recorded.
3. Retry according to configured retry policy.
4. If retry fails, use the application's fallback behavior.
5. Never invent an answer.

Example fallback:

> "Sorry, I didn't catch that. Could you say it once more?"

---

# 31. Retry Policy

Retries must be bounded.

Recommended:

```text
max_live_retries = 1
```

For transient infrastructure failures, the system may retry according to backend policy.

Do not repeatedly retry expensive model calls indefinitely.

---

# 32. Idempotency

Every LLM call should have a unique request ID.

If a network timeout occurs after the model may have completed:

```text
Do not blindly execute the same state transition twice.
```

Use request IDs / state checks to prevent duplicate:

* Answers
* Question transitions
* Follow-ups
* Completion events

---

# 33. Context Consistency

Every LLM call must be associated with the context used to produce it.

Example:

```text
request_id
    ↓
context_snapshot_id
    ↓
survey_state_version
```

This makes it possible to determine:

> What state and context existed when this response was generated?

---

# 34. Live vs Offline Calls

The system has two major classes of LLM work.

## Live

Must optimize for:

```text
latency
reliability
short responses
```

Used for:

* Answer understanding
* Clarification
* Conversational response

## Offline

Can optimize for:

```text
accuracy
depth
analysis
```

Used for:

* Profile generation
* Qualitative analysis
* Dataset enrichment
* Research summaries
* Quality evaluation

Do not make offline work block the live interview.

---

# 35. Recommended Default Call Pattern

For a normal question:

```text
STT
 ↓
1 × LIVE_INTERVIEW
 ↓
structured answer
+
spoken response
 ↓
TTS
```

For an ambiguous answer:

```text
STT
 ↓
1 × LIVE_INTERVIEW
 ↓
CLARIFY
 ↓
TTS
 ↓
student answers again
 ↓
1 × LIVE_INTERVIEW
```

For an open-ended question:

```text
STT
 ↓
1 × LIVE_INTERVIEW
 ↓
save raw response
 ↓
continue survey
```

Optional:

```text
ASYNC QUALITATIVE_EXTRACTION
```

For survey completion:

```text
final answer
 ↓
persist state
 ↓
END LIVE SESSION
 ↓
ASYNC POST_SURVEY_ANALYSIS
```

---

# 36. Cost Principle

Do not optimize only for minimum number of calls.

Optimize for:

```text
useful information / latency / cost
```

One additional call is acceptable when it substantially improves answer accuracy or research value.

Unnecessary calls are not acceptable merely because an LLM can perform the task.

---

# 37. Final LLM Principle

The system follows:

> **One good call is better than three loosely separated calls.**

The LLM should provide conversational intelligence while the application provides:

* State
* Rules
* Memory
* Validation
* Persistence
* Deterministic survey progression

The LLM interprets and communicates.

The application controls what is true.
