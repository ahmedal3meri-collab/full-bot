# API

الوضع الحالي: **معظم منطق القراءة يمرّ عبر Server Components تستعلم Prisma مباشرة (`lib/modules/*/queries.ts`)**، لا عبر REST. الكتابة تمر عبر **Server Actions** (`"use server"`)، ليست REST endpoints تقليدية. `/api/v1/*` REST المذكور بـ `ARCHITECTURE.md` مخطَّط للمرحلة القادمة (تكامل تطبيق جوال مستقبلي) — لم يُبنَ بعد باستثناء `/api/health`.

## نقاط REST الموجودة فعليًا

### `GET /api/health`
```json
{ "status": "ok", "db": "up", "timestamp": "2026-07-27T12:44:07.663Z" }
```
`503` مع `{"status":"error","db":"down"}` إذا فشل الاستعلام. مصدر: `app/api/health/route.ts` (اختُبِر فعليًا، راجع README).

## Server Actions الموجودة (استدعاء مباشر من React، ليست REST)

| الدالة | الملف | المدخلات | الوصف |
|---|---|---|---|
| `registerAction` | `lib/modules/auth/actions.ts` | `{fullName, email?, phone?, password, emirateId?}` | تسجيل مستخدم جديد، Argon2، إنشاء جلسة |
| `loginAction` | نفسه | `{identifier, password}` | تسجيل دخول، rate-limited (10 محاولات/15 دقيقة/IP) |
| `logoutAction` | نفسه | — | إلغاء الجلسة الحالية |

## استعلامات القراءة (Server Components، لا HTTP منفصل)

| الوظيفة | الملف | تُستخدم في |
|---|---|---|
| `getTopLevelCategories` | `lib/modules/categories/queries.ts` | الصفحة الرئيسية |
| `getCategoryBySlug` | نفسه | صفحة القسم |
| `getFeaturedListings`, `getLatestListings`, `getListingsByCategorySlug`, `getListingById` | `lib/modules/listings/queries.ts` | الرئيسية، صفحة القسم، صفحة الإعلان |
| `getVerifiedCompanies`, `getCompanyBySlug` | `lib/modules/companies/queries.ts` | الرئيسية (صفحة الشركة نفسها لم تُبنَ بعد) |

## المخطط للمراحل القادمة (غير مبني)

- `POST /api/v1/listings` — إنشاء إعلان (يحتاج رفع صور MinIO أولًا)
- `POST /api/v1/service-requests` + `POST /api/v1/quotes`
- `GET /api/v1/search?q=...` — يستخدم `Listing.searchVector` الموجود فعليًا بقاعدة البيانات
- Webhook للدفع (بعد اختيار مزود — راجع `REQUIRED_USER_INPUT.md` #3)
- REST كامل تحت `/api/v1` فقط إذا احتاجه تطبيق جوال مستقبلي؛ الويب سيستمر بـ Server Actions/Components (أسرع وأبسط لـ SSR كما وثّق `ARCHITECTURE.md`)
