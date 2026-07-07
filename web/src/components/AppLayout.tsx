import { ReactNode, useEffect, useState } from "react";
import Link from "next/link";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Container,
  Box,
} from "@mui/material";
import { getCurrentUser, signInWithRedirect, signOut } from "aws-amplify/auth";

/**
 * App shell with a simple auth guard (UI-1). Unauthenticated users are prompted
 * to sign in via Cognito (Amplify hosted UI). Backend remains the authoritative
 * enforcer (UI-11).
 */
export function AppLayout({ children }: { children: ReactNode }) {
  const [authed, setAuthed] = useState<boolean | null>(null);

  useEffect(() => {
    getCurrentUser()
      .then(() => setAuthed(true))
      .catch(() => setAuthed(false));
  }, []);

  if (authed === null) {
    return <Container sx={{ mt: 4 }}>Loading…</Container>;
  }

  if (!authed) {
    return (
      <Container sx={{ mt: 8, textAlign: "center" }}>
        <Typography variant="h5" gutterBottom>
          CLAIRO Reviewer
        </Typography>
        <Button
          variant="contained"
          data-testid="login-button"
          onClick={() => signInWithRedirect()}
        >
          Sign in
        </Button>
      </Container>
    );
  }

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            CLAIRO
          </Typography>
          <Button color="inherit" component={Link} href="/" data-testid="nav-queue">
            Review Queue
          </Button>
          <Button color="inherit" component={Link} href="/status" data-testid="nav-status">
            Claim Status
          </Button>
          <Button color="inherit" onClick={() => signOut()} data-testid="logout-button">
            Sign out
          </Button>
        </Toolbar>
      </AppBar>
      <Container sx={{ mt: 4 }}>{children}</Container>
    </Box>
  );
}
