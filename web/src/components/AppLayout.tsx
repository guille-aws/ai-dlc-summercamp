import { ReactNode, useEffect, useState } from "react";
import Link from "next/link";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Container,
  Box,
  TextField,
  Alert,
  Stack,
} from "@mui/material";
import { getCurrentUser, signIn, signOut } from "aws-amplify/auth";

/**
 * App shell with an in-app username/password auth guard (UI-1).
 * Uses Amplify `signIn` (USER_SRP) directly — no hosted-UI redirect needed.
 * Backend remains the authoritative enforcer (UI-11).
 */
export function AppLayout({ children }: { children: ReactNode }) {
  const [authed, setAuthed] = useState<boolean | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    getCurrentUser()
      .then(() => setAuthed(true))
      .catch(() => setAuthed(false));
  }, []);

  const handleSignIn = async () => {
    setError(null);
    setBusy(true);
    try {
      const { isSignedIn } = await signIn({ username: email, password });
      if (isSignedIn) {
        setAuthed(true);
      } else {
        setError("Additional sign-in step required. Contact your administrator.");
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Sign in failed";
      setError(msg);
    } finally {
      setBusy(false);
    }
  };

  if (authed === null) {
    return <Container sx={{ mt: 4 }}>Loading…</Container>;
  }

  if (!authed) {
    return (
      <Container maxWidth="sm" sx={{ mt: 8 }}>
        <Typography variant="h5" gutterBottom align="center">
          CLAIRO Reviewer
        </Typography>
        <Stack spacing={2} sx={{ mt: 3 }}>
          {error && <Alert severity="error">{error}</Alert>}
          <TextField
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            fullWidth
            inputProps={{ "data-testid": "login-email" }}
          />
          <TextField
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            fullWidth
            inputProps={{ "data-testid": "login-password" }}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSignIn();
            }}
          />
          <Button
            variant="contained"
            onClick={handleSignIn}
            disabled={busy || !email || !password}
            data-testid="login-button"
          >
            {busy ? "Signing in…" : "Sign in"}
          </Button>
        </Stack>
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
          <Button
            color="inherit"
            onClick={() => signOut().then(() => setAuthed(false))}
            data-testid="logout-button"
          >
            Sign out
          </Button>
        </Toolbar>
      </AppBar>
      <Container sx={{ mt: 4 }}>{children}</Container>
    </Box>
  );
}
