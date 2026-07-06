# CLAIRO U3 Adjudication - Code Summary

## Generated Files (workspace root)
```
services/adjudication/
├── requirements.txt
├── __init__.py
├── types.py           # RetrievedPassage, RetrievalResult, WEAK_MATCH_THRESHOLD
├── kb_client.py       # Bedrock RetrieveAndGenerate wrapper (top-5, weak flag), injectable
├── reasoner.py        # prompt + defensive parse -> PreliminaryDecision; confidence clamp; weak-basis handling
└── handler.py         # AdjudicationService: load -> RAG -> decision -> persist Adjudicated -> audit

infra/stacks/agents_stack.py   # UPDATED: adjudication -> real asset 1024/5min; +RetrieveAndGenerate IAM; +KB_ID env
scripts/build_lambdas.sh       # UPDATED: SERVICES now includes adjudication
```

## Decisions Applied
- Managed RAG via `RetrieveAndGenerate` (top-5); LLM self-assessed confidence (clamped [0,1]).
- Hardcoded weak-match threshold (0.4); weak retrieval caps confidence ≤0.3 → HITL routing.
- Unusable output → low-confidence `needs_more_info` (never hard-fails); unrecoverable → Failed.
- Result tuples; injectable clients; 1024MB/5min; no unit tests.

## Verification Performed
- Ran `scripts/build_lambdas.sh` (vendors clairo_shared into intake + adjudication).
- Offline logic check with fake clients: **approve path** (confidence preserved, status Adjudicated), **weak-retrieval path** (confidence capped ≤0.3), **unusable-output path** (needs_more_info @0.0) — all passed.
- `cdk synth`: succeeds; `RetrieveAndGenerate` IAM present; intake+adjudication both 1024 MB; adjudication asset bundles handler + clairo_shared.

## Deployment Prerequisite
- Bedrock Knowledge Base must be created over the OpenSearch Serverless collection with policy docs ingested; pass its id via `CLAIRO_KB_ID` env at deploy (surfaces to the Lambda as `KB_ID`).

## Notes
- No unit tests (NFR Q4:A); integration testing in Build & Test.
- U4 Compliance and U6 Feedback Lambdas remain inline placeholders until generated.
