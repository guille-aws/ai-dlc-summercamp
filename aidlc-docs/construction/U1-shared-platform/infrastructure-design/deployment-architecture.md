# CLAIRO U1 Shared Platform - Deployment Architecture

## Deployment Model
U1 is a **library**, not a deployable service. It is included in consuming units' deployment packages.

## Packaging Options
- **Chosen for MVP**: bundle `libs/clairo_shared` into each consuming Lambda's package via the CDK Lambda asset build (each service's `requirements`/build includes the shared lib).
- **Alternative (future)**: publish as a Lambda Layer shared across functions.

## Diagram (text)
```
libs/clairo_shared  (source)
        |
        | bundled into
        v
+-------------------------------------------------------+
| Consuming Lambdas (U2 Intake, U3 Adjudication,        |
| U4 Compliance, U5 API/Orchestrator, U6 Feedback)      |
|   import clairo_shared.{models,repositories,audit,...} |
+-------------------------------------------------------+
        |
        | uses (via injectable boto3 clients)
        v
  Shared AWS resources (U0): DynamoDB, S3, SSM, Cognito
```

## Build Integration
- During Code Generation for each consuming unit, the shared library is referenced so the Lambda asset includes it.
- Build & Test phase verifies the shared package imports cleanly and consuming units resolve it.
