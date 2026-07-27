// بيانات تجريبية (Seed) — راجع README قسم "بيانات تجريبية"
// كل شركة/مستخدم تجريبي مُعلَّم بوضوح (اسم ينتهي بـ "(تجريبي)") — لا أسماء شركات حقيقية.

import { PrismaClient } from "@prisma/client";
import argon2 from "argon2";
import { ROLES, PERMISSIONS, DEFAULT_ROLE_PERMISSIONS } from "../lib/rbac/constants";

const db = new PrismaClient();

// ==================== الجغرافيا ====================
// كل إمارة مع مدنها الرئيسية ومناطق تجريبية لكل مدينة
const GEO = [
  {
    slug: "abu-dhabi", nameAr: "أبوظبي", nameEn: "Abu Dhabi",
    cities: [
      { slug: "abu-dhabi-city", nameAr: "مدينة أبوظبي", nameEn: "Abu Dhabi City", regions: ["الخالدية", "الكورنيش", "مصفح", "الشامخة"] },
      { slug: "al-ain", nameAr: "العين", nameEn: "Al Ain", regions: ["الجيمي", "المطاوعة"] },
    ],
  },
  {
    slug: "dubai", nameAr: "دبي", nameEn: "Dubai",
    cities: [
      { slug: "dubai-city", nameAr: "مدينة دبي", nameEn: "Dubai City", regions: ["ديرة", "بر دبي", "الجميرا", "مارينا دبي", "قدرة"] },
    ],
  },
  {
    slug: "sharjah", nameAr: "الشارقة", nameEn: "Sharjah",
    cities: [
      { slug: "sharjah-city", nameAr: "مدينة الشارقة", nameEn: "Sharjah City", regions: ["الممزر", "الياسمين", "المجاز"] },
    ],
  },
  {
    slug: "ajman", nameAr: "عجمان", nameEn: "Ajman",
    cities: [{ slug: "ajman-city", nameAr: "مدينة عجمان", nameEn: "Ajman City", regions: ["الراشدية", "الجرف"] }],
  },
  {
    slug: "umm-al-quwain", nameAr: "أم القيوين", nameEn: "Umm Al Quwain",
    cities: [{ slug: "uaq-city", nameAr: "مدينة أم القيوين", nameEn: "UAQ City", regions: ["الرأس", "الصالحية"] }],
  },
  {
    slug: "ras-al-khaimah", nameAr: "رأس الخيمة", nameEn: "Ras Al Khaimah",
    cities: [{ slug: "rak-city", nameAr: "مدينة رأس الخيمة", nameEn: "RAK City", regions: ["الناخيل", "الجزيرة الحمراء"] }],
  },
  {
    slug: "fujairah", nameAr: "الفجيرة", nameEn: "Fujairah",
    cities: [{ slug: "fujairah-city", nameAr: "مدينة الفجيرة", nameEn: "Fujairah City", regions: ["الفصيل", "سكمكم"] }],
  },
];

// ==================== الأقسام والتصنيفات ====================
type CatDef = { slug: string; nameAr: string; nameEn: string; icon: string; children?: { slug: string; nameAr: string; nameEn: string }[] };

