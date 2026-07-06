# CLAIRO U2 Intake - Business Logic Model

## Components & Flow

### 1. OCR Adapter
- Input: DocumentRef (PDF/image, by content_type — Q1:A).
- Uses Amazon Textract to extract text blocks with page + bbox.
- Output: ExtractedText (with positional metadata for US-06, Q5:A).

### 2. Email/Text Parser
- Input: DocumentRef (email/text by content_type — Q1:A).
- Parses plain text/email body into ExtractedBlocks (single page, no bbox or synthetic bbox).
- Output: ExtractedText.

### 3. LLM Extractor
- Input: combined ExtractedText from all documents (Q3:A merge).
- Single structured-output prompt to Bedrock Claude Sonnet returning canonical claim JSON directly (Q2:A).
- Output: draft CanonicalClaim fields + which evidence blocks support which fields.

### 4. Claim Normalizer
- Maps LLM output into a `CanonicalClaim` (clairo_shared model).
- Attaches EvidenceRefs (page + bbox) for supporting blocks.
- Runs strict validation via `clairo_shared.rules.validate_claim`.

## Orchestration (Intake Service handler)
```
1. Receive IntakeInput (from API call or S3-upload event via orchestrator).
2. For each document: route by content_type -> OCR Adapter or Email/Text Parser.
3. Merge all ExtractedText.
4. LLM Extractor -> draft canonical claim JSON.
5. Claim Normalizer -> CanonicalClaim + evidence_refs.
6. validate_claim:
   - valid  -> persist claim (status IntakeComplete), audit, return IntakeResult
   - invalid-> set status Rejected with reason, audit, return IntakeResult (Q4:A)
7. Persist raw documents already in S3; store canonical claim via ClaimRepository.
8. Append audit entry for intake step (actor=agent).
```

## Interactions
- **U1 shared**: ClaimRepository (persist), DocumentStore (read docs / store nothing new here), AuditLogger (append), models, rules.
- **AWS**: Textract (OCR), Bedrock (extraction).
- **Downstream**: On IntakeComplete, the orchestrator (U5) advances to Adjudication.

## Error Handling
- Textract/Bedrock errors -> surfaced as result-tuple errors; on unrecoverable failure the claim is set `Failed` (distinct from validation `Rejected`).
- Empty/unreadable extraction -> `Rejected` with reason (Q4:A).
