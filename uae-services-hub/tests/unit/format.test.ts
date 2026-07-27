import { describe, expect, it } from "vitest";
import { formatAed } from "@/lib/format";

describe("formatAed", () => {
  it("formats a whole number in Arabic locale with AED", () => {
    const out = formatAed(185000, "ar");
    expect(out).toContain("185,000");
  });

  it("formats a numeric string the same as a number", () => {
    expect(formatAed("95000", "en")).toBe(formatAed(95000, "en"));
  });

  it("rounds to whole AED (no fraction digits)", () => {
    const out = formatAed(99.5, "en");
    expect(out).not.toMatch(/\.\d/);
  });
});
