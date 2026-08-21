# Voice Survey Student App — Design System

## 1. Design Direction

### Product

**Voice Survey Student App (`frontendapp`)**

### Design Concept

A calm, futuristic voice-interview interface for students aged 12–15.

The experience should feel less like a traditional school form and more like entering a **quiet AI conversation space**.

The visual direction is inspired by a dark-stage aesthetic:

- Pure black canvas
- Large, lightweight typography
- Electric violet as the primary interaction color
- Small amber highlights
- Minimal containers
- Generous whitespace
- Soft ambient motion
- Audio-reactive visualizations
- No unnecessary dashboards, menus, or dense UI

The interface should feel:

> **calm + futuristic + friendly + trustworthy**

It should never feel:

> corporate + clinical + childish + game-like + intimidating

---

# 2. Design Principles

## 2.1 Voice First

The voice interaction is the product.

The UI should support the conversation rather than compete with it.

Avoid:

- Large navigation systems
- Dense information
- Excessive controls
- Multiple competing CTAs
- Complex menus

---

## 2.2 One Primary Action

Every screen should have one obvious next action.

Examples:

- Access Gate → **Start Voice Survey**
- Mic Check → **Join Interview**
- Voice Room → **End Survey**
- Completion → **Close Session**

Primary actions use Electric Iris.

---

## 2.3 Calm Visual Hierarchy

The interface should have very few visual layers.

Use:

- Typography
- Whitespace
- Violet accents
- Subtle motion
- Audio visualization

Avoid:

- Heavy shadows
- Borders everywhere
- Gradient cards
- Excessive icons
- Multiple colored buttons

---

## 2.4 Friendly, Not Childish

The audience is Grade 7–8 students.

Do not use cartoon characters, childish illustrations, emojis everywhere, or overly gamified UI.

Instead use:

- Soft animated orb
- Friendly copy
- Clear instructions
- Subtle celebratory motion
- Conversational language

---

# 3. Color System

The primary visual tokens are derived from the provided dark-stage style reference.

| Token | Value | Usage |
|---|---|---|
| `--color-void` | `#000000` | Main background |
| `--color-bone-white` | `#ffffff` | Primary text |
| `--color-ash-gray` | `#9a9a9a` | Secondary text |
| `--color-silver-mist` | `#bdbdbd` | Supporting text |
| `--color-electric-iris` | `#8052ff` | Primary CTA / active state |
| `--color-saffron-spark` | `#ffb829` | Highlights / progress / attention |
| `--color-deep-verdant` | `#15846e` | Secondary visual accent |

### Usage Rules

### Black

Black is the primary surface.

```css
background: #000000;
```

Do not replace it with dark gray.

---

### White

Use white for:

- Main headings
- Important information
- Active controls
- Transcript text

---

### Ash Gray

Use for:

- Instructions
- Secondary labels
- Inactive controls
- Helper text

---

### Electric Iris

Use for:

- Primary CTA
- Active progress
- Mic state
- AI speaking visualization
- Focus states
- Brand accent

Do not use violet as a large background section.

---

### Saffron Spark

Use sparingly for:

- Section labels
- Small highlights
- Completion accents
- Attention states

It should remain an accent rather than a second primary color.

---

# 4. Typography

Use **PPNeueMontreal** when available, with **Inter** as the fallback. The reference system uses PPNeueMontreal across the interface and relies heavily on scale rather than boldness for hierarchy.

```css
font-family:
  'PPNeueMontreal',
  Inter,
  ui-sans-serif,
  system-ui,
  sans-serif;
```

## Type Scale

| Role | Size | Weight | Usage |
|---|---:|---:|---|
| Caption | 12px | 400 | Small metadata |
| Label | 14px | 600 | Uppercase labels |
| Body | 18px | 200 | Instructions |
| Small Heading | 24px | 400 | Secondary headings |
| Subheading | 36px | 400 | Screen headings |
| Heading | 48px | 400 | Main headings |
| Display | 78px | 400 | Hero moments |

The source design uses 78–113px display typography and ultra-light 18px body copy. For this student application, the larger display sizes should be used selectively because the app is an interaction product rather than a marketing site.

---

# 5. Spacing

Use a 6px base spacing unit.

```css
--spacing-6: 6px;
--spacing-12: 12px;
--spacing-18: 18px;
--spacing-24: 24px;
--spacing-30: 30px;
--spacing-36: 36px;
--spacing-60: 60px;
--spacing-96: 96px;
```

Primary screen content should generally use:

