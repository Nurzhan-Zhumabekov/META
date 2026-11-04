import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";
import { Appeal } from "./Appeal";

beforeEach(() => {
  window.location.hash = "";
  vi.unstubAllGlobals();
});

it("keeps the successfully accepted capability when a password manager changes the input during access", async () => {
  let finish!: (value: Response) => void;
  const first = new Promise<Response>((resolve) => {
    finish = resolve;
  });
  const data = {
    claim: {
      id: "demo1234",
      suspect_handle: "fictional.copy",
      status: "confirmed",
    },
    decisions: [],
    appeals: [],
  };
  const fetcher = vi
    .fn()
    .mockImplementationOnce(() => first)
    .mockResolvedValue(Response.json(data));
  vi.stubGlobal("fetch", fetcher);
  render(<Appeal />);
  fireEvent.change(screen.getByLabelText("Private appeal access"), {
    target: { value: "accepted-report-access" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Open my report" }));
  fireEvent.change(screen.getByLabelText("Private appeal access"), {
    target: { value: "late-password-manager-value" },
  });
  finish(Response.json(data));
  await screen.findByRole("button", { name: "Refresh report" });
  fireEvent.click(screen.getByRole("button", { name: "Refresh report" }));
  expect(JSON.parse(fetcher.mock.calls[1][1].body)).toEqual({
    token: "accepted-report-access",
  });
});

it("refreshes a pending appeal to the moderator's final outcome", async () => {
  let resolved = false;
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      Response.json({
        claim: {
          id: "demo1234",
          suspect_handle: "fictional.copy",
          status: resolved ? "rejected" : "confirmed",
        },
        decisions: [],
        appeals: [
          {
            id: "appeal1",
            reason: "Photos used with permission.",
            status: resolved ? "overturn" : "pending",
            created_at: "2026-11-05T00:00:00Z",
            ...(resolved
              ? { resolution_reason: "Permission context accepted." }
              : {}),
          },
        ],
      }),
    ),
  );
  render(<Appeal />);
  fireEvent.change(screen.getByLabelText("Private appeal access"), {
    target: { value: "scoped-demo-access" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Open my report" }));
  expect(await screen.findByRole("status")).toHaveTextContent(
    "awaiting a moderator",
  );
  resolved = true;
  fireEvent.click(screen.getByRole("button", { name: "Refresh report" }));
  expect(
    await screen.findByText("Moderator response: Permission context accepted."),
  ).toBeVisible();
  expect(screen.getByRole("status")).toHaveTextContent(
    "no longer adds a confirmed warning",
  );
});

it("explains expired appeal access without referring to a moderator login", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      Response.json(
        { detail: "Invalid or expired appeal access." },
        { status: 401 },
      ),
    ),
  );
  render(<Appeal />);
  fireEvent.change(screen.getByLabelText("Private appeal access"), {
    target: { value: "expired-demo-link" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Open my report" }));
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "private appeal link is invalid or expired",
  );
});

it("submits an explanation with report-scoped access and retains the current warning while pending", async () => {
  const calls = vi.fn(async (url: string, options: RequestInit) => {
    if (url.endsWith("/appeals/access"))
      return Response.json({
        claim: {
          id: "demo1234",
          suspect_handle: "fictional.copy",
          status: "confirmed",
        },
        decisions: [],
        appeals: [],
      });
    return Response.json(
      { id: "appeal-demo", status: "pending" },
      { status: 201 },
    );
  });
  vi.stubGlobal("fetch", calls);
  render(<Appeal />);
  fireEvent.change(screen.getByLabelText("Private appeal access"), {
    target: { value: "report-scoped-demo-access" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Open my report" }));
  await screen.findByText("@fictional.copy");
  expect(screen.getByRole("button", { name: "Submit appeal" })).toBeDisabled();
  fireEvent.change(screen.getByLabelText("Appeal explanation"), {
    target: { value: "These stock photographs are shared with permission." },
  });
  fireEvent.click(screen.getByRole("button", { name: "Submit appeal" }));
  expect(await screen.findByRole("status")).toHaveTextContent(
    "current warning remains",
  );
  const sent = calls.mock.calls.find(([url]) => url === "/api/appeals");
  expect(JSON.parse(sent![1].body as string)).toEqual({
    token: "report-scoped-demo-access",
    reason: "These stock photographs are shared with permission.",
  });
  expect(
    calls.mock.calls.every(
      ([url]) => !url.includes("report-scoped-demo-access"),
    ),
  ).toBe(true);
});
