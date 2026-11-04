import { lazy, Suspense, useState } from "react";
import type { PickerProps } from "emoji-picker-react";
import { Dialog } from "./Dialog";

const Picker = lazy(async () => {
  const [{ default: Component }, { default: emojiData }] = await Promise.all([
    import("./LocalizedEmojiPicker"),
    import("emoji-picker-react/data/emojis-en"),
  ]);
  // Mount search only after the dataset is ready, so an early query is not
  // cleared by the picker's asynchronous dataset initialization.
  return {
    default: (props: PickerProps) => (
      <Component {...props} emojiData={emojiData} />
    ),
  };
});
export function EmojiButton({
  onSelect,
  label = "Add emoji",
}: {
  onSelect: (emoji: string) => void;
  label?: string;
}) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        type="button"
        className="emoji-button icon-button"
        aria-label={label}
        aria-expanded={open}
        onClick={() => setOpen(true)}
      >
        <svg
          width="22"
          height="22"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.7"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="9.5" />
          <path d="M7.5 14.5c1 4 8 4 9 0" />
          <circle cx="8.5" cy="9" r=".8" fill="currentColor" />
          <circle cx="15.5" cy="9" r=".8" fill="currentColor" />
        </svg>
      </button>
      {open && (
        <Dialog
          title="Emoji"
          className="emoji-dialog"
          onClose={() => setOpen(false)}
        >
          <Suspense
            fallback={
              <p className="emoji-loading" role="status">
                Loading emoji…
              </p>
            }
          >
            <Picker
              width="100%"
              height={390}
              emojiStyle="native"
              colorScheme="light"
              searchPlaceholder="Search emoji"
              previewConfig={{ showPreview: false }}
              onEmojiClick={(data) => {
                onSelect(data.emoji);
                setOpen(false);
              }}
            />
          </Suspense>
        </Dialog>
      )}
    </>
  );
}
