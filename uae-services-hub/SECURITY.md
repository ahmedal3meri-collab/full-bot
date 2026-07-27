# SECURITY

## مطبَّق فعليًا ومُختبَر

| التدبير | التفاصيل |
|---|---|
| تشفير كلمات المرور | Argon2id، `memoryCost=19456` (19 MiB)، `timeCost=2` — توصية OWASP 2024 (`lib/auth/password.ts`) |
| جلسات آمنة | Cookie بـ `httpOnly`, `sameSite=lax`, `secure` بالإنتاج، توكن عشوائي 256-bit، **hash فقط** يُخزَّن بقاعدة البيانات (`lib/auth/session.ts`) |
| إلغاء الجلسات | `Session.revokedAt` — إلغاء فوري ممكن (تسجيل الخروج يستخدمه فعليًا، مُختبَر) |
| عدم تسجيل الأسرار | لا `console.log` لكلمة مرور أو Argon2 hash أو رمز جلسة بأي مكان بالكود |
| الأسرار في env فقط | `.env.example` بدون أي قيمة حقيقية، `.env` (لو أُنشئ) يجب أن يكون بـ `.gitignore` — تحقق قبل أي `git add` |
| RBAC | جداول `Role`/`Permission`/`RolePermission`، لا صلاحيات مبنية بالكود بشكل صلب |
| Zod على مدخلات النماذج | `lib/modules/auth/schemas.ts` يتحقق من طول كلمة المرور، صيغة البريد/الهاتف الإماراتي قبل أي كتابة لقاعدة البيانات |
| منع تعداد المستخدمين | رسالة خطأ دخول موحّدة `invalid_credentials` بدل "البريد غير موجود" مقابل "كلمة مرور خطأ" |
| منفذ قاعدة البيانات | `docker-compose.prod.yml`: لا `ports:` على postgres/redis/qdrant/minio — شبكة `backend` بها `internal: true` |
| Security headers + CSP | `docker/Caddyfile`: HSTS, X-Content-Type-Options, X-Frame-Options, CSP أساسي |
| Health check لا يكشف تفاصيل حساسة | `/api/health` يرجع `{status, db}` فقط |

## غير مكتمل — لا تشغّل إنتاجًا قبل إغلاق هذه الفجوات

| الفجوة | الخطر | الخطة |
|---|---|---|
| Rate limiting بالذاكرة فقط (`lib/auth/rate-limit.ts`) | يُعاد تصفيره عند كل إعادة تشغيل، ولا يعمل عبر أكثر من نسخة `web` (multi-instance) | ربطه بـ Redis (الخدمة موجودة بـ docker-compose لكن غير مستخدمة من auth بعد) |
| لا CSRF token صريح على Server Actions | Next.js Server Actions محمية جزئيًا بـ Origin check المدمج، لكن لم يُراجَع صراحة | مراجعة أمنية قبل الإنتاج |
| رفع الملفات (صور/فيديو) | لم يُبنَ بعد — لا تحقق MIME ولا حد حجم مطبَّق لأن الميزة غير موجودة | يُبنى بالمرحلة 2 مع تحقق MIME صارم + presigned URLs من MinIO فقط |
| `realtime/index.ts` | يقبل `senderId` من العميل مباشرة بدون تحقق من الجلسة — **قابل للانتحال حاليًا** | ربطه بـ cookie الجلسة قبل أي استخدام إنتاجي، موثّق كـ TODO داخل الملف نفسه |
| لا 2FA/OTP فعلي | `OTP_PROVIDER=console` افتراضي — الحساب يُفعَّل فورًا بدون تحقق حقيقي من الهاتف | ينتظر قرارك بمزود SMS (`REQUIRED_USER_INPUT.md` #2) |
| لا فحص أمني آلي (SAST/dependency scan) بخط الأنابيب | لم يُبنَ CI بعد | أضِف `npm audit`/Snyk/CodeQL عند إعداد CI |
| لوحة الإدارة | لم تُبنَ — لا يوجد بعد فصل صريح لصلاحياتها عن باقي التطبيق | يُبنى بالمرحلة 4 مع تحقق دور `SYSTEM_ADMIN`/`SUPER_ADMIN` على كل route |
| IDOR على `/listings/[id]` وما شابه | القراءة عامة (متوقّع لإعلان منشور)، لكن مسارات التعديل/الحذف لم تُبنَ بعد فلم تُختبَر لثغرات IDOR | تُراجَع عند بناء نموذج تعديل الإعلان |

## قبل أي نشر إنتاجي فعلي

1. غيّر كل قيمة `CHANGE_ME` في `.env` بأسرار حقيقية (`openssl rand -base64 48`).
2. غيّر كلمة مرور `admin@ush.local` فورًا بعد أول تسجيل دخول.
3. تأكد أن `.env` غير موجود بالـ git (تحقق بـ `git check-ignore .env`).
4. فعّل `NODE_ENV=production` (يفعّل `secure` على الكوكيز).
5. راجع فقرة "غير مكتمل" أعلاه — لا تفتح رفع الملفات أو المحادثات الفورية للمستخدمين النهائيين قبل إغلاق فجواتها.
