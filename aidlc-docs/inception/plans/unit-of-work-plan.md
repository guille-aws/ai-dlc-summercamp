# CLAIRO - Unit of Work Plan

**Purpose**: Decompose CLAIRO into units of work for structured per-unit design and code generation.

**Context**: Greenfield, AWS-native MVP. Python agents + TypeScript UI, deployed via AWS CDK (Python). Components and services already defined in Application Design.

---

## Part A: Decomposition Questions

Please answer each question by filling in the letter after the `[Answer]:` tag. Choose **X) Other** and describe if none fit. Let me know when done.

### Question 1: Unit Decomposition Strategy
How should the system be decomposed into units of work?

A) By agent/capability — Intake, Adjudication, Compliance, HITL/Review, Feedback, plus a Shared Platform unit and an Infrastructure unit

B) Fewer, coarser units — Claims Pipeline (all 3 agents + orchestration), HITL/Review+Feedback, Shared Platform, Infrastructure

C) A single unit — one deployable application containing all modules

X) Other (please describe after [Answer]: tag below)

[Answer]: A) By agent/capability — Intake, Adjudication, Compliance, HITL/Review, Feedback, plus a Shared Platform unit and an Infrastructure unit

### Question 2: Deployment Model
How should the units be deployed?

A) Serverless — each agent/service as Lambda functions behind API Gateway + event triggers, orchestrated by AgentCore

B) Containerized — services on ECS/Fargate

C) Mixed — serverless for agents/APIs, managed services for KB/data

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Serverless — each agent/service as Lambda functions behind API Gateway + event triggers, orchestrated by AgentCore

### Question 3: Repository / Directory Structure (Greenfield)
How should the code be organized in the repository?

A) Monorepo — one repo with per-unit directories (e.g., `/services/intake`, `/services/adjudication`, `/web`, `/infra`)

B) Polyrepo — separate repositories per unit

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Monorepo — one repo with per-unit directories (e.g., `/services/intake`, `/services/adjudication`, `/web`, `/infra`)

### Question 4: Shared Code Strategy
How should shared code (canonical schema, data-access, audit, config, auth helpers) be handled?

A) A shared library/package used by all units (part of the Shared Platform unit)

B) Duplicated per unit to keep units fully independent

X) Other (please describe after [Answer]: tag below)

[Answer]: A) A shared library/package used by all units (part of the Shared Platform unit)

### Question 5: Build Sequence
Which unit should be built first to unblock the others?

A) Shared Platform + Infrastructure first (data stores, schema, auth, KB), then agents, then HITL/UI, then Feedback

B) Vertical slice first — one thin end-to-end path (intake→adjudicate→compliance→decision) then expand

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Shared Platform + Infrastructure first (data stores, schema, auth, KB), then agents, then HITL/UI, then Feedback

---

## Part B: Execution Checklist (executed after plan approval)

- [x] Generate `aidlc-docs/inception/application-design/unit-of-work.md` (unit definitions, responsibilities, code organization strategy)
- [x] Generate `aidlc-docs/inception/application-design/unit-of-work-dependency.md` (dependency matrix + build sequence)
- [x] Generate `aidlc-docs/inception/application-design/unit-of-work-story-map.md` (stories → units)
- [x] Validate unit boundaries and dependencies
- [x] Ensure all 12 stories are assigned to units
- [x] Update aidlc-state.md and audit.md
