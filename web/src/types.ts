// CLAIRO UI types mirroring the canonical claim/decision shapes from the API.

export type DecisionOutcome = "approve" | "deny" | "partial" | "needs_more_info";

export type ClaimStatus =
  | "Received"
  | "IntakeComplete"
  | "Adjudicated"
  | "ComplianceChecked"
  | "PendingReview"
  | "Decided"
  | "Rejected"
  | "Failed";

export interface PolicyCitation {
  source_id: string;
  excerpt: string;
  score: number;
}

export interface PreliminaryDecision {
  outcome: DecisionOutcome;
  confidence: number;
  reasoning_chain: string[];
  citations: PolicyCitation[];
}

export interface EvidenceRef {
  document_ref: { bucket: string; key: string; content_type: string };
  page?: number;
  bbox?: number[];
}

export interface Claim {
  claim_id: string;
  claimant: { name: string; claimant_id?: string };
  line_items: Array<{
    procedure_code: string;
    amount: string;
    diagnosis_code?: string;
    service_date?: string;
  }>;
  total_amount: string;
  currency: string;
  status: ClaimStatus;
  evidence_refs: EvidenceRef[];
  adjudication_result?: PreliminaryDecision;
  compliance_result?: {
    compliant: boolean;
    anomalies: string[];
    gdpr_flags: string[];
  };
}

export interface ReviewSubmission {
  outcome: DecisionOutcome;
  rationale: string;
  is_override: boolean;
}
