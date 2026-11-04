# MirrorCheck landing page

Goal: make the existing demo entry page a polished introduction that explains the feature and opens the working prototype or either recorded outcome.

Scope: combine the supplied Liquid Navbar water/glass navigation and the supplied Tilted Grid Hero curved image band. Adapt both to React 19, TypeScript and the existing CSS stack in `web/src/components/ui/`, preserving author attribution. Build a separate Vite HTML entry at `/demo-guide.html` with isolated styles, local media, live availability, a three-step explanation and both outcome links.

The Instagram application routes, report API, saved decisions and evidence remain outside this change. No additional UI framework or remote photo dependency is needed.

Design: warm white, ink typography, an editorial serif accent, restrained orange actions and green availability indicators. The gallery is decorative; primary actions and explanations stay readable. Navigation labels remain available on small screens. Animations honor reduced motion and can be paused; background/offscreen animation stops.

Acceptance: both supplied effects are visible; all prototype/video/walkthrough links work; workflow controls work by keyboard; loading and unavailable service states are truthful; no horizontal overflow at 320, 768, 1024 and 1440px; the main social application still builds and passes its existing tests.

Implementation slices: (1) regression tests for links, service states, workflow controls and keyboard navigation; (2) adapt the two provided primitives; (3) compose and style the landing entry; (4) build and inspect desktop/mobile/reduced-motion behavior in the browser; (5) verify the app and publish the change.
