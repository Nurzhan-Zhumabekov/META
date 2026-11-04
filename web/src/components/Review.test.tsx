import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { AppProvider } from "../lib/context";
import App from "../App";

let signedIn = false;
let state = "under_review";
const fetchMock = vi.fn();
const row = () => ({
  id: "testcase",
  suspect_handle: "aigerim.k.studio",
  owner_handle: "aigerim.k",
  status: state,
  score: 0.8,
  reasons: [],
  analysis: {
    provider: "meta",
    model: "muse-spark-1.3",
    summary: "Some content matches.",
    evidence: [],
    differences: [],
    limitations: [],
  },
});
beforeEach(() => {
  signedIn = false;
  state = "under_review";
  fetchMock.mockReset();
  Object.defineProperty(window, "scrollTo", {
    configurable: true,
    value: vi.fn(),
  });
  vi.stubGlobal(
    "fetch",
    fetchMock.mockImplementation(async (url: string, options: RequestInit) => {
      if (url.endsWith("/analysis/status"))
        return Response.json({
          provider: "meta",
          ready: true,
          profile_ml: { ready: true },
        });
      if (url.endsWith("/reviewer/session")) {
        if (options.method === "POST") signedIn = true;
        return Response.json(
          { authenticated: signedIn },
          { status: signedIn ? 200 : 401 },
        );
      }
      if (url.endsWith("/claims/pending")) return Response.json([row()]);
      if (url.includes("/status?status=")) {
        state = url.split("status=")[1];
        return Response.json({ ok: true });
      }
      if (url.endsWith("/statuses"))
        return Response.json(
          state === "rejected" ? {} : { "aigerim.k.studio": state },
        );
      return Response.json({});
    }),
  );
});
function app() {
  render(
    <MemoryRouter initialEntries={["/review"]}>
      <AppProvider>
        <App />
      </AppProvider>
    </MemoryRouter>,
  );
}
async function login() {
  fireEvent.change(await screen.findByLabelText("Moderator code"), {
    target: { value: "test-review-code" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Log in" }));
  await screen.findByTestId("review-testcase");
}

it("requires reviewer sign-in and never sends the reviewer code with a decision", async () => {
  app();
  await screen.findByLabelText("Moderator code");
  expect(
    fetchMock.mock.calls.some(([url]) => url.endsWith("/claims/pending")),
  ).toBe(false);
  await login();
  fireEvent.click(
    screen.getByRole("button", { name: "Confirm impersonation" }),
  );
  await screen.findByText("Decision saved.");
  const action = fetchMock.mock.calls.find(([url]) =>
    url.includes("/status?status="),
  );
  expect(action?.[1].credentials).toBe("same-origin");
  expect(JSON.stringify(action?.[1])).not.toContain("test-review-code");
});
it("updates the same profile badge only after a human confirms the complaint", async () => {
  app();
  await login();
  expect(screen.queryByText("Impersonation confirmed")).not.toBeInTheDocument();
  fireEvent.click(
    screen.getByRole("button", { name: "Confirm impersonation" }),
  );
  fireEvent.click(await screen.findByRole("link", { name: "View profile" }));
  await waitFor(() =>
    expect(screen.getByText("Impersonation confirmed")).toBeInTheDocument(),
  );
  expect(state).toBe("confirmed");
});
it("does not create a warning label when a moderator rejects the claim", async () => {
  app();
  await login();
  fireEvent.click(screen.getByRole("button", { name: "Dismiss report" }));
  fireEvent.click(await screen.findByRole("link", { name: "View profile" }));
  await waitFor(() => expect(state).toBe("rejected"));
  expect(screen.queryByText("Impersonation confirmed")).not.toBeInTheDocument();
});
