# CLAIRO U6 Feedback - Business Logic Model

## Component

### Feedback Ingestor
- Triggered by an EventBridge `ClaimOverridden` event from U5 (Q3:A).
- Loads the claim (for summary) and reads the reviewer decision from the event detail.
- Builds a CorrectiveExample text document: claim summary + final overridden decision + reviewer rationale (Q1:A).
- Writes the document to the kb-source S3 bucket at a deterministic key `corrective/{claim_id}.md` (Q4:A).
- Triggers a Bedrock Knowledge Base ingestion job (StartIngestionJob) so the example becomes retrievable (Q2:A).
- Appends an audit entry for the feedback write-back (FR-5.3).

## Orchestration (Feedback handler)
```
1. Receive ClaimOverridden event (claim_id, decision).
2. Load claim via ClaimRepository (for summary fields).
3. Build corrective example text.
4. DocumentStore/S3 put -> corrective/{claim_id}.md in kb-source bucket.
5. Bedrock StartIngestionJob(knowledgeBaseId, dataSourceId).
6. Audit append (actor=feedback-agent, step="feedback", detail includes s3_key).
```

## Interactions
- **U1 shared**: ClaimRepository (read), AuditLogger (append), models.
- **AWS**: S3 (kb-source write), Bedrock Agent (StartIngestionJob).
- **Upstream**: U5 emits the override event.

## Error Handling
- S3 write or ingestion failure → logged + audited; best-effort (does not affect the already-finalized claim). Retries via boto3 defaults.
- Later similar claims retrieve the corrective example through normal adjudication RAG (U3 AR-3), improving decisions (US-08 acceptance).
