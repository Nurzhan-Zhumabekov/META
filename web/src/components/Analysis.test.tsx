import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import type { Claim } from "../lib/types";
import { AnalysisView } from "./Analysis";

it("separates pair text reuse from standalone spam patterns and explains synthetic training", () => {
  const claim = {
    id: "test",
    status: "under_review",
    suspect_handle: "copy",
    owner_handle: "owner",
    score: 0.5,
    reasons: [],
    analysis: {
      provider: "meta",
      pair_ml: {
        risk_score: 0.93,
        assessment: "needs_review",
        training_data: "synthetic",
        factors: [],
        limitations: [],
      },
      profile_ml: {
        risk_score: 0.06,
        risk_band: "low",
        factors: [],
        limitations: [],
        out_of_range_features: [],
      },
    },
  } satisfies Claim;
  render(<AnalysisView claim={claim} />);
  expect(screen.getByText("Content reuse signals · ML")).toBeInTheDocument();
  expect(screen.getByText("Spam patterns · ML")).toBeInTheDocument();
  expect(screen.getByText(/synthetic pairs/)).toBeInTheDocument();
  expect(screen.getByText("93")).toBeInTheDocument();
});

it("translates historical provider observations for display without altering the record", () => {
  const claim: Claim = {
    id: "historical",
    status: "under_review",
    suspect_handle: "copy",
    owner_handle: "owner",
    score: 0.7,
    reasons: [],
    analysis: {
      provider: "meta",
      summary: "Одинаковое отображаемое имя Aigerim K. в обоих профилях",
      evidence: [],
      differences: [],
      limitations: [
        "Скриншоты сами по себе не доказывают владение аккаунтом, решение должен принять человек.",
      ],
    },
  };
  const original = JSON.stringify(claim);
  render(<AnalysisView claim={claim} detailed />);
  expect(
    screen.getByText("Both profiles display the name Aigerim K."),
  ).toBeInTheDocument();
  expect(
    screen.getByText(
      "Screenshots alone do not prove account ownership; a human must decide.",
    ),
  ).toBeInTheDocument();
  expect(document.body.textContent).not.toMatch(/[\u0400-\u04ff]/);
  expect(JSON.stringify(claim)).toBe(original);
});

it("separates Meta visual similarity from the combined score and the saved human decision", () => {
  const claim: Claim = {
    id: "ordinary",
    status: "rejected",
    suspect_handle: "ordinary",
    owner_handle: "owner",
    score: 0.664,
    reasons: [],
    analysis: {
      provider: "meta",
      similarity_score: 0.78,
      recommendation: "needs_review",
      pair_ml: {
        risk_score: 0.0063,
        assessment: "low_copy_signal",
        training_data: "synthetic",
        factors: [],
        limitations: [],
      },
    },
  };
  render(<AnalysisView claim={claim} detailed />);
  expect(screen.getByText("Meta visual similarity")).toBeInTheDocument();
  expect(screen.getByText("78")).toBeInTheDocument();
  expect(screen.getByText("Combined content reuse")).toBeInTheDocument();
  expect(screen.getByText("66.4")).toBeInTheDocument();
  expect(screen.getByText("0.6")).toBeInTheDocument();
  expect(
    screen.getByText("Meta recommendation: Human review suggested"),
  ).toBeInTheDocument();
  expect(
    screen.getByText("Moderator decision: Report dismissed"),
  ).toBeInTheDocument();
});

it("does not invent a Meta visual score for older reports and keeps an insufficient-evidence recommendation", () => {
  const claim: Claim = {
    id: "insufficient",
    status: "under_review",
    suspect_handle: "ordinary",
    owner_handle: "owner",
    score: 0.1,
    reasons: [],
    analysis: { provider: "meta", recommendation: "insufficient_evidence" },
  };
  render(<AnalysisView claim={claim} />);
  expect(screen.queryByText("Meta visual similarity")).not.toBeInTheDocument();
  expect(
    screen.getByText("Meta recommendation: Not enough evidence"),
  ).toBeInTheDocument();
  expect(
    screen.getByText("Moderator decision: Awaiting review"),
  ).toBeInTheDocument();
});
