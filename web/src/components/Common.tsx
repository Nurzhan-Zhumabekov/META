import { Link, useNavigate } from "react-router-dom";
import { useApp } from "../lib/context";
import type { Account, Post } from "../lib/types";
import { Dialog } from "./Dialog";
import { Icon, Verified } from "./Icon";

export function Avatar({
  account,
  size = "md",
  ring = false,
  linked = true,
}: {
  account: Account;
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  ring?: boolean;
  linked?: boolean;
}) {
  const image = (
    <span className={`avatar avatar-${size} ${ring ? "story-ring" : ""}`}>
      <img src={account.avatar} alt={`Profile photo of ${account.handle}`} />
    </span>
  );
  return linked ? (
    <Link to={`/profile/${account.handle}`} className="avatar-link">
      {image}
    </Link>
  ) : (
    image
  );
}
export function Username({
  account,
  status = false,
}: {
  account: Account;
  status?: boolean;
}) {
  return (
    <span className="username">
      <Link to={`/profile/${account.handle}`}>{account.handle}</Link>
      {account.verified && <Verified />}
      {status && <StatusBadge handle={account.handle} compact />}
    </span>
  );
}
export function StatusBadge({
  handle,
  compact = false,
}: {
  handle: string;
  compact?: boolean;
}) {
  const status = useApp().statuses[handle];
  if (!status || status === "rejected") return null;
  const text =
    status === "confirmed" ? "Impersonation confirmed" : "Account under review";
  return (
    <span
      className={`status-badge ${status === "confirmed" ? "confirmed" : "pending"} ${compact ? "badge-compact" : ""}`}
      title={text}
    >
      <Icon name={status === "confirmed" ? "shield" : "clock"} size={13} />
      <span>{text}</span>
    </span>
  );
}
export function AccountActions({
  account,
  post,
  onClose,
}: {
  account: Account;
  post?: Post;
  onClose: () => void;
}) {
  const { setReport, saved, toggleSave, notify, user } = useApp();
  const navigate = useNavigate();
  return (
    <Dialog title="Options" onClose={onClose} className="action-dialog">
      <div className="action-list">
        {account.handle !== user.handle && (
          <button
            className="danger"
            onClick={() => {
              onClose();
              setReport(account);
            }}
          >
            Report
          </button>
        )}
        {post && (
          <button
            onClick={() => {
              toggleSave(post.id);
              onClose();
            }}
          >
            {saved.has(post.id) ? "Remove from saved" : "Save"}
          </button>
        )}
        <button
          onClick={() => {
            onClose();
            navigate(`/profile/${account.handle}`);
          }}
        >
          Go to profile
        </button>
        <button
          onClick={() => {
            void navigator.clipboard
              .writeText(`${location.origin}/profile/${account.handle}`)
              .then(() => notify("Link copied"))
              .catch(() => notify("Could not copy the link"));
            onClose();
          }}
        >
          Copy link
        </button>
        <button onClick={onClose}>Cancel</button>
      </div>
    </Dialog>
  );
}
export function EmptyState({
  icon = "instagram",
  title,
  children,
}: {
  icon?: Parameters<typeof Icon>[0]["name"];
  title: string;
  children?: React.ReactNode;
}) {
  return (
    <div className="empty-state">
      <span className="empty-symbol">
        <Icon name={icon} size={34} />
      </span>
      <h2>{title}</h2>
      {children && <p>{children}</p>}
    </div>
  );
}
