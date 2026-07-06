# CLAIRO - Unit of Work / Story Map

## Story-to-Unit Assignment

| Story | Title | Primary Unit | Supporting Units |
|---|---|---|---|
| US-01 | Submit a claim via API | U5 (API) | U1, U2 |
| US-02 | Submit a claim via document upload (event-driven) | U2 | U0 (S3 trigger), U1 |
| US-03 | Intake Agent extracts and normalizes | U2 | U1 |
| US-04 | Adjudication decision + confidence + reasoning | U3 | U1 |
| US-05 | Compliance validation + explanation | U4 | U1 |
| US-06 | Low-confidence claims route to reviewer | U5 | U7 (UI), U1 |
| US-07 | Human reviewer decides/overrides | U5 | U7 (UI), U1 |
| US-08 | Overrides feed back into KB automatically | U6 | U1 |
| US-09 | Retrieve claim status and decision | U5 (API) | U7 (UI), U1 |
| US-10 | Configure the confidence threshold | U5 (API) | U1 (Config Provider) |
| US-11 | Retrieve audit trail for a claim | U5 (API) | U1 (Audit Logger) |
| US-12 | Authenticate + role-based access | U1 (auth helpers) | U5 (API authz), U7 (login), U0 (Cognito) |

## Coverage Check
- **All 12 stories assigned**: ✔
- **Every unit has at least one story or clear infrastructure role**:
  - U0 Infrastructure — enabling role for all stories (Cognito, S3 triggers, IAM, resources)
  - U1 Shared Platform — US-12 + cross-cutting support for all stories
  - U2 Intake — US-02, US-03 (+US-01 support)
  - U3 Adjudication — US-04
  - U4 Compliance — US-05
  - U5 HITL/API/Orchestration — US-01, US-06, US-07, US-09, US-10, US-11
  - U6 Feedback — US-08
  - U7 Web UI — US-06, US-07, US-09, US-12 (UI aspects)

## Notes
- Orchestration (main sequence + pause/resume) is grouped into U5 since it coordinates U2/U3/U4 and drives the review lifecycle.
- UI-facing aspects of reviewer stories (US-06, US-07, US-09, US-12) are realized in U7 but depend on U5's API contract.
