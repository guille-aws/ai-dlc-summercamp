# CLAIRO - Requirements Verification Questions

Please answer each question by filling in the letter choice after the `[Answer]:` tag. If none of the options match, choose the "Other" option and describe your preference after the `[Answer]:` tag. Let me know when you're done.

---

## Section 1: Scope & Delivery Target

## Question 1
What is the primary goal for this initial build of CLAIRO?

A) Proof of Concept / demo — show the end-to-end three-agent flow working on sample claims, prioritize speed over hardening

B) MVP — a functional, deployable system on AWS with core features, some hardening, ready for pilot with real users

C) Production-grade system — full hardening, compliance, resiliency, and security for real-world claims

X) Other (please describe after [Answer]: tag below)

[Answer]: B) MVP

## Question 2
Which insurance domain(s) should the initial claim schema and policy logic target? (This shapes the canonical claim schema and knowledge base content.)

A) Auto/property claims (photos of damage, repair estimates)

B) Health/medical claims (medical reports, procedure codes)

C) General/multi-line (a generic schema flexible across claim types)

X) Other (please describe after [Answer]: tag below)

[Answer]: B) Health/medical claims

## Question 3
For this build, what claim input types must the Intake Agent support at minimum?

A) PDFs and images only

B) PDFs, images, and emails (text)

C) PDFs, images, emails, and handwritten notes (via Textract handwriting)

X) Other (please describe after [Answer]: tag below)

[Answer]: B) PDFs, images, and emails (text)

---

## Section 2: Architecture & Interaction Model

## Question 4
How should the three agents be orchestrated on AWS?

A) AWS Step Functions state machine coordinating Lambda-based agents (visual workflow, built-in retry, HITL wait states)

B) Amazon Bedrock Agents (managed agent runtime) with an orchestration layer

C) A single containerized orchestrator service (ECS/Fargate) invoking each agent in sequence

X) Other (please describe after [Answer]: tag below)

[Answer]: X) Other - Amazon Bedrock AgentCore

## Question 5
How should users and external systems interact with CLAIRO?

A) REST API (API Gateway) only — programmatic submission and status retrieval

B) REST API plus a lightweight web UI for claim submission and human review

C) Web UI for human reviewers plus API for claim ingestion, plus async/event-driven intake (e.g., S3 upload triggers)

X) Other (please describe after [Answer]: tag below)

[Answer]: C) Web UI for human reviewers plus API for claim ingestion, plus async/event-driven intake (e.g., S3 upload triggers)

## Question 6
How should the Human-in-the-Loop reviewer experience be delivered in this build?

A) A dedicated review web UI showing pre-filled recommendation, confidence, and highlighted evidence

B) Task routing into an existing tool (e.g., Amazon A2I / SQS queue + email notification) with a minimal review screen

C) API-only for now — expose review tasks via API, defer full UI

X) Other (please describe after [Answer]: tag below)

[Answer]: A) A dedicated review web UI showing pre-filled recommendation, confidence, and highlighted evidence

## Question 7
The description mentions human overrides feeding back into the knowledge base as corrective examples. How should this feedback loop work initially?

A) Automatic — approved overrides are written back to the knowledge base immediately

B) Curated — overrides are staged for a supervisor to approve before entering the knowledge base

C) Logged only for this build — capture overrides in a store, defer automated re-ingestion to a later phase

X) Other (please describe after [Answer]: tag below)

[Answer]: A) Automatic — approved overrides are written back to the knowledge base immediately

---

## Section 3: Data, Persistence & Identity

## Question 8
Where should claim records, decisions, and audit trails be persisted?

A) Amazon DynamoDB (claims + decisions) with S3 for documents/artifacts

B) Amazon Aurora/RDS (relational) with S3 for documents

C) DynamoDB for operational state + S3 for documents + a separate audit store (e.g., append-only S3 / QLDB-style)

X) Other (please describe after [Answer]: tag below)

[Answer]: C) DynamoDB for operational state + S3 for documents + a separate audit store (e.g., append-only S3 / QLDB-style)

## Question 9
What authentication/authorization approach should the system use?

A) Amazon Cognito user pools (roles: claim submitter, human reviewer, supervisor/admin)

