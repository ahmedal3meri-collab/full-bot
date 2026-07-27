import { describe, expect, it } from "vitest";
import { registerSchema, loginSchema } from "@/lib/modules/auth/schemas";

describe("registerSchema", () => {
  it("accepts a valid UAE phone number and password", () => {
    const result = registerSchema.safeParse({
      fullName: "أحمد محمد",
      phone: "+971501234567",
      email: "",
      password: "SuperSecret1",
    });
    expect(result.success).toBe(true);
  });

  it("rejects a non-UAE phone number", () => {
    const result = registerSchema.safeParse({
      fullName: "Test User",
      phone: "+15551234567",
      email: "",
      password: "SuperSecret1",
    });
    expect(result.success).toBe(false);
  });

  it("rejects when neither email nor phone is provided", () => {
    const result = registerSchema.safeParse({
      fullName: "Test User",
      email: "",
      phone: "",
      password: "SuperSecret1",
    });
    expect(result.success).toBe(false);
  });

  it("rejects a password shorter than 8 characters", () => {
    const result = registerSchema.safeParse({
      fullName: "Test User",
      email: "a@b.com",
      password: "short",
    });
    expect(result.success).toBe(false);
  });
});

describe("loginSchema", () => {
  it("requires a non-empty identifier and password", () => {
    expect(loginSchema.safeParse({ identifier: "a@b.com", password: "x" }).success).toBe(true);
    expect(loginSchema.safeParse({ identifier: "", password: "x" }).success).toBe(false);
  });
});
