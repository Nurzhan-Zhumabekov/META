import copy from "./english-copy.json";

const translations: Readonly<Record<string, string>> = copy;
// Translate known historical service text at the display boundary. Stored
// observations, evidence and moderator decisions are never rewritten.
export function englishText(text: string): string {
  return (
    translations[text] ?? translations[text.replace(/\s+/g, " ").trim()] ?? text
  );
}
export function hasEnglishTranslation(text: string): boolean {
  return englishText(text) !== text;
}
