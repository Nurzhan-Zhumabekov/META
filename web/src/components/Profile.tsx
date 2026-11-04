import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  accountByHandle,
  compact,
  discoveryAccounts,
  number,
  profilePost,
} from "../lib/data";
import { useApp } from "../lib/context";
import { AccountActions, Avatar, EmptyState, StatusBadge } from "./Common";
import { Dialog } from "./Dialog";
import { PostCard, Story } from "./Feed";
import { Icon, Verified } from "./Icon";

export function Profile() {
  const { handle = "" } = useParams();
  const account = accountByHandle(handle);
  const {
    user,
    statuses,
    setReport,
    following,
    toggleFollow,
    refresh,
    notify,
  } = useApp();
  const [tab, setTab] = useState("posts");
  const [menu, setMenu] = useState(false);
  const [selected, setSelected] = useState<number | null>(null);
  const [story, setStory] = useState(false);
  const [edit, setEdit] = useState(false);
  const [people, setPeople] = useState<"followers" | "following" | null>(null);
  const [name, setName] = useState(account?.name ?? "");
  const [bio, setBio] = useState(account?.bio ?? "");
  useEffect(() => {
    setName(account?.name ?? "");
    setBio(account?.bio ?? "");
    setTab("posts");
    setPeople(null);
    void refresh();
  }, [handle, account, refresh]);
  if (!account)
    return (
      <EmptyState icon="search" title="Profile not found">
        Check the username or <Link to="/">return to the feed</Link>.
      </EmptyState>
    );
  const own = user.handle === account.handle;
  return (
    <section className="profile-page" aria-label={`Profile ${account.handle}`}>
      <div className="mobile-profile-bar">
        <Link to="/" className="icon-button" aria-label="Back to feed">
          <Icon name="back" size={21} />
        </Link>
        <h1 className="mobile-profile-heading">{account.handle}</h1>
        <button
          className="icon-button"
          aria-label="Account options"
          onClick={() => setMenu(true)}
        >
          <Icon name="more" />
        </button>
      </div>
      <header className="profile-header">
        <div className="profile-avatar">
          <Avatar account={account} size="xl" ring linked={false} />
        </div>
        <div className="profile-info">
          <div className="profile-title-row">
            <h1>{account.handle}</h1>
            <span className="profile-mobile-handle" aria-hidden="true">
              {account.handle}
            </span>
            {account.verified && <Verified />}
            <button
              className="icon-button desktop-profile-menu"
              aria-label="Account options"
              onClick={() => setMenu(true)}
            >
              <Icon name="more" />
            </button>
          </div>
          <strong className="profile-display-name">{name}</strong>
          <div className="profile-stats">
            <span>
              <strong>{number(account.posts)}</strong> posts
            </span>
            <button
              type="button"
              aria-label={`Followers list for ${account.handle}`}
              onClick={() => setPeople("followers")}
            >
              <strong>
                {compact(
                  account.followers + (following.has(account.handle) ? 1 : 0),
                )}
              </strong>{" "}
              followers
            </button>
            <button
              type="button"
              aria-label={`Following list for ${account.handle}`}
              onClick={() => setPeople("following")}
            >
              <strong>{number(account.following)}</strong> following
            </button>
          </div>
          <div className="profile-bio">
            <strong>{name}</strong>
            {account.profileLabel && (
              <span className="profile-category">{account.profileLabel}</span>
            )}
            <p>{bio}</p>
            <StatusBadge handle={account.handle} />
            {statuses[account.handle] === "under_review" && (
              <p className="profile-status-note">
                This report is under review. No decision has been made yet.
              </p>
            )}
            {!own && (
              <button
                className="profile-report-link"
                onClick={() => setReport(account)}
              >
                Report account
              </button>
            )}
          </div>
        </div>
        <div className="profile-buttons">
          {own ? (
            <>
              <button
                className="button secondary"
                onClick={() => setEdit(true)}
              >
                Edit profile
              </button>
              <Link className="button secondary" to="/saved">
                Saved
              </Link>
            </>
          ) : (
            <>
              <button
                className={`button ${following.has(account.handle) ? "secondary" : "primary"}`}
                onClick={() => toggleFollow(account.handle)}
              >
                {following.has(account.handle) ? "Following" : "Follow"}
              </button>
              <Link
                className="button secondary"
                to={`/messages/${account.handle}`}
              >
                Send message
              </Link>
            </>
          )}
        </div>
      </header>
      <div className="profile-highlights">
        {(
          account.highlights ?? ["Moments", "On the road", "Behind the scenes"]
        ).map((label, i) => (
          <button key={label} onClick={() => setStory(true)}>
            <span>
              <img
                src={account.photos[(i + 1) % account.photos.length]}
                alt=""
              />
            </span>
            <strong>{label}</strong>
          </button>
        ))}
        {own && (
          <button onClick={() => setStory(true)}>
            <span className="highlight-new">+</span>
            <strong>New</strong>
          </button>
        )}
      </div>
      <div
        className="profile-grid-tabs"
        role="tablist"
        aria-label="Profile posts"
      >
        <button
          role="tab"
          aria-label="Posts"
          aria-selected={tab === "posts"}
          className={tab === "posts" ? "active" : ""}
          onClick={() => setTab("posts")}
        >
          <Icon name="grid" size={13} />
          <span>POSTS</span>
        </button>
        {own && (
          <Link to="/saved" aria-label="Saved">
            <Icon name="save" size={13} />
            <span>SAVED</span>
          </Link>
        )}
        {!own && (
          <button
            role="tab"
            aria-label="Profile Reels"
            aria-selected={tab === "reels"}
            className={tab === "reels" ? "active" : ""}
            onClick={() => setTab("reels")}
          >
            <Icon name="reels" size={24} />
            <span>REELS</span>
          </button>
        )}
        <button
          role="tab"
          aria-label="Tagged posts"
          aria-selected={tab === "tagged"}
          className={tab === "tagged" ? "active" : ""}
          onClick={() => setTab("tagged")}
        >
          <Icon name="tag" size={14} />
          <span>TAGGED</span>
        </button>
      </div>
      {tab === "posts" ? (
        <div className="profile-grid">
          {account.photos.map((image, i) => (
            <button
              key={`${image}-${i}`}
              aria-label={`Open post ${i + 1}`}
              onClick={() => setSelected(i)}
            >
              <img
                src={image}
                alt={`Photo ${i + 1} from profile ${account.handle}`}
                loading={i > 2 ? "lazy" : "eager"}
              />
              <span className="grid-hover">
                <Icon name="heart" filled size={22} /> {74 + i * 37}
                <Icon name="comment" filled size={22} /> {i + 3}
              </span>
            </button>
          ))}
        </div>
      ) : tab === "reels" ? (
        <EmptyState icon="reels" title="No Reels yet">
          Short videos from this account will appear here.
        </EmptyState>
      ) : (
        <EmptyState icon="tag" title="Photos of you">
          Posts tagging this account will appear here.
        </EmptyState>
      )}
      <p className="profile-footer">
        Instagram · Unofficial feature concept · 2026 ·{" "}
        <a href="/photo-credits.html" target="_blank" rel="noreferrer">
          Photo credits
        </a>
      </p>
      {people && (
        <Dialog
          title={people === "followers" ? "Followers" : "Following"}
          onClose={() => setPeople(null)}
          className="people-dialog"
        >
          <p className="dialog-footnote">
            A selection of demo profiles. Counts and connections are not
            imported from Instagram.
          </p>
          <div className="people-list">
            {discoveryAccounts
              .filter((a) => a.handle !== account.handle)
              .slice(0, 16)
              .map((person) => (
                <div className="person-row" key={person.handle}>
                  <Avatar account={person} />
                  <Link
                    to={`/profile/${person.handle}`}
                    onClick={() => setPeople(null)}
                    className="person-name"
                  >
                    <strong>{person.handle}</strong>
                    <span>{person.name}</span>
                  </Link>
                  {person.handle !== user.handle && (
                    <button
                      className={`button ${following.has(person.handle) ? "secondary" : "primary"}`}
                      onClick={() => toggleFollow(person.handle)}
                    >
                      {following.has(person.handle) ? "Following" : "Follow"}
                    </button>
                  )}
                </div>
              ))}
          </div>
        </Dialog>
      )}
      {menu && (
        <AccountActions account={account} onClose={() => setMenu(false)} />
      )}
      {story && <Story account={account} onClose={() => setStory(false)} />}
      {selected !== null && (
        <Dialog
          title="Post"
          onClose={() => setSelected(null)}
          className="post-dialog"
        >
          <PostCard expanded post={profilePost(account, selected)} />
        </Dialog>
      )}
      {edit && (
        <Dialog title="Edit profile" onClose={() => setEdit(false)}>
          <form
            className="settings-form"
            onSubmit={(event) => {
              event.preventDefault();
              setEdit(false);
              notify("Profile updated for this session");
            }}
          >
            <label>
              Name
              <input
                value={name}
                maxLength={100}
                onChange={(event) => setName(event.target.value)}
              />
            </label>
            <label>
              Bio
              <textarea
                value={bio}
                maxLength={500}
                rows={4}
                onChange={(event) => setBio(event.target.value)}
              />
            </label>
            <button className="button primary" type="submit">
              Save
            </button>
          </form>
        </Dialog>
      )}
    </section>
  );
}
