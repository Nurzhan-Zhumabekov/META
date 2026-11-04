import { readFileSync, readdirSync } from "node:fs";
import { resolve } from "node:path";
import { expect, it } from "vitest";

it("ships English application copy and English document metadata", () => {
  const root = resolve(process.cwd(), "src");
  const files = readdirSync(root, { recursive: true, encoding: "utf8" }).filter(
    (name) =>
      /\.(ts|tsx)$/.test(name) &&
      !name.includes(".test.") &&
      !name.startsWith("test"),
  );
  const leftovers = files.filter((name) =>
    /[\u0400-\u04ff]/.test(readFileSync(resolve(root, name), "utf8")),
  );
  expect(leftovers).toEqual([]);
  const html = readFileSync(resolve(process.cwd(), "index.html"), "utf8");
  expect(html).toContain('lang="en"');
  expect(html).not.toMatch(/[\u0400-\u04ff]/);
});
