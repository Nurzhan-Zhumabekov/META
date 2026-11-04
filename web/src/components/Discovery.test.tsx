import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { AppProvider } from "../lib/context";
import App from "../App";

beforeEach(() => {
  localStorage.clear();
  window.scrollTo = vi.fn();
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) =>
      Response.json(
        url.endsWith("/statuses")
          ? {}
          : { provider: "meta", ready: true, profile_ml: { ready: true } },
      ),
    ),
  );
  HTMLDialogElement.prototype.showModal = function () {
    this.setAttribute("open", "");
  };
  HTMLDialogElement.prototype.close = function () {
    this.removeAttribute("open");
  };
});
afterEach(() => vi.restoreAllMocks());
it("adds a football fan follow to the following feed", async () => {
  view("/profile/leomessi.fan");
  fireEvent.click(screen.getByRole("button", { name: "Follow" }));
  fireEvent.click(
    within(
      screen.getByRole("navigation", { name: "Main navigation" }),
    ).getByRole("link", { name: "Home" }),
  );
  fireEvent.click(screen.getByRole("tab", { name: "Following" }));
  expect(
    await screen.findByRole("region", {
      name: "Post photos football-messi",
    }),
  ).toBeInTheDocument();
  expect(
    screen.queryByRole("region", { name: "Post photos football-ronaldo" }),
  ).not.toBeInTheDocument();
});
function view(path = "/explore") {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AppProvider>
        <App />
      </AppProvider>
    </MemoryRouter>,
  );
}
it("discovers football profiles and opens a complete fan profile with follower lists", async () => {
  view();
  fireEvent.click(screen.getByRole("button", { name: "Football" }));
  fireEvent.change(screen.getByRole("searchbox", { name: "Search accounts" }), {
    target: { value: "Messi" },
  });
  fireEvent.click(await screen.findByRole("link", { name: /leomessi.fan/ }));
  expect(await screen.findByText("Fan community")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /Followers list/ }));
  const list = await screen.findByRole("dialog", { name: "Followers" });
  expect(within(list).getAllByRole("link").length).toBeGreaterThan(0);
});
it("keeps carousel keyboard navigation and dots usable without wraparound", async () => {
  view("/");
  const carousel = await screen.findByRole("region", {
    name: "Post photos football-ronaldo",
  });
  expect(
    within(carousel).getByRole("button", { name: "Previous photo" }),
  ).toBeDisabled();
  fireEvent.keyDown(carousel, { key: "ArrowRight" });
  expect(within(carousel).getByText("2 / 3")).toBeInTheDocument();
  fireEvent.click(
    within(carousel).getByRole("button", { name: "Photo 3 of 3" }),
  );
  expect(
    within(carousel).getByRole("button", { name: "Next photo" }),
  ).toBeDisabled();
});
it("inserts an English-search emoji into the actual Direct composer", async () => {
  // jsdom has no layout. Give the real picker a viewport so its virtualized
  // catalog behaves as it does in the browser instead of mounting every emoji.
  vi.spyOn(HTMLElement.prototype, "clientWidth", "get").mockImplementation(
    function (this: HTMLElement) {
      return this.closest(".EmojiPickerReact") ? 340 : 0;
    },
  );
  vi.spyOn(HTMLElement.prototype, "clientHeight", "get").mockImplementation(
    function (this: HTMLElement) {
      return this.closest(".EmojiPickerReact") ? 300 : 0;
    },
  );
  view("/messages/leomessi.fan");
  fireEvent.click(screen.getByRole("button", { name: "Message emoji" }));
  const picker = await screen.findByRole("dialog", { name: "Emoji" });
  // Wait for the real lazy picker and English catalog, including on a busy
  // two-core Docker builder, before starting the search interaction.
  await act(async () => {
    await vi.dynamicImportSettled();
  });
  const search = await within(picker).findByPlaceholderText("Search emoji");
  fireEvent.change(search, { target: { value: "soccer" } });
  fireEvent.click(
    await within(picker).findByRole("gridcell", { name: "soccer ball" }),
  );
  expect(screen.getByRole("textbox", { name: "Message" })).toHaveValue("⚽");
  expect(
    screen.queryByRole("dialog", { name: "Emoji" }),
  ).not.toBeInTheDocument();
});
