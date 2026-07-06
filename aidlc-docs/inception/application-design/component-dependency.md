# CLAIRO - Component Dependencies

## Dependency Matrix

| Component / Service | Depends On |
|---|---|
| Claim Orchestrator (S1) | Intake Service, Adjudication Service, Compliance Service, Routing Evaluator, Claim Repository, Audit Logger |
| Intake Service (S2) | OCR Adapter, Email/Text Parser, LLM Extractor, Claim Normalizer, Document Store, Claim Repository, Audit Logger |
| Adjudication Service (S3) | KB Retriever (read KB), Decision Reasoner, Claim Repository, Audit Logger |
| Compliance Service (S4) | GDPR Rule Validator, Explanation Generator, Document Store, Config Provider, Audit Logger |
| Review Service (S5) | Review Task Manager, Evidence Highlighter, Claim Repository, Audit Logger, Identity & Access, Orchestrator (resume) |
| Feedback Service (S6) | Feedback Ingestor (write KB), Audit Logger |
| Claim API Service (S7) | Identity & Access, Orchestrator, Review Service, Claim Repository, Audit Logger, Config Provider |
| OCR Adapter | Amazon Textract, Document Store |
| LLM Extractor / Decision Reasoner | Amazon Bedrock (Claude Sonnet) |
| KB Retriever | Bedrock Knowledge Base (OpenSearch Serverless) — read |
| Feedback Ingestor | Bedrock Knowledge Base (OpenSearch Serverless) — write |
| Claim Repository | Amazon DynamoDB |
| Document Store | Amazon S3 |
| Audit Logger | Append-only audit store (S3/QLDB-style) |
| Config Provider | Config source (env/Parameter Store) |
| Identity & Access | Amazon Cognito (UI) + IAM (service-to-service) |

## Communication Patterns
- **Synchronous (in-sequence)**: Orchestrator → Intake → Adjudication → Compliance → Routing (request/response within AgentCore).
- **Event-driven (async)**:
  - New claim via S3 upload → event → Orchestrator.
  - Routing = human → "Pending Review" event → task created, pipeline pauses.
  - Reviewer submit → Review Service → Orchestrator.resume_after_review.
  - Override → "Feedback" event → Feedback Service → KB write.
- **Read/Write separation on KB**: Adjudication reads only; Feedback writes only (Q4:A).

## Data Flow Diagram (text)
```
[Submitter API / S3 upload]
        |
        v
  Claim Repository (create, status=Received)  --> Audit Logger
        |
        v
  Intake Service ---> Document Store (raw docs)
        |            \--> CanonicalClaim -> Claim Repository (status=Intake Complete)
        v
  Adjudication Service --(read)--> Knowledge Base
        |  PreliminaryDecision -> Claim Repository (status=Adjudicated)
        v
  Compliance Service --> Explanation -> Document Store (S3)
        |  ComplianceFindings -> Claim Repository (status=Compliance Checked)
        v
  Routing Evaluator --(confidence vs threshold from Config Provider)
     |                         |
   auto                      human
     |                         |
 finalize (status=Decided)   Review Task (status=Pending Review) [PAUSE]
                               |
                        Reviewer UI (Review Service)
                               |
                     submit decision/override --> Audit Logger
                               |
                     Orchestrator.resume_after_review (status=Decided)
                               |
                     override? --> Feedback Service --(write)--> Knowledge Base --> Audit Logger
```

## Coupling Notes
- Shared Platform components (Claim Repository, Document Store, Audit Logger, Config Provider, Identity & Access) are cross-cutting and used by multiple services.
- Agents do not call each other directly; the Orchestrator mediates the main sequence to keep agents independent (supports INVEST independence and per-unit development).
