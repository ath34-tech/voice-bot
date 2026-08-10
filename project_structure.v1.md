# Project Structure v1 — Voice Surveyor

## 1. Goal

Build the minimum practical architecture for a multi-room AI voice survey system.

The system uses:

* FastAPI
* LiveKit Server running through Docker
* LiveKit Python Agent
* STT
* LLM
* TTS
* Survey/questionnaire engine
* Conversation memory
* Persistent session state

The first version should remain a **single Python application/repository**.

Do not split the system into microservices.

---

# 2. Project Structure

```text
voice-surveyor/
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
├── .env.example
├── README.md
│
├── main.py
├── server.py
├── rooms.py
├── pipeline.py
├── stt.py
├── llm.py
├── tts.py
├── memory.py
├── questionnaire.py
├── state.py
├── storage.py
├── schemas.py
│
├── system.v1.md
├── questionnaire.v1.md
├── memory.v1.md
├── llm_calls.v1.md
└── project_structure.v1.md
```

This is intentionally small.

All application source files and system instruction files live in the same project directory.

---

# 3. Infrastructure

## `docker-compose.yml`

Docker Compose runs the local infrastructure required by the system.

At minimum, it should run:

```text
LiveKit Server
```

Conceptually:

```text
Docker Compose
│
└── LiveKit Server
        │
        │ WebRTC
        │
        ▼
   Python Agent
```

The Python application may run:

* directly on the host during development, or
* inside Docker when required.

The LiveKit server should be independently restartable from the Python application.

---

# 4. LiveKit Server

LiveKit is responsible for real-time audio transport.

It handles:

* Rooms
* Participants
* Audio tracks
* WebRTC
* Audio routing
* Connection management

The Python application should **not implement WebRTC itself**.

The architecture is:

```text
Student Browser
       │
       │ WebRTC
       ▼
LiveKit Server
       │
       │ Audio Track
       ▼
Python Voice Agent
```

---

# 5. `main.py`

The application entry point.

Responsibilities:

* Start the application
* Initialize required services
* Start FastAPI
* Start/prepare the LiveKit agent environment where appropriate

Do not put questionnaire logic or provider-specific voice logic here.

---

# 6. `server.py`

FastAPI HTTP server.

Responsibilities:

* Create survey sessions
* Create LiveKit rooms
* Generate LiveKit access tokens
* Return room information to the frontend
* Return survey status
* Return survey results
* Stop/end sessions when required

Minimum endpoints:

```text
POST /start_call
GET  /session/{session_id}
GET  /session/{session_id}/results
GET  /session/{session_id}/transcript
```

Example flow:

```text
Frontend
   │
   │ POST /start_call
   ▼
FastAPI
   │
   ├── Create session
   ├── Create LiveKit room
   ├── Generate token
   └── Dispatch agent
   │
   ▼
Frontend joins room
```

---

# 7. `rooms.py`

Responsible for LiveKit room management.

Responsibilities:

* Generate unique room names
* Create rooms
* Generate participant tokens
* Associate rooms with sessions
* Dispatch the appropriate agent
* Track active sessions

Example:

```text
session_83921
     │
     └── room_session_83921
```

Every survey gets its own room.

Never reuse one room for multiple independent students.

---

# 8. `pipeline.py`

This is the main real-time voice agent.

It connects the components:

```text
LiveKit
   ↓
Audio
   ↓
STT
   ↓
Survey State
   ↓
Memory
   ↓
LLM
   ↓
TTS
   ↓
LiveKit
```

The pipeline is responsible for orchestration.

It should not contain:

* The entire questionnaire
* Provider-specific STT implementation
* Provider-specific TTS implementation
* Database implementation
* Large prompt strings

Those belong in their respective files.

---

# 9. `stt.py`

Speech-to-text layer.

Responsibilities:

* Receive student audio
* Process speech
* Detect completed speech
* Return transcript
* Handle STT errors
* Support interruption/VAD behavior where provided by the voice framework

Interface should be provider-independent.

Example:

```python
class SpeechToText:
    async def transcribe(self, audio):
        ...
```

The pipeline should only care about:

```text
audio → transcript
```

It should not care which STT provider produced it.

---

# 10. `llm.py`

LLM interface.

Responsibilities:

* Load model configuration
* Build/send LLM requests
* Handle structured responses
* Support streaming where useful
* Handle retries/timeouts
* Return validated model output
* Record LLM metadata

The behavior of the LLM is defined by:

```text
system.v1.md
questionnaire.v1.md
memory.v1.md
llm_calls.v1.md
```

Do not hardcode all of those rules inside Python.

---

# 11. `tts.py`

Text-to-speech layer.

Responsibilities:

```text
LLM response
     ↓
TTS
     ↓
audio
     ↓
LiveKit
```

It should support:

* Streaming audio
* Cancellation
* Interruption
* Provider errors

