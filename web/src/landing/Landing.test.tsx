import { fireEvent, render, screen, within } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";
import { Landing } from "./Landing";

const healthy = {
  provider: "meta",
  ready: true,
  meta_key_configured: true,
  human_review_required: true,
  privacy_redaction_required: true,
  profile_ml: { ready: true, enabled: true },
  pair_ml: { ready: true },
  evidence_tools: {
    ready: true,
    ocr: { provider: "paddleocr" },
    photo_comparison: { provider: "imagededup" },
    privacy: { ready: true, provider: "presidio" },
  },
};
beforeEach(() => {
  vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(null);
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => Response.json(healthy)),
  );
});

it("keeps the prototype and both recorded outcomes reachable from the new entry page", async () => {
  render(<Landing />);
  expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
    "A familiar face. A clearer signal.",
  );
  expect(screen.getByRole("link", { name: "Try MirrorCheck" })).toHaveAttribute(
    "href",
    "/",
  );
  expect(
    screen.getByRole("link", { name: "Watch the 3-min demo" }),
  ).toHaveAttribute("href", "/demo-video.html");
  expect(
    screen.getByRole("link", { name: "Explore the dismissed report" }),
  ).toHaveAttribute("href", "/rejected-report-walkthrough.html");
  expect(await screen.findByText("All systems ready")).toBeInTheDocument();
});

it("explains the workflow through keyboard-accessible tabs with no automatic verdict", () => {
  render(<Landing />);
  fireEvent.click(screen.getByRole("tab", { name: "02 Compare" }));
  expect(screen.getByRole("tabpanel")).toHaveTextContent(
    "Different signals. One clear view.",
  );
  fireEvent.keyDown(screen.getByRole("tab", { name: "02 Compare" }), {
    key: "ArrowRight",
  });
  expect(screen.getByRole("tab", { name: "03 Decide" })).toHaveFocus();
  expect(screen.getByRole("tabpanel")).toHaveTextContent(
    "A person makes the call.",
  );
});

it("does not claim availability when a required privacy service is unavailable", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      Response.json({
        ...healthy,
        evidence_tools: {
          ...healthy.evidence_tools,
          privacy: { provider: "presidio", ready: false },
        },
      }),
    ),
  );
  render(<Landing />);
  expect(
    await screen.findByText("Some services need attention"),
  ).toBeInTheDocument();
  expect(screen.queryByText("All systems ready")).not.toBeInTheDocument();
  expect(
    within(
      screen.getByRole("region", { name: "Service availability" }),
    ).getByText("Contact redaction unavailable"),
  ).toBeInTheDocument();
});

it("keeps recorded demos accessible if the local API is offline", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => {
      throw new TypeError("offline");
    }),
  );
  render(<Landing />);
  expect(
    await screen.findByText("Live services unavailable"),
  ).toBeInTheDocument();
  expect(
    screen.getByRole("link", { name: "Watch the 3-min demo" }),
  ).toBeVisible();
});

it("offers a pause control for decorative motion", () => {
  render(<Landing />);
  expect(
    screen.getByRole("region", { name: "A familiar face. A clearer signal." }),
  ).toHaveAttribute("data-motion", "play");
  fireEvent.click(
    screen.getByRole("button", { name: "Pause gallery animation" }),
  );
  expect(
    screen.getByRole("button", { name: "Resume gallery animation" }),
  ).toBeInTheDocument();
  expect(
    screen.getByRole("region", { name: "A familiar face. A clearer signal." }),
  ).toHaveAttribute("data-paused", "true");
});

it("removes the technology logo strip while preserving the workflow", () => {
  render(<Landing />);
  expect(
    screen.queryByRole("region", { name: "Technology behind the review" }),
  ).not.toBeInTheDocument();
  expect(screen.getByRole("tab", { name: "01 Report" })).toBeInTheDocument();
});

it("keeps the supplied liquid navigation usable with a keyboard and without WebGL", () => {
  render(<Landing />);
  const nav = screen.getByRole("navigation", { name: "Landing navigation" });
  expect(nav).toHaveAttribute("data-gl", "off");
  fireEvent.keyDown(within(nav).getByRole("link", { name: "Overview" }), {
    key: "ArrowRight",
  });
  const next = within(nav).getByRole("link", { name: "How it works" });
  expect(next).toHaveFocus();
  expect(next).toHaveAttribute("aria-current", "page");
});

it("does not restart decorative animation after leaving during a delayed ripple", () => {
  vi.useFakeTimers();
  try {
    const raf = vi.spyOn(window, "requestAnimationFrame").mockReturnValue(1);
    const { unmount } = render(<Landing />);
    const nav = screen.getByRole("navigation", { name: "Landing navigation" });
    fireEvent.click(within(nav).getByRole("link", { name: "Privacy" }));
    unmount();
    raf.mockClear();
    vi.advanceTimersByTime(500);
    expect(raf).not.toHaveBeenCalled();
  } finally {
    vi.useRealTimers();
  }
});
