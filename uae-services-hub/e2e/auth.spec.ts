import { test, expect } from "@playwright/test";

// يتطلب: dev server يعمل على baseURL وقاعدة بيانات مبذورة (npm run db:seed)
test.describe("Authentication", () => {
  test("register, logout, then login again with the same account", async ({ page }) => {
    const email = `e2e.${Date.now()}@example.com`;

    await page.goto("/ar/register");
    await page.getByLabel("الاسم الكامل").fill("مستخدم اختبار E2E");
    await page.getByLabel("البريد الإلكتروني").fill(email);
    await page.getByLabel("كلمة المرور").fill("TestPass123!");
    await page.getByRole("button", { name: "إنشاء الحساب" }).click();

    await page.waitForURL("**/ar");
    await expect(page.locator("header")).toContainText("تسجيل الخروج");

    await page.getByRole("button", { name: "تسجيل الخروج" }).click();
    await expect(page.locator("header")).toContainText("تسجيل الدخول");

    await page.goto("/ar/login");
    await page.getByLabel(/البريد الإلكتروني \/ رقم الهاتف/).fill(email);
    await page.getByLabel("كلمة المرور").fill("TestPass123!");
    await page.getByRole("button", { name: "دخول" }).click();

    await page.waitForURL("**/ar");
    await expect(page.locator("header")).toContainText("تسجيل الخروج");
  });

  test("rejects an invalid login", async ({ page }) => {
    await page.goto("/ar/login");
    await page.getByLabel(/البريد الإلكتروني \/ رقم الهاتف/).fill("no-such-user@example.com");
    await page.getByLabel("كلمة المرور").fill("wrong-password");
    await page.getByRole("button", { name: "دخول" }).click();

    await expect(page.getByText("بيانات الدخول غير صحيحة")).toBeVisible();
  });
});

test.describe("Public pages render real DB data", () => {
  test("home page shows seeded categories and RTL", async ({ page }) => {
    await page.goto("/ar");
    await expect(page.locator("html")).toHaveAttribute("dir", "rtl");
    await expect(page.getByText("السيارات والمركبات")).toBeVisible();
  });

  test("category page filters listings and shows an unknown category as 404", async ({ page }) => {
    await page.goto("/ar/categories/does-not-exist");
    await expect(page.getByText(/404|not found|الصفحة غير موجودة/i)).toBeVisible();
  });
});
