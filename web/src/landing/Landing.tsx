import { useState } from "react";
import { Icon } from "../components/Icon";
import {
  LiquidNavbar,
  NimbusIcons,
} from "../components/ui/liquid-glass-navbar";
import { TiltedGridHero } from "../components/ui/tilted-grid-hero";
import { Workflow } from "./Workflow";
import { useLiveServices } from "./use-live-services";

const gallery = [
  { src: "/media/lake.jpg" },
  { src: "/media/flowers.jpg" },
  { src: "/rejected-report-demo/12-profile-without-label.png" },
  { src: "/media/coffee.jpg" },
  { src: "/media/coast.jpg" },
  { src: "/media/forest.jpg" },
  { src: "/media/city.jpg" },
];
const navItems = [
  {
    label: "Overview",
    href: "#overview",
    icon: NimbusIcons.home,
    fx: "glow" as const,
  },
  {
    label: "How it works",
    href: "#how-it-works",
    icon: NimbusIcons.globe,
    fx: "spin" as const,
  },
  {
    label: "Privacy",
    href: "#privacy",
    icon: NimbusIcons.drop,
    fx: "drop" as const,
  },
  {
    label: "Demo",
    href: "#demo",
    icon: NimbusIcons.plane,
    fx: "plane" as const,
  },
];
function MirrorMark() {
  return (
    <svg
      viewBox="0 0 36 36"
      width="34"
      height="34"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M9 7h8v22H9a6 6 0 0 1-6-6V13a6 6 0 0 1 6-6Z"
        stroke="currentColor"
        strokeWidth="2.5"
      />
      <path
        d="M27 7h-8v22h8a6 6 0 0 0 6-6V13a6 6 0 0 0-6-6Z"
        stroke="currentColor"
        strokeWidth="2.5"
      />
      <path
        d="m11 18 5 5 10-10"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
export function Landing() {
  const [paused, setPaused] = useState(false);
  const services = useLiveServices();
  const allReady =
    services.phase === "loaded" &&
    services.checks.every((check) => check.ready);
  const status =
    services.phase === "loading"
      ? "Checking live services"
      : services.phase === "offline"
        ? "Live services unavailable"
        : allReady
          ? "All systems ready"
          : "Some services need attention";
  return (
    <div className="mirror-landing">
      <a className="mc-skip-link" href="#main-content">
        Skip to content
      </a>
      <header className="mc-header">
        <a className="mc-brand" href="#overview" aria-label="MirrorCheck home">
          <MirrorMark />
          <span>
            mirrorcheck<span className="mc-brand-dot">.</span>
          </span>
        </a>
        <LiquidNavbar
          items={navItems}
          tone="light"
          compact={false}
          sound={false}
          className="mc-liquid-nav"
        />
        <a href="/" className="mc-header-action">
          Open prototype
          <Icon name="external" size={15} />
        </a>
      </header>
      <main id="main-content">
        <TiltedGridHero
          role="region"
          id="overview"
          images={gallery}
          speed={6.5}
          tileHeight={32}
          aspectRatio={0.83}
          gap={8}
          axis={74}
          curve={68}
          fade={13}
          paused={paused}
          className="mc-hero"
          aria-labelledby="hero-title"
        >
          <div className="mc-hero-copy">
            <span className="mc-eyebrow">
              <span className="mc-live-dot" /> A LITTLE MORE CLARITY. A LOT MORE
              TRUST.
            </span>
            <h1 id="hero-title">
              A familiar face. <br />
              <em>A clearer signal.</em>
            </h1>
            <p>
              Copied profiles can look convincing.
              <br />
              Turn a second look into evidence, with AI that helps
              <br className="mc-desktop-break" /> and a human who decides.
            </p>
            <div className="mc-hero-actions">
              <a href="/" className="mc-button mc-button-primary">
                Try MirrorCheck
                <Icon name="external" size={17} />
              </a>
              <a href="/demo-video.html" className="mc-button mc-button-video">
                <span className="mc-play-circle">
                  <Icon name="play" size={12} filled />
                </span>
                Watch the 3-min demo
              </a>
            </div>
          </div>
          <div className="mc-orbit-caption">
            <span className="mc-orbit-line" />
            <span>
              Similar content.
              <br />
              <strong>Not always the same story.</strong>
            </span>
          </div>
          <div className="mc-hero-bottom">
            <span>
              Made for familiar feeds.
              <br />
              <strong>Built for a little more trust.</strong>
            </span>
            <button
              type="button"
              onClick={() => setPaused((value) => !value)}
              aria-label={
                paused ? "Resume gallery animation" : "Pause gallery animation"
              }
              className="mc-motion-button"
            >
              {paused ? (
                <Icon name="play" size={13} />
              ) : (
                <span className="mc-pause-icon" aria-hidden="true" />
              )}
              <span>{paused ? "Resume motion" : "Pause motion"}</span>
            </button>
            <a href="#how-it-works">
              Take a closer look<span aria-hidden="true">↓</span>
            </a>
          </div>
        </TiltedGridHero>
        <section
          className="mc-technology"
          aria-label="Technology behind the review"
        >
          <span>
            THE TOOLS BEHIND
            <br />
            <strong>A BETTER SECOND LOOK</strong>
          </span>
          <div>
            <span className="mc-meta-logo" aria-hidden="true">
              ∞
            </span>
            Meta AI
          </div>
          <div>
            <Icon name="search" size={21} />
            PaddleOCR
          </div>
          <div>
            <Icon name="grid" size={20} />
            imagededup
          </div>
          <div>
            <Icon name="shield" size={21} />
            Presidio
          </div>
          <div>
            <span className="mc-ml-logo" aria-hidden="true">
              ML
            </span>
            Independent signals
          </div>
        </section>
        <Workflow />
        <section
          className="mc-privacy mc-section"
          id="privacy"
          aria-labelledby="privacy-heading"
        >
          <div className="mc-privacy-symbol">
            <Icon name="shield" size={32} />
            <span>
              <Icon name="check" size={13} />
            </span>
          </div>
          <div>
            <span className="mc-kicker">02 / CARE IN EVERY CHECK</span>
            <h2 id="privacy-heading">
              A little less exposure.
              <br />
              <em>A little more peace of mind.</em>
            </h2>
            <p>
              Detected emails and phone numbers are masked locally
              <br className="mc-desktop-break" /> before screenshots reach Meta
              AI. You review the prepared images.
            </p>
            <span className="mc-privacy-note">
              Automatic detection can miss details. Always check the preview.
            </span>
          </div>
          <div
            className="mc-redaction-demo"
            aria-label="Illustration of masked contact details"
          >
            <span>
              <Icon name="shield" size={13} /> READY FOR REVIEW
            </span>
            <div>
              Contact details
              <span className="mc-mask-line" />
            </div>
            <div>
              Phone number
              <span className="mc-mask-line mc-mask-short" />
            </div>
            <footer>
              <span className="mc-live-dot" /> Masked before sending
            </footer>
          </div>
        </section>
        <section
          className="mc-demo-section"
          id="demo"
          aria-labelledby="demo-heading"
        >
          <div className="mc-demo-inner">
            <div className="mc-demo-heading">
              <span className="mc-kicker">03 / SEE IT FOR YOURSELF</span>
              <h2 id="demo-heading">
                One report.
                <br />
                <em>Two possible outcomes.</em>
              </h2>
              <p>
                A warning when the evidence supports it.
                <br />A dismissal when it does not.
              </p>
            </div>
            <a
              href="/demo-video.html"
              className="mc-video-preview"
              aria-label="Watch the full English demo"
            >
              <img
                src="/demo-video-poster.jpg"
                alt="Recorded MirrorCheck demonstration with English narration"
                loading="lazy"
                width="1920"
                height="1080"
              />
              <span className="mc-video-overlay">
                <span className="mc-video-play">
                  <Icon name="play" filled size={22} />
                </span>
                <span>
                  <strong>The full story, in three minutes.</strong>
                  <small>English narration · recorded demonstration</small>
                </span>
                <span className="mc-video-duration">03:00</span>
              </span>
            </a>
            <a
              href="/rejected-report-walkthrough.html"
              className="mc-dismissed-link"
              aria-label="Explore the dismissed report"
            >
              <span className="mc-dismissed-icon">
                <Icon name="check" size={19} />
              </span>
              <span>
                <small>THE OTHER SIDE OF A GOOD REVIEW</small>
                <strong>Explore the dismissed report</strong>
                <span>
                  A fictional ordinary profile. A report dismissed. No warning
                  added.
                </span>
              </span>
              <Icon name="external" size={22} />
            </a>
          </div>
        </section>
        <section
          className="mc-availability mc-section"
          aria-label="Service availability"
        >
          <div>
            <span className={`mc-live-dot ${!allReady ? "is-pending" : ""}`} />
            <strong>{status}</strong>
            <span>Live local service status</span>
          </div>
          <ul>
            {services.checks.map((check) => (
              <li key={check.name} data-ready={check.ready}>
                <Icon name={check.ready ? "check" : "warning"} size={13} />
                {check.name}
                {!check.ready ? " unavailable" : ""}
              </li>
            ))}
          </ul>
          <p>
            {services.phase === "offline"
              ? "The recorded demos are still available while live services are offline."
              : "Availability checks do not submit a report or make a paid model request."}
          </p>
        </section>
      </main>
      <footer className="mc-footer">
        <a className="mc-brand" href="#overview">
          <MirrorMark />
          <span>
            mirrorcheck<span className="mc-brand-dot">.</span>
          </span>
        </a>
        <p>A second look. A human decision.</p>
        <nav aria-label="Project links">
          <a href="https://github.com/Nurzhan-Zhumabekov/META">
            Source code
            <Icon name="external" size={12} />
          </a>
          <a href="/photo-credits.html">Credits</a>
          <a href="/review">Moderator access</a>
        </nav>
        <details>
          <summary>About this prototype</summary>
          <p>
            MirrorCheck is an unofficial Instagram-style hackathon concept using
            fictional profiles and stock photography. It does not modify
            Instagram. Text-reuse ML uses synthetic training data; real-account
            performance remains unvalidated. Screenshots and model signals do
            not prove ownership. The video is an edited sequence of authentic
            browser captures with synthesized English narration.
          </p>
        </details>
        <span className="mc-copyright">
          © 2026 MirrorCheck · An independent feature concept.
        </span>
      </footer>
    </div>
  );
}
