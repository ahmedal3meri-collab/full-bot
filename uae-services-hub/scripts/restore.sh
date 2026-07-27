#!/usr/bin/env bash
# استعادة من نسخة احتياطية أنشأها scripts/backup.sh
# الاستخدام: ./scripts/restore.sh /var/backups/ush/20260101-030000   (أو ملف .tar.gz.gpg)
# تحذير: يستبدل قاعدة البيانات الحالية بالكامل. خذ نسخة احتياطية جديدة قبل التشغيل إن أمكن.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/.env"
cd "$ROOT"

SRC="${1:?الاستخدام: restore.sh <مسار مجلد النسخة أو ملف .tar.gz.gpg>}"
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

if [[ "$SRC" == *.gpg ]]; then
  echo "==> فك التشفير"
  gpg --decrypt "$SRC" | tar -xzf - -C "$WORKDIR"
  SRC="$WORKDIR"
fi

[ -f "$SRC/postgres.dump.gz" ] || { echo "لا يوجد postgres.dump.gz في $SRC" >&2; exit 1; }

read -r -p "سيتم استبدال قاعدة البيانات '$POSTGRES_DB' بالكامل. متأكد؟ (اكتب yes) " CONFIRM
[ "$CONFIRM" = "yes" ] || { echo "أُلغي."; exit 1; }

echo "==> استعادة PostgreSQL"
gunzip -c "$SRC/postgres.dump.gz" | docker compose exec -T postgres pg_restore \
  -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner

if [ -d "$SRC/listings" ] || [ -d "$SRC/documents" ]; then
  echo "==> استعادة MinIO"
  docker compose run --rm --entrypoint sh minio -c "
    mc alias set local http://minio:9000 '$MINIO_ROOT_USER' '$MINIO_ROOT_PASSWORD' >/dev/null &&
    mc mirror --quiet /backup/listings local/$S3_BUCKET_LISTINGS &&
    mc mirror --quiet /backup/documents local/$S3_BUCKET_DOCS
  " -v "$SRC:/backup"
fi

echo "==> ملاحظة: استعادة Qdrant تدوية عبر Qdrant Snapshot API — راجع BACKUP_RESTORE.md قسم Qdrant"
echo "[RESTORE OK]"
