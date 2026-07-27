# DEPLOYMENT

> لم تُنفَّذ هذه الخطوات فعليًا على أي سيرفر — بيئة تنفيذ هذه الجلسة بلا Docker daemon ولا وصول لسيرفرك. اتبعها بدقة وتحقق من كل خطوة بنفسك.

## المتطلبات

- Linux (Ubuntu 22.04+ مُوصى به)، Docker + Docker Compose v2
- 8GB RAM كحد أدنى (16GB مريح) — راجع `REQUIRED_USER_INPUT.md` #14
- نطاق يشير بـ DNS A/AAAA record لعنوان IP السيرفر — راجع `REQUIRED_USER_INPUT.md` #1
- منافذ مفتوحة بالجدار الناري: **80، 443، ومنفذ SSH فقط**

## خطوات النشر

### 1. تجهيز السيرفر

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER   # ثم أعد تسجيل الدخول
```

### 2. استنساخ المشروع وتهيئة البيئة

```bash
git clone <repo-url> && cd full-bot/uae-services-hub
cp .env.example .env
```

عدّل `.env`:
- كل `CHANGE_ME` → قيمة عشوائية حقيقية: `openssl rand -base64 48`
- `APP_DOMAIN` → نطاقك الحقيقي
- `NODE_ENV=production`

### 3. البناء والتشغيل

```bash
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d postgres redis qdrant minio
# انتظر حتى healthy فعليًا:
docker compose -f docker-compose.prod.yml ps
```

### 4. الهجرة والبذر (مرة واحدة أول نشر)

```bash
docker compose -f docker-compose.prod.yml run --rm web npx prisma migrate deploy
docker compose -f docker-compose.prod.yml run --rm web npm run db:seed
```

**غيّر كلمة مرور `admin@ush.local` فورًا بعد أول دخول.**

### 5. تشغيل باقي الخدمات

```bash
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml ps   # تأكد الكل healthy، لا تتابع قبل ذلك
```

Caddy يطلب شهادة SSL تلقائيًا من Let's Encrypt عند أول طلب لنطاقك (يحتاج DNS مُهيَّأ مسبقًا وإلا سيفشل).

### 6. التحقق

```bash
curl -sf https://<نطاقك>/api/health
```

يجب أن يرجع `{"status":"ok","db":"up",...}`. إن فشل، راجع `docker compose -f docker-compose.prod.yml logs web`.

## التحديثات اللاحقة (Low-Downtime)

```bash
git pull
docker compose -f docker-compose.prod.yml build web worker realtime
docker compose -f docker-compose.prod.yml run --rm web npx prisma migrate deploy
docker compose -f docker-compose.prod.yml up -d web worker realtime
```

`--build` قبل `up -d` يعيد بناء الصورة الجديدة، و`restart: always` يعيد تشغيل الحاوية تلقائيًا عند فشلها أو إعادة تشغيل السيرفر. Zero-downtime كامل (بدون انقطاع أي طلب) يحتاج orchestrator مثل Docker Swarm/Kubernetes مع rolling update — غير مُعدّ هنا؛ التوقف الحالي هو ثوانٍ معدودة أثناء إعادة تشغيل حاوية `web`.

## الموارد والحدود

`docker-compose.prod.yml` يحدد `deploy.resources.limits` لكل خدمة (راجع الملف). عدّلها حسب سعة سيرفرك الفعلية.

## Rollback

```bash
git checkout <commit-سابق>
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d web
```

إن كانت الهجرة الأخيرة تضيف عمودًا/جدولًا فقط (لا تحذف)، الرجوع بالكود آمن دون رجوع بقاعدة البيانات. إن حذفت أو عدّلت عمودًا، راجع `BACKUP_RESTORE.md` للاستعادة من نسخة احتياطية سابقة.
