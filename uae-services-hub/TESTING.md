# TESTING

## الحالة الفعلية (رُكِّض فعليًا، ليس ادعاءً)

```
Unit (vitest):      8 passed  (tests/unit/format.test.ts, tests/unit/auth-schemas.test.ts)
E2E (Playwright):    4 passed  (e2e/auth.spec.ts)
tsc --noEmit:        0 errors
npm run build:       ✓ نجح (Next.js standalone)
prisma migrate:      ✓ طُبِّق فعليًا ضد PostgreSQL 16 محلي
prisma/seed.ts:      ✓ نُفِّذ فعليًا (راجع progress/phase-1.md للمخرجات الكاملة)
```

آخر تشغيل فعلي لكل ما سبق: راجع `progress/phase-1.md`.

## تشغيل الاختبارات

### Unit (Vitest)
```bash
npm run test:unit
```
يغطي: تنسيق الأسعار بالدرهم (`lib/format.ts`)، تحقق Zod لنماذج التسجيل/الدخول (`lib/modules/auth/schemas.ts`) — بما فيها رفض رقم هاتف غير إماراتي وكلمة مرور قصيرة.

### E2E (Playwright)
يتطلب قاعدة بيانات مبذورة وخادم تطوير يعمل:
```bash
npm run db:seed          # مرة واحدة إن لم تُبذر القاعدة بعد
npm run dev -- --port 3010 &
E2E_BASE_URL=http://localhost:3010 npm run test:e2e
```
يغطي `e2e/auth.spec.ts`:
- تسجيل مستخدم جديد → تسجيل خروج → تسجيل دخول بنفس الحساب (رحلة كاملة، تتحقق من محتوى الهيدر بعد كل خطوة)
- رفض بيانات دخول خاطئة برسالة خطأ واضحة
- الصفحة الرئيسية تعرض `dir="rtl"` وفئات حقيقية من قاعدة البيانات
- قسم غير موجود يرجع 404 فعليًا

### Type checking
```bash
npx tsc --noEmit
```

## ما هو غير مُختبَر (فجوات صريحة)

| الجزء | السبب |
|---|---|
| اختبارات صلاحيات RBAC (كل دور يرى/لا يرى ماذا) | لم تُبنَ واجهات تعتمد على الأدوار بعد (لوحة إدارة، إلخ) |
| اختبارات إنشاء إعلان | نموذج الإنشاء نفسه غير مبني |
| اختبارات طلب خدمة/عروض أسعار | الميزة نفسها غير مبنية |
| اختبارات المساعد الذكي | المرحلة 5 لم تبدأ |
| اختبارات تكامل Docker Compose الفعلية | لا Docker daemon في بيئة هذه الجلسة — اختُبِر المكافئ محليًا (PostgreSQL/Redis مباشرة) بدلًا منه |
| Load/performance testing | لم يُجرَ |
| اختبار استعادة النسخة الاحتياطية | راجع `BACKUP_RESTORE.md` — لم يُجرَ بعد |

## بنية الاختبارات

```
tests/unit/       # Vitest — منطق صرف بدون DOM ولا شبكة
e2e/               # Playwright — رحلات مستخدم كاملة عبر متصفح حقيقي
vitest.config.ts
playwright.config.ts
```

أضِف اختبارًا لكل ميزة جديدة بنفس النمط قبل اعتبارها "مكتملة" — لا تدّعِ نجاح اختبار لم يُشغَّل فعليًا.