const CATEGORIES: CatDef[] = [
  {
    slug: "vehicles", nameAr: "السيارات والمركبات", nameEn: "Vehicles", icon: "car",
    children: [
      { slug: "cars-sale", nameAr: "بيع وشراء السيارات", nameEn: "Cars for Sale" },
      { slug: "car-rental", nameAr: "تأجير السيارات", nameEn: "Car Rental" },
      { slug: "motorcycles-boats-equipment", nameAr: "الدراجات النارية والقوارب والمعدات", nameEn: "Motorcycles, Boats & Equipment" },
      { slug: "vehicle-inspection", nameAr: "فحص المركبات", nameEn: "Vehicle Inspection" },
      { slug: "vehicle-financing-insurance", nameAr: "تمويل وتأمين المركبات", nameEn: "Vehicle Financing & Insurance" },
      { slug: "vehicle-registration-transfer", nameAr: "تسجيل ونقل ملكية المركبات", nameEn: "Vehicle Registration & Transfer" },
    ],
  },
  {
    slug: "plates", nameAr: "لوحات المركبات", nameEn: "Vehicle Plates", icon: "hash",
    children: [
      { slug: "plates-sale", nameAr: "بيع وشراء اللوحات", nameEn: "Plates for Sale" },
      { slug: "plates-auction", nameAr: "مزادات اللوحات", nameEn: "Plate Auctions" },
      { slug: "plate-valuation", nameAr: "تقييم سعر اللوحة", nameEn: "Plate Valuation" },
      { slug: "plate-transfer", nameAr: "نقل أو تنازل عن اللوحة", nameEn: "Plate Transfer" },
    ],
  },
  {
    slug: "real-estate", nameAr: "العقارات", nameEn: "Real Estate", icon: "building",
    children: [
      { slug: "villas", nameAr: "فلل", nameEn: "Villas" },
      { slug: "apartments", nameAr: "شقق", nameEn: "Apartments" },
      { slug: "land", nameAr: "أراضٍ", nameEn: "Land" },
      { slug: "buildings", nameAr: "مبانٍ", nameEn: "Buildings" },
      { slug: "offices", nameAr: "مكاتب", nameEn: "Offices" },
      { slug: "shops", nameAr: "محلات", nameEn: "Shops" },
      { slug: "warehouses", nameAr: "مستودعات", nameEn: "Warehouses" },
      { slug: "labor-housing", nameAr: "سكن عمال", nameEn: "Labor Housing" },
      { slug: "commercial-investment", nameAr: "عقارات تجارية واستثمارية", nameEn: "Commercial & Investment" },
      { slug: "property-management", nameAr: "إدارة العقارات", nameEn: "Property Management" },
    ],
  },
  {
    slug: "vehicle-services", nameAr: "خدمات المركبات", nameEn: "Vehicle Services", icon: "wrench",
    children: [
      { slug: "recovery-towing", nameAr: "ريكفري وسحب المركبات", nameEn: "Recovery & Towing" },
      { slug: "inter-emirate-transport", nameAr: "نقل المركبات بين الإمارات", nameEn: "Inter-Emirate Vehicle Transport" },
      { slug: "mobile-car-wash", nameAr: "غسيل سيارات متنقل", nameEn: "Mobile Car Wash" },
      { slug: "polishing-detailing", nameAr: "التلميع والتفصيل", nameEn: "Polishing & Detailing" },
      { slug: "nano-ceramic", nameAr: "النانو سيراميك", nameEn: "Nano Ceramic" },
      { slug: "ppf", nameAr: "حماية PPF", nameEn: "Paint Protection Film" },
      { slug: "window-tinting", nameAr: "تظليل الزجاج", nameEn: "Window Tinting" },
      { slug: "workshops-maintenance", nameAr: "الورش والصيانة", nameEn: "Workshops & Maintenance" },
      { slug: "electrical-mechanical", nameAr: "كهرباء وميكانيكا", nameEn: "Electrical & Mechanical" },
      { slug: "oil-change", nameAr: "تبديل الزيوت", nameEn: "Oil Change" },
      { slug: "tires", nameAr: "الإطارات", nameEn: "Tires" },
      { slug: "mobile-battery", nameAr: "البطاريات المتنقلة", nameEn: "Mobile Battery Service" },
      { slug: "computer-diagnostics", nameAr: "فحص الكمبيوتر", nameEn: "Computer Diagnostics" },
      { slug: "ac-repair-vehicle", nameAr: "إصلاح المكيف", nameEn: "AC Repair" },
      { slug: "body-paint", nameAr: "السمكرة والصبغ", nameEn: "Body & Paint" },
      { slug: "glass-repair", nameAr: "إصلاح الزجاج", nameEn: "Glass Repair" },
      { slug: "car-keys", nameAr: "مفاتيح السيارات", nameEn: "Car Keys" },
    ],
  },
  {
    slug: "transport-delivery", nameAr: "النقل والتوصيل", nameEn: "Transport & Delivery", icon: "truck",
    children: [
      { slug: "delivery", nameAr: "توصيل الطلبات", nameEn: "Delivery" },
      { slug: "shipping", nameAr: "الشحن المحلي والدولي", nameEn: "Local & International Shipping" },
      { slug: "furniture-moving", nameAr: "نقل الأثاث", nameEn: "Furniture Moving" },
      { slug: "home-office-moving", nameAr: "نقل المنازل والمكاتب", nameEn: "Home & Office Moving" },
      { slug: "packing", nameAr: "التغليف", nameEn: "Packing" },
      { slug: "storage", nameAr: "التخزين", nameEn: "Storage" },
      { slug: "truck-rental", nameAr: "تأجير الشاحنات", nameEn: "Truck Rental" },
      { slug: "equipment-transport", nameAr: "نقل المعدات", nameEn: "Equipment Transport" },
      { slug: "courier", nameAr: "خدمات المندوبين", nameEn: "Courier Services" },
    ],
  },
  {
    slug: "home-services", nameAr: "خدمات المنازل", nameEn: "Home Services", icon: "home",
    children: [
      { slug: "cleaning", nameAr: "التنظيف", nameEn: "Cleaning" },
      { slug: "deep-cleaning", nameAr: "التنظيف العميق", nameEn: "Deep Cleaning" },
      { slug: "pest-control", nameAr: "مكافحة الحشرات", nameEn: "Pest Control" },
      { slug: "ac-maintenance", nameAr: "صيانة المكيفات", nameEn: "AC Maintenance" },
      { slug: "electrical", nameAr: "الكهرباء", nameEn: "Electrical" },
      { slug: "plumbing", nameAr: "السباكة", nameEn: "Plumbing" },
      { slug: "painting", nameAr: "الصبغ", nameEn: "Painting" },
      { slug: "carpentry", nameAr: "النجارة", nameEn: "Carpentry" },
      { slug: "gardening", nameAr: "الحدائق", nameEn: "Gardening" },
      { slug: "pools", nameAr: "المسابح", nameEn: "Pools" },
      { slug: "cctv", nameAr: "كاميرات المراقبة", nameEn: "CCTV" },
      { slug: "smart-homes", nameAr: "المنازل الذكية", nameEn: "Smart Homes" },
      { slug: "general-maintenance", nameAr: "الصيانة العامة", nameEn: "General Maintenance" },
      { slug: "furniture-assembly", nameAr: "تركيب الأثاث", nameEn: "Furniture Assembly" },
    ],
  },
  {
    slug: "business-services", nameAr: "خدمات الأعمال", nameEn: "Business Services", icon: "briefcase",
    children: [
      { slug: "company-formation", nameAr: "تأسيس الشركات", nameEn: "Company Formation" },
      { slug: "trade-licenses", nameAr: "الرخص التجارية", nameEn: "Trade Licenses" },
      { slug: "pro-services", nameAr: "خدمات PRO", nameEn: "PRO Services" },
      { slug: "visas", nameAr: "التأشيرات", nameEn: "Visas" },
      { slug: "printing-centers", nameAr: "مراكز الطباعة", nameEn: "Printing Centers" },
      { slug: "accounting-tax", nameAr: "المحاسبة والضرائب", nameEn: "Accounting & Tax" },
      { slug: "marketing", nameAr: "التسويق", nameEn: "Marketing" },
      { slug: "web-app-design", nameAr: "تصميم المواقع والتطبيقات", nameEn: "Web & App Design" },
      { slug: "printing-ads", nameAr: "الطباعة والإعلانات", nameEn: "Printing & Advertising" },
      { slug: "customs-clearance", nameAr: "الشحن والتخليص الجمركي", nameEn: "Shipping & Customs Clearance" },
    ],
  },
];