- 24px internal spacing
- 36px component spacing
- 60px major section spacing

The reference design uses generous 60–120px section spacing and a 1280px maximum content width.

---

# 6. Shape Language

Use rounded shapes selectively.

| Component | Radius |
|---|---:|
| Primary Button | 24px |
| Input | 18px |
| Modal | 24px |
| Transcript | 24px |
| Audio Orb | 9999px |
| Progress Track | 9999px |
| Small Badge | 9999px |

The overall system should feel soft without becoming overly card-based.

---

# 7. Global Layout

## Desktop

```text
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  LOGO / SURVEY                          SESSION STATUS        │
│                                                              │
│                                                              │
│                                                              │
│              MAIN INTERACTION AREA                           │
│                                                              │
│                                                              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

Maximum content width:

```text
1280px
```

Horizontal padding:

```text
Desktop: 48–64px
Tablet: 32px
Mobile: 20–24px
```

---

# 8. Ambient Background

The application should use a subtle procedural particle field inspired by the reference's constellation visualization. The reference describes thousands of small triangular particles against black as its signature visual language.

For the student app:

- Keep particle density low
- Avoid visual distraction
- Use mostly violet particles
- Occasionally introduce amber and teal
- Keep opacity extremely low
- Add slow floating motion

The background should never interfere with text readability.

### Example

```text
                    ·        △

          ·                  ·

                ✦     △

                         ·

     ┌─────────────────────────────┐
     │                             │
     │       SURVEY CONTENT        │
     │                             │
     └─────────────────────────────┘

          △                   ·
```

---

# 9. Navigation

The app does not need traditional navigation.

Instead use a minimal top status bar.

```text
┌──────────────────────────────────────────────────────────────┐
│  ◢ Voice Survey                              ● Connected     │
└──────────────────────────────────────────────────────────────┘
```

### Left

Small brand mark:

```text
◢ Voice Survey
```

### Right

Connection state:

```text
● Connected
```

States:

- `Connecting...`
- `Connected`
- `Reconnecting...`
- `Offline`

The connection indicator should use text + a small animated dot.

---

# 10. Screen 1 — Access Gate

## Objective

Allow the student to enter the survey with minimum friction.

The screen should feel welcoming immediately.

### Layout

```text
                     VOICE SURVEY

                Ready to get started?

          Enter the details provided by your school.

                 School Code
              ┌───────────────────┐
              │ SCH-804            │
              └───────────────────┘

                 Student ID
              ┌───────────────────┐
              │ STU-1029          │
              └───────────────────┘

                 Your Name
              ┌───────────────────┐
              │ Alex              │
              └───────────────────┘

                 Grade
              ┌───────────────────┐
              │ Grade 8        ˅  │
              └───────────────────┘

              ┌───────────────────────┐
              │  Start Voice Survey → │
              └───────────────────────┘
```

### Heading

```text
Ready to talk?
```

Alternative:

```text
Let's get started.
```

### Supporting Copy

```text
Enter the details provided by your school.
No account or password is needed.
```

### Form

Inputs should be visually minimal.

Do not use heavy cards.

Input style:

- Black background
- 1px subtle translucent white border
- 18px radius
- White text
- Violet focus ring
- 52–56px height

### CTA

Electric Iris pill.

```text
START VOICE SURVEY →
```

The button should have a subtle hover glow.

---

# 11. Access Gate States

## Empty

CTA disabled or visually subdued.

## Typing

Focused input receives:

```text
border: #8052ff
```

## Valid

Input returns to minimal neutral state.

## Invalid

Show inline error directly below the field.

Example:

```text
We couldn't find that school code.
Check the code and try again.
```

Do not use aggressive red screens.

## Loading

CTA becomes:

```text
CONNECTING...
```

with a small animated indicator.

---

# 12. Screen 2 — Microphone Check

This screen should feel like a short preparation moment rather than a technical setup page.

### Layout

```text
                    One quick check.

              Let's make sure we can hear you.

                         ◉
                    ╱  │  ╲
                  ╱    │    ╲
                     AUDIO

                  Speak normally.

                ███████░░░░░░

             Microphone detected

             [ Join Interview → ]
```

---

## Audio Orb

Central animated orb.

### Idle

Small violet breathing glow.

### Listening

Orb expands slightly.

### Audio detected

Create concentric ripples based on microphone amplitude.

### No audio

Show:

```text
We can't hear anything yet.
Try saying "Hello".
```

---

# 13. Permission State

If microphone permission has not been granted:

```text
Allow microphone access

Your microphone is needed so the interviewer
can hear your answers.

