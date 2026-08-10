# Memory v1 — Conversation & Context Management

## 1. Purpose

This document defines how conversation history, survey state, summaries, structured answers, and LLM context are stored and reconstructed during a survey session.

The goal is to provide the LLM with enough context to conduct a natural conversation without repeatedly sending the entire conversation history.

The system must distinguish between:

1. Raw conversation history
2. Recent conversation context
3. Conversation summary
4. Structured survey state
5. Student/session memory
6. LLM context
7. LLM context snapshots

These are different representations and must not be treated as interchangeable.

---

# 2. Core Memory Principle

The system follows:

```text
Raw Data
    ↓
Stored History
    ↓
Structured State
    ↓
Compressed Memory
    ↓
LLM Context
```

The LLM context is **derived from stored state**.

The LLM context is not the authoritative source of truth.

If LLM context conflicts with application state:

> Application state wins.

If a summary conflicts with the raw transcript:

> Raw transcript wins.

If an LLM interpretation conflicts with the student's actual response:

> The student's actual response wins.

---

# 3. Memory Layers

Each active session maintains the following layers.

```text
Session
│
├── Raw Transcript
│
├── Recent Turns
│
├── Conversation Summary
│
├── Survey State
│
├── Structured Answers
│
├── Session Memory
│
└── LLM Context Snapshot
```

---

# 4. Raw Transcript

The raw transcript is the permanent conversational record.

Every meaningful speech turn should be stored.

Example:

```json
{
  "session_id": "sess_123",
  "turn_id": 18,
  "speaker": "student",
  "text": "I usually study at night because it's quieter.",
  "timestamp": 182.42
}
```

For AI turns:

```json
{
  "session_id": "sess_123",
  "turn_id": 19,
  "speaker": "assistant",
  "text": "Got it. How do you usually study?",
  "timestamp": 185.10
}
```

The transcript should preserve chronological order.

---

# 5. Raw Transcript Must Never Be Overwritten

Do not replace the student's original answer with:

* A summary
* A normalized answer
* An LLM interpretation
* A corrected sentence
* A cleaned-up sentence

Example:

Student says:

> "Umm, I study mostly at night... because during the day I get distracted."

Store exactly that transcription as the raw response.

A normalized interpretation may separately contain:

```json
{
  "study_time": "night",
  "daytime_distraction": true
}
```

Both must remain available.

---

# 6. Audio Relationship

Where audio recording is enabled, every relevant transcript turn should be traceable to its corresponding audio segment.

Conceptually:

```text
Audio Segment
     ↓
STT
     ↓
Transcript Turn
     ↓
Question Answer
```

Store identifiers allowing the system to connect:

```text
audio_segment_id
turn_id
question_id
timestamp
```

Do not require the LLM to infer this relationship.

---

# 7. Recent Conversation Memory

The system maintains a short window of recent conversational turns.

Purpose:

* Preserve immediate conversational continuity
* Resolve references such as "that", "it", or "yes"
* Understand corrections
* Handle interruptions
* Understand the immediate previous answer

Example:

```text
Student:
"I study better with diagrams."

AI:
"Do you make those diagrams yourself?"

Student:
"Yes, mostly."

```

The recent context should preserve enough of this exchange for the LLM to understand:

> "those diagrams"

without sending the entire transcript.

---

# 8. Recent Turn Window

The number of recent turns should be configurable.

Default recommendation:

```text
Last 4–8 conversational turns
```

The system should not blindly increase this window as the conversation becomes longer.

If a specific older turn becomes relevant, retrieve it through structured memory or targeted history retrieval rather than continuously expanding the context window.

---

# 9. Conversation Summary

The system maintains a compact summary of important information discovered during the conversation.

The summary should contain information useful for future conversation.

Example:

```text
Student prefers studying in short sessions.
Student finds long-term retention difficult.
Student uses diagrams to remember topics.
Student usually studies at night.
Student sometimes revises after a few days.
```

The summary should NOT contain:

* Greetings
* Filler conversation
* Repeated answers
* Unimportant small talk
* LLM-generated opinions
* Unsupported conclusions

---

# 10. Summary Rules

The summary should be:

* Short
* Factual
* Student-specific
* Derived from actual responses
* Updated incrementally