The pipeline should not depend directly on a specific TTS provider.

---

# 12. `questionnaire.py`

Survey engine.

Responsibilities:

* Load the questionnaire definition
* Track question progression
* Get current question
* Validate answers
* Handle allowed clarification
* Handle follow-ups
* Determine when the survey is complete

The actual survey definition is:

```text
questionnaire.v1.md
```

Do not scatter questions across `pipeline.py`.

---

# 13. `state.py`

Authoritative survey state.

Example:

```python
class SurveyState:
    session_id
    room_id
    survey_version
    current_section
    current_question
    completed_questions
    answers
    status
```

Possible states:

```text
created
connecting
in_progress
completed
failed
```

The LLM cannot directly control this state.

The application validates the LLM's output and updates state.

---

# 14. `memory.py`

Conversation memory manager.

Responsibilities:

* Store recent turns
* Maintain summary
* Retrieve relevant previous turns
* Build LLM context
* Save context snapshots
* Recover context after restart

It implements the rules defined in:

```text
memory.v1.md
```

It must distinguish:

```text
Raw Transcript
Recent Turns
Summary
Structured Answers
LLM Context
```

---

# 15. `storage.py`

Persistence layer.

The first version can use a simple database or local persistent storage.

It must store at minimum:

```text
sessions
survey state
answers
transcript
memory
LLM call metadata
```

The rest of the application should interact through this module instead of directly writing database queries everywhere.

---

# 16. `schemas.py`

Shared data models.

Use this for Pydantic models such as:

```text
Session
SurveyState
Question
Answer
TranscriptTurn
LLMResponse
MemorySnapshot
LLMCall
```

Example:

```python
class Answer(BaseModel):
    question_id: str
    raw_response: str
    normalized_answer: str | None
    confidence: float | None
```

---

# 17. Instruction Files

The project contains five Markdown instruction files.

```text
system.v1.md
questionnaire.v1.md
memory.v1.md
llm_calls.v1.md
project_structure.v1.md
```

These are **instructions to the coding/AI system**, not Python modules.

---

# 18. `system.v1.md`

Defines:

* AI interviewer identity
* General behavior
* Voice behavior
* Neutrality
* Student interaction
* Session isolation
* Error handling
* Interruption behavior

This is the global system contract.

---

# 19. `questionnaire.v1.md`

Defines:

* Survey sections
* Questions
* Question IDs
* Answer types
* Options
* Clarifications
* Follow-ups
* Question progression
* Qualitative responses

This is the survey contract.

---

# 20. `memory.v1.md`

Defines:

* Raw transcript
* Recent conversation
* Summary
* Structured memory
* LLM context
* Context snapshots
* Recovery
* Memory persistence

This is the memory contract.

---

# 21. `llm_calls.v1.md`

Defines:

* Normal LLM call
* Clarification call
* Follow-up call
* Post-survey analysis
* Retry behavior
* Streaming
* Logging
* Context requirements

This is the LLM invocation contract.

---

# 22. `project_structure.v1.md`

Defines the responsibility of every source file.

The coding agent must follow this document before creating new modules.

---

# 23. Docker Architecture

Development environment:

```text
                    Docker Compose
                         │
                         ▼
                 ┌────────────────┐
                 │ LiveKit Server │
                 └───────┬────────┘
                         │
                    WebRTC / WS
                         │
                         ▼
                 ┌────────────────┐
                 │ Python Agent   │
                 │                │
                 │ pipeline.py    │
                 │ stt.py         │
                 │ llm.py         │
                 │ tts.py         │
                 │ memory.py      │
                 └───────┬────────┘
                         │
                         ▼
                    FastAPI API
```

The frontend connects to LiveKit directly for media.

FastAPI handles session/control operations.

---

# 24. Multi-Room Runtime

When multiple students start surveys:

```text
                    LiveKit Server
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
       Room A          Room B          Room C
          │              │              │
          ▼              ▼              ▼
      Agent A         Agent B         Agent C
          │              │              │
       Student A      Student B      Student C
```

Each agent maintains its own:

```text
session state
memory
transcript
questionnaire progress
LLM context
```

No conversational state is shared between rooms.

---

# 25. Agent Lifecycle

For each new survey:

```text
POST /start_call
      ↓
Create session
      ↓
Create LiveKit room
      ↓
Generate frontend token
      ↓
Dispatch voice agent
      ↓
Agent joins room
      ↓
Load questionnaire
      ↓
Initialize state
      ↓
Initialize memory
      ↓
Start conversation
```

---

# 26. Normal Voice Turn

```text
Student speaks
      ↓
LiveKit
      ↓
STT
      ↓
Transcript
      ↓
Memory update
      ↓
Questionnaire / State
      ↓
LLM
      ↓
Validated response
      ↓
State update
      ↓
TTS
      ↓
LiveKit
      ↓
Student hears response
```

