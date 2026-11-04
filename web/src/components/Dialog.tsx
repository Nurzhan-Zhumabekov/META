import { useEffect, useRef } from "react";
import type { ReactNode } from "react";
import { Icon } from "./Icon";

export function Dialog({
  title,
  children,
  onClose,
  className = "",
  busy = false,
}: {
  title: string;
  children: ReactNode;
  onClose: () => void;
  className?: string;
  busy?: boolean;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const close = useRef(onClose);
  close.current = onClose;
  useEffect(() => {
    const node = ref.current!;
    const previous = document.activeElement as HTMLElement | null;
    node.showModal();
    return () => {
      node.close();
      previous?.focus();
    };
  }, []);
  return (
    <dialog
      ref={ref}
      aria-label={title}
      className={`dialog ${className}`}
      onCancel={(event) => {
        event.preventDefault();
        if (!busy) close.current();
      }}
      onClick={(event) => {
        if (event.target === event.currentTarget && !busy) close.current();
      }}
    >
      <div className="dialog-inner">
        <header className="dialog-header">
          <h2>{title}</h2>
          <button
            className="icon-button"
            aria-label="Close"
            onClick={onClose}
            disabled={busy}
          >
            <Icon name="close" size={21} />
          </button>
        </header>
        {children}
      </div>
    </dialog>
  );
}
