# Performance Test Instructions

> Performance testing is **light-touch for this MVP** (no formal SLAs; resiliency extension off). This documents a basic approach; full load testing is deferred.

## MVP Performance Expectations (indicative, not SLAs)
- Straight-through (auto-adjudicated) claims complete within a few minutes under normal load (NFR-3.1).
- Submission API returns immediately with a claim_id (async processing, NFR-3.2).

## Basic Approach
1. Submit a batch of synthetic claims via `POST /claims` (e.g., 20–50) and measure time-to-Decided by polling `GET /claims/{id}`.
2. Observe Lambda duration/concurrency and any throttles in CloudWatch metrics.
3. Note Bedrock/Textract latency as the dominant factor for agent stages.

## Tooling (optional)
- A simple script (Python/k6) that submits claims and polls status suffices for the MVP.

## Optimization Levers (if needed later)
- Increase Lambda memory (already 1024 MB for agents) or reserved concurrency.
- Batch/parallelize independent claims (DynamoDB is on-demand; scales automatically).
- Consider async Textract for large multi-page documents (deferred).

## Status
- Not executed as part of MVP construction; documented for future runs.
