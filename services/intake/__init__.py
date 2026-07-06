"""CLAIRO U2 Intake service.

Extracts structured data from multi-modal inputs (PDF/image via Textract,
email/text via parser), uses Bedrock Claude Sonnet for extraction, and
normalizes into the canonical health-claim schema.
"""
