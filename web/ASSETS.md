# Demo media

Local avatars and wordmark reuse the user-authorized concept assets.

Navigation SVG geometry in `src/components/InstagramIcons.tsx` was copied from the
visible instagram.com UI on 2026-11-02 to match the user's requested design reference.
The account content remains fictional demo data; the user's feed and profile media
were not imported into the app.

Photos from Unsplash:
- https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=85
- https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=1200&q=85
- https://images.unsplash.com/photo-1449824913935-59a10b8d2000?auto=format&fit=crop&w=1200&q=85
- https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=1200&q=85
- https://images.unsplash.com/photo-1442512595331-e89e73853f31?auto=format&fit=crop&w=1200&q=85
- https://images.unsplash.com/photo-1494438639946-1ebd1d20bf85?auto=format&fit=crop&w=1200&q=85
- https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=85
- https://images.unsplash.com/photo-1490750967868-88aa4486c946?auto=format&fit=crop&w=1200&q=85

CC0 video: https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4

## Football fan profiles (0.9)

`public/media/football/` contains eight attributed player photographs and four
football atmosphere photos. `credits.json` records each source, author, license
and display-crop note; `public/photo-credits.html` exposes those attributions in
the site. Run `../scripts/fetch_football_media.py` from the project environment to
recreate the files. Commons photographs retain their per-image CC BY / CC BY-SA
licenses; the four generic photos use the Unsplash license. Source files are not
pixel-edited. These fictional fan accounts and authored captions do not represent
the public figures' real Instagram accounts, posts, statistics or endorsement.

Embla Carousel 8.6.0 and emoji-picker-react 5.1.4 are MIT open source packages.
Emoji render as native system glyphs. Picker code and the supplied English CLDR
search dataset are separate lazy chunks; emoji image assets are not fetched from
a third-party CDN.
