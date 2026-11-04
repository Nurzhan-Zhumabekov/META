# Screenshot-matched Instagram feature concept

## Goal and source
Match the 588 x 1280 iPhone screenshot supplied by the user on 2026-10-27.
The supplied screenshot takes priority over the previous generic Instagram layout.

## Scope and design contract
- Centered Instagram wordmark; plus left and heart right.
- Large circular stories with the names and media from the reference.
- Collaboration header, verified symbol and a 4:5 portrait post.
- Floating white bottom capsule: Home, Reels, Messages (1), Search, Profile.
- Browser-only simulated iOS status line; real mobile builds use the OS status bar.
- Account reporting in post actions and the profile; API-driven statuses remain real.

## Non-goals
Real Instagram integration, authentication, publishing and Reels playback. Meta analysis is implemented separately; live verification requires a server API key.

## Acceptance and verification
- Reference proportions at 390 x 849; no horizontal overflow at 320 and 430 pixels.
- Post and profile actions open the correct evidence form.
- Missing evidence validation, status updates, likes and saves keep working.
- Flutter tests, analyzer and release web build pass.

## Assets
The wordmark, story thumbnails, collaboration avatars and first post image are extracted
from the user-supplied screenshot for this local concept. They are bundled in assets/reference/.
Only imagery is raster content: the layout, controls, post header, stories, navigation,
status line, menus, scrolling and reporting flow are Flutter widgets.
The 1/2 mark belongs to the supplied first-post image; this demo does not implement its carousel.
Subsequent demo posts use Picsum. Other profile avatars come from Pravatar.
Grand Hotel remains bundled with its SIL OFL license from the previous iteration.
