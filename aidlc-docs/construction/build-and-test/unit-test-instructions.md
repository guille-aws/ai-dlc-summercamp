# Unit Test Execution

## Note on Test Scope
Per unit NFR decisions, **no automated unit-test suites** were generated (Security/Resiliency/PBT extensions off; each unit opted out of unit tests). Instead, each code-bearing unit was verified during code generation via:
- **Import checks** (all Python modules import cleanly)
- **Offline logic checks** with injected fake AWS clients (no live AWS)
- **CDK synth** (infrastructure validity)
- **Web build/typecheck** (U7)

## Re-running the Verifications

### Shared library (U1) logic
```bash
PYTHONPATH=libs/clairo_shared infra/.venv/bin/python -c "import clairo_shared, clairo_shared.models, clairo_shared.rules; print('clairo_shared import OK')"
```
Validated behavior: claim serialization round-trip; strict validation (BR-1..BR-5); status transitions (BR-7..BR-9).

### Agent + orchestration logic (U2–U6)
The offline logic checks executed during code generation covered:
- **U2 Intake**: success path (IntakeComplete + persist + audit) and rejection path (invalid claim → Rejected).
- **U3 Adjudication**: approve path, weak-retrieval low-confidence capping, unusable-output → needs_more_info.
- **U4 Compliance**: compliant path (JSON+MD stored, ComplianceChecked), flagged annotate-only path.
- **U5 Orchestration/API**: routing (auto/human/needs_more_info), review submit + override event, review-on-non-pending rejection, API role authz (403/200).
- **U6 Feedback**: corrective example write + ingestion job + audit; EventBridge event parsing.

To re-run any of these, recreate the small check scripts using injected fakes as documented in each unit's `code/README.md` (they were run and then removed as temporary artifacts).

### Web UI (U7)
```bash
cd web && npm install && npm run build
```
Expected: typecheck passes; static export of all routes.

## Recommendation
For production, add real automated test suites (pytest with moto for repositories/agents; React Testing Library for the UI). This was deliberately deferred for the MVP.
