import type { Account, Post } from "./types";
import { footballAccounts, creatorAccounts, socialPosts } from "./social-data";

export const media = (name: string) => `/media/${name}.jpg`;
const gallery = [
  "lake",
  "mountains",
  "city",
  "coast",
  "coffee",
  "forest",
  "flowers",
  "interior",
  "lake",
].map(media);
export const accounts: Account[] = [
  {
    handle: "aigerim.k",
    name: "Aigerim K.",
    avatar: media("aigerim"),
    bio: "Collecting moments, not things.\nPhotographer · Astana, Kazakhstan\nBookings and collaborations ↓",
    location: "Astana",
    posts: 128,
    followers: 5400,
    following: 310,
    verified: true,
    photos: gallery,
  },
  {
    handle: "aigerim.k.studio",
    name: "Aigerim K.",
    avatar: media("aigerim"),
    bio: "New photography booking page.\nCollaborations and bookings in Direct.",
    posts: 6,
    followers: 40,
    following: 2100,
    photos: [
      gallery[0],
      gallery[1],
      gallery[2],
      gallery[3],
      gallery[4],
      gallery[5],
    ],
  },
  {
    handle: "nurzhan.dev",
    name: "Nurzhan Zhumabekov",
    avatar: media("nurzhan"),
    bio: "Building what is missing.\nSoftware Engineering · Astana",
    posts: 42,
    followers: 890,
    following: 450,
    photos: [
      media("interior"),
      media("coffee"),
      media("city"),
      ...gallery.slice(0, 6),
    ],
  },
  {
    handle: "madina.travels",
    name: "Madina",
    avatar: media("friend"),
    bio: "Chasing beautiful light and new places.\nNext stop: the mountains.",
    posts: 86,
    followers: 2340,
    following: 624,
    photos: [
      media("coast"),
      media("forest"),
      media("lake"),
      ...gallery.slice(0, 6),
    ],
  },
  {
    handle: "almaty.today",
    name: "Almaty, with love",
    avatar: media("mountains"),
    bio: "A city worth coming back to.\nPlaces, people and little discoveries.",
    posts: 346,
    followers: 18400,
    following: 187,
    verified: true,
    photos: [
      media("mountains"),
      media("city"),
      media("coffee"),
      ...gallery.slice(0, 6),
    ],
  },
  {
    handle: "adil.frames",
    name: "Adil",
    avatar: media("city"),
    bio: "See a little differently.\nStreet & travel photography",
    posts: 72,
    followers: 1260,
    following: 304,
    photos: [
      media("city"),
      media("interior"),
      media("coast"),
      ...gallery.slice(0, 6),
    ],
  },
  {
    handle: "aruzhan.jpg",
    name: "Aruzhan",
    avatar: media("flowers"),
    bio: "Finding beauty in everyday things. 🌷",
    posts: 35,
    followers: 780,
    following: 211,
    photos: [
      media("flowers"),
      media("coffee"),
      media("forest"),
      ...gallery.slice(0, 6),
    ],
  },
  {
    handle: "slow.mornings",
    name: "Slow mornings",
    avatar: media("coffee"),
    bio: "A little pause for your day.\nCoffee, light & everyday things.",
    posts: 164,
    followers: 8670,
    following: 148,
    photos: [
      media("coffee"),
      media("interior"),
      media("flowers"),
      ...gallery.slice(0, 6),
    ],
  },
];
// A fresh fictional copy for the live report walkthrough. Historical claims stay intact.
accounts.push({
  handle: "aigerim.k.backup",
  name: "Aigerim K.",
  avatar: media("aigerim"),
  bio: "New photographer page.\nPhoto sessions and bookings in Direct.",
  posts: 6,
  followers: 36,
  following: 2350,
  photos: gallery.slice(0, 6),
});

// Unlabelled fictional copy for the full walkthrough in the current web design.
accounts.push({
  handle: "aigerim.k.photo",
  name: "Aigerim K.",
  avatar: media("aigerim"),
  bio: "New photographer page.\nPhoto sessions, collaborations and bookings in Direct.",
  posts: 6,
  followers: 28,
  following: 2400,
  photos: gallery.slice(0, 6),
});