const PLANS = [
  { code: "free", nameAr: "مجانية", nameEn: "Free", priceMonthly: 0, priceYearly: 0, maxListings: 3, maxImagesPerListing: 5, maxBranches: 1, maxStaff: 1, hasFeaturedListing: false, hasTopSearchPlacement: false, hasVerifiedBadge: false, hasAdvancedAnalytics: false, monthlyMessagesQuota: 50 },
  { code: "basic", nameAr: "أساسية", nameEn: "Basic", priceMonthly: 99, priceYearly: 999, maxListings: 15, maxImagesPerListing: 10, maxBranches: 1, maxStaff: 3, hasFeaturedListing: false, hasTopSearchPlacement: false, hasVerifiedBadge: true, hasAdvancedAnalytics: false, monthlyMessagesQuota: 300 },
  { code: "pro", nameAr: "احترافية", nameEn: "Professional", priceMonthly: 299, priceYearly: 2999, maxListings: 60, maxImagesPerListing: 20, maxBranches: 3, maxStaff: 10, hasFeaturedListing: true, hasTopSearchPlacement: true, hasVerifiedBadge: true, hasAdvancedAnalytics: true, monthlyMessagesQuota: 1500 },
  { code: "premium", nameAr: "مميزة", nameEn: "Premium", priceMonthly: 799, priceYearly: 7999, maxListings: 999, maxImagesPerListing: 40, maxBranches: 10, maxStaff: 50, hasFeaturedListing: true, hasTopSearchPlacement: true, hasVerifiedBadge: true, hasAdvancedAnalytics: true, monthlyMessagesQuota: null },
];

