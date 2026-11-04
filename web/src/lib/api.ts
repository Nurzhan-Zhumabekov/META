import { englishText } from "./english";

export async function initializeDemo() {
  const status = await fetch("/api/demo/session", {
    credentials: "same-origin",
  });
  if (status.status === 404) return;
  if (!status.ok)
    throw new Error("The demonstration is temporarily unavailable.");
  const session = await status.json();
  if (session.enabled && !session.active) {
    const started = await fetch("/api/demo/session", {
      method: "POST",
      credentials: "same-origin",
    });
    if (!started.ok)
      throw new Error(
        "Cannot start a private demonstration session. Please try again later.",
      );
  }
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status = 0,
    public code = "",
  ) {
    super(message);
    this.name = "ApiError";
  }
}
export async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...options,
    credentials: "same-origin",
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const detail =
      typeof data?.detail === "string"
        ? data.detail
        : "Check your details and try again.";
    throw new ApiError(englishText(detail), response.status, data?.code ?? "");
  }
  if (data === null)
    throw new ApiError(
      "The server returned an unexpected response. Please try again.",
    );
  return data as T;
}
export function readableError(error: unknown): string {
  if (error instanceof TypeError)
    return "Cannot reach the server. Try again in a few seconds.";
  if (error instanceof ApiError) {
    if (error.status === 401)
      return "The moderator code is incorrect or your session has expired.";
    if (error.status === 403)
      return "You do not have access to this action. Reload the page and log in again.";
    if (error.status === 429)
      return "Too many requests. Please try again later.";
    if (error.status === 413)
      return "The screenshot is too large. Choose an image up to 5 MB.";
    if (error.status === 504)
      return "The analysis timed out. The report was not saved; you can try again.";
    if (error.status === 502 || error.status === 503)
      return "The analysis service is unavailable. Your report was not submitted; please try again later.";
  }
  return error instanceof Error
    ? englishText(error.message)
    : "Could not complete the action. Please try again.";
}
export function fileError(file: File): string | null {
  if (
    !["image/jpeg", "image/png", "image/webp"].includes(file.type) ||
    file.size === 0
  )
    return "Choose a JPG, PNG or WebP image.";
  if (file.size > 5 * 1024 * 1024)
    return "Each screenshot must be no larger than 5 MB.";
  return null;
}
export interface FactValues {
  handle: string;
  display_name: string;
  bio: string;
  num_posts: string;
  num_followers: string;
  num_following: string;
  has_profile_picture: boolean;
  has_external_url: boolean;
  is_private: boolean;
}
export function profileFacts(values: FactValues) {
  const keys = ["num_posts", "num_followers", "num_following"] as const;
  for (const key of keys)
    if (!/^\d+$/.test(values[key]) || Number(values[key]) > 2147483647)
      throw new Error(
        "Post, follower and following counts must be non-negative whole numbers.",
      );
  return {
    ...values,
    ...Object.fromEntries(keys.map((key) => [key, Number(values[key])])),
  };
}
