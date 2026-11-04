import { useEffect, useState } from "react";

interface Status {
  provider?: string;
  ready?: boolean;
  meta_key_configured?: boolean;
  human_review_required?: boolean;
  privacy_redaction_required?: boolean;
  profile_ml?: { ready?: boolean; enabled?: boolean };
  pair_ml?: { ready?: boolean };
  evidence_tools?: {
    ready?: boolean;
    ocr?: { provider?: string };
    photo_comparison?: { provider?: string };
    privacy?: { ready?: boolean; provider?: string };
  };
}
export function useLiveServices() {
  const [state, setState] = useState<{
    phase: "loading" | "loaded" | "offline";
    checks: { name: string; ready: boolean }[];
  }>({ phase: "loading", checks: [] });
  useEffect(() => {
    const controller = new AbortController();
    void (async () => {
      try {
        const response = await fetch("/api/analysis/status", {
          credentials: "same-origin",
          cache: "no-store",
          signal: controller.signal,
        });
        if (!response.ok) throw new Error("Service status unavailable");
        const s: Status = await response.json();
        const e = s.evidence_tools;
        const checks = [
          {
            name: "Meta AI",
            ready:
              s.provider === "meta" &&
              s.ready === true &&
              s.meta_key_configured === true,
          },
          {
            name: "Independent ML",
            ready:
              s.profile_ml?.ready === true &&
              s.profile_ml.enabled === true &&
              s.pair_ml?.ready === true,
          },
          {
            name: "Screenshot tools",
            ready:
              e?.ready === true &&
              e.ocr?.provider === "paddleocr" &&
              e.photo_comparison?.provider === "imagededup",
          },
          {
            name: "Contact redaction",
            ready:
              s.privacy_redaction_required === true &&
              e?.privacy?.ready === true &&
              e.privacy.provider === "presidio",
          },
          { name: "Human review", ready: s.human_review_required === true },
        ];
        if (!controller.signal.aborted) setState({ phase: "loaded", checks });
      } catch {
        if (!controller.signal.aborted)
          setState({ phase: "offline", checks: [] });
      }
    })();
    return () => controller.abort();
  }, []);
  return state;
}
