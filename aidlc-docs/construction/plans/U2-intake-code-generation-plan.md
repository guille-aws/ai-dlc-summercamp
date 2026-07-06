# CLAIRO U2 Intake - Code Generation Plan

**Unit**: U2 Intake (serverless Lambda agent)
**Workspace root**: /Users/ggarcava/Desktop/Kiro/AI-DLC
**Code location**: `services/intake/` (application code at workspace root)
**Project type**: Greenfield monorepo

## Unit Context
- **Purpose**: Extract structured data from multi-modal inputs and normalize to CanonicalClaim.
- **Depends on**: U1 (`clairo_shared`), U0 (Textract, Bedrock, S3, DynamoDB, intake Lambda).
- **Stories**: US-01 (API support), US-02 (event upload), US-03 (extraction + normalization).

## Design Inputs
- FD: `aidlc-docs/construction/U2-intake/functional-design/`
- NFR: `aidlc-docs/construction/U2-intake/nfr-requirements/`, `nfr-design/`
- Infra: `aidlc-docs/construction/U2-intake/infrastructure-design/`

## Decisions Applied
- Content-type routing; single-shot structured LLM extraction; merge multiple docs; Rejected on unreadable; capture page+bbox evidence; async; sync Textract APIs; 1024MB/5min; result tuples; no unit tests.

## Generation Steps

- [x] **Step 1: Service scaffolding** — `services/intake/requirements.txt`, `__init__.py`.
- [x] **Step 2: Extractor types + Email/Text Parser** — `extraction.py`, `text_parser.py`.
- [x] **Step 3: OCR Adapter** — `ocr_adapter.py` (Textract sync, page+bbox).
- [x] **Step 4: LLM Extractor** — `llm_extractor.py` (Bedrock structured-output, defensive parse).
- [x] **Step 5: Claim Normalizer** — `normalizer.py` (→ CanonicalClaim + evidence, strict validate).
- [x] **Step 6: Handler** — `handler.py` (IntakeService orchestration).
- [x] **Step 7: CDK sizing update** — `agents_stack.py` intake → 1024MB/5min + real asset; `scripts/build_lambdas.sh` added.
- [x] **Step 8: Verify** — synth OK (MemorySize 1024, Timeout 300, asset bundles handler + clairo_shared); offline logic check (success + rejection) passed.
- [x] **Step 9: Documentation** — `aidlc-docs/construction/U2-intake/code/README.md`.

## Notes
- No unit tests (per NFR Q4:B); verification via import + synth + a lightweight logic check with injected fake clients.
- Bedrock/Textract calls use injectable clients so the logic check runs without AWS.
