import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";
import { accounts, accountByHandle } from "../lib/data";
import { useApp } from "../lib/context";
import { Avatar, StatusBadge, Username } from "./Common";
import { Dialog } from "./Dialog";
import { Icon } from "./Icon";
import type { IconName } from "./Icon";
import { CreatePost } from "./SocialViews";

export function Shell({ children }: { children: ReactNode }) {
  const { user } = useApp();
  const location = useLocation();
  const [notifications, setNotifications] = useState(false);
  const [more, setMore] = useState(false);
  const [create, setCreate] = useState(false);
  const [about, setAbout] = useState(false);
  const closePanels = () => {
    setNotifications(false);
    setMore(false);
  };
  useEffect(() => {
    setNotifications(false);
    setMore(false);
    window.scrollTo({ top: 0 });
  }, [location.pathname]);
  useEffect(() => {
    const close = (e: KeyboardEvent) => {
      if (e.key === "Escape") closePanels();
    };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, []);
  const navLink = (to: string, label: string, name: IconName) => (
    <NavLink
      key={to}
      to={to}
      end={to === "/"}
      aria-label={label}
      title={label}
      className={({ isActive }) =>
        `nav-item ${isActive && !notifications ? "active" : ""}`
      }
      onClick={closePanels}
    >
      <Icon name={name} filled={to === "/" && location.pathname === "/"} />
      <span className="nav-text">{label}</span>
      {name === "messages" && <span className="nav-dot">1</span>}
    </NavLink>
  );
  return (
    <div className={`app-shell ${notifications ? "panel-open" : ""}`}>
      <aside className="sidebar">
        <Link className="brand" to="/" aria-label="Instagram home">
          <img src="/media/wordmark.png" alt="Instagram" />
          <span className="brand-symbol">
            <Icon name="instagram" size={24} />
          </span>
        </Link>
        <nav aria-label="Main navigation">
          {navLink("/", "Home", "home")}
          {navLink("/reels", "Reels", "reels")}
          {navLink("/messages", "Messages", "messages")}
          {navLink("/explore", "Search", "search")}
          <button
            className={`nav-item ${notifications ? "active" : ""}`}
            aria-label="Notifications"
            aria-expanded={notifications}
            title="Notifications"
            onClick={() => {
              setNotifications(!notifications);
              setMore(false);
            }}
          >
            <Icon name="heart" />
            <span className="nav-text">Notifications</span>
          </button>
          <button
            className="nav-item"
            aria-label="Create"
            title="Create"
            onClick={() => {
              closePanels();
              setCreate(true);
            }}
          >
            <Icon name="create" />
            <span className="nav-text">Create</span>
          </button>
          <NavLink
            to={`/profile/${user.handle}`}
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
            aria-label="Profile"
            title="Profile"
          >
            <Avatar account={user} size="xs" linked={false} />
            <span className="nav-text">Profile</span>
          </NavLink>
        </nav>
        <div className="sidebar-bottom">
          <button
            className={`nav-item ${more ? "active" : ""}`}
            aria-label="More"
            aria-expanded={more}
            title="More"
            onClick={() => {
              setMore(!more);
              setNotifications(false);
            }}
          >
            <Icon name="menu" />
            <span className="nav-text">More</span>
          </button>
          <button
            className="nav-item"
            aria-label="More from Meta"
            title="More from Meta"
            onClick={() => setAbout(true)}
          >
            <Icon name="products" />
            <span className="nav-text">More from Meta</span>
          </button>
        </div>
        <span className="concept-caption">FEATURE CONCEPT</span>
      </aside>
      {more && (
        <div className="more-menu">
          <Link to="/explore" onClick={closePanels}>
            <Icon name="explore" size={21} />
            Explore
          </Link>
          <Link to="/saved" onClick={closePanels}>
            <Icon name="save" size={21} />
            Saved
          </Link>
          <Link to="/review" onClick={closePanels}>
            <Icon name="shield" size={21} />
            Report review
          </Link>
          <button
            onClick={() => {
              setMore(false);
              setAbout(true);
            }}
          >
            <Icon name="instagram" size={21} />
            About this app
          </button>
        </div>
      )}
      {notifications && (
        <NotificationsPanel onClose={() => setNotifications(false)} />
      )}
      <main id="main-content" className="main-content">
        <div
          className={`mobile-header ${location.pathname.startsWith("/profile/") ? "hide-on-profile" : ""}`}
        >
          <Link to="/" aria-label="Instagram home">
            <img src="/media/wordmark.png" alt="Instagram" />
          </Link>
          <div>
            <button
              className="icon-button"
              aria-label="Create new post"
              onClick={() => setCreate(true)}
            >
              <Icon name="create" />
            </button>
            <button
              className="icon-button"
              aria-label="Notifications"
              onClick={() => setNotifications(!notifications)}
            >
              <Icon name="heart" />
            </button>
            <button
              className="icon-button"
              aria-label="Open menu"
              onClick={() => setMore(!more)}
            >
              <Icon name="menu" />
            </button>
          </div>
        </div>
        {children}
      </main>
      <nav className="mobile-nav" aria-label="Mobile navigation">
        <NavLink to="/" aria-label="Home">
          <Icon name="home" filled={location.pathname === "/"} />
        </NavLink>
        <NavLink to="/explore" aria-label="Search">
          <Icon name="search" />
        </NavLink>
        <NavLink to="/reels" aria-label="Reels">
          <Icon name="reels" />
        </NavLink>
        <button aria-label="Create new post" onClick={() => setCreate(true)}>
          <Icon name="create" />
        </button>
        <NavLink to="/messages" aria-label="Messages">
          <Icon name="messages" />
          <span className="mobile-count">1</span>
        </NavLink>
        <NavLink to={`/profile/${user.handle}`} aria-label="Profile">
          <Avatar account={user} size="xs" linked={false} />
        </NavLink>
      </nav>
      {!location.pathname.startsWith("/messages") && (
        <Link
          className="desktop-message-dock"
          to="/messages"
          aria-label="Open messages"
        >
          <Icon name="messages" size={24} />
          <strong>Messages</strong>
          <span>
            {accounts.slice(2, 5).map((account) => (
              <Avatar
                key={account.handle}
                account={account}
                size="xs"
                linked={false}
              />
            ))}
          </span>
        </Link>
      )}
      {create && <CreatePost onClose={() => setCreate(false)} />}
      {about && (
        <Dialog title="About this app" onClose={() => setAbout(false)}>
          <div className="about-body">
            <Icon name="instagram" size={44} />
            <h3>The Instagram you know. More trust.</h3>
            <p>
              An unofficial feature concept for the Meta AI Hackathon: account
              reports, evidence checks with Meta AI and human moderation.
            </p>
            <p className="muted">
              Profiles and social interactions are for demonstration. Reports
              are processed by the application server.
            </p>
            <p className="muted">
              Football accounts are fan communities. Posts, follower counts and
              connections are demo content.
            </p>
            <p>
              <a href="/photo-credits.html" target="_blank" rel="noreferrer">
                Photos and credits
              </a>{" "}
              ·{" "}
              <a
                href="/open-source-licenses.txt"
                target="_blank"
                rel="noreferrer"
              >
                Open source licenses
              </a>
            </p>
            <Link
              className="button primary"
              to="/review"
              onClick={() => setAbout(false)}
            >
              Report review center
            </Link>
          </div>
        </Dialog>
      )}
    </div>
  );
}
function NotificationsPanel({ onClose }: { onClose: () => void }) {
  const { statuses } = useApp();
  const entries = Object.entries(statuses).filter(([handle]) =>
    accountByHandle(handle),
  );
  return (
    <aside
      className="search-panel notifications-panel"
      role="dialog"
      aria-label="Notifications"
    >
      <div className="panel-heading">
        <h2>Notifications</h2>
        <button
          className="icon-button"
          aria-label="Close notifications"
          onClick={onClose}
        >
          <Icon name="close" size={20} />
        </button>
      </div>
      <h3>Account reviews</h3>
      {entries.length ? (
        entries.map(([handle, status]) => (
          <Link
            key={handle}
            to={`/profile/${handle}`}
            className="notification-item"
            onClick={onClose}
          >
            <Avatar account={accountByHandle(handle)!} linked={false} />
            <p>
              <strong>{handle}</strong>
              <br />
              {status === "confirmed"
                ? "Review complete. A warning label has been added to the profile."
                : "Report received. Awaiting a moderator decision."}
            </p>
            <Icon name="shield" size={20} />
          </Link>
        ))
      ) : (
        <div className="notification-empty">
          <Icon name="heart" size={45} />
          <h3>You are all caught up</h3>
          <p>Updates on your reports will appear here.</p>
        </div>
      )}
    </aside>
  );
}
