import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

afterEach(cleanup);
// Browser layout observers are unavailable in jsdom. Carousel controls remain
// testable without layout; real drag/swipe is verified in the browser.
if (!window.matchMedia)
  window.matchMedia = () => ({
    matches: false,
    addEventListener() {},
    removeEventListener() {},
    addListener() {},
    removeListener() {},
    dispatchEvent() {
      return false;
    },
    media: "",
    onchange: null,
  });
if (!globalThis.ResizeObserver)
  globalThis.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
if (!globalThis.IntersectionObserver)
  globalThis.IntersectionObserver = class {
    root = null;
    rootMargin = "0px";
    scrollMargin = "0px";
    thresholds = [0];
    constructor(private callback: IntersectionObserverCallback) {}
    observe(target: Element) {
      const rect = target.getBoundingClientRect();
      this.callback(
        [
          {
            target,
            isIntersecting: true,
            intersectionRatio: 1,
            time: performance.now(),
            rootBounds: rect,
            boundingClientRect: rect,
            intersectionRect: rect,
          },
        ],
        this,
      );
    }
    unobserve() {}
    disconnect() {}
    takeRecords() {
      return [];
    }
  };