async function main() {
  console.log("== Seeding UAE Services Hub ==");

  // ---------- RBAC ----------
  const permByCode = new Map<string, string>();
  for (const p of PERMISSIONS) {
    const rec = await db.permission.upsert({ where: { code: p.code }, update: {}, create: p });
    permByCode.set(p.code, rec.id);
  }
  const roleByCode = new Map<string, string>();
  for (const r of ROLES) {
    const rec = await db.role.upsert({ where: { code: r.code }, update: {}, create: r });
    roleByCode.set(r.code, rec.id);
    const perms = DEFAULT_ROLE_PERMISSIONS[r.code];
    for (const pc of perms) {
      await db.rolePermission.upsert({
        where: { roleId_permissionId: { roleId: rec.id, permissionId: permByCode.get(pc)! } },
        update: {},
        create: { roleId: rec.id, permissionId: permByCode.get(pc)! },
      });
    }
  }
  console.log(`✓ ${ROLES.length} أدوار، ${PERMISSIONS.length} صلاحية`);

  // ---------- الجغرافيا ----------
  const emirateByS = new Map<string, string>();
  const cityByS = new Map<string, string>();
  const regionIds: string[] = [];
  for (const [i, e] of GEO.entries()) {
    const em = await db.emirate.upsert({
      where: { slug: e.slug }, update: {},
      create: { slug: e.slug, nameAr: e.nameAr, nameEn: e.nameEn, sortOrder: i },
    });
    emirateByS.set(e.slug, em.id);
    for (const c of e.cities) {
      const city = await db.city.upsert({
        where: { emirateId_slug: { emirateId: em.id, slug: c.slug } }, update: {},
        create: { emirateId: em.id, slug: c.slug, nameAr: c.nameAr, nameEn: c.nameEn },
      });
      cityByS.set(c.slug, city.id);
      for (const rName of c.regions) {
        const rSlug = rName.replace(/\s+/g, "-");
        const reg = await db.region.upsert({
          where: { cityId_slug: { cityId: city.id, slug: rSlug } }, update: {},
          create: { cityId: city.id, slug: rSlug, nameAr: rName, nameEn: rName },
        });
        regionIds.push(reg.id);
      }
    }
  }
  console.log(`✓ ${GEO.length} إمارات، ${cityByS.size} مدن، ${regionIds.length} منطقة`);

  // ---------- الأقسام ----------
  const categoryIdBySlug = new Map<string, string>();
  for (const [i, top] of CATEGORIES.entries()) {
    const parent = await db.category.upsert({
      where: { slug: top.slug }, update: {},
      create: { slug: top.slug, nameAr: top.nameAr, nameEn: top.nameEn, icon: top.icon, sortOrder: i },
    });
    categoryIdBySlug.set(top.slug, parent.id);
    for (const [j, child] of (top.children ?? []).entries()) {
      const c = await db.category.upsert({
        where: { slug: child.slug }, update: {},
        create: { slug: child.slug, nameAr: child.nameAr, nameEn: child.nameEn, parentId: parent.id, sortOrder: j },
      });
      categoryIdBySlug.set(child.slug, c.id);
    }
  }
  console.log(`✓ ${categoryIdBySlug.size} قسم/تصنيف`);

  // ---------- خصائص ديناميكية (أمثلة السيارات/العقارات/اللوحات من المواصفة) ----------
  const carsSaleId = categoryIdBySlug.get("cars-sale")!;
  const carAttrs = [
    { key: "make", labelAr: "الشركة", labelEn: "Make", type: "STRING" as const, sortOrder: 1, isRequired: true },
    { key: "model", labelAr: "الموديل", labelEn: "Model", type: "STRING" as const, sortOrder: 2, isRequired: true },
    { key: "year", labelAr: "السنة", labelEn: "Year", type: "NUMBER" as const, sortOrder: 3, isRequired: true },
    { key: "mileage_km", labelAr: "المسافة المقطوعة", labelEn: "Mileage", type: "NUMBER" as const, unit: "km", sortOrder: 4 },
    {
      key: "fuel", labelAr: "نوع الوقود", labelEn: "Fuel", type: "SELECT" as const, sortOrder: 5,
      options: [{ value: "petrol", labelAr: "بنزين", labelEn: "Petrol" }, { value: "diesel", labelAr: "ديزل", labelEn: "Diesel" }, { value: "electric", labelAr: "كهربائي", labelEn: "Electric" }, { value: "hybrid", labelAr: "هجين", labelEn: "Hybrid" }],
    },
    {
      key: "transmission", labelAr: "ناقل الحركة", labelEn: "Transmission", type: "SELECT" as const, sortOrder: 6,
      options: [{ value: "automatic", labelAr: "أوتوماتيك", labelEn: "Automatic" }, { value: "manual", labelAr: "يدوي", labelEn: "Manual" }],
    },
    { key: "color", labelAr: "اللون", labelEn: "Color", type: "STRING" as const, sortOrder: 7 },
    {
      key: "specs", labelAr: "المواصفات", labelEn: "Specs", type: "SELECT" as const, sortOrder: 8,
      options: [{ value: "gcc", labelAr: "خليجي", labelEn: "GCC" }, { value: "us", labelAr: "وارد أمريكي", labelEn: "US Import" }, { value: "eu", labelAr: "وارد أوروبي", labelEn: "EU Import" }, { value: "other", labelAr: "أخرى", labelEn: "Other" }],
    },
    { key: "vin", labelAr: "رقم الهيكل", labelEn: "VIN", type: "STRING" as const, sortOrder: 9, isRequired: false },
  ];
  for (const a of carAttrs) {
    await db.attributeDefinition.upsert({
      where: { categoryId_key: { categoryId: carsSaleId, key: a.key } }, update: {},
      create: { categoryId: carsSaleId, ...a, options: a.options ?? undefined },
    });
  }

  for (const reSlug of ["villas", "apartments"]) {
    const catId = categoryIdBySlug.get(reSlug)!;
    const reAttrs = [
      { key: "area_sqft", labelAr: "المساحة", labelEn: "Area", type: "NUMBER" as const, unit: "sqft", sortOrder: 1, isRequired: true },
      { key: "bedrooms", labelAr: "عدد الغرف", labelEn: "Bedrooms", type: "NUMBER" as const, sortOrder: 2 },
      { key: "bathrooms", labelAr: "الحمامات", labelEn: "Bathrooms", type: "NUMBER" as const, sortOrder: 3 },
      { key: "furnished", labelAr: "مفروش", labelEn: "Furnished", type: "BOOLEAN" as const, sortOrder: 4 },
      { key: "parking", labelAr: "موقف سيارة", labelEn: "Parking", type: "BOOLEAN" as const, sortOrder: 5 },
    ];
    for (const a of reAttrs) {
      await db.attributeDefinition.upsert({
        where: { categoryId_key: { categoryId: catId, key: a.key } }, update: {},
        create: { categoryId: catId, ...a },
      });
    }
  }

  const platesSaleId = categoryIdBySlug.get("plates-sale")!;
  const plateAttrs = [
    { key: "plate_code", labelAr: "الكود", labelEn: "Code", type: "STRING" as const, sortOrder: 1, isRequired: true },
    { key: "plate_number", labelAr: "الرقم", labelEn: "Number", type: "STRING" as const, sortOrder: 2, isRequired: true },
    { key: "digit_count", labelAr: "عدد الخانات", labelEn: "Digit Count", type: "NUMBER" as const, sortOrder: 3 },
    {
      key: "ownership_type", labelAr: "نوع الملكية", labelEn: "Ownership Type", type: "SELECT" as const, sortOrder: 4,
      options: [{ value: "free", labelAr: "ملك حر", labelEn: "Freehold" }, { value: "mortgaged", labelAr: "رهن", labelEn: "Mortgaged" }],
    },
  ];
  for (const a of plateAttrs) {
    await db.attributeDefinition.upsert({
      where: { categoryId_key: { categoryId: platesSaleId, key: a.key } }, update: {},
      create: { categoryId: platesSaleId, ...a, options: a.options ?? undefined },
    });
  }
  console.log("✓ خصائص ديناميكية للسيارات والعقارات واللوحات");

  // ---------- الباقات ----------
  for (const p of PLANS) {
    await db.plan.upsert({ where: { code: p.code }, update: {}, create: p as any });
  }
  console.log(`✓ ${PLANS.length} باقات اشتراك`);

  // ---------- Super Admin ----------
  const adminPasswordHash = await argon2.hash("ChangeMe!Admin123", { type: argon2.argon2id });
  await db.user.upsert({
    where: { email: "admin@ush.local" },
    update: {},
    create: {
      email: "admin@ush.local",
      passwordHash: adminPasswordHash,
      fullName: "Super Admin (تجريبي)",
      roleId: roleByCode.get("SUPER_ADMIN")!,
      status: "ACTIVE",
      isEmailVerified: true,
      emirateId: emirateByS.get("dubai"),
      locale: "ar",
    },
  });
  console.log("✓ حساب Super Admin — admin@ush.local / ChangeMe!Admin123 (غيّره فورًا)");

  // ---------- مستخدمون وشركات تجريبية (معلَّمة بوضوح) ----------
  const demoPasswordHash = await argon2.hash("Demo!12345", { type: argon2.argon2id });

  const demoUser1 = await db.user.upsert({
    where: { email: "sara.demo@ush.local" }, update: {},
    create: {
      email: "sara.demo@ush.local", phone: "+971500000001", passwordHash: demoPasswordHash,
      fullName: "سارة أحمد (مستخدم تجريبي)", roleId: roleByCode.get("REGISTERED_USER")!,
      status: "ACTIVE", isEmailVerified: true, isPhoneVerified: true,
      emirateId: emirateByS.get("dubai"), locale: "ar",
    },
  });

  const demoCompanyOwner = await db.user.upsert({
    where: { email: "owner.demo@ush.local" }, update: {},
    create: {
      email: "owner.demo@ush.local", phone: "+971500000002", passwordHash: demoPasswordHash,
      fullName: "مالك معرض تجريبي", roleId: roleByCode.get("CAR_SHOWROOM")!,
      status: "ACTIVE", isEmailVerified: true, isPhoneVerified: true,
      emirateId: emirateByS.get("abu-dhabi"), locale: "ar",
    },
  });

  const demoCompany = await db.company.upsert({
    where: { ownerUserId: demoCompanyOwner.id }, update: {},
    create: {
      ownerUserId: demoCompanyOwner.id,
      name: "معرض الواحة للسيارات (بيانات تجريبية)",
      slug: "al-waha-motors-demo",
      descriptionAr: "بيانات تجريبية لغرض الاختبار فقط — ليست شركة حقيقية مسجّلة بالمنصة.",
      phone: "+97121234567",
      whatsapp: "+971500000002",
      status: "ACTIVE",
      isVerified: true,
      verifiedAt: new Date(),
      tradeLicenseNumber: "TEST-0000",
      openingHours: { sat: ["09:00", "20:00"], sun: ["09:00", "20:00"], mon: ["09:00", "20:00"], tue: ["09:00", "20:00"], wed: ["09:00", "20:00"], thu: ["09:00", "20:00"], fri: ["14:00", "20:00"] },
      coverage: { create: [{ emirateId: emirateByS.get("abu-dhabi")! }, { emirateId: emirateByS.get("dubai")! }] },
    },
  });

  const demoListing = await db.listing.upsert({
    where: { id: "demo-listing-1" }, update: {},
    create: {
      id: "demo-listing-1",
      ownerId: demoCompanyOwner.id,
      companyId: demoCompany.id,
      categoryId: carsSaleId,
      titleAr: "تويوتا لاندكروزر 2022 (إعلان تجريبي)",
      titleEn: "Toyota Land Cruiser 2022 (Demo Listing)",
      descriptionAr: "بيانات تجريبية لغرض اختبار المنصة فقط. حالة ممتازة، صيانة دورية، فحص شامل متوفر عند الطلب.",
      offerType: "SALE",
      price: 185000,
      isPriceNegotiable: true,
      emirateId: emirateByS.get("abu-dhabi")!,
      contactPhone: "+97121234567",
      whatsapp: "+971500000002",
      status: "PUBLISHED",
      verificationStatus: "VERIFIED",
      isFeatured: true,
      images: { create: [{ url: "/demo/car-1.svg", sortOrder: 0, isCover: true }] },
      attributes: {
        create: [
          { attributeDefinitionId: (await db.attributeDefinition.findFirstOrThrow({ where: { categoryId: carsSaleId, key: "make" } })).id, valueString: "Toyota" },
          { attributeDefinitionId: (await db.attributeDefinition.findFirstOrThrow({ where: { categoryId: carsSaleId, key: "model" } })).id, valueString: "Land Cruiser VXR" },
          { attributeDefinitionId: (await db.attributeDefinition.findFirstOrThrow({ where: { categoryId: carsSaleId, key: "year" } })).id, valueNumber: 2022 },
          { attributeDefinitionId: (await db.attributeDefinition.findFirstOrThrow({ where: { categoryId: carsSaleId, key: "mileage_km" } })).id, valueNumber: 32000 },
          { attributeDefinitionId: (await db.attributeDefinition.findFirstOrThrow({ where: { categoryId: carsSaleId, key: "fuel" } })).id, valueString: "petrol" },
          { attributeDefinitionId: (await db.attributeDefinition.findFirstOrThrow({ where: { categoryId: carsSaleId, key: "transmission" } })).id, valueString: "automatic" },
          { attributeDefinitionId: (await db.attributeDefinition.findFirstOrThrow({ where: { categoryId: carsSaleId, key: "specs" } })).id, valueString: "gcc" },
        ],
      },
    },
  });

  // إعلان عقاري تجريبي
  await db.listing.upsert({
    where: { id: "demo-listing-2" }, update: {},
    create: {
      id: "demo-listing-2",
      ownerId: demoUser1.id,
      categoryId: categoryIdBySlug.get("apartments")!,
      titleAr: "شقة غرفتين وصالة في دبي مارينا (إعلان تجريبي)",
      titleEn: "2BR Apartment in Dubai Marina (Demo Listing)",
      descriptionAr: "بيانات تجريبية لغرض اختبار المنصة فقط.",
      offerType: "RENT_YEARLY",
      price: 95000,
      emirateId: emirateByS.get("dubai")!,
      contactPhone: "+971500000001",
      status: "PUBLISHED",
      isFeatured: false,
      images: { create: [{ url: "/demo/apartment-1.svg", sortOrder: 0, isCover: true }] },
    },
  });

  // خدمة منزلية تجريبية (طلب + عرض سعر)
  const demoRequest = await db.serviceRequest.upsert({
    where: { id: "demo-request-1" }, update: {},
    create: {
      id: "demo-request-1",
      userId: demoUser1.id,
      categoryId: categoryIdBySlug.get("deep-cleaning")!,
      emirateId: emirateByS.get("dubai")!,
      budgetMin: 200,
      budgetMax: 500,
      details: "تنظيف عميق لشقة غرفتين وصالة (طلب تجريبي)",
      status: "AWAITING_QUOTES",
    },
  });

  await db.review.upsert({
    where: { id: "demo-review-1" }, update: {},
    create: {
      id: "demo-review-1",
      authorId: demoUser1.id,
      targetType: "COMPANY",
      companyId: demoCompany.id,
      rating: 5,
      comment: "تعامل ممتاز وسرعة في الرد (تقييم تجريبي).",
    },
  });

  console.log("✓ بيانات تجريبية: مستخدمون، شركة، إعلانات، طلب خدمة، تقييم");
  console.log("== اكتمل الـ Seed ==");
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await db.$disconnect();
  });
