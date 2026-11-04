# Native web migration

## Goal
Replace the Flutter frontend with a responsive React web app. Match Instagram's
visual language and familiar desktop/mobile navigation, with the impersonation
reporting feature integrated into profiles and post menus.

## Scope
- React + TypeScript + Vite; semantic HTML and a dedicated CSS design system.
- Feed, stories, profile grids, search, explore, local demo interactions and messages.
- Real Meta screenshot analysis and independent profile ML through the existing API.
- Human moderation, protected evidence images and server-side reviewer sessions.
- Same-origin `/api`, one local web server, deterministic build and launch script.

## Non-goals
Changes to the real Instagram service, Instagram login/password collection, automatic
account suspension, public deployment, and production identity verification.

## Design contract
White surfaces, near-black type, quiet gray borders, compact controls, generous media,
Instagram-style outline icons, gradient story rings and the supplied Instagram wordmark.
Updated against the signed-in instagram.com site on 2026-11-02: desktop and tablet
use the current 72px icon rail; the centered media feed is 470px with 82px story
rings and desktop recommendations. Profiles use a 680px header, actions below the
bio, icon-only tabs and four grid columns. Phones use three profile columns and six
bottom navigation items. A floating messages dock matches the desktop reference.
Reporting uses familiar action sheets and dialogs. Technical details stay in reviewer
evidence views; users see clear progress, recoverable errors and report status.

## Plan and acceptance
1. Add failing behavior tests for upload/report boundaries, reviewer sessions and
   protected evidence; preserve the old API regression suite.
2. Implement the web shell and native components, with accessible dialogs and forms.
3. Connect upload -> Meta + ML -> under review -> human decision -> profile label.
4. Build, run and verify the same new complaint through the browser. Check desktop,
   768px and 390px/320px widths, keyboard dialogs and unavailable/error states.
5. Make web the documented default. Keep earlier source/history recoverable.

The Meta key and reviewer secret must be absent from all frontend source and built
assets. Old claims remain readable; existing confirmed statuses are preserved.
