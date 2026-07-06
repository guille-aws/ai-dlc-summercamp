# CLAIRO - User Story Generation Plan

**Role**: Product Owner
**Purpose**: Define the methodology and decisions for converting CLAIRO requirements into user stories and personas.

---

## Part A: Planning Questions

Please answer each question by filling in the letter after the `[Answer]:` tag. Choose **X) Other** and describe if none fit. Let me know when done.

### Question 1: Story Breakdown Approach
How should stories be organized?

A) User Journey-Based — stories follow end-to-end claim workflows

B) Feature-Based — stories organized around system features/capabilities

C) Persona-Based — stories grouped by user type

D) Hybrid — Persona-based grouping, with stories written along user journeys within each persona

X) Other (please describe after [Answer]: tag below)

[Answer]: A) User Journey-Based — stories follow end-to-end claim workflows

### Question 2: Personas to Include
Which personas should be modeled? (The requirements identified submitter, reviewer, supervisor/admin roles.)

A) Claim Submitter, Human Reviewer, Supervisor/Admin

B) The above plus a Compliance Officer persona

C) The above plus an integrating External System (API consumer) as an actor

D) All of the above (Submitter, Reviewer, Supervisor/Admin, Compliance Officer, External System)

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Claim Submitter, Human Reviewer, Supervisor/Admin

### Question 3: Acceptance Criteria Format
What format should acceptance criteria use?

A) Given/When/Then (Gherkin-style)

B) Bulleted checklist of conditions

C) Given/When/Then for behavior-heavy stories, bulleted checklist for simple ones

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Given/When/Then (Gherkin-style)

### Question 4: Story Granularity
What level of granularity do you want?

A) Coarse — epic-level stories (fewer, broader)

B) Medium — feature-level stories sized for a few days of work each

C) Fine — small, narrowly-scoped stories with detailed criteria

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Coarse — epic-level stories (fewer, broader)

### Question 5: Should the agent pipeline behaviors be written as user stories?
The three agents act autonomously (not a human user). How should we represent them?

A) As system/technical stories ("As the Intake Agent, the system shall...") alongside human-user stories

B) Only as acceptance criteria under human-facing stories (agents are implementation detail)

C) As a mix — key agent behaviors get their own system stories; the rest are acceptance criteria

X) Other (please describe after [Answer]: tag below)

[Answer]: A) As system/technical stories ("As the Intake Agent, the system shall...") alongside human-user stories

### Question 6: Prioritization / MoSCoW
Should stories carry a priority label (Must/Should/Could/Won't) for this MVP?

A) Yes — apply MoSCoW labels to every story

B) No — keep stories unprioritized for now

X) Other (please describe after [Answer]: tag below)

[Answer]: B) No — keep stories unprioritized for now

---

## Part B: Execution Checklist (executed after plan approval)

- [x] Generate `personas.md` with user archetypes and characteristics (per Q2 answer)
- [x] Generate `stories.md` with user stories using the approved breakdown approach (Q1) and granularity (Q4)
- [x] Represent agent behaviors per Q5 answer
- [x] Write acceptance criteria for each story using the approved format (Q3)
- [x] Apply prioritization per Q6 answer (N/A — user chose no prioritization)
- [x] Ensure stories follow INVEST criteria (Independent, Negotiable, Valuable, Estimable, Small, Testable)
- [x] Map personas to relevant user stories
- [x] Trace each story back to requirements (FR/NFR IDs) for coverage
- [x] Update aidlc-state.md and audit.md
