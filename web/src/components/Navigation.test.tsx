import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import App from "../App";
import { AppProvider } from "../lib/context";

beforeEach(() => {
  Object.defineProperty(window, "scrollTo", {
    configurable: true,
    value: vi.fn(),
  });
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) =>
      Response.json(
        url.endsWith("/statuses")
          ? { "aigerim.k.backup": "confirmed" }
          : { provider: "meta", ready: true, profile_ml: { ready: true } },
      ),
    ),
  );
});

it("finds a reported account from the website search route and preserves its server label", async () => {
  render(
    <MemoryRouter>
      <AppProvider>
        <App />
      </AppProvider>
    </MemoryRouter>,
  );
  fireEvent.click(
    within(
      screen.getByRole("navigation", { name: "Main navigation" }),
    ).getByRole("link", { name: "Search" }),
  );
  fireEvent.change(
    await screen.findByRole("searchbox", { name: "Search accounts" }),
    { target: { value: "aigerim.k.backup" } },
  );
  fireEvent.click(
    await screen.findByRole("link", { name: /aigerim.k.backup/ }),
  );
  await waitFor(() =>
    expect(
      screen.getAllByRole("heading", { name: "aigerim.k.backup" }).length,
    ).toBeGreaterThan(0),
  );
  expect(screen.getByText("Impersonation confirmed")).toBeInTheDocument();
});
