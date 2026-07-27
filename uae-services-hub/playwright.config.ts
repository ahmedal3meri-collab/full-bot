import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:3010",
    // البيئة السحابية تستخدم كروميوم مُثبَّت مسبقًا على هذا المسار — عدّله محليًا إن اختلف عندك
    launchOptions: { executablePath: process.env.PLAYWRIGHT_CHROMIUM_PATH || "/opt/pw-browsers/chromium" },
  },
  // شغّل يدويًا: npm run dev -- --port 3010 قبل npm run test:e2e (لا webServer تلقائي هنا لأن قاعدة البيانات تحتاج seed مسبقًا)
});
