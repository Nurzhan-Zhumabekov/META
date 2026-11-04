import type { CSSProperties } from "react";
import { instagramHomeFilled, instagramIcons } from "./InstagramIcons";

export type IconName =
  | "home"
  | "search"
  | "explore"
  | "reels"
  | "messages"
  | "heart"
  | "create"
  | "compose"
  | "menu"
  | "threads"
  | "products"
  | "more"
  | "comment"
  | "save"
  | "grid"
  | "tag"
  | "back"
  | "close"
  | "chevron"
  | "shield"
  | "check"
  | "upload"
  | "clock"
  | "logout"
  | "settings"
  | "volume"
  | "mute"
  | "play"
  | "instagram"
  | "external"
  | "warning";
const paths: Record<IconName, React.ReactNode> = {
  compose: (
    <>
      <path d="M14 4H5a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h13a2 2 0 0 0 2-2v-9" />
      <path d="m19 2 3 3-12 12-4 1 1-4Z" />
    </>
  ),
  products: <path d="M8 2h8v8H8ZM2 14h8v8H2Zm12 0h8v8h-8Z" />,
  home: (
    <>
      <path d="m3 10 9-8 9 8v10a1 1 0 0 1-1 1h-6v-7h-4v7H4a1 1 0 0 1-1-1Z" />
    </>
  ),
  search: (
    <>
      <circle cx="10.8" cy="10.8" r="8" />
      <path d="m16.5 16.5 5 5" />
    </>
  ),
  explore: (
    <>
      <circle cx="12" cy="12" r="10" />
      <path d="m16.5 7.5-3 6-6 3 3-6Z" />
    </>
  ),
  reels: (
    <>
      <rect x="3" y="3" width="18" height="18" rx="4" />
      <path d="M3 8h18M7 3l4 5m4-5 4 5" />
      <path d="m10 12 6 3.5-6 3.5Z" />
    </>
  ),
  messages: (
    <>
      <path d="M22 2 9.5 14.5M22 2l-7.5 20-5-7.5L2 9Z" />
    </>
  ),
  heart: (
    <path d="M20.8 4.8a5.6 5.6 0 0 0-8 0l-.8.8-.8-.8a5.6 5.6 0 0 0-8 8l8.8 8.2 8.8-8.2a5.6 5.6 0 0 0 0-8Z" />
  ),
  create: (
    <>
      <rect x="3" y="3" width="18" height="18" rx="5" />
      <path d="M12 7v10M7 12h10" />
    </>
  ),
  menu: (
    <>
      <path d="M3 5h18M3 12h18M3 19h18" />
    </>
  ),
  threads: (
    <>
      <path d="M17 8c-1-5-10-5-11 2-1 8 9 11 13 5 3-5-2-9-7-7-6 3 2 8 4 3 1-3-1-6-4-5M19 5c-5-7-17-2-17 6 0 8 9 13 16 8" />
    </>
  ),
  more: (
    <>
      <circle cx="4" cy="12" r="1" />
      <circle cx="12" cy="12" r="1" />
      <circle cx="20" cy="12" r="1" />
    </>
  ),
  comment: (
    <path d="M21.5 11.5a9.5 9.5 0 1 0-4.3 8l4.3 1-1-4a9.5 9.5 0 0 0 1-5Z" />
  ),
  save: <path d="M5 3h14v19l-7-5-7 5Z" />,
  grid: (
    <>
      <path d="M3 3h18v18H3ZM3 9h18M3 15h18M9 3v18M15 3v18" />
    </>
  ),
  tag: (
    <>
      <path d="M4 21V7l8-5 8 5v14Z" />
      <circle cx="12" cy="10" r="3" />
      <path d="M7 21v-3c0-4 10-4 10 0v3" />
    </>
  ),
  back: <path d="m14 5-7 7 7 7M7 12h15" />,
  close: <path d="m5 5 14 14M19 5 5 19" />,
  chevron: <path d="m9 5 7 7-7 7" />,
  shield: (
    <>
      <path d="m12 2 9 4v6c0 5-5 9-9 10-4-1-9-5-9-10V6Z" />
      <path d="m8 12 3 3 5-6" />
    </>
  ),
  check: <path d="m5 12 4 4L20 5" />,
  upload: (
    <>
      <path d="M12 16V3m-5 5 5-5 5 5M4 15v6h16v-6" />
    </>
  ),
  clock: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 6v6l4 2" />
    </>
  ),
  logout: (
    <>
      <path d="M9 3H3v18h6m6-14 5 5-5 5M8 12h12" />
    </>
  ),
  settings: (
    <>
      <circle cx="12" cy="12" r="4" />
      <path d="m9 2 1 3h4l1-3 4 3-1 3 3 2v4l-3 2 1 3-4 3-1-3h-4l-1 3-4-3 1-3-3-2v-4l3-2-1-3Z" />
    </>
  ),
  volume: (
    <>
      <path d="M3 9v6h4l5 5V4L7 9ZM16 7c3 3 3 7 0 10m3-13c5 5 5 11 0 16" />
    </>
  ),
  mute: (
    <>
      <path d="M3 9v6h4l5 5V4L7 9Zm13 0 6 6m0-6-6 6" />
    </>
  ),
  play: <path d="m8 4 13 8-13 8Z" />,
  instagram: (
    <>
      <rect x="3" y="3" width="18" height="18" rx="5" />
      <circle cx="12" cy="12" r="4" />
      <circle cx="17.5" cy="6.5" r=".5" />
    </>
  ),
  external: (
    <>
      <path d="M14 3h7v7M21 3 10 14M10 3H3v18h18v-7" />
    </>
  ),
  warning: (
    <>
      <path d="M12 3 1 21h22Z" />
      <path d="M12 9v5m0 3v.1" />
    </>
  ),
};
export function Icon({
  name,
  size = 24,
  filled = false,
  className = "",
  style,
}: {
  name: IconName;
  size?: number;
  filled?: boolean;
  className?: string;
  style?: CSSProperties;
}) {
  const reference =
    name === "home" && filled
      ? instagramHomeFilled
      : !filled
        ? instagramIcons[name]
        : undefined;
  return (
    <svg
      aria-hidden="true"
      className={`icon ${className}`}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill={reference || filled ? "currentColor" : "none"}
      stroke={reference ? "none" : "currentColor"}
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      style={style}
    >
      {reference ?? paths[name]}
    </svg>
  );
}
export function Verified() {
  return (
    <svg
      className="verified"
      width="14"
      height="14"
      viewBox="0 0 24 24"
      aria-label="Verified account"
    >
      <path
        fill="#0095f6"
        d="m12 0 3.1 2.1 3.7.6 1.3 3.5L23 9l-1 3.6 1 3.5-2.9 2.8-1.3 3.5-3.7.6L12 24l-3.1-2.1-3.7-.6-1.3-3.5L1 15l1-3.6L1 8l2.9-2.8L5.2 2l3.7-.6Z"
      />
      <path
        d="m6.8 12 3.3 3.3 7.2-7.2"
        fill="none"
        stroke="white"
        strokeWidth="2.4"
      />
    </svg>
  );
}