// Fresh fictional text-and-photo copy for the ML v2 browser walkthrough.
accounts.push({
  handle: "aigerim.k.copy",
  name: accounts[0].name,
  avatar: accounts[0].avatar,
  bio: accounts[0].bio,
  posts: 6,
  followers: 24,
  following: 2380,
  photos: gallery.slice(0, 6),
});

// Fictional contacts are reserved example data for the OCR/privacy walkthrough.
accounts.push({
  handle: "aigerim.k.vision",
  name: accounts[0].name,
  avatar: accounts[0].avatar,
  bio:
    accounts[0].bio +
    "\nEmail: studio.demo@example.com\nPhone: +1 202 555 0147",
  posts: 6,
  followers: 29,
  following: 2310,
  photos: gallery.slice(0, 6),
});

// Fresh fictional account for automatic image-redaction verification.
accounts.push({
  handle: "aigerim.k.safe",
  name: "Aigerim K.",
  avatar: media("aigerim"),
  bio: `${accounts[0].bio}\nEmail: studio.demo@example.com\nPhone: +1 202 555 0147`,
  posts: 6,
  followers: 29,
  following: 2310,
  photos: gallery.slice(0, 6),
});

// A fresh fictional copy for the complete English browser walkthrough.
accounts.push({
  handle: "aigerim.k.archive",
  name: accounts[0].name,
  avatar: accounts[0].avatar,
  bio: `${accounts[0].bio}\nEmail: studio.demo@example.com\nPhone: +1 202 555 0147`,
  posts: 6,
  followers: 29,
  following: 2310,
  photos: gallery.slice(0, 6),
});

export const accountByHandle = (handle: string) =>
  accounts.find((a) => a.handle === handle.replace(/^@/, ""));
accounts.push(...footballAccounts, ...creatorAccounts);
export const discoveryAccounts = [
  ...footballAccounts,
  ...creatorAccounts,
  ...accounts.filter(
    (a) => !footballAccounts.includes(a) && !creatorAccounts.includes(a),
  ),
];
export const posts: Post[] = [
  ...socialPosts,
  {
    id: "p-lake",
    account: "aigerim.k",
    image: media("lake"),
    location: "Somewhere closer to nature",
    caption:
      "Sometimes the best plan is to take a different path. 🌿\nI wish I could put this day on repeat.",
    likes: 1284,
    comments: 32,
    age: "2h",
    images: [media("lake"), media("mountains")],
  },
  {
    id: "p-coast",
    account: "madina.travels",
    image: media("coast"),
    location: "By the ocean",
    caption: "No schedule. Just the sound of waves and a little sunshine. ☀️",
    likes: 846,
    comments: 18,
    age: "4h",
  },
  {
    id: "p-copy",
    account: "aigerim.k.studio",
    image: media("lake"),
    location: "Astana, Kazakhstan",
    caption: "My favorite shots. Book a session in Direct ✨",
    likes: 16,
    comments: 3,
    age: "5h",
  },
  {
    id: "p-city",
    account: "adil.frames",
    image: media("city"),
    location: "On the move",
    caption: "Every city has its own rhythm. You just have to listen.",
    likes: 638,
    comments: 12,
    age: "7h",
  },
];
export function profilePost(account: Account, index: number): Post {
  return (
    posts.find(
      (post) =>
        post.account === account.handle && post.image === account.photos[index],
    ) ?? {
      id: `${account.handle}-${index}`,
      account: account.handle,
      image: account.photos[index],
      caption: "One of those moments worth keeping. 🤍",
      likes: 74 + index * 37,
      comments: 3 + index,
      location: account.location ?? "Memories",
      age: "3d",
    }
  );
}
export const reelPost: Post = {
  id: "reel-flowers",
  account: "aruzhan.jpg",
  image: media("flowers"),
  caption: "A little peace in your feed. 🌷",
  likes: 3842,
  comments: 64,
  age: "1d",
  location: "Little joys",
};
export const number = (value: number) =>
  new Intl.NumberFormat("en-US").format(value);
export const compact = (value: number) =>
  value >= 1_000_000
    ? `${(value / 1_000_000).toFixed(1).replace(".0", "")}M`
    : value >= 10000
      ? `${(value / 1000).toFixed(1).replace(".0", "")}K`
      : number(value);
