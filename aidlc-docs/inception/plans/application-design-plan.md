# CLAIRO - Application Design Plan

**Role**: Solution Architect
**Purpose**: Identify high-level components, their responsibilities/interfaces, the service/orchestration layer, and dependencies. (Detailed business logic comes later in Functional Design.)

---

## Part A: Design Clarification Questions

Please answer each question by filling in the letter after the `[Answer]:` tag. Choose **X) Other** and describe if none fit. Let me know when done.

### Question 1: Component Granularity
How granular should the top-level components be?

A) Coarse — one component per agent (Intake, Adjudication, Compliance) plus HITL, plus shared platform

B) Medium — each agent split into its logical sub-parts (e.g., Intake = OCR adapter + LLM extractor + normalizer)

C) Fine — many small single-responsibility components

X) Other (please describe after [Answer]: tag below)

[Answer]: B) Medium — each agent split into its logical sub-parts (e.g., Intake = OCR adapter + LLM extractor + normalizer)

### Question 2: Orchestration Style with Bedrock AgentCore
How should the three agents coordinate within AgentCore?

A) Sequential pipeline — a top-level orchestrator invokes Intake → Adjudication → Compliance in order, then routes to HITL if needed

B) Event-driven — each stage completes and emits an event that triggers the next (looser coupling)

C) Hybrid — orchestrator drives the main sequence, with events used for the async HITL wait and feedback write-back

X) Other (please describe after [Answer]: tag below)

[Answer]: C) Hybrid — orchestrator drives the main sequence, with events used for the async HITL wait and feedback write-back

### Question 3: Claim State Management
How should a claim's progress through the pipeline be tracked?

A) A single claim record in DynamoDB with a status field updated at each stage

B) A claim record plus a separate per-stage results structure (intake result, adjudication result, compliance result)

C) Orchestrator-managed state (AgentCore session) plus a persisted claim record for durability

X) Other (please describe after [Answer]: tag below)

[Answer]: A) A single claim record in DynamoDB with a status field updated at each stage

### Question 4: Knowledge Base Access
Which components should talk to the Bedrock Knowledge Base (OpenSearch Serverless)?

A) Only the Adjudication component reads; only the Feedback component writes

B) A dedicated Knowledge Base Service that both Adjudication (read) and Feedback (write) call — centralizes KB access

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Only the Adjudication component reads; only the Feedback component writes

### Question 5: Reviewer UI ↔ Backend Communication
How should the reviewer web UI communicate with the backend?

A) Through the same REST API (API Gateway) used for ingestion, with role-scoped endpoints

B) A separate dedicated review API distinct from the ingestion API

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Through the same REST API (API Gateway) used for ingestion, with role-scoped endpoints

### Question 6: Human Review Wait Pattern
When a claim routes to a human, how should the pipeline handle the wait?

A) Pause/async — pipeline persists a "Pending Review" task and stops; a reviewer action later resumes finalization

B) Polling — a process periodically checks for completed reviews

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Pause/async — pipeline persists a "Pending Review" task and stops; a reviewer action later resumes finalization

---

## Part B: Execution Checklist (executed after plan approval)

- [x] Generate `components.md` (component definitions, responsibilities, interfaces)
- [x] Generate `component-methods.md` (method signatures + I/O types; business rules deferred)
- [x] Generate `services.md` (service/orchestration layer definitions and interactions)
- [x] Generate `component-dependency.md` (dependency matrix, communication patterns, data flow)
- [x] Generate consolidated `application-design.md`
- [x] Validate design completeness and consistency
- [x] Update aidlc-state.md and audit.md
