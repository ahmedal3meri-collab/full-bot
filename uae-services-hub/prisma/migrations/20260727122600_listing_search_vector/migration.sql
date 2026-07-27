-- Full-Text Search: عمود tsvector + trigger يجمع العربي والإنجليزي
-- Prisma لا يدير محتوى الأعمدة Unsupported، لذا التريغر مكتوب يدويًا هنا.

CREATE EXTENSION IF NOT EXISTS unaccent;

CREATE INDEX IF NOT EXISTS "Listing_searchVector_idx" ON "Listing" USING GIN ("searchVector");

CREATE OR REPLACE FUNCTION listing_search_vector_update() RETURNS trigger AS $$
BEGIN
  NEW."searchVector" :=
    setweight(to_tsvector('arabic', unaccent(coalesce(NEW."titleAr", ''))), 'A') ||
    setweight(to_tsvector('simple', unaccent(coalesce(NEW."titleEn", ''))), 'A') ||
    setweight(to_tsvector('arabic', unaccent(coalesce(NEW."descriptionAr", ''))), 'B') ||
    setweight(to_tsvector('simple', unaccent(coalesce(NEW."descriptionEn", ''))), 'B');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS listing_search_vector_trigger ON "Listing";
CREATE TRIGGER listing_search_vector_trigger
  BEFORE INSERT OR UPDATE OF "titleAr", "titleEn", "descriptionAr", "descriptionEn"
  ON "Listing"
  FOR EACH ROW EXECUTE FUNCTION listing_search_vector_update();
