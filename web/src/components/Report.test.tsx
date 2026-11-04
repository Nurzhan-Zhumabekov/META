import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { AppProvider } from "../lib/context";
import { accounts } from "../lib/data";
import { ReportDialog } from "./Report";

const claim = {
  id: "newclaim1",
  suspect_handle: "aigerim.k.studio",
  owner_handle: "aigerim.k",
  status: "under_review",
  score: 0.7,
  reasons: [],
  analysis: {
    provider: "meta",
    model: "muse-spark-1.3",
    summary: "The name is reused.",
    evidence: ["The name matches."],
    differences: [],
    limitations: [],
    profile_ml: {
      risk_score: 0.91,
      factors: [],
      limitations: [],
      out_of_range_features: [],
    },
  },
};
const fetchMock = vi.fn();
let inspectionReady = false;
let privacyRequired = false;
const observation = (value: string | number) => ({ value, confidence: 0.97 });
const inspected = {
  inspection_id: "verified-screenshots",
  providers: { ocr: "paddleocr", photos: "imagededup", privacy: "presidio" },
  elapsed_seconds: 2,
  redaction: {
    applied: true,
    policy_version: "presidio-opaque-lines-v1",
    regions_masked: 1,
    previews: {
      original: "data:image/jpeg;base64,originalmasked",
      suspect: "data:image/jpeg;base64,suspectmasked",
    },
  },
  original: {
    fields: {
      handle: observation("aigerim.k"),
      display_name: observation("OCR Original"),
      bio: observation("Original bio from image"),
    },
    warnings: [],
    privacy: { count: 0, findings: [] },
  },
  suspect: {
    fields: {
      handle: observation("aigerim.k.studio"),
      display_name: observation("OCR Candidate"),
      bio: observation("Candidate bio from image"),
      num_posts: observation(8),
      num_followers: observation(123),
      num_following: observation(234),
    },
    warnings: [],
    privacy: { count: 1, findings: [{ entity_type: "EMAIL_ADDRESS" }] },
  },
  photos: {
    count: 1,
    matches: [{ original_index: 0, suspect_index: 0 }],
    original_boxes: [[0.1, 0.5, 0.4, 0.9]],
    suspect_boxes: [[0.1, 0.5, 0.4, 0.9]],
    limitations: [],
  },
};
beforeEach(() => {
  inspectionReady = false;
  privacyRequired = false;
  vi.stubGlobal("fetch", fetchMock);
  fetchMock.mockImplementation(async (url: string) =>
    Response.json(
      url.endsWith("/analysis/status")
        ? {
            provider: "meta",
            privacy_redaction_required: privacyRequired,
            model: "muse-spark-1.3",
            ready: true,
            profile_ml: { ready: true },
            pair_ml: { ready: true },
            evidence_tools: { ready: inspectionReady },
          }
        : url.endsWith("/evidence/inspect")
          ? inspected
          : url.endsWith("/claims")
            ? claim
            : {},
    ),
  );
  Object.defineProperty(HTMLDialogElement.prototype, "showModal", {
    configurable: true,
    value() {
      this.setAttribute("open", "");
    },
  });
  Object.defineProperty(HTMLDialogElement.prototype, "close", {
    configurable: true,
    value() {
      this.removeAttribute("open");
    },
  });
  vi.stubGlobal(
    "URL",
    class extends URL {
      static createObjectURL() {
        return "blob:test";
      }
      static revokeObjectURL() {}
    },
  );
});
function form() {
  render(
    <MemoryRouter>
      <AppProvider>
        <ReportDialog account={accounts[1]} onClose={() => {}} />
      </AppProvider>
    </MemoryRouter>,
  );
  fireEvent.click(
    screen.getByRole("button", { name: "Pretending to be someone else" }),
  );
}
describe("complaint submission", () => {
  it("blocks submission if mandatory local privacy tools are unavailable", async () => {
    privacyRequired = true;
    form();
    await screen.findByText(
      "Contact redaction is temporarily unavailable. Nothing was sent to Meta AI.",
    );
    expect(
      screen.getByRole("button", { name: "Submit report" }),
    ).toBeDisabled();
    expect(fetchMock.mock.calls.some(([url]) => url.endsWith("/claims"))).toBe(
      false,
    );
  });
  it("autofills OCR and shows provider image previews with contacts burned into pixels", async () => {
    inspectionReady = true;
    form();
    await screen.findByText(/Meta AI/);
    const file = new File(["image"], "proof.png", { type: "image/png" });
    for (const name of [
      "Your profile screenshot",
      "Reported profile screenshot",
    ])
      fireEvent.change(screen.getByLabelText(name), {
        target: { files: [file] },
      });
    await screen.findByText("Fields extracted by PaddleOCR");
    expect(screen.getByLabelText("Name", { exact: true })).toHaveValue(
      "OCR Candidate",
    );
    expect(screen.getByLabelText("Followers", { exact: true })).toHaveValue(
      123,
    );
    const submit = screen.getByRole("button", { name: "Submit report" });
    expect(submit).toBeDisabled();
    expect(
      screen.getByRole("img", { name: "For Meta AI: reported profile" }),
    ).toHaveAttribute("src", inspected.redaction.previews.suspect);
    expect(
      screen.getByText("Redacted before sending to Meta AI: 1"),
    ).toBeInTheDocument();
    expect(
      screen.queryByLabelText(/I confirm sending unredacted screenshots/),
    ).not.toBeInTheDocument();
    fireEvent.click(
      screen.getByLabelText("I have reviewed the extracted data"),
    );
    expect(submit).toBeEnabled();
    fireEvent.click(submit);
    await screen.findByText("Thank you. We received your report.");
    const body = fetchMock.mock.calls.find(([url]) =>
      url.endsWith("/claims"),
    )![1].body;
    expect(body.get("inspection_id")).toBe("verified-screenshots");
    expect(JSON.parse(body.get("profile_facts")).num_followers).toBe(123);
    expect(JSON.parse(body.get("original_profile_facts")).bio).toBe(
      "Original bio from image",
    );
    expect(body.get("ocr_reviewed")).toBe("true");
    expect(body.has("pii_acknowledged")).toBe(false);
  });
  it("does not call analysis until both evidence images are attached", async () => {
    form();
    fireEvent.click(screen.getByRole("button", { name: "Submit report" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "two screenshots",
    );
    expect(
      fetchMock.mock.calls.filter(([url]) => url.endsWith("/claims")),
    ).toHaveLength(0);
  });
  it("sends multipart facts and shows human review instead of a confirmed verdict", async () => {
    form();
    await screen.findByText(/Meta AI/);
    const file = new File(["image"], "proof.png", { type: "image/png" });
    fireEvent.change(screen.getByLabelText("Your profile screenshot"), {
      target: { files: [file] },
    });
    fireEvent.change(screen.getByLabelText("Reported profile screenshot"), {
      target: { files: [file] },
    });
    fireEvent.click(screen.getByRole("button", { name: "Submit report" }));
    await screen.findByText("Thank you. We received your report.");
    const call = fetchMock.mock.calls.find(([url]) => url.endsWith("/claims"))!;
    expect(call[1].body).toBeInstanceOf(FormData);
    expect(call[1].body.get("suspect")).toBe("aigerim.k.studio");
    expect(JSON.parse(call[1].body.get("profile_facts")).num_followers).toBe(
      40,
    );
    expect(JSON.parse(call[1].body.get("original_profile_facts"))).toEqual({
      handle: accounts[0].handle,
      display_name: accounts[0].name,
      bio: accounts[0].bio,
    });
    expect(screen.getByText(/A moderator will decide/)).toBeInTheDocument();
    expect(
      screen.queryByText("Impersonation confirmed"),
    ).not.toBeInTheDocument();
  });
  it("clears original text when the owner changes instead of sending another account's bio", async () => {
    form();
    const bio = await screen.findByLabelText("Original profile bio");
    expect(bio).toHaveValue(accounts[0].bio);
    fireEvent.change(screen.getByLabelText("Your original account"), {
      target: { value: "other.owner" },
    });
    expect(bio).toHaveValue("");
  });
  it("keeps a failed request retryable and never shows a successful report", async () => {
    form();
    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
    fetchMock.mockImplementation(async (url: string) =>
      url.endsWith("/claims")
        ? Promise.reject(new TypeError("Failed to fetch"))
        : Response.json({}),
    );
    const file = new File(["image"], "proof.png", { type: "image/png" });
    for (const name of [
      "Your profile screenshot",
      "Reported profile screenshot",
    ])
      fireEvent.change(screen.getByLabelText(name), {
        target: { files: [file] },
      });
    fireEvent.click(screen.getByRole("button", { name: "Submit report" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("server");
    expect(
      screen.queryByText("Thank you. We received your report."),
    ).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Submit report" })).toBeEnabled();
  });
});
