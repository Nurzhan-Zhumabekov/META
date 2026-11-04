import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AppProvider } from "./lib/context";
import App from "./App";
import { initializeDemo } from "./lib/api";
import "./styles.css";
import "./instagram-web.css";
import "./social-polish.css";

const root = createRoot(document.getElementById("root")!);
void initializeDemo()
  .then(() =>
    root.render(
      <StrictMode>
        <BrowserRouter>
          <AppProvider>
            <App />
          </AppProvider>
        </BrowserRouter>
      </StrictMode>,
    ),
  )
  .catch(() =>
    root.render(
      <main className="review-page">
        <h1>MirrorCheck</h1>
        <p role="alert">
          The demonstration is temporarily unavailable. Reload this page to try
          again.
        </p>
        <button
          className="button primary"
          onClick={() => window.location.reload()}
        >
          Reload
        </button>
      </main>,
    ),
  );
