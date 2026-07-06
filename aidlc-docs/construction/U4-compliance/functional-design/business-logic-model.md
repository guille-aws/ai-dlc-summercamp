# CLAIRO U4 Compliance - Business Logic Model

## Components & Flow

### 1. GDPR Rule Validator
- Loads the natural-language GDPR policy document from the SSM-referenced S3 location (Q1:B).
- Pure LLM evaluation (Q2:B): a Bedrock prompt assesses the claim + adjudication decision against the GDPR text and returns structured findings (compliant, anomalies, gdpr_flags, rationale).
- Annotate-only: does not change the decision outcome (Q5:A).

### 2. Explanation Generator
- Produces both a structured JSON explanation and a rendered Markdown document (Q3:C) combining: the claim summary, the adjudication decision + reasoning chain + citations, and the compliance findings.
- Stores both artifacts in S3 (documents bucket, explanations/ prefix).

## Orchestration (Compliance Service handler)
```
1. Load claim (status Adjudicated) + its adjudication_result (PreliminaryDecision).
2. Config Provider -> gdpr_rules_ref; Document Store -> load GDPR policy text.
3. GDPR Rule Validator (LLM) -> ComplianceEvaluation (findings).
4. Explanation Generator -> JSON + Markdown artifacts -> S3.
5. Persist ComplianceFindings to claim (compliance_result); status -> ComplianceChecked.
6. Record gdpr_flags in findings but DO NOT force routing (Q4:B) and DO NOT change outcome (Q5:A).
7. Append audit entry (actor=compliance-agent, step="compliance").
```

## Interactions
- **U1 shared**: ClaimRepository (read/update), DocumentStore (store explanations), ConfigProvider (gdpr_rules_ref), AuditLogger (append), models.
- **AWS**: Bedrock (LLM evaluation), S3 (explanation docs).
- **Downstream**: Orchestrator (U5) applies routing based on adjudication confidence (compliance findings are informational).

## Error Handling
- Missing/unloadable GDPR rules -> StorageError; claim `Failed` if unrecoverable.
- Unusable LLM output -> conservative findings (compliant=false, anomaly noted) + explanation still generated; does not block the pipeline.
