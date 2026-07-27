# OPERATIONS

## Health Checks

| الخدمة | الفحص |
|---|---|
| `web` | `GET /api/health` → `{status, db}` — يستعلم PostgreSQL فعليًا عبر `SELECT 1` (`app/api/health/route.ts`) |
| `realtime` | `GET /health` (منفذ 4000) → `{status: "ok"}` |
| `postgres` | `pg_isready` (Docker healthcheck مدمج) |
| `redis` | `redis-cli ping` |
| `minio` | `mc ready local` |
| `worker` | لا HTTP health check — راقب اللوغ (`docker compose logs worker`)، يطبع نبضة كل 60 ثانية عند إنهاء إعلانات |

## المراقبة

```bash
docker compose -f docker-compose.prod.yml ps            # حالة كل الحاويات
docker compose -f docker-compose.prod.yml logs -f web    # لوغ حي
docker stats                                              # استهلاك CPU/RAM لحظي
```

**غير مُعدّ بعد** (يحتاج قرارك/وقتًا إضافيًا):
- Sentry (متغيّر `SENTRY_DSN` موجود بـ `.env.example` لكن لم يُربط بالكود بعد)
- Prometheus/Grafana metrics endpoint
- تنبيه تلقائي عند فشل `scripts/backup.sh` (شغّله يدويًا حاليًا وراقب رمز الخروج)

## مساحة التخزين

```bash
docker system df                 # مساحة صور/حاويات/volumes Docker
df -h /var/lib/docker             # مساحة القرص الفعلية
du -sh /var/backups/ush/*         # حجم كل نسخة احتياطية
```

## إعادة التشغيل بعد سقوط السيرفر

كل الخدمات `restart: always` (بـ `docker-compose.prod.yml`) — يعيد Docker تشغيلها تلقائيًا مع Docker daemon نفسه عند إقلاع السيرفر (فعّل `sudo systemctl enable docker`).

## Log Rotation

معرّف عبر `x-logging` بـ `docker-compose.prod.yml`: `max-size: 10m`, `max-file: 3` لكل حاوية — لا حاجة لإعداد `logrotate` منفصل لسجلات الحاويات. سجل Caddy (`docker/Caddyfile`) يدوّر ذاتيًا (`roll_size 20mb`, `roll_keep 5`).

## عمليات صيانة شائعة

```bash
# دخول psql داخل الحاوية
docker compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB

# تشغيل هجرة جديدة بعد سحب تحديث
docker compose run --rm web npx prisma migrate deploy

# إعادة توليد Prisma Client بعد تعديل schema
docker compose run --rm web npx prisma generate
```
