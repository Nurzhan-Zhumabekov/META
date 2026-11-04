import { useCallback, useEffect, useState } from "react";
import useEmblaCarousel from "embla-carousel-react";
import { Icon } from "./Icon";

export function PostCarousel({
  images,
  caption,
  id,
  priority = false,
  onDoubleClick,
}: {
  images: string[];
  caption: string;
  id: string;
  priority?: boolean;
  onDoubleClick: () => void;
}) {
  const [viewport, api] = useEmblaCarousel({
    loop: false,
    align: "start",
    duration: 24,
    breakpoints: { "(prefers-reduced-motion: reduce)": { duration: 0 } },
  });
  const [index, setIndex] = useState(0);
  useEffect(() => {
    if (!api) return;
    const sync = () => {
      // A hidden/zero-width viewport cannot measure slides until reInit.
      if (api.scrollSnapList().length === images.length)
        setIndex(api.selectedScrollSnap());
    };
    api.on("select", sync);
    api.on("reInit", sync);
    return () => {
      api.off("select", sync);
      api.off("reInit", sync);
    };
  }, [api, images.length]);
  const move = useCallback(
    (next: number) => {
      const target = Math.max(0, Math.min(images.length - 1, next));
      setIndex(target);
      api?.scrollTo(target);
    },
    [api, images.length],
  );
  return (
    <div
      className="post-media swipe-carousel"
      role="region"
      aria-roledescription="carousel"
      aria-label={`Post photos ${id}`}
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
          e.preventDefault();
          move(index + (e.key === "ArrowRight" ? 1 : -1));
        }
      }}
      onDoubleClick={onDoubleClick}
    >
      <div className="carousel-viewport" ref={viewport}>
        <div className="carousel-track">
          {images.map((image, i) => (
            <div
              className="carousel-slide"
              key={`${image}-${i}`}
              role="group"
              aria-roledescription="slide"
              aria-label={`${i + 1} of ${images.length}`}
              aria-hidden={i !== index}
            >
              <img
                src={image}
                alt={i === 0 ? caption : `${caption} · photo ${i + 1}`}
                loading={priority && i === 0 ? "eager" : "lazy"}
                fetchPriority={priority && i === 0 ? "high" : "auto"}
                draggable={false}
              />
            </div>
          ))}
        </div>
      </div>
      {images.length > 1 && (
        <>
          <span className="carousel-count" aria-live="polite">
            {index + 1} / {images.length}
          </span>
          <button
            type="button"
            className="carousel-prev carousel-control"
            aria-label="Previous photo"
            disabled={index === 0}
            onClick={() => move(index - 1)}
          >
            <Icon name="back" size={16} />
          </button>
          <button
            type="button"
            className="carousel-next carousel-control"
            aria-label="Next photo"
            disabled={index === images.length - 1}
            onClick={() => move(index + 1)}
          >
            <Icon name="chevron" size={16} />
          </button>
          <div className="carousel-pagination">
            {images.map((_, i) => (
              <button
                type="button"
                key={i}
                aria-label={`Photo ${i + 1} of ${images.length}`}
                aria-current={i === index ? "true" : undefined}
                onClick={() => move(i)}
              >
                <span />
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
