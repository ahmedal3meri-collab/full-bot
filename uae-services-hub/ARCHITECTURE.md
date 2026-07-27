# ARCHITECTURE

## نظرة عامة

```
                        ┌─────────────┐
   Internet ───443/80──▶│    Caddy     │  (TLS تلقائي، reverse proxy)
                        └──────┬──────┘
                               │ (شبكة frontend)
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        ┌──────────┐    ┌───────────┐    ┌────────────┐
        │   web    │    │  realtime │    │   MinIO     │ (console/API عبر Caddy فقط عند الحاجة)
        │ Next.js  │    │ Socket.IO │    │  (S3-compat) │
        └────┬─────┘    └─────┬─────┘    └──────┬──────┘
             │ (شبكة backend - internal، لا إنترنت مباشر)
   ┌─────────┼───────────┬──────────┬───────────┐
   ▼         ▼           ▼          ▼           ▼
┌──────┐ ┌───────┐  ┌────────┐ ┌────────┐ ┌──────────┐
│Postgres│ Redis │  │ Qdrant │ │ worker │ │  (Ollama  │
│  16   │ │  7    │  │(vector)│ │ BullMQ │ │  خارجي)   │
└──────┘ └───────┘  └────────┘ └────────┘ └──────────┘
```

## الخدمات

| الخدمة | الدور | يُكشَف للإنترنت؟ |
|---|---|---|
| `web` | Next.js 15 App Router — UI + REST `/api/v1` + Server Actions | لا (خلف Caddy فقط) |
| `worker` | BullMQ: إشعارات، انتهاء إعلانات، فهرسة RAG، تنظيف دوري | لا |
| `realtime` | Socket.IO للمحادثات الفورية | لا (خلف Caddy فقط، مسار `/socket.io`) |
| `postgres` | مصدر الحقيقة الوحيد للبيانات العلائقية | لا — شبكة `backend` بها `internal: true` |
| `redis` | Cache + BullMQ queues + rate limiting + sessions store | لا |
| `qdrant` | Vector DB لـ RAG (المرحلة 5) | لا |
| `minio` | تخزين الصور/الملفات (S3-compatible) | لا مباشرة؛ روابط presigned تُصدَر من `web` |
| `caddy` | Reverse proxy + HTTPS تلقائي عبر Let's Encrypt | نعم (80/443 فقط) |

## لماذا Next.js موحّد بدل NestJS منفصل

راجع `IMPLEMENTATION_PLAN.md` §1 للمقارنة الكاملة. الخلاصة: SEO قوي لكل صفحة إمارة/قسم يحتاج SSR أصلي، وفريق صغير يستفيد من عدم تكرار DTOs بين Backend/Frontend عبر Prisma + Zod مشتركة. المهام الثقيلة (embeddings، إشعارات مجدولة) معزولة في `worker` fun حتى لا تحجب طلبات HTTP.

## تنظيم الكود

```
uae-services-hub/
├── app/                      # Next.js App Router
│   ├── [locale]/             # ar | en — next-intl
│   │   ├── (public)/         # الصفحة الرئيسية، الأقسام، الإعلانات
│   │   ├── (auth)/           # تسجيل الدخول/التسجيل
│   │   └── layout.tsx
│   └── api/v1/                # REST endpoints (webhooks، health، إلخ)
├── lib/
│   ├── db/                   # Prisma client singleton
│   ├── auth/                 # جلسات، Argon2، RBAC
│   ├── otp/                  # OTP provider abstraction
│   ├── config/                # site.ts — مصدر مركزي للاسم/الشعار/الألوان
│   └── modules/               # منطق كل نطاق (categories, listings, ...)
├── prisma/
│   ├── schema.prisma
│   └── seed.ts
├── docker/                    # Dockerfiles لكل خدمة
├── scripts/                   # backup.sh, restore.sh
└── progress/                  # تقرير كل مرحلة
```

## قرارات إضافية موثّقة

- **المصادقة**: جلسات مخزّنة في قاعدة البيانات (جدول `Session`) بدل JWT عديم الحالة، حتى يمكن **إلغاء الجلسات** فوريًا (مطلوب صراحة في المواصفة الأمنية). كلمة المرور بـ Argon2id.
- **RBAC**: جداول `Role`/`Permission`/`RolePermission` بدل enum ثابت — الأدوار التسعة المطلوبة تُبذر كبيانات (seed) وقابلة للتعديل من لوحة الإدارة لاحقًا دون نشر كود جديد.
- **الخصائص الديناميكية**: `AttributeDefinition` (لكل تصنيف) + `ListingAttributeValue` (JSON-typed) بدل عمود لكل خاصية — يسمح بإضافة قسم "قوارب" أو حقل جديد على أي تصنيف من لوحة الإدارة دون migration.
- **الأسعار**: `Decimal(12,2)` بالدرهم في كل مكان — ممنوع Float للنقود.
- **البحث**: PostgreSQL FTS (`tsvector` + GIN index) كبداية، مع حقل `embeddingId` احتياطي على `Listing` لربط اختياري بـ Qdrant لاحقًا (بحث دلالي) دون migration إضافية.
