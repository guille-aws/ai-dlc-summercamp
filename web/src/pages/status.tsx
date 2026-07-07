import { useState } from "react";
import { Typography, TextField, Button, Alert, Stack } from "@mui/material";
import { apiClient, ApiError } from "../lib/apiClient";
import type { Claim } from "../types";
import { ClaimStatusCard } from "../components/ClaimStatusCard";

/** Claim Status lookup (US-09). */
export default function ClaimStatusPage() {
  const [claimId, setClaimId] = useState("");
  const [claim, setClaim] = useState<Claim | null>(null);
  const [error, setError] = useState<string | null>(null);

  const lookup = () => {
    setError(null);
    setClaim(null);
    apiClient
      .getClaim(claimId.trim())
      .then(setClaim)
      .catch((e: ApiError) => setError(e.message));
  };

  return (
    <>
      <Typography variant="h5" gutterBottom>
        Claim Status
      </Typography>
      <Stack direction="row" spacing={2}>
        <TextField
          label="Claim ID"
          value={claimId}
          onChange={(e) => setClaimId(e.target.value)}
          inputProps={{ "data-testid": "claim-search-input" }}
        />
        <Button
          variant="contained"
          onClick={lookup}
          disabled={!claimId.trim()}
          data-testid="claim-search-submit"
        >
          Look up
        </Button>
      </Stack>
      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
      {claim && <ClaimStatusCard claim={claim} />}
    </>
  );
}
