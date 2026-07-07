import { useState } from "react";
import {
  Box,
  Button,
  MenuItem,
  TextField,
  Typography,
} from "@mui/material";
import type { DecisionOutcome, PreliminaryDecision, ReviewSubmission } from "../types";

const OUTCOMES: DecisionOutcome[] = ["approve", "deny", "partial", "needs_more_info"];

/**
 * Reviewer decision form (UI-5). Rationale required when the outcome differs
 * from the recommendation (override).
 */
export function DecisionForm({
  recommendation,
  onSubmit,
  submitting,
}: {
  recommendation?: PreliminaryDecision;
  onSubmit: (s: ReviewSubmission) => void;
  submitting: boolean;
}) {
  const [outcome, setOutcome] = useState<DecisionOutcome>(
    recommendation?.outcome ?? "approve"
  );
  const [rationale, setRationale] = useState("");

  const isOverride = recommendation ? outcome !== recommendation.outcome : true;
  const rationaleRequired = isOverride;
  const canSubmit = !submitting && (!rationaleRequired || rationale.trim().length > 0);

  return (
    <Box sx={{ mt: 3 }} data-testid="decision-form">
      <Typography variant="h6">Your Decision</Typography>
      <TextField
        select
        label="Outcome"
        value={outcome}
        onChange={(e) => setOutcome(e.target.value as DecisionOutcome)}
        fullWidth
        margin="normal"
        inputProps={{ "data-testid": "decision-outcome-select" }}
      >
        {OUTCOMES.map((o) => (
          <MenuItem key={o} value={o}>
            {o}
          </MenuItem>
        ))}
      </TextField>
      <TextField
        label={rationaleRequired ? "Rationale (required for override)" : "Rationale"}
        value={rationale}
        onChange={(e) => setRationale(e.target.value)}
        fullWidth
        multiline
        minRows={2}
        margin="normal"
        required={rationaleRequired}
        inputProps={{ "data-testid": "rationale-input" }}
      />
      <Button
        variant="contained"
        disabled={!canSubmit}
        data-testid="decision-form-submit"
        onClick={() => onSubmit({ outcome, rationale, is_override: isOverride })}
      >
        {submitting ? "Submitting…" : "Submit Decision"}
      </Button>
    </Box>
  );
}