Do not rewrite the entire summary after every turn unless necessary.

Prefer incremental updates.

Example:

Existing:

```text
Student prefers short study sessions.
```

New information:

```text
Student studies mostly at night.
```

Updated:

```text
Student prefers short study sessions and usually studies at night.
```

---

# 11. Summary Must Not Become a Source of Truth

A summary is compressed memory.

It can contain omissions or compression.

Therefore:

```text
Raw transcript > structured answer > summary
```

If the summary says:

> "Student does not revise."

but the raw transcript contains:

> "I revise sometimes, usually after three days."

The raw response must be treated as authoritative.

The summary must be corrected.

---

# 12. Structured Survey State

Survey state is maintained separately from conversational memory.

Example:

```json
{
  "section": "learning_memory",
  "question_id": "LM07",
  "status": "in_progress",
  "completed_questions": [
    "SP01",
    "SP02",
    "SP03"
  ]
}
```

This state determines where the interview currently is.

The LLM must not infer the current question solely from conversation history.

---

# 13. Structured Answers

Every questionnaire response should be stored independently from the transcript.

Example:

```json
{
  "question_id": "SP02",
  "raw_response": "I usually study for like twenty minutes and then take a break.",
  "normalized_answer": "short_sessions_with_breaks",
  "confidence": 0.96,
  "turn_id": 27
}
```

Structured answers allow the system to build context without repeatedly reading the entire transcript.

---

# 14. Answer History

If an answer is corrected, do not silently overwrite the previous value.

Example:

```text
Initial:
SP02 = long_sessions

Student later clarifies:
"I meant when I have exams. Normally I study in short sessions."
```

Store the correction history.

Final normalized state:

```text
SP02 = short_sessions
```

But preserve the earlier interpretation in the history/audit record.

---

# 15. Session Memory

Session memory contains information discovered during the current survey that may help the interviewer behave naturally.

Examples:

```text
Student prefers examples.
Student struggles with formulas.
Student studies mostly at night.
Student is comfortable asking teachers questions.
```

Session memory must remain scoped to the current session unless explicitly configured otherwise.

---

# 16. Cross-Session Student Memory

Persistent student memory is optional.

If enabled, it must be clearly separated from session memory.

Example:

```text
student_memory
    ↓
session_001
session_002
session_003
```

Do not automatically carry information from a previous survey into a new survey unless the application explicitly allows it.

Previous answers must not influence the student's current survey response.

---

# 17. No Cross-Student Memory

Student memory must never leak across sessions.

Never reuse:

```text
Student A's summary
Student A's answers
Student A's transcript
Student A's LLM context
```

for Student B.

Every memory object must be associated with a unique session/student scope.

---

# 18. LLM Context Construction

The LLM should receive a dynamically constructed context.

Default structure:

```text
SYSTEM INSTRUCTIONS
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
        ↓
       LLM
```

Do not automatically include the complete transcript.

---

# 19. Context Priority

When constructing LLM context, use this priority:

```text
1. Current question
2. Current survey state
3. Relevant structured answers
4. Recent turns
5. Conversation summary
6. Other retrieved history
```

The current question must remain clearly identifiable.

---

# 20. Relevant History Retrieval

Older conversation should only be retrieved when it is relevant.

Example:

Student says:

> "I told you earlier that I use a trick for this."

The system may retrieve the earlier answer about the memory technique.

It should not load the entire previous conversation.

Possible retrieval:

```text
query:
student memory technique
```

Then provide the relevant turn to the LLM.

---

# 21. Context Budget

The system must respect the configured context/token budget.

If context becomes too large:

1. Keep system instructions.
2. Keep questionnaire instructions required for the current question.
3. Keep current survey state.
4. Keep current question.
5. Keep relevant structured answers.
6. Keep recent turns.
7. Compress or retrieve older information as needed.

Never solve context growth by blindly sending the entire transcript.

---

# 22. Context Snapshots

The system should save snapshots of the context used by important LLM calls.

A snapshot may contain:

```json
{
  "session_id": "sess_123",
  "snapshot_id": "ctx_029",
  "timestamp": "...",
  "survey_state": {},
  "summary": "...",
  "recent_turns": [],
  "structured_answers": {},
  "context_hash": "..."
}
```

Snapshots are useful for:

* Debugging
* Reproducing model behavior
* Investigating incorrect answers
* Auditing survey sessions
* Comparing model versions

---

# 23. LLM Request Logging

The memory system should support storing the actual context sent to the LLM.

Where configured, record:

```text
request_id
session_id
model
prompt/context
response
timestamp
token usage
latency
```

This allows the system to answer:

> "What did the model actually know when it generated this response?"

Do not assume that the current memory state is identical to the context that was used historically.

---

# 24. Memory Update Timing

Memory updates should happen after meaningful conversational events.

Typical flow:

```text
Student speaks
      ↓
STT
      ↓
Answer understanding
      ↓
Survey state update
      ↓
Structured answer saved
      ↓
Memory update
      ↓
Context construction
      ↓
LLM response
```

Do not update memory based on incomplete speech unless the application explicitly supports partial-turn memory.

---

# 25. Interruption Handling

When the student interrupts the AI:

1. Stop unnecessary TTS output.
2. Preserve already completed transcript content.
3. Cancel unnecessary generation.
4. Process the new student turn.
5. Do not create duplicate conversation turns.
6. Reconstruct context using the updated state.

If the AI had generated a response that was never fully spoken, distinguish:

```text
generated_response
```

from:

```text
spoken_response
```

when the implementation supports this.

---

# 26. Failed LLM Calls

If an LLM call fails:

Do not modify survey state using an assumed response.

The system should:

1. Preserve the student's input.
2. Keep the current question unchanged.
3. Retry according to `llm_calls.md`.
4. Reconstruct context from stored state if necessary.

Never lose the student's response because an LLM call failed.

---

# 27. Session Recovery

If the voice agent restarts during an active survey:

The system must reconstruct the session from persistent state.

Recovery order:

```text
session state
      ↓
structured answers
      ↓
conversation summary
      ↓
recent turns
      ↓
current question
      ↓
LLM context
```

Do not depend solely on in-memory Python variables.

---

# 28. Context Reconstruction

The LLM context should be reproducible from stored state.

Conceptually:

```text
Stored Session
      +
Stored Survey
      +
Stored Answers
      +
Stored Memory
      ↓
Context Builder
      ↓
LLM Context
```

This means context should be treated as a **derived artifact**, not the only copy of memory.

---

# 29. Memory Persistence

At minimum, persist:

```text
session_id
survey_version
current_question
survey_status
transcript
structured_answers
conversation_summary
memory_version
```

Where supported:

```text
audio references
LLM request logs
context snapshots
token usage
model version
```

---

# 30. Data Separation

Keep these concepts separate:

```text
RAW
├── audio
└── transcript

STATE
├── current question
├── survey status
└── completed questions

ANSWERS
├── raw answer
├── normalized answer
└── confidence

MEMORY
├── summary
├── recent turns
└── relevant retrieved history

LLM
├── context
├── request
└── response
```

Do not collapse all of these into a single `conversation_history` object.

---

# 31. Memory and Future Model Training

Because the collected data may later be used for research, ML, or LLM development, preserve the distinction between:

```text
What the student said
```

and:

```text
What the system thinks the student meant
```

Example:

```json
{
  "raw_response": "I make little stories in my head.",
  "normalized_response": {
    "strategy": "storytelling"
  }
}
```

The normalized response is derived data.

The raw response is the original evidence.

Never treat an LLM-generated interpretation as if it were the student's original statement.

---

# 32. Versioning

Memory behavior must be versioned.

Every session should record:

```text
memory_version = v1
```

If the memory algorithm changes:

```text
memory_version = v2
```

This allows old sessions to remain interpretable.

---

# 33. Memory Integrity Rules

The system must never:

* Mix memories between students
* Invent memories
* Invent previous answers
* Treat summaries as exact transcripts
* Modify raw transcripts
* Forget the current survey state
* Use old student data without permission/configuration
* Let LLM-generated context override application state

---

# 34. Core Principle

The memory architecture follows one fundamental rule:

> **Store everything important, send only what is necessary.**

The system should retain enough information to reconstruct the complete session while giving the live LLM only the context required for the current conversational task.

The raw transcript is the historical record.

The structured state is the operational truth.

The summary is compressed memory.

The LLM context is a temporary, derived view of the information needed for the current model call.
