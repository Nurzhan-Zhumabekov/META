# English interface

Goal: make all application-owned interface copy and demo social content English.
Scope: navigation, feed, stories, profiles, discovery, messages, comments, composer,
emoji search, report/inspection/analysis/reviewer screens, accessible names,
validation and service messages, English number/date formatting, and HTML metadata.
Translate historical analysis for display without changing stored evidence or
moderation records. Keep model features, API contracts and privacy behavior intact.

Acceptance: English interface regression checks and existing behavior tests pass;
production build succeeds; key desktop/mobile routes and report/review entry
points show English; existing claims/evidence remain unchanged.

Plan: failing language checks -> English copy/content -> historical display and
service messages -> existing tests/build -> desktop/mobile browser verification.
