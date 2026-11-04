import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  accounts,
  discoveryAccounts,
  accountByHandle,
  compact,
  profilePost,
  reelPost,
} from "../lib/data";
import type { Post } from "../lib/types";
import { fileError } from "../lib/api";
import { useApp } from "../lib/context";
import {
  AccountActions,
  Avatar,
  EmptyState,
  StatusBadge,
  Username,
} from "./Common";
import { Dialog } from "./Dialog";
import { PostCard } from "./Feed";
import { Icon } from "./Icon";
import { EmojiButton } from "./EmojiButton";

export function Explore() {
  const [selected, setSelected] = useState<Post | null>(null);
  const [query, setQuery] = useState("");
  const [topic, setTopic] = useState("all");
  const normalized = query.trim().toLocaleLowerCase();
  const topicAccounts = discoveryAccounts.filter(
    (account) => topic === "all" || account.category === topic,
  );
  const matches = topicAccounts.filter((account) =>
    `${account.handle} ${account.name} ${account.bio}`
      .toLocaleLowerCase()
      .includes(normalized),
  );
  const tiles = topicAccounts
    .filter((a) => !a.handle.startsWith("aigerim.k."))
    .flatMap((account) =>
      account.photos.slice(0, 3).map((_, i) => profilePost(account, i)),
    );
  return (
    <section className="explore-page">
      <h1 className="sr-only">Explore</h1>
      <div className="explore-search">
        <Icon name="search" size={18} />
        <input
          type="search"
          aria-label="Search accounts"
          placeholder="Search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          autoComplete="off"
        />
        {query && (
          <button aria-label="Clear search" onClick={() => setQuery("")}>
            <Icon name="close" size={16} />
          </button>
        )}
      </div>
      <div className="discovery-topics" aria-label="Post topics">
        {[
          ["all", "For you"],
          ["football", "Football"],
          ["travel", "Travel"],
          ["photography", "Photography"],
          ["technology", "Technology"],
          ["lifestyle", "Lifestyle"],
        ].map(([value, label]) => (
          <button
            type="button"
            key={value}
            aria-pressed={topic === value}
            onClick={() => setTopic(value)}
          >
            {label}
          </button>
        ))}
      </div>
      {normalized ? (
        <div className="explore-search-results" aria-live="polite">
          {matches.map((account) => (
            <Link
              className="search-result"
              to={`/profile/${account.handle}`}
              key={account.handle}
            >
              <Avatar account={account} linked={false} />
              <div>
                <strong>{account.handle}</strong>
                <span>{account.name}</span>
                <StatusBadge handle={account.handle} compact />
              </div>
            </Link>
          ))}
          {!matches.length && (
            <p className="search-empty">
              No accounts found. Check the username.
            </p>
          )}
        </div>
      ) : (
        <div className="explore-grid">
          {tiles.map((post, i) => (
            <button
              className={i % 10 === 2 ? "tall-tile" : ""}
              aria-label={`Open post ${post.account} ${i + 1}`}
              key={`${post.id}-${i}`}
              onClick={() => setSelected(post)}
            >
              <img
                src={post.image}
                alt={post.caption}
                loading={i > 5 ? "lazy" : "eager"}
              />
              <span className="grid-hover">
                <Icon name="heart" filled />
                {compact(post.likes)}
                <Icon name="comment" filled />
                {post.comments}
              </span>
            </button>
          ))}
        </div>
      )}
      {selected && (
        <Dialog
          title="Post"
          className="post-dialog"
          onClose={() => setSelected(null)}
        >
          <PostCard post={selected} expanded />
        </Dialog>
      )}
    </section>
  );
}
export function CreatePost({ onClose }: { onClose: () => void }) {
  const { user, addPost, notify } = useApp();
  const navigate = useNavigate();
  const [file, setFile] = useState<File>();
  const [preview, setPreview] = useState("");
  const [caption, setCaption] = useState("");
  const [error, setError] = useState("");
  const shared = useRef(false);
  useEffect(() => {
    if (!file) return;
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => {
      if (!shared.current) URL.revokeObjectURL(url);
    };
  }, [file]);
  const choose = (value: File | undefined) => {
    if (!value) return;
    const problem = fileError(value);
    if (problem) {
      setError(problem);
      return;
    }
    setError("");
    setFile(value);
  };
  return (
    <Dialog title="Create new post" onClose={onClose} className="create-dialog">
      {!file ? (
        <label
          className="create-drop"
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            choose(e.dataTransfer.files[0]);
          }}
        >
          <div className="create-illustration">
            <Icon name="grid" size={55} />
            <Icon name="reels" size={39} />
          </div>
          <h3>Drag a photo here</h3>
          <span className="button primary">Select from computer</span>
          <input
            type="file"
            aria-label="Post photo"
            accept="image/jpeg,image/png,image/webp"
            onChange={(e) => choose(e.target.files?.[0])}
          />
        </label>
      ) : (
        <form
          onSubmit={(event) => {
            event.preventDefault();
            shared.current = true;
            addPost({
              id: `local-${Date.now()}`,
              account: user.handle,
              image: preview,
              caption,
              likes: 0,
              comments: 0,
              location: "New post",
              age: "now",
            });
            onClose();
            navigate("/");
            notify("Post added to the demo feed");
          }}
        >
          <img className="create-preview" src={preview} alt="Post preview" />
          <div className="create-caption">
            <div className="inline-user">
              <Avatar account={user} size="xs" linked={false} />
              <strong>{user.handle}</strong>
            </div>
            <textarea
              placeholder="Write a caption…"
              aria-label="Post caption"
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              maxLength={2200}
              rows={3}
            />
            <button className="button primary full">Share</button>
            <p className="dialog-footnote">
              This post is available for the current demo session.
            </p>
          </div>
        </form>
      )}
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
    </Dialog>
  );
}
export function Reels() {
  const video = useRef<HTMLVideoElement>(null);
  const { liked, toggleLike } = useApp();
  const [playing, setPlaying] = useState(true);
  const [muted, setMuted] = useState(true);
  const [menu, setMenu] = useState(false);
  const [comments, setComments] = useState(false);
  const account = accountByHandle(reelPost.account)!;
  useEffect(() => {
    const element = video.current;
    if (!element) return;
    if (playing) void element.play().catch(() => setPlaying(false));
    else element.pause();
  }, [playing]);
  return (
    <section className="reels-page">
      <h1 className="sr-only">Reels</h1>
      <div className="reel-frame">
        <video
          ref={video}
          src="/media/reel.mp4"
          poster="/media/flowers.jpg"
          muted={muted}
          loop
          playsInline
          onLoadedData={() => {
            if (playing)
              void video.current?.play().catch(() => setPlaying(false));
          }}
        />
        <button
          className="reel-play"
          aria-label={playing ? "Pause video" : "Play video"}
          onClick={() => setPlaying(!playing)}
        >
          {!playing && <Icon name="play" filled size={55} />}
        </button>
        <button
          className="reel-sound"
          aria-label={muted ? "Unmute" : "Mute"}
          onClick={() => setMuted(!muted)}
        >
          <Icon name={muted ? "mute" : "volume"} size={19} />
        </button>
        <div className="reel-copy">
          <div className="inline-user">
            <Avatar account={account} size="sm" />
            <Username account={account} />
            <Link className="reel-follow" to={`/profile/${account.handle}`}>
              Profile
            </Link>
          </div>
          <p>{reelPost.caption}</p>
          <span>♫ Original audio · {account.handle}</span>
        </div>
      </div>
      <div className="reel-actions">
        <button
          aria-label="Like"
          className={liked.has(reelPost.id) ? "liked" : ""}
          onClick={() => toggleLike(reelPost.id)}
        >
          <Icon name="heart" filled={liked.has(reelPost.id)} size={27} />
          <span>
            {compact(reelPost.likes + (liked.has(reelPost.id) ? 1 : 0))}
          </span>
        </button>
        <button aria-label="Reel comments" onClick={() => setComments(true)}>
          <Icon name="comment" size={27} />
          <span>64</span>
        </button>
        <Link aria-label="Share Reel" to={`/messages/${account.handle}`}>
          <Icon name="messages" size={26} />
        </Link>
        <button aria-label="Reel options" onClick={() => setMenu(true)}>
          <Icon name="more" />
        </button>
        <Avatar account={account} size="xs" />
      </div>
      {menu && (
        <AccountActions
          account={account}
          post={reelPost}
          onClose={() => setMenu(false)}
        />
      )}
      {comments && (
        <Dialog
          title="Reel comments"
          onClose={() => setComments(false)}
          className="post-dialog"
        >
          <PostCard post={reelPost} expanded />
        </Dialog>
      )}
    </section>
  );
}
export function Messages() {
  const { handle } = useParams();
  const navigate = useNavigate();
  const { user, statuses, notify } = useApp();
  const account = accountByHandle(handle ?? "");
  const contacts = accounts.filter((a) => a.handle !== user.handle);
  const [query, setQuery] = useState("");
  const visibleContacts = contacts.filter((contact) =>
    `${contact.handle} ${contact.name}`
      .toLocaleLowerCase()
      .includes(query.trim().toLocaleLowerCase()),
  );
  const noteContacts = contacts
    .filter((contact) => !contact.handle.startsWith("aigerim."))
    .slice(0, 3);
  const noteTexts = [
    "Building something new",
    "The mountains are calling",
    "Inspiration is all around",
  ];
  const [myNote, setMyNote] = useState("");
  const [noteDraft, setNoteDraft] = useState("");
  const [openNote, setOpenNote] = useState<string | null>(null);
  const noteScroller = useRef<HTMLDivElement>(null);
  const [text, setText] = useState("");
  const [messages, setMessages] = useState<Record<string, string[]>>({});
  const [select, setSelect] = useState(false);
  const send = (event: React.FormEvent) => {
    event.preventDefault();
    if (!account || !text.trim()) return;
    setMessages((old) => ({
      ...old,
      [account.handle]: [...(old[account.handle] ?? []), text.trim()],
    }));
    setText("");
  };
  return (
    <section className={`messages-page ${account ? "conversation-open" : ""}`}>
      <aside className="inbox">
        <div className="inbox-account">
          <h1>{user.handle}</h1>
          <button
            className="icon-button"
            aria-label="New message"
            onClick={() => setSelect(true)}
          >
            <Icon name="compose" />
          </button>
        </div>
        <div className="inbox-search">
          <Icon name="search" size={18} />
          <input
            type="search"
            aria-label="Search messages"
            placeholder="Search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          {query && (
            <button
              aria-label="Clear message search"
              onClick={() => setQuery("")}
            >
              <Icon name="close" size={16} />
            </button>
          )}
        </div>
        <div className="inbox-notes-wrap">
          <div className="inbox-notes" aria-label="Notes" ref={noteScroller}>
            <button
              className="inbox-note"
              aria-label="Your note"
              onClick={() => {
                setNoteDraft(myNote);
                setOpenNote(user.handle);
              }}
            >
              <span className="note-bubble">
                {myNote || "Share a thought…"}
              </span>
              <Avatar account={user} size="lg" linked={false} />
              <span className="note-author">Your note</span>
            </button>
            {noteContacts.map((contact, index) => (
              <button
                className="inbox-note"
                aria-label={`Note from ${contact.name}`}
                key={contact.handle}
                onClick={() => setOpenNote(contact.handle)}
              >
                <span className="note-bubble">{noteTexts[index]}</span>
                <Avatar account={contact} size="lg" linked={false} />
                <span className="note-author">
                  {contact.name.split(" ")[0]}
                </span>
              </button>
            ))}
          </div>
          <button
            className="notes-next"
            aria-label="Next notes"
            onClick={() => noteScroller.current?.scrollBy({ left: 180 })}
          >
            <Icon name="chevron" size={16} />
          </button>
        </div>
        <div className="inbox-title">
          <strong>Messages</strong>
          <button className="text-button" onClick={() => setSelect(true)}>
            Compose
          </button>
        </div>
        <nav className="inbox-threads" aria-label="Conversations">
          {visibleContacts.map((contact) => (
            <Link
              className={`conversation-item ${account?.handle === contact.handle ? "selected" : ""}`}
              to={`/messages/${contact.handle}`}
              key={contact.handle}
              aria-current={
                account?.handle === contact.handle ? "page" : undefined
              }
            >
              <Avatar account={contact} size="md" linked={false} />
              <span className="conversation-copy">
                <strong>{contact.name}</strong>
                <small>
                  {messages[contact.handle]?.at(-1) ??
                    (contact.handle.includes("studio")
                      ? "Photography bookings are open"
                      : "Start a conversation")}
                </small>
              </span>
              {contact.handle.includes("studio") && (
                <span className="unread-indicator" />
              )}
            </Link>
          ))}
          {!visibleContacts.length && (
            <p className="inbox-no-results">
              No conversations found. Try a different name.
            </p>
          )}
        </nav>
      </aside>
      <div className="conversation">
        {account ? (
          <>
            <header className="conversation-heading">
              <Link
                className="icon-button mobile-chat-back"
                aria-label="Back to messages"
                to="/messages"
              >
                <Icon name="back" />
              </Link>
              <Avatar account={account} size="sm" />
              <Link
                className="conversation-person"
                to={`/profile/${account.handle}`}
              >
                <strong>{account.name}</strong>
                <small>{account.handle}</small>
              </Link>
              <StatusBadge handle={account.handle} compact />
              <button
                className="icon-button"
                aria-label="Open conversation profile"
                onClick={() => navigate(`/profile/${account.handle}`)}
              >
                <Icon name="external" size={20} />
              </button>
            </header>
            {statuses[account.handle] === "confirmed" && (
              <div className="chat-warning">
                <Icon name="shield" size={22} />
                <p>
                  <strong>Be careful with this account.</strong>
                  <br />A moderator review added an impersonation label to this
                  profile.
                </p>
              </div>
            )}
            <div className="chat-content">
              <Avatar account={account} size="lg" linked={false} />
              <h2>{account.name}</h2>
              <p>{account.handle} · Instagram concept</p>
              <Link
                className="button secondary"
                to={`/profile/${account.handle}`}
              >
                View profile
              </Link>
              <div className="chat-date">Today</div>
              {(messages[account.handle] ?? []).map((message, i) => (
                <div className="sent-message" key={i}>
                  {message}
                </div>
              ))}
            </div>
            <form className="message-composer" onSubmit={send}>
              <EmojiButton
                label="Message emoji"
                onSelect={(emoji) =>
                  setText((v) =>
                    v.length + emoji.length <= 2000 ? v + emoji : v,
                  )
                }
              />
              <input
                placeholder="Message…"
                aria-label="Message"
                value={text}
                onChange={(e) => setText(e.target.value)}
                maxLength={2000}
              />
              <button disabled={!text.trim()}>Send</button>
            </form>
            <p className="chat-demo-note">Local demo conversation</p>
          </>
        ) : (
          <EmptyState icon="messages" title="Your messages">
            Send a message to an account you know.
            <br />
            <button className="button primary" onClick={() => setSelect(true)}>
              Write a message
            </button>
          </EmptyState>
        )}
      </div>
      {openNote && (
        <Dialog
          title={openNote === user.handle ? "Your note" : "Note"}
          onClose={() => setOpenNote(null)}
        >
          {openNote === user.handle ? (
            <form
              className="settings-form"
              onSubmit={(event) => {
                event.preventDefault();
                setMyNote(noteDraft.trim());
                setOpenNote(null);
                notify("Note saved for this session");
              }}
            >
              <label>
                What is on your mind?
                <textarea
                  aria-label="Note text"
                  value={noteDraft}
                  onChange={(event) => setNoteDraft(event.target.value)}
                  maxLength={60}
                  rows={3}
                  placeholder="Share a thought…"
                />
              </label>
              <p className="dialog-footnote">
                Your note is available for the current demo session.
              </p>
              <button className="button primary">Save note</button>
            </form>
          ) : (
            <div className="note-preview">
              <Avatar
                account={accountByHandle(openNote)!}
                size="lg"
                linked={false}
              />
              <strong>{accountByHandle(openNote)!.name}</strong>
              <p>
                {
                  noteTexts[
                    noteContacts.findIndex(
                      (contact) => contact.handle === openNote,
                    )
                  ]
                }
              </p>
            </div>
          )}
        </Dialog>
      )}
      {select && (
        <Dialog title="New message" onClose={() => setSelect(false)}>
          <div className="new-message-list">
            {contacts.map((contact) => (
              <Link
                to={`/messages/${contact.handle}`}
                onClick={() => setSelect(false)}
                key={contact.handle}
              >
                <Avatar account={contact} linked={false} />
                <span className="new-message-copy">
                  <strong>{contact.handle}</strong>
                  <small>{contact.name}</small>
                </span>
                <Icon name="chevron" size={18} />
              </Link>
            ))}
          </div>
        </Dialog>
      )}
    </section>
  );
}
