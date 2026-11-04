import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { fireEvent, render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AppProvider } from "../lib/context";
import App from "../App";

let style: HTMLStyleElement;
beforeEach(() => {
  style = document.createElement("style");
  style.textContent = readFileSync(
    resolve(process.cwd(), "src/styles.css"),
    "utf8",
  );
  document.head.append(style);
  Object.defineProperty(window, "scrollTo", {
    configurable: true,
    value: vi.fn(),
  });
  HTMLDialogElement.prototype.showModal = function () {
    this.setAttribute("open", "");
  };
  HTMLDialogElement.prototype.close = function () {
    this.removeAttribute("open");
  };
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) =>
      Response.json(
        url.endsWith("/statuses")
          ? { "aigerim.k.studio": "confirmed" }
          : { provider: "meta", ready: true, profile_ml: { ready: true } },
      ),
    ),
  );
  render(
    <MemoryRouter initialEntries={["/messages"]}>
      <AppProvider>
        <App />
      </AppProvider>
    </MemoryRouter>,
  );
});
afterEach(() => style.remove());

it("keeps conversation avatars fixed instead of stretching them into the text column", () => {
  const images = screen
    .getAllByRole("img", { name: /Profile photo/ })
    .filter((image) => image.closest(".conversation-item"));
  expect(images.length).toBeGreaterThan(0);
  for (const image of images) {
    const avatar = image.parentElement!;
    const css = getComputedStyle(avatar);
    expect(css.flexGrow).toBe("0");
    expect(css.flexShrink).toBe("0");
    expect(css.width).toBe(css.height);
  }
});

it("keeps avatars fixed in the new-message picker too", () => {
  fireEvent.click(screen.getByRole("button", { name: "New message" }));
  const picker = screen.getByRole("dialog", { name: "New message" });
  for (const image of within(picker).getAllByRole("img")) {
    expect(getComputedStyle(image.parentElement!).flexGrow).toBe("0");
    expect(getComputedStyle(image.parentElement!).flexShrink).toBe("0");
  }
});

it("saves an own note in the demo without sending a message", () => {
  fireEvent.click(screen.getByRole("button", { name: "Your note" }));
  const note = screen.getByRole("dialog", { name: "Your note" });
  fireEvent.change(within(note).getByRole("textbox", { name: "Note text" }), {
    target: { value: "Building a new feature" },
  });
  fireEvent.click(within(note).getByRole("button", { name: "Save note" }));
  expect(screen.getByRole("button", { name: "Your note" })).toHaveTextContent(
    "Building a new feature",
  );
  expect(
    screen.queryByRole("dialog", { name: "Your note" }),
  ).not.toBeInTheDocument();
});

it("filters conversations by handle and still opens and sends to the selected person", async () => {
  fireEvent.change(screen.getByRole("searchbox", { name: "Search messages" }), {
    target: { value: "nurzhan.dev" },
  });
  const threads = screen.getByRole("navigation", { name: "Conversations" });
  expect(within(threads).getAllByRole("link")).toHaveLength(1);
  fireEvent.click(within(threads).getByRole("link", { name: /Nurzhan/ }));
  fireEvent.change(await screen.findByRole("textbox", { name: "Message" }), {
    target: { value: "Checking the updated Direct" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Send" }));
  expect(
    screen.getByText("Checking the updated Direct", {
      selector: ".sent-message",
    }),
  ).toBeInTheDocument();
});