[ Allow Microphone ]
```

Browser permission itself should be triggered by the browser.

The UI should explain **why** permission is needed before requesting it.

---

# 14. Screen 3 — Live Voice Room

This is the most important screen.

The interface should become extremely minimal.

No traditional chat layout.

No giant transcript history.

No unnecessary navigation.

---

## Main Layout

```text
┌──────────────────────────────────────────────────────────────┐
│  VOICE SURVEY                              ● Connected       │
│                                                              │
│                                                              │
│                                                              │
│                        ◉                                     │
│                     ╱     ╲                                  │
│                  ╱           ╲                               │
│                                                              │
│                  I'm listening.                              │
│                                                              │
│        "What helps you understand something new?"            │
│                                                              │
│                                                              │
│  Section B · Teaching Style                         62%       │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━░░░░░░░░                 │
│                                                              │
│                  🎤      🔊      End                          │
└──────────────────────────────────────────────────────────────┘
```

---

# 15. AI Audio Orb

The orb is the primary visual representation of the AI.

## State: Idle

```text
        ·
     ·  ◉  ·
        ·
```

Slow breathing animation.

---

## State: AI Speaking

Orb grows and contracts according to audio amplitude.

Use:

- Violet core
- Soft violet glow
- Thin surrounding rings
- Small particle displacement

Animation should be fluid, not flashy.

---

## State: User Speaking

The orb becomes slightly quieter while a separate microphone ripple appears.

```text
             ◉
          (     )
        ((       ))
      (((         )))
```

This gives immediate feedback that the user's voice is being detected.

---

## State: Barge-In

If the student starts speaking while the AI is talking:

- AI orb immediately contracts
- Microphone ripple appears
- Small label appears:

```text
Listening...
```

The visual transition should happen immediately.

---

# 16. Transcript

Transcript is supportive rather than dominant.

Only show the current relevant conversational content.

### AI Question

Large white text:

```text
What helps you understand something new?
```

### Student Speech

Smaller muted text:

```text
You: When someone explains it with an example...
```

Live speech can appear with a subtle typing/fade effect.

Do not display a huge scrolling transcript window.

---

# 17. Transcript States

### AI Thinking

```text
Thinking...
```

Small amber indicator.

### AI Speaking

Question appears progressively.

### Student Speaking

```text
Listening...
```

with live transcription.

### Processing

```text
Got it.
```

briefly appears before the next question.

---

# 18. Progress Indicator

Keep progress subtle.

Example:

```text
SECTION B · TEACHING STYLE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━░░░░░

6 / 10
```

Avoid gamified percentage animations.

The student should understand:

- How far they are
- Which section they are in
- That the interview is progressing

without feeling like a test.

---

# 19. Control Dock

Controls should remain at the bottom.

```text
             🎤       🔊       End Survey
```

### Mic

Primary control.

States:

```text
🎤 Mic On
🎤 Mic Off
```

When muted, use a subtle warning state rather than bright red.

---

### Speaker

Allow volume adjustment.

A compact volume slider may appear when activated.

---

### End Survey

Text/ghost button.

Do not make it visually equal to the primary CTA.

---

# 20. End Survey Modal

The student must not accidentally terminate the interview.

```text
End the survey?

Your answers so far will be submitted.

        [ Continue Survey ]

             End Survey
```

Primary action:

```text
Continue Survey
```

Secondary action:

```text
End Survey
```

The modal should remain minimal and use the black canvas.

---

# 21. Connection States

## Connecting

```text
Connecting to your interviewer...
```

## Connected

```text
● Connected
```

## Reconnecting

```text
Connection interrupted.

Trying to reconnect...
```

The interview screen should remain visible.

Do not immediately throw the student back to the access screen.

---

# 22. Screen 4 — Completion

The completion screen should provide positive reinforcement without becoming overly gamified.

### Layout

```text
                    ✓

              You're all done.

        Thanks for sharing your thoughts.

              10 questions answered
              08:42 interview time

              [ Close Session ]
```

---

## Completion Visual

Use:

- Violet circular mark
- Small particle burst
- Very subtle amber accents

Avoid:

- Confetti overload
- Trophies
- Leaderboards
- Points
- Competitive language

---

# 23. Responsive Design

## Desktop

Use centered interaction area with large whitespace.

Minimum recommended:

```text
1280 × 720
```

---

## Tablet

Primary target.

Recommended:

```text
768 × 1024
```

Reduce typography.

Keep orb large.

Controls should be easy to tap.

Minimum touch target:

```text
44 × 44px
```

---

## Mobile

Recommended:

```text
360 × 800
```

Layout becomes single-column.

Access form fills approximately 90% of available width.

Voice room:

```text
Header
   ↓
