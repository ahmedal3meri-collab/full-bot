# UAE Services Hub

منصة إماراتية موحّدة للبيع والشراء والإيجار والخدمات المحلية (سيارات، لوحات مركبات، عقارات، خدمات مركبات، نقل وتوصيل، خدمات منازل، خدمات أعمال).

> **حالة المشروع: المرحلة 1 مكتملة وحقيقية (مُشغَّلة ومُختبَرة فعليًا)، المرحلة 2 جزئية.**
> راجع `IMPLEMENTATION_PLAN.md` للتفاصيل الكاملة، و`progress/phase-1.md` لتقرير ما اختُبِر بالضبط.
> لا يوجد Docker daemon في بيئة تنفيذ هذه الجلسة — كل ما هو موصوف "مُختبَر" هنا اختُبِر ضد PostgreSQL/Redis مثبَّتين محليًا مباشرة، وليس عبر `docker compose`. شغّل `docker compose up` بنفسك على سيرفرك وتحقق من `docker compose ps` قبل اعتبار الإنتاج جاهزًا.

## المُنجَز فعليًا ومُختبَر

| الجزء | الحالة |
|---|---|
| `prisma/schema.prisma` — 42 جدول | ✅ هُوجِر فعليًا ضد PostgreSQL 16 محلي |
| `prisma/seed.ts` | ✅ نُفِّذ فعليًا: 8 أدوار، 18 صلاحية، 7 إمارات/8 مدن/22 منطقة، 77 قسم، 4 باقات، بيانات تجريبية |
| البحث النصي (FTS) | ✅ عمود tsvector + trigger عربي/إنجليزي مُطبَّق بميغريشن يدوية |
| نظام التصميم (RTL/LTR، Dark/Light، IBM Plex Sans Arabic) | ✅ لقطات شاشة فعلية بالعربي والإنجليزي |
| next-intl (ar افتراضي / en) | ✅ |
| المصادقة (Argon2id، جلسات DB قابلة للإلغاء) | ✅ اختُبِر تسجيل/دخول/خروج كامل عبر Playwright ضد قاعدة بيانات حقيقية |
| الصفحة الرئيسية، صفحة القسم، صفحة الإعلان | ✅ SSR حقيقي من قاعدة البيانات (لا mock data) |
| `npm run build` (Next.js standalone) | ✅ نجح بدون أخطاء TypeScript |
| Docker Compose (dev + prod) + Dockerfiles + Caddy | ✅ مكتوبة، غير مُشغَّلة (لا Docker daemon هنا) |
| `worker/index.ts` (سويب إنهاء الإعلانات) | ✅ اختُبِر محليًا: يتصل بـ Redis وPostgres وينفّذ المهمة |
| `realtime/index.ts` (Socket.IO) | ✅ اختُبِر: health check + غرف محادثة أساسية (بدون تحقق جلسة أو حفظ رسائل بعد) |
| نموذج إضافة إعلان (واجهة كاملة + رفع صور) | ❌ لم يُبنَ |
| طلبات الخدمة/عروض الأسعار/الحجوزات (واجهة) | ❌ لم يُبنَ (الجداول موجودة بالمخطط) |
| لوحة الإدارة | ❌ لم تُبنَ |
| المساعد الذكي + RAG + Qdrant | ❌ لم يُبنَ |
| الدفع | ❌ لا مزود مربوط (لا مفاتيح وهمية بالكود) |
| اختبارات آلية (Vitest/Playwright كمشروع اختبار دائم) | ⚠️ جزئي — راجع `TESTING.md` |

## التشغيل محليًا (بدون Docker)

هكذا اختُبِر المشروع فعليًا في هذه الجلسة:

```bash
cp .env.example .env
# عدّل DATABASE_URL و REDIS_URL ليشيرا لـ localhost بدل أسماء خدمات Docker

npm install
npx prisma migrate deploy
npm run db:seed
npm run dev
```

افتح http://localhost:3000 — يُعاد توجيهك إلى `/ar` تلقائيًا.

حساب Super Admin التجريبي: `admin@ush.local` / `ChangeMe!Admin123` — **غيّره فورًا، هذا حساب seed فقط.**

## التشغيل عبر Docker (على سيرفرك — لم يُختبَر هنا)

```bash
cp .env.example .env
# املأ كل CHANGE_ME — ولّد الأسرار: openssl rand -base64 48
docker compose up -d postgres redis qdrant minio
docker compose run --rm web npx prisma migrate deploy
docker compose run --rm web npm run db:seed
docker compose up -d
docker compose ps   # تحقق أن الكل healthy فعليًا قبل المتابعة
```

الوصول: http://localhost:3000 · MinIO Console: http://localhost:9001

للإنتاج راجع `DEPLOYMENT.md`.

## بنية المستودع

هذا المشروع يعيش داخل مجلد فرعي `uae-services-hub/` من مستودع `full-bot` الذي يحتوي أيضًا بوت تلغرام منفصل تمامًا (`bot.py` وما حوله بجذر المستودع). لا علاقة بين المشروعين — راجع `IMPLEMENTATION_PLAN.md` §0 لسبب هذا القرار.

## الوثائق

| الملف | المحتوى |
|---|---|
| `IMPLEMENTATION_PLAN.md` | خطة المراحل وحالة كل بند |
| `REQUIRED_USER_INPUT.md` | ما يحتاج قرارك (نطاق، مزودي SMS/دفع/AI، نصوص قانونية) |
| `ARCHITECTURE.md` | مخطط الخدمات والقرارات الهندسية |
| `DATABASE.md` | شرح المخطط والقرارات (RBAC، الخصائص الديناميكية، FTS) |
| `SECURITY.md` | التدابير المطبَّقة والفجوات المتبقية |
| `DEPLOYMENT.md` | خطوات نشر Production فعلية على سيرفر Linux |
| `OPERATIONS.md` | التشغيل اليومي، المراقبة، الـ Health Checks |
| `BACKUP_RESTORE.md` | النسخ الاحتياطي والاستعادة |
| `API.md` | نقاط REST الحالية |
| `AI_INTEGRATION.md` | تصميم المرحلة 5 (لم تُبنَ بعد) |
| `TESTING.md` | ما هو مُختبَر فعليًا وكيف تشغّل الاختبارات |
| `progress/phase-1.md` | تقرير المرحلة 1 المفصّل |

## ملاحظات على المخطط

- **جميع الأسعار `Decimal(12,2)` بالدرهم AED** — ممنوع استخدام Float للنقود.
- **الحقول الديناميكية**: `AttributeDefinition` + `ListingAttributeValue` — أُضيفت أمثلة فعلية للسيارات والعقارات واللوحات (`prisma/seed.ts`)، إضافة قسم جديد بحقوله لا يحتاج migration.
- **RBAC**: `Role` ↔ `Permission` بجداول (`lib/rbac/constants.ts` هو مصدر الحقيقة)، وليس enum ثابت.
- **البحث**: عمود `tsvector` + trigger مُطبَّقان فعليًا (`prisma/migrations/20260727122600_listing_search_vector`)، مع حقل احتياطي على `Listing` لربط Qdrant اختياريًا لاحقًا.
