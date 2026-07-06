# CLAIRO U3 Adjudication - Business Rules

## Retrieval
- **AR-1**: Retrieve top-5 policy passages from the Bedrock Knowledge Base per claim (Q3:A).
- **AR-2**: KB access is read-only for adjudication (Q4:A design; enforced by IAM in U0).
- **AR-3**: Corrective examples (written by U6) are retrieved as ordinary KB content — no special weighting (Q5:A).
- **AR-4**: If no passages are returned OR all scores fall below a weak-match threshold, mark the retrieval `weak`.

## Decision Reasoning
- **AR-5**: A single RAG prompt produces outcome, confidence, reasoning_chain, and citations (Q1:A).
- **AR-6**: `confidence` is the LLM's self-assessed value clamped to [0.0, 1.0] (Q2:A).
- **AR-7**: `outcome` MUST be one of approve/deny/partial/needs_more_info.
- **AR-8**: Every decision MUST include a non-empty reasoning_chain and cite the policy passages it relied on.
- **AR-9**: On weak retrieval (AR-4), the reasoner is told the policy basis is weak and is expected to return low confidence, which drives HITL routing downstream (Q4:A).

## Persistence & Status
- **AR-10**: The PreliminaryDecision is persisted to the claim (adjudication_result) and status transitions `IntakeComplete -> Adjudicated` (via check_transition).
- **AR-11**: Unrecoverable errors set status `Failed`; unusable reasoner output yields a low-confidence `needs_more_info` decision instead of failing.

## Auditing
- **AR-12**: An audit entry is appended for the adjudication step (actor_type=agent, step="adjudication") including outcome and confidence.
