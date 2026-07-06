# CLAIRO U2 Intake - Code Summary

## Generated Files (workspace root)
```
services/intake/
├── requirements.txt
├── __init__.py
├── extraction.py       # ExtractedBlock/Text, IntakeInput/Result, content-type routing helpers
├── text_parser.py      # Email/Text Parser (IR-2)
├── ocr_adapter.py      # Textract sync OCR (IR-1), captures page+bbox
├── llm_extractor.py    # Bedrock Claude Sonnet single structured-output prompt (Q2:A)
├── normalizer.py       # -> CanonicalClaim + evidence; strict validate (IR-7)
└── handler.py          # Lambda entry: IntakeService orchestration; IntakeComplete/Rejected/Failed

infra/stacks/agents_stack.py   # UPDATED: intake Lambda -> 1024MB/5min + real services/intake asset
scripts/build_lambdas.sh       # Vendors clairo_shared into service dirs before cdk deploy
```

## Decisions Applied
- Content-type routing (PDF/image → Textract; text/email → parser).
- Single-shot structured LLM extraction → canonical JSON with defensive parsing.
- Merge multiple documents into one claim; capture page+bbox evidence.
- Unreadable/invalid → `Rejected`; unrecoverable → `Failed`; success → `IntakeComplete`.
- Async processing; sync Textract; 1024MB/5min; result tuples; injectable clients.

## Verification Performed
- Ran `scripts/build_lambdas.sh` to vendor `clairo_shared` into `services/intake`.
- Offline logic check with injected fake clients (no AWS): **success path** (valid claim → IntakeComplete, persisted, audited) and **rejection path** (no line items → Rejected with BR-2 reason) — both passed.
- `cdk synth`: all stacks synthesize; intake Lambda shows `MemorySize: 1024`, `Timeout: 300`; asset bundles handler modules + `clairo_shared`.

## Deployment Prerequisite
- Run `bash scripts/build_lambdas.sh` before `cdk deploy` so the shared library is bundled into the intake asset. (`services/*/clairo_shared/` is gitignored as a build artifact.)

## Notes
- No unit tests (per NFR Q4:B); verification via offline logic check + synth here and integration testing in Build & Test.
- U3/U4/U6 Lambdas remain inline placeholders until their code is generated.
