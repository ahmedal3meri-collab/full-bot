#!/usr/bin/env bash
# نسخ احتياطي: PostgreSQL + Qdrant + MinIO مع تدوير
# الاستخدام: ./scripts/backup.sh   (cron: 0 3 * * *)
# ملاحظة: لم يُشغَّل هذا السكربت فعليًا (بيئة تنفيذ هذه الجلسة بلا Docker daemon) —
# اختبره يدويًا على سيرفرك أول مرة قبل الاعتماد عليه بجدولة تلقائية. راجع BACKUP_RESTORE.md.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/.env"

BACKUP_DIR="${BACKUP_DIR:-/var/backups/ush}"
RETAIN_DAYS="${BACKUP_RETAIN_DAYS:-14}"
STAMP="$(date +%Y%m%d-%H%M%S)"
DEST="$BACKUP_DIR/$STAMP"
mkdir -p "$DEST"

fail() { echo "[BACKUP FAILED] $*" >&2; exit 1; }
trap 'fail "خطأ عند السطر $LINENO"' ERR

cd "$ROOT"

echo "==> PostgreSQL"
docker compose exec -T postgres pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc \
  | gzip > "$DEST/postgres.dump.gz"
[ -s "$DEST/postgres.dump.gz" ] || fail "ملف قاعدة البيانات فارغ"

echo "==> Qdrant snapshot"
docker compose exec -T qdrant sh -c \
  "curl -sf -X POST 'http://localhost:6333/collections/${QDRANT_COLLECTION}/snapshots' -H 'api-key: ${QDRANT_API_KEY}'" \
  > "$DEST/qdrant-snapshot.json" || echo "تحذير: فشل نسخ Qdrant (قد تكون المجموعة غير موجودة بعد — طبيعي قبل المرحلة 5)"

echo "==> MinIO"
docker compose run --rm --entrypoint sh minio -c "
  mc alias set local http://minio:9000 '$MINIO_ROOT_USER' '$MINIO_ROOT_PASSWORD' >/dev/null &&
  mc mirror --quiet local/$S3_BUCKET_LISTINGS /backup/listings &&
  mc mirror --quiet local/$S3_BUCKET_DOCS /backup/documents
" -v "$DEST:/backup" || echo "تحذير: فشل نسخ MinIO (قد تكون الحاويات غير منشأة بعد)"

echo "==> تشفير"
if [ -n "${BACKUP_GPG_RECIPIENT:-}" ]; then
  tar -czf - -C "$DEST" . | gpg --encrypt --recipient "$BACKUP_GPG_RECIPIENT" \
    --output "$BACKUP_DIR/$STAMP.tar.gz.gpg"
  rm -rf "$DEST"
fi

echo "==> تدوير النسخ الأقدم من $RETAIN_DAYS يوم"
find "$BACKUP_DIR" -maxdepth 1 -mtime "+$RETAIN_DAYS" -exec rm -rf {} +

echo "[BACKUP OK] $STAMP"
