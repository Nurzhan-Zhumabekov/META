# MirrorCheck — AI-Assisted Impersonation Review

Working submission title. This packet does not rename the application or claim an official affiliation.

## One-line pitch (100 characters)

Turn suspected profile copies into reviewable evidence with Meta AI, local ML and contact redaction.

## Main project description (268 words)

A copied profile can look convincing long before anyone checks it. MirrorCheck helps users document suspected impersonation and gives reviewers a structured path from complaint to decision.

Built as an unofficial Instagram-style web prototype, it starts inside the profile flow. A reporter attaches screenshots of the original and suspected copy. PaddleOCR extracts editable profile fields, while imagededup flags matching image regions. The reporter reviews and corrects the extracted data before submitting.

Before screenshots reach Meta AI, a local Presidio pipeline detects email and phone lines and covers them with opaque masks. The preview, provider-prepared image and stored reviewer evidence are checked for matching bytes. Processing failures block the external image request.

Meta Muse Spark, accessed through the backend with muse-spark-1.3, compares the processed screenshots and returns structured similarities, differences, limitations and a review recommendation. Two local ML models add separate signals: text reuse between profiles and auxiliary spam patterns in profile statistics. Avatar presence is excluded from the profile model, so an ordinary default avatar cannot change that model's score by itself.

The report stays under review until a separate moderator action. In the completed fictional demo, the moderator confirms impersonation and the profile warning persists after a reload. The English interface demonstrates the whole journey in context.

MirrorCheck is a working local prototype, with a real Meta API run and a recorded end-to-end browser walkthrough. It does not connect to or modify the real Instagram service. Screenshots and model scores cannot establish ownership; the pair model uses synthetic training data, and performance on real account-copy cases remains unvalidated. The next step is consented evaluation and production hardening.

## Short description (97 words)

MirrorCheck is an unofficial Instagram-style web prototype for reporting suspected profile copies. Users attach two screenshots, review PaddleOCR fields, inspect image matches and preview contact details masked locally with Presidio before Meta AI receives images. Meta Muse Spark returns structured visual evidence; local ML adds separate text-reuse and profile spam-pattern signals. A moderator reviews the evidence and explicitly decides whether to add a persistent profile warning. A real Meta API run demonstrates the complete workflow with fictional accounts. The prototype does not modify Instagram, and its scores do not prove ownership. Real-world copy-detection performance still requires evaluation.

## Compact description (48 words)

MirrorCheck combines Meta Muse Spark, editable OCR, image deduplication and local contact redaction to help review suspected profile copies. Reports stay under review until a separate moderator decision adds a persistent warning. The working Instagram-style web demo uses fictional accounts; it does not modify Instagram or establish ownership.

## Recommended positioning

- Track recommendation: Indie developer, if this matches the actual registration and team eligibility.
- Theme recommendation: Build for Your World.
- Category: AI-assisted trust and safety / social-platform feature prototype.
- Submission status: working local prototype; this packet is a draft for the owner to review and submit.

The final authenticated form's field labels and character limits were not accessible in this session. Choose the variant that fits the actual field; the word counts above are measured, not organizer limits.
