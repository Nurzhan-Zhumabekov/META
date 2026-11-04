import type { Account, Post } from "./types";

const photo = (name: string) => `/media/football/${name}.jpg`;
const base = (name: string) => `/media/${name}.jpg`;
const players = [
  [
    "ronaldo",
    "cristiano.fan",
    "Cristiano Ronaldo",
    "Portugal",
    "Work. Character. Football. 🇵🇹",
  ],
  ["messi", "leomessi.fan", "Lionel Messi", "Argentina", "Football is joy. 🇦🇷"],
  [
    "mbappe",
    "k.mbappe.fan",
    "Kylian Mbappé",
    "France",
    "Speed is just the beginning. 🇫🇷",
  ],
  [
    "haaland",
    "erling.haaland.fan",
    "Erling Haaland",
    "Norway",
    "It all starts on the training ground. 🇳🇴",
  ],
  [
    "bellingham",
    "jude.bellingham.fan",
    "Jude Bellingham",
    "England",
    "Big games. Bigger moments. 🏟️",
  ],
  [
    "salah",
    "mo.salah.fan",
    "Mohamed Salah",
    "Egypt",
    "Stories written by football. 🇪🇬",
  ],
  ["neymar", "neymarjr.fan", "Neymar Jr.", "Brazil", "Play beautifully. 🇧🇷"],
  [
    "vini",
    "vinijr.fan",
    "Vinícius Júnior",
    "Brazil",
    "Anything is possible with a ball. 🇧🇷",
  ],
] as const;

export const footballAccounts: Account[] = players.map(
  ([slug, handle, name, location, bio], i) => ({
    handle,
    name,
    location,
    bio: `${bio}\nA fan archive of favorite moments. ⚽\nPhoto sources and credits below ↓`,
    avatar: photo(slug),
    category: "football",
    profileLabel: "Fan community",
    posts: 84 + i * 17,
    followers: 68000 + i * 7310,
    following: 120 + i * 13,
    highlights: ["Matchday", "Training", "Moments"],
    photos: [
      photo(slug),
      photo("stadium"),
      photo("matchday"),
      photo("pitch"),
      photo("training"),
      photo(slug),
    ],
  }),
);

export const creatorAccounts: Account[] = [
  [
    "dana.wanders",
    "Dana | Travel diaries",
    "travel",
    "mountains",
    "Travel",
    "A small backpack. A big world.\nMountains, cities and routes to inspire.",
  ],
  [
    "timur.outdoors",
    "Timur",
    "travel",
    "forest",
    "Digital creator",
    "Life is better outside.\nHiking trails and weekends without an alarm.",
  ],
  [
    "saule.film",
    "Saule | Film & light",
    "photography",
    "interior",
    "Photographer",
    "Slowing down to see more.\nFilm, light and faces.",
  ],
  [
    "urban.astana",
    "Urban Astana",
    "photography",
    "city",
    "Photographer",
    "A fresh perspective on a favorite city.\nThe architecture and people of Astana.",
  ],
  [
    "aliya.builds",
    "Aliya | Design & code",
    "technology",
    "coffee",
    "Digital creator",
    "Ideate, design, build.\nInterfaces, side projects & good coffee.",
  ],
  [
    "dias.codes",
    "Dias",
    "technology",
    "interior",
    "Developer",
    "From an idea to a first release.\nWeb, open source and development notes.",
  ],
  [
    "weekend.journal",
    "Weekend Journal",
    "lifestyle",
    "coast",
    "Personal blog",
    "A place for little discoveries.\nGood coffee, new places and long walks.",
  ],
  [
    "matchday.club",
    "Matchday Club",
    "football",
    "football/pitch",
    "Sports community",
    "Football brings us together. ⚽\nStadium atmosphere and local matches.",
  ],
].map(([handle, name, category, avatar, profileLabel, bio], i) => ({
  handle,
  name,
  category: category as Account["category"],
  profileLabel,
  bio,
  avatar: base(avatar),
  posts: 42 + i * 23,
  followers: 4800 + i * 2560,
  following: 280 + i * 31,
  highlights:
    category === "technology"
      ? ["Projects", "Process", "Behind the scenes"]
      : ["Moments", "On the road", "Inspiration"],
  photos: [
    base(avatar),
    base("lake"),
    base("coffee"),
    base("forest"),
    base("coast"),
    base("city"),
  ],
}));

const captions = [
  "These are the moments we love football for. ⚽🔥\nFan archive: the energy that stays with you after the final whistle.",
  "When the ball says more than words ever could. ✨⚽\nThe best part of football is sharing its moments with the world.",
  "The first step makes the difference. Speed, courage and love for the game. 💨",
  "Behind every great goal are hundreds of repetitions. Another session, another step. 💪",
  "Some emotions cannot fit into ninety minutes. 🏟️🤍",
  "From the first touch to the final whistle. Football is a feeling. ❤️",
  "A little Brazilian magic in your feed. 🇧🇷✨ #jogabonito",
  "Dream big. Play boldly. ⚽✨",
];
export const socialPosts: Post[] = [
  ...footballAccounts.map((a, i) => ({
    id: `football-${players[i][0]}`,
    account: a.handle,
    image: a.photos[0],
    images: [a.photos[0], a.photos[1], a.photos[3]],
    caption: captions[i],
    likes: 14520 + i * 4217,
    comments: 148 + i * 27,
    age: `${i + 1}h`,
    location: a.location ?? "Football",
  })),
  ...creatorAccounts.map((a, i) => ({
    id: `creator-${a.handle}`,
    account: a.handle,
    image: a.photos[0],
    images: [a.photos[0], a.photos[1]],
    caption: [
      "A place I want to return to. Saving this route for next time. 🏔️",
      "Chose a trail over notifications today. Best decision of the week. 🌲",
      "The light changes every second. Sometimes all you need is to stop. 📷",
      "The city is waking up. I love the moment when the streets are still quiet.",
      "A little progress every day adds up. Building a new interface today. ✨",
      "Starting the morning with coffee and an interesting pull request. ☕💻",
      "A good weekend does not need a big plan. Just a little time for yourself. ☀️",
      "Our weekends start on the pitch. Who is joining us next Saturday? ⚽",
    ][i],
    likes: 843 + i * 317,
    comments: 24 + i * 9,
    age: `${i + 2}h`,
    location: a.location ?? "Everyday moments",
  })),
];
