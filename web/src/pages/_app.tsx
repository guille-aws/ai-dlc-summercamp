import type { AppProps } from "next/app";
import { useEffect } from "react";
import { ThemeProvider, createTheme, CssBaseline } from "@mui/material";
import { configureAmplify } from "../lib/amplify";
import { AppLayout } from "../components/AppLayout";

const theme = createTheme({ palette: { mode: "light" } });

export default function App({ Component, pageProps }: AppProps) {
  useEffect(() => {
    configureAmplify();
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppLayout>
        <Component {...pageProps} />
      </AppLayout>
    </ThemeProvider>
  );
}
