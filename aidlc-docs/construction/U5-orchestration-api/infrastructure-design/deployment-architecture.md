# CLAIRO U5 Orchestration/API - Deployment Architecture

## Diagram (text)
```
Submitter/Reviewer --HTTPS--> API Gateway (Cognito authz) --> API Handler Lambda (512/30s)
                                                                  |
                     +--------------------------------------------+
                     | create claim (Received) / reviews / audit / threshold
                     v
              DynamoDB Claims  --(stream NEW_AND_OLD_IMAGES)--> Orchestrator Lambda (512/1min)
                     ^                                              |
                     | status updates                               | on status:
                     |                                              |  Received->invoke Intake
        Intake/Adjudication/Compliance Lambdas <--async invoke------+  IntakeComplete->Adjudication
                                                                       Adjudicated->Compliance
                                                                       ComplianceChecked->Routing
   Override (review submit) --> EventBridge (clairo.review: ClaimOverridden) --> Feedback (U6)
```

## Packaging
- API handler + orchestrator share the `services/orchestration_api/` asset (different handlers), bundled with `clairo_shared` via `build_lambdas.sh` (extended to include `orchestration_api`).

## Deploy
- `cdk deploy --all`. New: Claims stream + orchestrator event-source mapping.

## First Deployable End-to-End Slice
- After U5, the pipeline is wired end-to-end. With the KB and GDPR seed data in place, a synthetic claim submitted via `POST /claims` (or S3 upload) flows Intake→Adjudication→Compliance→Routing, and low-confidence claims appear in `GET /reviews`. This is the first meaningful deploy/test point.
