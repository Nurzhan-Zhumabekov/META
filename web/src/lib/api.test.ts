import { describe, expect, it } from "vitest";
import { fileError, profileFacts, readableError } from "./api";

describe("report evidence boundaries", () => {
  it("rejects non-images and oversized evidence before a paid request", () => {
    expect(
      fileError(new File(["x"], "proof.txt", { type: "text/plain" })),
    ).toMatch(/image/i);
    expect(
      fileError(
        new File([new Uint8Array(5 * 1024 * 1024 + 1)], "proof.png", {
          type: "image/png",
        }),
      ),
    ).toMatch(/5 MB/);
    expect(
      fileError(new File(["png"], "proof.png", { type: "image/png" })),
    ).toBeNull();
  });
  it("rejects an invented or fractional count and preserves the exact suspect handle", () => {
    const values = {
      handle: "alice.studio",
      display_name: "Alice",
      bio: "Hello",
      num_posts: "6",
      num_followers: "40",
      num_following: "2100",
      has_profile_picture: true,
      has_external_url: false,
      is_private: false,
    };
    expect(profileFacts(values)).toMatchObject({
      handle: "alice.studio",
      num_posts: 6,
      num_followers: 40,
    });
    expect(() => profileFacts({ ...values, num_followers: "-1" })).toThrow(
      /whole numbers/i,
    );
    expect(() => profileFacts({ ...values, num_posts: "2.5" })).toThrow(
      /whole numbers/i,
    );
  });
  it("returns a recoverable user message for a disconnected server", () => {
    expect(readableError(new TypeError("Failed to fetch"))).toMatch(/server/i);
  });
});
