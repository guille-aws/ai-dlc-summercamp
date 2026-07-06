# CLAIRO U3 Adjudication - Business Logic Model

## Components & Flow

### 1. KB Retriever (read-only)
- Input: CanonicalClaim (builds a retrieval query from claim facts).
- Queries the Bedrock Knowledge Base (OpenSearch Serverless) for top-5 policy passages (Q3:A).
- Corrective examples written by U6 are retrieved as normal KB content (Q5:A).
- Output: RetrievalResult (passages + `weak` flag when scores are low/absent, Q4:A).

### 2. Decision Reasoner
- Input: CanonicalClaim + RetrievalResult.
- Single-shot RAG prompt to Bedrock Claude Sonnet (Q1:A) returning structured JSON:
  outcome, confidence (self-assessed, Q2:A), reasoning_chain, citations.
- Output: AdjudicationOutput.

## Orchestration (Adjudication Service handler)
```
1. Load claim (status IntakeComplete) — provided by orchestrator or fetched by claim_id.
2. KB Retriever.retrieve(claim) -> RetrievalResult (top-5).
3. If retrieval weak (Q4:A): proceed but instruct the reasoner that policy basis is weak;
   expect low confidence (which will drive HITL routing downstream).
4. Decision Reasoner.decide(claim, passages) -> AdjudicationOutput.
5. Map to PreliminaryDecision; persist to claim (adjudication_result); status -> Adjudicated.
6. Append audit entry (actor=adjudication-agent, step="adjudication").
```

## Interactions
- **U1 shared**: ClaimRepository (read/update), AuditLogger (append), models.
- **AWS**: Bedrock Knowledge Base (retrieve, read-only), Bedrock (reasoning).
- **Downstream**: Orchestrator (U5) advances to Compliance after Adjudicated.

## Error Handling
- Retrieval failure -> treated as weak retrieval (proceed low-confidence) OR StorageError → claim `Failed` if unrecoverable.
- Malformed reasoner output -> defensive parse; if unusable, low-confidence needs_more_info decision (routes to human) rather than hard failure.