---

# 27. Interruption

When the student interrupts the AI:

```text
AI speaking
    ↓
Student starts speaking
    ↓
VAD detects speech
    ↓
Stop TTS
    ↓
Cancel unnecessary LLM generation
    ↓
Capture student speech
    ↓
STT
    ↓
Process new turn
```

The system must not force the student to wait for the AI to finish.

---

# 28. Session Storage

A simple initial storage layout may be:

```text
data/
└── sessions/
    ├── session_001/
    │   ├── state.json
    │   ├── answers.json
    │   ├── transcript.jsonl
    │   ├── memory.json
    │   └── llm_calls.jsonl
    │
    └── session_002/
        ├── state.json
        ├── answers.json
        ├── transcript.jsonl
        ├── memory.json
        └── llm_calls.jsonl
```

If audio recording is enabled:

```text
session_001/
└── audio/
```

The storage backend may later be replaced with PostgreSQL/object storage without changing the voice pipeline.

---

# 29. Environment

`.env` contains runtime secrets/configuration.

Example:

```text
LIVEKIT_URL=
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=

LLM_API_KEY=
STT_API_KEY=
TTS_API_KEY=
```

`.env` must never be committed.

`.env.example` contains variable names without secrets.

---

# 30. Requirements

`requirements.txt` contains only dependencies actually used by the application.

At minimum, the project will need packages for:

```text
FastAPI
LiveKit
Pydantic
Environment/configuration
Selected STT provider
Selected LLM provider
Selected TTS provider
```

Do not install large frameworks unless they provide a concrete benefit.

---

# 31. Docker Responsibility

Docker should initially be used primarily for:

```text
LiveKit Server
```

The Python application can run locally during development for faster iteration.

Once the application is stable, the Python agent can also be containerized.

Do not introduce Kubernetes or multiple containers for every Python module.

---

# 32. Frontend Boundary

The frontend is not part of this Python project structure unless explicitly added later.

The frontend is responsible for:

* Joining the LiveKit room
* Microphone permissions
* Displaying survey/session status
* Ending the session

FastAPI is responsible for:

* Session creation
* Room/token generation
* Survey status
* Results

LiveKit is responsible for:

* Real-time audio transport

Python Agent is responsible for:

* Interview intelligence
* Survey progression
* Memory
* STT/LLM/TTS orchestration

---

# 33. Minimum Dependency Flow

Keep the dependency flow simple:

```text
server.py
    ↓
rooms.py
    ↓
pipeline.py
    ↓
┌──────────┬──────────┬──────────┐
│          │          │          │
stt.py    llm.py     tts.py   memory.py
│          │          │          │
└──────────┴──────────┴──────────┘
               │
          questionnaire.py
               │
            state.py
               │
          storage.py
```

`schemas.py` provides shared models.

No module should import the pipeline merely to perform its own task.

---

# 34. Implementation Order

Build in this order:

```text
1. schemas.py
2. state.py
3. questionnaire.py
4. storage.py
5. memory.py
6. llm.py
7. stt.py
8. tts.py
9. pipeline.py
10. rooms.py
11. server.py
12. main.py
13. docker-compose.yml
```

First make the survey work without real-time voice.

Then connect:

```text
STT → LLM → TTS
```

Then connect LiveKit.

Then test multiple rooms.

---

# 35. Do Not Overengineer v1

Do NOT create:

```text
microservices/
agents/
repositories/
factories/
event_bus/
message_broker/
vector_db/
kafka/
redis/
celery/
kubernetes/
```

unless a real requirement appears.

The initial system should remain:

```text
One repository
One Python application
One LiveKit server
Multiple isolated rooms
Clear module boundaries
```

---

# 36. Final v1 Architecture

```text
voice-surveyor/
│
├── docker-compose.yml        # LiveKit server
├── Dockerfile
├── requirements.txt
├── .env
├── .env.example
├── README.md
│
├── main.py                   # Application entry
├── server.py                 # FastAPI
├── rooms.py                  # LiveKit rooms/tokens
├── pipeline.py               # Voice agent orchestration
├── stt.py                    # Speech → text
├── llm.py                    # LLM calls
├── tts.py                    # Text → speech
├── memory.py                 # Context/history
├── questionnaire.py          # Survey engine
├── state.py                  # Authoritative state
├── storage.py                # Persistence
├── schemas.py                # Data models
│
├── system.v1.md
├── questionnaire.v1.md
├── memory.v1.md
├── llm_calls.v1.md
└── project_structure.v1.md
```

## Core rule

Keep the repository **small and explicit**.

The Python files implement the system.

The Markdown files define how the AI system should behave.

LiveKit handles real-time media.

FastAPI handles control/session management.

The pipeline connects everything.

The survey state remains deterministic.

Memory remains separate from the LLM.

The LLM provides intelligence, not application state.
