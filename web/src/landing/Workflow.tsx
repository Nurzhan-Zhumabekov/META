import { useId, useRef, useState } from "react";
import { Icon } from "../components/Icon";

const steps = [
  {
    name: "Report",
    title: "A second look starts here.",
    body: "Something feels familiar? Add screenshots of the original and the suspected copy. Review the details we extract before sending.",
  },
  {
    name: "Compare",
    title: "Different signals. One clear view.",
    body: "Meta AI reviews the visuals. Independent ML checks text reuse and profile patterns. You see the matches, differences and limitations together.",
  },
  {
    name: "Decide",
    title: "A person makes the call.",
    body: "A moderator reviews the evidence and confirms or dismisses the report. A warning appears only after confirmation.",
  },
];
export function Workflow() {
  const [active, setActive] = useState(0);
  const buttons = useRef<(HTMLButtonElement | null)[]>([]);
  const id = useId();
  const step = steps[active];
  return (
    <section
      className="mc-workflow mc-section"
      id="how-it-works"
      aria-labelledby="workflow-heading"
    >
      <div className="mc-section-heading">
        <span className="mc-kicker">01 / A BETTER WAY TO CHECK</span>
        <h2 id="workflow-heading">
          Less guesswork.
          <br />
          <em>More perspective.</em>
        </h2>
        <p>
          From a suspicious profile to a thoughtful decision.
          <br />
          Three steps, with a human at the heart.
        </p>
      </div>
      <div className="mc-workflow-layout">
        <div
          className="mc-step-list"
          role="tablist"
          aria-label="How MirrorCheck works"
          aria-orientation="vertical"
        >
          {steps.map((item, index) => (
            <button
              key={item.name}
              ref={(el) => {
                buttons.current[index] = el;
              }}
              type="button"
              role="tab"
              aria-label={`0${index + 1} ${item.name}`}
              id={`${id}-tab-${index}`}
              aria-controls={`${id}-panel`}
              aria-selected={index === active}
              tabIndex={index === active ? 0 : -1}
              onClick={() => setActive(index)}
              onKeyDown={(event) => {
                if (
                  ![
                    "ArrowDown",
                    "ArrowUp",
                    "ArrowRight",
                    "ArrowLeft",
                    "Home",
                    "End",
                  ].includes(event.key)
                )
                  return;
                event.preventDefault();
                const next =
                  event.key === "Home"
                    ? 0
                    : event.key === "End"
                      ? 2
                      : (index +
                          (["ArrowDown", "ArrowRight"].includes(event.key)
                            ? 1
                            : -1) +
                          3) %
                        3;
                setActive(next);
                buttons.current[next]?.focus();
              }}
            >
              <span className="mc-step-number">0{index + 1}</span>
              <span>{item.name}</span>
              <Icon name="external" size={17} />
            </button>
          ))}
          <p className="mc-step-note">
            <Icon name="shield" size={17} />
            Evidence guides the review.
            <br />
            It never replaces the reviewer.
          </p>
        </div>
        <div
          className="mc-workflow-panel"
          role="tabpanel"
          id={`${id}-panel`}
          aria-labelledby={`${id}-tab-${active}`}
          tabIndex={0}
        >
          <div className="mc-panel-top">
            <span>
              <span className="mc-live-dot" /> EXAMPLE REVIEW
            </span>
            <span>0{active + 1} / 03</span>
          </div>
          <h3>{step.title}</h3>
          <p>{step.body}</p>
          {active === 0 ? (
            <div className="mc-profile-pair">
              <div className="mc-mini-profile">
                <img src="/media/aigerim.jpg" width="48" height="48" alt="" />
                <strong>aigerim.k</strong>
                <span>Original profile</span>
                <div className="mc-mini-photos">
                  <img src="/media/lake.jpg" alt="" />
                  <img src="/media/forest.jpg" alt="" />
                  <img src="/media/coffee.jpg" alt="" />
                </div>
              </div>
              <span className="mc-compare-mark">
                <Icon name="search" size={21} />
              </span>
              <div className="mc-mini-profile">
                <img src="/media/flowers.jpg" width="48" height="48" alt="" />
                <strong>aruzhan.jpg</strong>
                <span>Reported profile</span>
                <div className="mc-mini-photos">
                  <img src="/media/flowers.jpg" alt="" />
                  <img src="/media/coffee.jpg" alt="" />
                  <img src="/media/lake.jpg" alt="" />
                </div>
              </div>
            </div>
          ) : active === 1 ? (
            <div className="mc-signal-list">
              <div>
                <span className="mc-signal-icon">
                  <Icon name="grid" size={18} />
                </span>
                <span>
                  <strong>Visual similarities</strong>
                  <small>Meta AI + photo comparison</small>
                </span>
                <span className="mc-result-tag">For review</span>
              </div>
              <div>
                <span className="mc-signal-icon">
                  <Icon name="search" size={18} />
                </span>
                <span>
                  <strong>Text reuse & profile patterns</strong>
                  <small>Two independent ML signals</small>
                </span>
                <span className="mc-result-tag">Separate checks</span>
              </div>
              <div>
                <span className="mc-signal-icon">
                  <Icon name="shield" size={18} />
                </span>
                <span>
                  <strong>Contact details</strong>
                  <small>Detected regions masked locally</small>
                </span>
                <span className="mc-result-tag is-green">Before sending</span>
              </div>
            </div>
          ) : (
            <div className="mc-decision-example">
              <span className="mc-decision-check">
                <Icon name="check" size={24} />
              </span>
              <div>
                <strong>Report dismissed</strong>
                <p>Different identities. Insufficient grounds for a warning.</p>
              </div>
              <span className="mc-result-tag is-green">No label added</span>
            </div>
          )}
          <div className="mc-panel-foot">
            <Icon name="clock" size={14} />
            <span>
              Illustrative review · fictional profiles · shared photos do not
              prove identity
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