Orb
   ↓
Transcript
   ↓
Progress
   ↓
Controls
```

---

# 24. Accessibility

The application is intended for students, so accessibility is a core requirement.

## Requirements

- Keyboard navigable inputs
- Visible focus states
- Minimum 44px touch targets
- Do not rely only on color to indicate state
- Transcript must remain readable
- Buttons must have accessible labels
- Microphone state must have text + visual indication
- Connection state must have text + visual indication
- Respect `prefers-reduced-motion`

---

# 25. Animation Principles

Animation should communicate state.

Never animate purely for decoration.

### Timing

```text
Micro interaction: 150–200ms
Button: 200ms
Screen transition: 300–400ms
Orb breathing: 2.5–4s
Connection pulse: 1.5–2s
```

### Reduced Motion

When:

```css
@media (prefers-reduced-motion: reduce)
```

Disable:

- Particle movement
- Orb breathing
- Ripple expansion
- Large transitions

Keep functional state changes visible.

---

# 26. Component Architecture

Suggested components:

```text
components/
├── layout/
│   ├── AppShell
│   └── SessionStatus
│
├── access/
│   ├── AccessGate
│   ├── AccessInput
│   └── GradeSelector
│
├── audio/
│   ├── AudioOrb
│   ├── AudioLevelMeter
│   ├── MicPermission
│   └── AudioRipple
│
├── interview/
│   ├── VoiceRoom
│   ├── Transcript
│   ├── ProgressIndicator
│   ├── ControlDock
│   └── EndSurveyModal
│
├── completion/
│   └── CompletionScreen
│
└── background/
    └── AmbientParticles
```

---

# 27. State Model

```text
ACCESS
  ↓
MIC_PERMISSION
  ↓
MIC_CHECK
  ↓
CONNECTING
  ↓
INTERVIEW
  ↓
COMPLETING
  ↓
COMPLETE
```

Error states can branch from any stage:

```text
ERROR
  ↓
RETRY
```

---

# 28. Design Tokens

```css
:root {
  --color-void: #000000;
  --color-bone-white: #ffffff;
  --color-ash-gray: #9a9a9a;
  --color-silver-mist: #bdbdbd;

  --color-electric-iris: #8052ff;
  --color-saffron-spark: #ffb829;
  --color-deep-verdant: #15846e;

  --font-display: 'PPNeueMontreal', Inter, sans-serif;

  --text-caption: 12px;
  --text-label: 14px;
  --text-body: 18px;
  --text-small-heading: 24px;
  --text-subheading: 36px;
  --text-heading: 48px;
  --text-display: 78px;

  --weight-light: 200;
  --weight-regular: 400;
  --weight-semibold: 600;

  --spacing-6: 6px;
  --spacing-12: 12px;
  --spacing-18: 18px;
  --spacing-24: 24px;
  --spacing-30: 30px;
  --spacing-36: 36px;
  --spacing-60: 60px;
  --spacing-96: 96px;

  --radius-input: 18px;
  --radius-button: 24px;
  --radius-modal: 24px;
  --radius-full: 9999px;

  --page-max-width: 1280px;
}
```

---

# 29. Visual Do's

- Use pure black as the dominant canvas.
- Use Electric Iris for primary actions.
- Keep typography large and lightweight.
- Use whitespace as the main layout tool.
- Make the audio orb the visual centerpiece.
- Use subtle procedural particles.
- Keep the transcript simple.
- Make interaction states immediately understandable.
- Keep the student focused on the conversation.
- Use motion to communicate audio and connection state.

---

# 30. Visual Don'ts

- Do not create a conventional SaaS dashboard.
- Do not use multiple large cards.
- Do not use heavy shadows.
- Do not use gradients on UI surfaces.
- Do not use bright red as the dominant error color.
- Do not make the app look like a children's game.
- Do not add unnecessary navigation.
- Do not show a huge transcript history.
- Do not overwhelm the student with technical WebRTC information.
- Do not introduce multiple competing primary buttons.

---

# 31. Overall Experience

The final experience should feel like:

```text
Enter
  ↓
Prepare
  ↓
Listen
  ↓
Speak
  ↓
Finish
```

The interface should disappear as much as possible once the conversation begins.

The **voice interaction is the product**.

The UI exists only to make that interaction feel clear, safe, responsive, and engaging.