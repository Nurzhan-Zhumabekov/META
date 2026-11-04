import { useState } from "react";
import { Link } from "react-router-dom";
import {
  accounts,
  discoveryAccounts,
  accountByHandle,
  compact,
  number,
  posts,
  profilePost,
  reelPost,
} from "../lib/data";
import { useApp } from "../lib/context";
import type { Account, Post } from "../lib/types";
import { AccountActions, Avatar, EmptyState, Username } from "./Common";
import { Dialog } from "./Dialog";
import { Icon } from "./Icon";
import { PostCarousel } from "./PostCarousel";
import { EmojiButton } from "./EmojiButton";

export function Feed({ savedOnly = false }: { savedOnly?: boolean }) {
  const { user, addedPosts, saved, following, refresh, connectionError } =
    useApp();
  const [tab, setTab] = useState("for-you");
  const [story, setStory] = useState<Account | null>(null);
  let feed = [...addedPosts, ...posts];
  if (savedOnly)
    feed = [
      ...new Map(
        [
          ...feed,
          ...accounts.flatMap((account) =>
            account.photos.map((_, i) => profilePost(account, i)),
          ),
          reelPost,
        ].map((post) => [post.id, post]),
      ).values(),
    ].filter((post) => saved.has(post.id));
  else if (tab === "following")
    feed = feed.filter(
      (post) => post.account === user.handle || following.has(post.account),
    );
  return (
    <div className="feed-layout">
      <section className="feed-column" aria-label="Post feed">
        {savedOnly ? (
          <div className="section-heading">
            <Icon name="save" size={18} />
            <h1>Saved</h1>
            <span className="muted">Only you can see this</span>
          </div>
        ) : (
          <>
            <div className="feed-tabs" role="tablist" aria-label="Feed">
              <button
                role="tab"
                aria-selected={tab === "for-you"}
                className={tab === "for-you" ? "active" : ""}
                onClick={() => setTab("for-you")}
              >
                For you
              </button>
              <button
                role="tab"
                aria-selected={tab === "following"}
                className={tab === "following" ? "active" : ""}
                onClick={() => setTab("following")}
              >
                Following
              </button>
            </div>
            <div className="stories" aria-label="Stories">
              {discoveryAccounts
                .filter((a) => a.handle !== user.handle)
                .map((a) => (
                  <button
                    key={a.handle}
                    className="story"
                    onClick={() => setStory(a)}
                  >
                    <Avatar account={a} size="lg" ring linked={false} />
                    <span>{a.handle}</span>
                  </button>
                ))}
            </div>
          </>
        )}
        {connectionError && (
          <div className="connection-note" role="status">
            <Icon name="warning" size={17} />
            <span>Account checks are temporarily unavailable.</span>
            <button onClick={() => void refresh()}>Try again</button>
          </div>
        )}
        <div className="posts">
          {feed.map((post, index) => (
            <PostCard key={post.id} post={post} priority={index === 0} />
          ))}
          {!feed.length && (
            <EmptyState
              icon={savedOnly ? "save" : "heart"}
              title={
                savedOnly ? "Save what inspires you" : "Your feed starts here"
              }
            >
              {savedOnly
                ? "Tap the bookmark below a post to save it here."
                : "Follow accounts you like to see their posts."}
            </EmptyState>
          )}
        </div>
      </section>
      <Suggestions />
      {story && <Story account={story} onClose={() => setStory(null)} />}
    </div>
  );
}
export function PostCard({
  post,
  expanded = false,
  priority = false,
}: {
  post: Post;
  expanded?: boolean;
  priority?: boolean;
}) {
  const account = accountByHandle(post.account) ?? accounts[0];
  const { user, liked, toggleLike, saved, toggleSave, comments, addComment } =
    useApp();
  const [menu, setMenu] = useState(false);
  const [detail, setDetail] = useState(false);
  const [caption, setCaption] = useState(expanded);
  const [text, setText] = useState("");
  const localComments = comments[post.id] ?? [];
  const send = (event: React.FormEvent) => {
    event.preventDefault();
    if (!text.trim()) return;
    addComment(post.id, text.trim());
    setText("");
  };
  return (
    <article className="post-card">
      <header className="post-header">
        <Avatar account={account} size="sm" ring />
        <div className="post-identity">
          <div>
            <Username account={account} status />
            <span className="post-age"> · {post.age}</span>
          </div>
          <span className="post-location">{post.location}</span>
        </div>
        <button
          className="icon-button"
          aria-label={`Post options ${post.id}`}
          onClick={() => setMenu(true)}
        >
          <Icon name="more" size={22} />
        </button>
      </header>
      <PostCarousel
        id={post.id}
        priority={priority}
        images={post.images ?? [post.image]}
        caption={post.caption.split("\n")[0]}
        onDoubleClick={() => {
          if (!liked.has(post.id)) toggleLike(post.id);
        }}
      />
      <div className="post-actions">
        <button
          className={`icon-button ${liked.has(post.id) ? "liked" : ""}`}
          aria-label={liked.has(post.id) ? "Unlike" : "Like"}
          aria-pressed={liked.has(post.id)}
          onClick={() => toggleLike(post.id)}
        >
          <Icon name="heart" filled={liked.has(post.id)} />
          <span className="post-inline-count" aria-hidden="true">
            {compact(post.likes + (liked.has(post.id) ? 1 : 0))}
          </span>
        </button>
        <button
          className="icon-button"
          aria-label="Comments"
          onClick={() => setDetail(true)}
        >
          <Icon name="comment" />
          <span className="post-inline-count" aria-hidden="true">
            {post.comments + localComments.length}
          </span>
        </button>
        <Link
          className="icon-button"
          aria-label="Share post"
          to={`/messages/${account.handle}`}
        >
          <Icon name="messages" />
        </Link>
        <button
          className="icon-button save-button"
          aria-label={saved.has(post.id) ? "Remove from saved" : "Save"}
          aria-pressed={saved.has(post.id)}
          onClick={() => toggleSave(post.id)}
        >
          <Icon name="save" filled={saved.has(post.id)} />
        </button>
      </div>
      <div className="post-copy">
        <p className="post-likes">
          {number(post.likes + (liked.has(post.id) ? 1 : 0))} likes
        </p>
        <p className={`post-caption ${caption ? "expanded" : ""}`}>
          <Link to={`/profile/${account.handle}`} className="bold">
            {account.handle}
          </Link>{" "}
          {post.caption}
        </p>
        {post.caption.length > 90 && !caption && (
          <button
            className="subtle-button more-caption"
            onClick={() => setCaption(true)}
          >
            more
          </button>
        )}
        <button
          className="subtle-button comments-link"
          onClick={() => setDetail(true)}
        >
          View all comments ({post.comments + localComments.length})
        </button>
        {localComments.slice(-2).map((comment, i) => (
          <p className="posted-comment" key={i}>
            <strong>{user.handle}</strong> {comment}
          </p>
        ))}
        <form className="comment-form" onSubmit={send}>
          <input
            aria-label="Add a comment"
            placeholder="Add a comment…"
            value={text}
            maxLength={500}
            onChange={(event) => setText(event.target.value)}
          />
          <button type="submit" disabled={!text.trim()}>
            Post
          </button>
          <EmojiButton
            label={`Emoji for post ${post.id}`}
            onSelect={(emoji) =>
              setText((v) => (v.length + emoji.length <= 500 ? v + emoji : v))
            }
          />
        </form>
      </div>
      {menu && (
        <AccountActions
          account={account}
          post={post}
          onClose={() => setMenu(false)}
        />
      )}
      {detail && (
        <Dialog
          title="Comments"
          onClose={() => setDetail(false)}
          className="comments-dialog"
        >
          <div className="comments-body">
            <div className="comment-row">
              <Avatar account={account} size="sm" />
              <p>
                <strong>{account.handle}</strong> {post.caption}
              </p>
            </div>
            <div className="comment-row">
              <Avatar account={accounts[3]} size="sm" />
              <p>
                <strong>{accounts[3].handle}</strong>{" "}
                {account.category === "football"
                  ? "These are the moments we love the game for! ⚽🔥"
                  : "Such beautiful light! 🤍"}
              </p>
            </div>
            {localComments.map((comment, i) => (
              <div className="comment-row" key={i}>
                <Avatar account={user} size="sm" />
                <p>
                  <strong>{user.handle}</strong> {comment}
                </p>
              </div>
            ))}
          </div>
          <form className="comment-form dialog-comment" onSubmit={send}>
            <input
              autoFocus
              aria-label="Your comment"
              placeholder="Add a comment…"
              value={text}
              onChange={(e) => setText(e.target.value)}
              maxLength={500}
            />
            <button disabled={!text.trim()}>Post</button>
            <EmojiButton
              label={`Emoji in comments ${post.id}`}
              onSelect={(emoji) =>
                setText((v) => (v.length + emoji.length <= 500 ? v + emoji : v))
              }
            />
          </form>
        </Dialog>
      )}
    </article>
  );
}
export function Suggestions() {
  const { user, setUser, following, toggleFollow } = useApp();
  const [switching, setSwitching] = useState(false);
  return (
    <aside className="suggestions" aria-label="Suggestions">
      <div className="suggestion-user">
        <Avatar account={user} size="md" />
        <div className="suggestion-names">
          <Username account={user} />
          <span>{user.name}</span>
        </div>
        <button className="text-button" onClick={() => setSwitching(true)}>
          Switch
        </button>
      </div>
      <div className="suggestions-heading">
        <span>Suggested for you</span>
        <Link to="/explore">See all</Link>
      </div>
      {discoveryAccounts
        .filter((a) => a.handle !== user.handle)
        .slice(0, 5)
        .map((account) => (
          <div className="suggestion-user" key={account.handle}>
            <Avatar account={account} size="sm" />
            <div className="suggestion-names">
              <Username account={account} />
              <span>
                {account.category === "football"
                  ? "Football · Suggested for you"
                  : account.handle.includes("studio")
                    ? "You may know each other"
                    : "Suggested for you"}
              </span>
            </div>
            <button
              className={`text-button ${following.has(account.handle) ? "is-following" : ""}`}
              onClick={() => toggleFollow(account.handle)}
            >
              {following.has(account.handle) ? "Following" : "Follow"}
            </button>
          </div>
        ))}
      <footer className="site-footer">
        <p>
          About · Help · Press · API · Jobs · Privacy · Terms · Locations ·
          Language
        </p>
        <p>© 2026 INSTAGRAM · FEATURE CONCEPT</p>
        <Link to="/review">Report review center</Link>
        <a href="/photo-credits.html" target="_blank" rel="noreferrer">
          Photo credits
        </a>
      </footer>
      {switching && (
        <Dialog title="Switch accounts" onClose={() => setSwitching(false)}>
          {[accounts[0], accounts[2]].map((account) => (
            <button
              className="switch-account"
              key={account.handle}
              onClick={() => {
                setUser(account);
                setSwitching(false);
              }}
            >
              <Avatar account={account} linked={false} />
              <strong>{account.handle}</strong>
              {account.handle === user.handle && (
                <Icon name="check" size={18} />
              )}
            </button>
          ))}
          <p className="dialog-footnote">Demo application profiles</p>
        </Dialog>
      )}
    </aside>
  );
}
export function Story({
  account,
  onClose,
}: {
  account: Account;
  onClose: () => void;
}) {
  const [index, setIndex] = useState(0);
  return (
    <Dialog
      title={`Story ${account.handle}`}
      onClose={onClose}
      className="story-dialog"
    >
      <div className="story-content">
        <img
          className="story-photo"
          src={account.photos[index % account.photos.length]}
          alt={`Story ${account.name}`}
        />
        <div className="story-top">
          <div className="story-segments">
            {[0, 1, 2].map((n) => (
              <span className={n <= index ? "seen" : ""} key={n} />
            ))}
          </div>
          <div className="story-user">
            <Avatar account={account} size="sm" linked={false} />
            <strong>{account.handle}</strong>
            <span>2h</span>
          </div>
        </div>
        <p className="story-caption">
          It is the little moments that make it all.
        </p>
        <button
          className="story-next"
          aria-label="Next story"
          onClick={() => (index < 2 ? setIndex(index + 1) : onClose())}
        >
          <Icon name="chevron" />
        </button>
      </div>
    </Dialog>
  );
}
