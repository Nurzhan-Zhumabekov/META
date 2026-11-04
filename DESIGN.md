# Instagram-style native web design

The current application uses HTML, CSS and React with the user's requested
Instagram visual language. [WEB_MIGRATION.md](WEB_MIGRATION.md) defines scope and
acceptance. The earlier Flutter design is archived in
[docs/LEGACY_FLUTTER_DESIGN.md](docs/LEGACY_FLUTTER_DESIGN.md).

On 2026-11-02 the current signed-in instagram.com website was inspected live in
Chrome. Desktop uses its 72px icon rail, vertically centered navigation, a 470px
feed, 82px story rings and a right recommendations column. The floating messages
dock, icon geometry, colors, typography and spacing follow that live reference.
Search opens Explore with a centered search field and working account results.

Profile content is 74% of the viewport; its header is at most 680px, with a 150px
avatar image and actions below the biography. Desktop uses four media columns and
icon-only tabs. Phones use three columns, profile stats next to the avatar, actions
under the biography and six bottom navigation controls. Responsive checks include
the original's 1707px desktop and 390px phone widths, plus the 320px edge case.
There is no simulated OS status bar or device frame.

White surfaces, near-black text, subtle gray borders, gradient story rings,
outline icons and the supplied wordmark connect the screens. Media is bundled
locally; see [web/ASSETS.md](web/ASSETS.md). Raster content is limited to photos,
video and the wordmark. Layout, text, navigation and dialogs are native DOM.

Reporting lives in profile and post menus. Reporters see reason selection, evidence
upload, analysis progress, a receipt and review status. Reviewers see both private
screenshots, provider observations, separate ML factors and explicit decisions.
Only human confirmation creates the profile label. Scores do not prove identity.

Native dialogs contain focus, dismiss with Escape and restore focus to their
opener. Forms have labels and inline validation. Icon controls and navigation have
accessible names. CSS supports visible focus and reduced motion. Verification
covers desktop, tablet, phone and 320px layouts. Full WCAG certification is not claimed.

Social interactions are local demo behavior. Report evidence and decisions persist
in the local backend. This concept does not log in to or change the real Instagram.

Version 0.9 adds 16 profiles and 16 feed posts without changing this shell.
Football communities use fan handles and a visible category, with real attributed
photographs and fictional statistics. Explore has horizontally scrollable topic
filters. Post carousels use Embla with swipe, arrow keys, endpoint controls,
clickable indicators and reduced-motion support. Comments and Direct open a
English emoji picker in a focus-contained native dialog; its code/data are lazy.
The first feed image loads eagerly; later post images remain lazy. The additional
interaction styles live in `web/src/social-polish.css` after the reference styles.