B) IAM-based / API keys for machine-to-machine only (no end-user auth in this build)

C) Cognito for UI + IAM for service-to-service

X) Other (please describe after [Answer]: tag below)

[Answer]: C) Cognito for UI + IAM for service-to-service

## Question 10
What programming language / stack do you prefer for the application code (agents, APIs, orchestration handlers)?

A) Python (strong fit for Bedrock/Textract SDKs, common for AI workloads)

B) TypeScript/Node.js

C) Python for agents/AI + TypeScript for any web UI

X) Other (please describe after [Answer]: tag below)

[Answer]: C) Python for agents/AI + TypeScript for any web UI

## Question 11
What Infrastructure-as-Code tool should define the AWS deployment?

A) AWS CDK (TypeScript)

B) AWS CDK (Python)

C) Terraform

X) Other (please describe after [Answer]: tag below)

[Answer]: B) AWS CDK (Python)

---

## Section 4: Compliance & Decision Rules

## Question 12
For the Compliance Agent's regulatory rules (state-specific, EU-specific), what scope should this build cover?

A) A small representative rule set (e.g., 1-2 US states + EU/GDPR) as a demonstrable framework, extensible later

B) A configurable rules engine with externalized rule definitions, seeded with sample jurisdictions

C) Comprehensive multi-jurisdiction coverage

X) Other (please describe after [Answer]: tag below)

[Answer]: X) Other - GDPR Only

## Question 13
How should the confidence threshold for human routing be determined?

A) A single global configurable threshold (e.g., environment/config value)

B) Per-claim-type configurable thresholds

C) Per-jurisdiction and per-claim-type configurable thresholds

X) Other (please describe after [Answer]: tag below)

[Answer]: A) A single global configurable threshold (e.g., environment/config value)

---

## Section 5: Extension Opt-Ins

## Question: Security Extensions
Should security extension rules be enforced for this project?

A) Yes — enforce all SECURITY rules as blocking constraints (recommended for production-grade applications)

B) No — skip all SECURITY rules (suitable for PoCs, prototypes, and experimental projects)

X) Other (please describe after [Answer]: tag below)

[Answer]: B) No — skip all SECURITY rules (suitable for PoCs, prototypes, and experimental projects)

## Question: Resiliency Extensions
Should the resiliency baseline be applied to this project?

**What this extension is.** Enabling it applies a set of **directional, design-time best practices** for building resilient systems, derived from the **AWS Well-Architected Framework (Reliability Pillar)** and resilience-review guidance. It steers requirements, design, and code toward fault tolerance, high availability, observability, and recoverability — covering 15 practice areas across business goals, change management, observability, high availability, disaster recovery, and continuous improvement.

**What this extension is NOT.** Enabling it does **not** make your workload production-ready, nor does it certify or guarantee any availability, RTO, or RPO target. It is a **starting point** that scaffolds good resiliency decisions early — it is not a substitute for a formal **AWS Well-Architected Review** of the built system.

Treat the output as a well-grounded **first draft of your resiliency posture** to build on and validate — not a finished, production-certified result.

A) Yes — apply the resiliency baseline as directional best practices and design-time guidance (recommended for business-critical workloads, as an informed starting point that you can validate and harden before go-live)

B) No — skip the resiliency baseline (suitable for PoCs, prototypes, and experimental projects where rapid iteration matters more than reliability)

X) Other (please describe after [Answer]: tag below)

[Answer]: B) No — skip the resiliency baseline (suitable for PoCs, prototypes, and experimental projects where rapid iteration matters more than reliability)


## Question: Property-Based Testing Extension
Should property-based testing (PBT) rules be enforced for this project?

A) Yes — enforce all PBT rules as blocking constraints (recommended for projects with business logic, data transformations, serialization, or stateful components)

B) Partial — enforce PBT rules only for pure functions and serialization round-trips (suitable for projects with limited algorithmic complexity)

C) No — skip all PBT rules (suitable for simple CRUD applications, UI-only projects, or thin integration layers with no significant business logic)

X) Other (please describe after [Answer]: tag below)

[Answer]: C) No — skip all PBT rules (suitable for simple CRUD applications, UI-only projects, or thin integration layers with no significant business logic)
