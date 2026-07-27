# BACKUP_RESTORE

> `scripts/backup.sh` و`scripts/restore.sh` صحيحان نحويًا (`bash -n` نجح) لكن **لم يُشغَّلا فعليًا** ضد Docker حقيقي — لا Docker daemon في بيئة تنفيذ هذه الجلسة. اختبرهما يدويًا على سيرفرك (بيئة staging إن أمكن) قبل الاعتماد عليهما.

## النسخ الاحتياطي

```bash
./scripts/backup.sh
```

يُنتج بـ `$BACKUP_DIR/<timestamp>/`:
- `postgres.dump.gz` — `pg_dump -Fc` (تنسيق مضغوط، يدعم استعادة انتقائية بالجداول)
- `qdrant-snapshot.json` — رابط snapshot من Qdrant API (يفشل بأمان قبل المرحلة 5 لأن المجموعة غير موجودة بعد — تحذير لا إيقاف)
- نسخة من `S3_BUCKET_LISTINGS` و`S3_BUCKET_DOCS` عبر `mc mirror`

إن كان `BACKUP_GPG_RECIPIENT` معرّفًا بـ `.env`، يُضغط ويُشفَّر المجلد كاملًا إلى `.tar.gz.gpg` ويُحذف المجلد غير المشفَّر.

النسخ الأقدم من `BACKUP_RETAIN_DAYS` (افتراضي 14 يومًا) تُحذف تلقائيًا آخر كل تشغيل.

### جدولة عبر Cron

```bash
# /etc/cron.d/ush-backup
0 3 * * * root cd /path/to/uae-services-hub && ./scripts/backup.sh >> /var/log/ush-backup.log 2>&1
```

## الاستعادة

```bash
./scripts/restore.sh /var/backups/ush/20260101-030000
# أو من نسخة مشفّرة:
./scripts/restore.sh /var/backups/ush/20260101-030000.tar.gz.gpg
```

**يستبدل قاعدة البيانات الحالية بالكامل** (`pg_restore --clean --if-exists`) — يطلب تأكيدًا صريحًا (`yes`) قبل التنفيذ. خذ نسخة احتياطية جديدة أولًا إن كان هناك بيانات حالية تستحق الحفظ.

### استعادة Qdrant (يدوية حاليًا)

لا يوجد سكربت آلي بعد لأن المرحلة 5 (RAG) لم تُبنَ. عند بنائها، استخدم Qdrant Snapshot API:

```bash
curl -X PUT "http://localhost:6333/collections/${QDRANT_COLLECTION}/snapshots/upload" \
  -H "api-key: ${QDRANT_API_KEY}" \
  -F "snapshot=@qdrant-snapshot.json"
```

## اختبار الاستعادة (مهم)

نسخة احتياطية غير مُختبَرة الاستعادة = لا نسخة احتياطية فعليًا. كل ربع سنة على الأقل:
1. استعد آخر نسخة على سيرفر/بيئة منفصلة (staging).
2. تحقق أن `npm run dev` يعمل ويعرض بيانات حقيقية من النسخة المستعادة.
3. وثّق تاريخ آخر اختبار استعادة ناجح هنا يدويًا.

**آخر اختبار استعادة موثّق:** لم يُجرَ بعد.
