import EmojiPicker, { type PickerProps } from "emoji-picker-react";

// This entire module is a lazy chunk; the feed does not load the picker/dataset.
export default function LocalizedEmojiPicker(props: PickerProps) {
  return (
    <EmojiPicker
      {...props}
      labels={{
        searchPlaceholder: "Search emoji",
        searchLabel: "Search emoji",
        searchClear: "Clear search",
        searchResultsNone: "No results found",
        searchResultsOne: "1 emoji found",
        searchResultsMany: "%n emoji found",
        categoryNavigation: "Emoji categories",
        loading: "Loading emoji…",
        loadingError: "Could not load emoji",
        retryLoading: "Try again",
        skinToneNeutral: "Default skin tone",
        skinToneLight: "Light skin tone",
        skinToneMediumLight: "Medium-light skin tone",
        skinToneMedium: "Medium skin tone",
        skinToneMediumDark: "Medium-dark skin tone",
        skinToneDark: "Dark skin tone",
      }}
    />
  );
}
