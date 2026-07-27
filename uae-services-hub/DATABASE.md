# DATABASE

مصدر الحقيقة: `prisma/schema.prisma` (42 جدولًا). هذا الملف يشرح القرارات، لا يكرر كل حقل.

## الاختبار الفعلي

هُوجِر المخطط ضد PostgreSQL 16 محليًا (`ush_dev`)، ونُفِّذ `prisma/seed.ts` بنجاح. راجع `progress/phase-1.md` للمخرجات الكاملة.

```bash
npx prisma migrate deploy   # يطبّق كل الميغريشنز بالترتيب
npm run db:seed
npx prisma studio           # تصفّح مرئي للبيانات
```

## المجموعات المنطقية

1. **المصادقة/RBAC**: `User`, `Role`, `Permission`, `RolePermission`, `Session`, `OtpCode`, `PasswordResetToken`
2. **الجغرافيا**: `Emirate` → `City` → `Region` (ثلاث مستويات، الإمارات السبع مبذورة)
3. **التصنيف**: `Category` (self-relation للأقسام الفرعية) + `AttributeDefinition` + `ListingAttributeValue`
4. **الإعلانات**: `Listing`, `ListingImage`, `ListingVideo`, `Favorite`
5. **الشركات**: `Company`, `CompanyCoverage`, `CompanyService`, `CompanyPortfolioImage`
6. **الاشتراكات**: `Plan`, `Subscription`, `Payment`
7. **المعاملات**: `ServiceRequest`, `ServiceRequestImage`, `Quote`, `Booking`, `StatusHistoryEntry`
8. **المحادثات**: `Conversation`, `ConversationParticipant`, `Message`, `Report`, `Block`
9. **التقييمات**: `Review`, `ReviewImage`
10. **الإشعارات**: `Notification`
11. **الذكاء الاصطناعي**: `KnowledgeArticle`, `AiConversation`, `AiMessage`
12. **التدقيق**: `AuditLog`

## قرارات مهمة

### RBAC بجداول لا enum
`lib/rbac/constants.ts` هو **مصدر الحقيقة الوحيد** للأدوار الثمانية والصلاحيات الافتراضية — يستورده `prisma/seed.ts` وطبقة `lib/auth/*` معًا حتى لا يختلفا. تعديل الصلاحيات مستقبلًا من لوحة الإدارة يكتب مباشرة في `RolePermission` دون نشر كود جديد.

### الخصائص الديناميكية
`AttributeDefinition` مرتبطة بـ `Category`، و`ListingAttributeValue` تخزّن القيمة حسب `AttributeType` (STRING/NUMBER/BOOLEAN/SELECT/MULTI_SELECT/DATE) في عمود مطابق. أُضيفت تعريفات فعلية لثلاث فئات (`prisma/seed.ts`):
- **السيارات** (`cars-sale`): الشركة، الموديل، السنة، المسافة، الوقود، ناقل الحركة، اللون، المواصفات، رقم الهيكل
- **العقارات** (`villas`, `apartments`): المساحة، الغرف، الحمامات، مفروش، موقف سيارة
- **اللوحات** (`plates-sale`): الكود، الرقم، عدد الخانات، نوع الملكية

باقي الـ 77 قسمًا مبذورة بدون خصائص ديناميكية بعد — إضافتها لاحقًا لا تحتاج migration، فقط صفوف جديدة في `AttributeDefinition`.

### الأسعار
`Decimal(12,2)` بكل مكان يخزّن مبلغًا نقديًا. **لا Float إطلاقًا.** العملة الافتراضية `AED` (`Listing.currency`).

### البحث النصي
`Listing.searchVector` معرّف `Unsupported("tsvector")` في Prisma (لا تستطيع مكتبة Prisma الاستعلام عليه مباشرة عبر الـ Client — يحتاج `$queryRaw`). المحتوى يُحدَّث تلقائيًا عبر trigger PL/pgSQL مكتوب يدويًا في `prisma/migrations/20260727122600_listing_search_vector/migration.sql` لأن Prisma لا يدير محتوى triggers. يستخدم:
- `to_tsvector('arabic', unaccent(...))` للعربي
- `to_tsvector('simple', unaccent(...))` للإنجليزي
- أوزان مختلفة: العنوان `A`، الوصف `B`

مثال استعلام بحث (لم يُبنَ endpoint له بعد — المرحلة 2 غير مكتملة):
```sql
SELECT * FROM "Listing"
WHERE "searchVector" @@ websearch_to_tsquery('arabic', 'لاندكروزر ابوظبي')
ORDER BY ts_rank("searchVector", websearch_to_tsquery('arabic', 'لاندكروزر ابوظبي')) DESC;
```

طبقة Meilisearch/OpenSearch اختيارية مستقبلًا: `KnowledgeArticle.qdrantPointId` وحقل مشابه يمكن إضافته لـ `Listing` دون كسر التوافق.

### الجلسات القابلة للإلغاء
`Session.revokedAt` — الإلغاء فوري ولا يعتمد على انتهاء صلاحية JWT، لأن الجلسات ليست JWT عديم الحالة بل صف بقاعدة البيانات (راجع `lib/auth/session.ts`).

## مخطط علاقات مبسّط

```
User ──< Listing >── Category ──< AttributeDefinition
  │         │              │
  │         >── Emirate/City/Region
  │
  >── Session, OtpCode, Favorite, ServiceRequest, Notification, AuditLog

Company ──< CompanyService, CompanyCoverage, Subscription >── Plan
   │
   >── Listing, Quote, Review

ServiceRequest ──< Quote ── Booking
       │
       >── Conversation ──< Message
