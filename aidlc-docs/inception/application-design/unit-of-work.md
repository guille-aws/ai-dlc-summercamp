# CLAIRO - Units of Work

**Decomposition strategy**: By agent/capability (Q1:A)
**Deployment model**: Serverless — Lambda + API Gateway + event triggers, orchestrated by Bedrock AgentCore (Q2:A)
**Repository structure**: Monorepo with per-unit directories (Q3:A)
**Shared code**: Shared library within the Shared Platform unit (Q4:A)
**Build sequence**: Shared Platform + Infrastructure first, then agents, then HITL/UI, then Feedback (Q5:A)

---

## Units

### U0: Infrastructure (AWS CDK)
- **Type**: Infrastructure-as-code (AWS CDK, Python)
- **Responsibility**: Define all AWS resources — Lambdas, API Gateway, DynamoDB, S3 buckets, audit store, Bedrock Knowledge Base + OpenSearch Serverless collection, Cognito user pool, IAM roles, AgentCore configuration, CloudWatch.
- **Contains**: CDK stacks per logical grouping (data, api, agents, auth, kb, web hosting).

### U1: Shared Platform
- **Type**: Shared Python library + platform Lambdas
- **Responsibility**: Canonical health-claim schema, Claim Repository (DynamoDB), Document Store (S3), Audit Logger (append-only), Config Provider (threshold + GDPR rules ref), Identity & Access helpers (Cognito/IAM), common utilities.
- **Consumed by**: all other units.

### U2: Intake
- **Type**: Serverless agent unit
- **Responsibility**: OCR Adapter (Textract), Email/Text Parser, LLM Extractor (Bedrock Claude Sonnet), Claim Normalizer. Produces CanonicalClaim.
- **Stories**: US-01, US-02, US-03.

### U3: Adjudication
- **Type**: Serverless agent unit
- **Responsibility**: KB Retriever (read Bedrock KB), Decision Reasoner (Bedrock). Produces PreliminaryDecision with confidence + reasoning.
- **Stories**: US-04.

### U4: Compliance
- **Type**: Serverless agent unit
- **Responsibility**: GDPR Rule Validator, Explanation Generator (S3). Produces ComplianceFindings + explanation.
- **Stories**: US-05.

### U5: HITL / Review + API + Orchestration
- **Type**: Serverless unit (APIs + orchestration + reviewer-facing backend)
- **Responsibility**: Claim Orchestrator (AgentCore hybrid sequence + events), Routing Evaluator, Review Task Manager, Evidence Highlighter, and the Claim API (role-scoped endpoints). Handles pause/async human review.
- **Stories**: US-06, US-07, US-09, US-10, US-11, US-12.
- **Note**: Orchestration lives here because it is the coordination layer that ties agents together and drives the review pause/resume.

### U6: Feedback (Learning Loop)
- **Type**: Serverless unit (event-triggered)
- **Responsibility**: Feedback Ingestor — on override event, write corrective example to Bedrock KB automatically.
- **Stories**: US-08.

### U7: Web UI
- **Type**: TypeScript web application
- **Responsibility**: Reviewer web UI (queue, recommendation, confidence, highlighted evidence, decision/override), claim status views, Cognito login.
- **Stories**: US-06 (UI), US-07 (UI), US-09 (UI), US-12 (login).

---

## Code Organization Strategy (Monorepo)
```
/                         (repo root)
├── infra/                # U0 - AWS CDK (Python) stacks
├── libs/
│   └── clairo_shared/    # U1 - shared Python library (schema, repos, audit, config, auth)
├── services/
│   ├── intake/           # U2
│   ├── adjudication/     # U3
│   ├── compliance/       # U4
│   ├── orchestration_api/# U5 (orchestrator + Claim API + HITL backend)
│   └── feedback/         # U6
├── web/                  # U7 - TypeScript reviewer UI
├── tests/                # cross-unit integration tests
└── aidlc-docs/           # documentation (already present)
```

## Validation
- All 12 stories are assigned (see `unit-of-work-story-map.md`). ✔
- Unit boundaries follow the medium-granularity components from Application Design. ✔
- Shared Platform centralizes cross-cutting concerns; agents remain independent and orchestrated. ✔
