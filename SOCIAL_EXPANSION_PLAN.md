# Instagram social expansion

Goal: fill the existing web shell with football fan profiles and richer content;
add useful open source interactions and refine feed, search, profiles and Direct.

Scope: locally bundled football/creator media, explicit demo/fan identities,
topic discovery, relevant recommendations, working follower/following lists,
Embla swipe/keyboard post carousels, and a lazy-loaded emoji picker in comments
and messages. Keep the Instagram visual reference and responsive layouts.

Non-goals: import live Instagram accounts/statistics, publish to Instagram,
change AI/moderation contracts, or label real public figures as impersonators.

Acceptance: new users appear in stories/feed/search/messages/profile grids;
topic filters and follows work; a carousel supports swipe and discrete navigation;
selected emoji reach the actual text field; original claim labels and redaction
reporting still work; desktop and phone have no horizontal overflow; relevant
tests, build, browser screenshots and unchanged-claims verification pass.

Plan: failing behavior tests -> data/media -> interactive components -> visual
refinement -> build/tests -> desktop and phone browser verification.
