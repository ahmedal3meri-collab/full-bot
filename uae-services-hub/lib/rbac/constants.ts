// مصدر الحقيقة الوحيد لأدوار وصلاحيات النظام — يُستخدم في seed.ts وطبقة auth معًا.
// الأدوار الثمانية المخزّنة (الزائر = غير مسجّل، لا يُخزَّن كصف).

export const ROLES = [
  { code: "REGISTERED_USER", nameAr: "مستخدم مسجّل", nameEn: "Registered User" },
  { code: "INDIVIDUAL_PROVIDER", nameAr: "مقدم خدمة فردي", nameEn: "Individual Provider" },
  { code: "COMPANY", nameAr: "شركة", nameEn: "Company" },
  { code: "REAL_ESTATE_AGENT", nameAr: "وكيل عقاري", nameEn: "Real Estate Agent" },
  { code: "CAR_SHOWROOM", nameAr: "معرض سيارات", nameEn: "Car Showroom" },
  { code: "CONTENT_MODERATOR", nameAr: "مشرف محتوى", nameEn: "Content Moderator" },
  { code: "SYSTEM_ADMIN", nameAr: "مدير النظام", nameEn: "System Admin" },
  { code: "SUPER_ADMIN", nameAr: "Super Admin", nameEn: "Super Admin" },
] as const;

export type RoleCode = (typeof ROLES)[number]["code"];

export const PERMISSIONS = [
  { code: "listing:create", descAr: "إنشاء إعلان" },
  { code: "listing:edit_own", descAr: "تعديل إعلاناته الخاصة" },
  { code: "listing:delete_own", descAr: "حذف إعلاناته الخاصة" },
  { code: "listing:moderate", descAr: "مراجعة/حذف أي إعلان" },
  { code: "company:manage_own", descAr: "إدارة صفحة شركته" },
  { code: "quote:submit", descAr: "إرسال عرض سعر" },
  { code: "request:create", descAr: "إنشاء طلب خدمة" },
  { code: "review:write", descAr: "كتابة تقييم بعد إكمال طلب" },
  { code: "review:moderate", descAr: "مراجعة التقييمات" },
  { code: "report:review", descAr: "مراجعة البلاغات" },
  { code: "user:ban", descAr: "حظر مستخدمين" },
  { code: "admin:categories:manage", descAr: "إدارة الأقسام والتصنيفات" },
  { code: "admin:geography:manage", descAr: "إدارة الإمارات والمناطق" },
  { code: "admin:users:manage", descAr: "إدارة المستخدمين والصلاحيات" },
  { code: "admin:plans:manage", descAr: "إدارة الباقات والاشتراكات" },
  { code: "admin:ai:manage", descAr: "إدارة إعدادات الذكاء الاصطناعي وقاعدة المعرفة" },
  { code: "admin:audit:view", descAr: "عرض سجل العمليات" },
  { code: "admin:full_access", descAr: "وصول كامل (Super Admin)" },
] as const;

export type PermissionCode = (typeof PERMISSIONS)[number]["code"];

// خريطة الدور → الصلاحيات الافتراضية (قابلة للتعديل لاحقًا من لوحة الإدارة، هذا فقط seed أولي)
export const DEFAULT_ROLE_PERMISSIONS: Record<RoleCode, PermissionCode[]> = {
  REGISTERED_USER: ["listing:create", "listing:edit_own", "listing:delete_own", "request:create", "review:write"],
  INDIVIDUAL_PROVIDER: ["listing:create", "listing:edit_own", "listing:delete_own", "quote:submit", "review:write"],
  COMPANY: ["listing:create", "listing:edit_own", "listing:delete_own", "company:manage_own", "quote:submit", "review:write"],
  REAL_ESTATE_AGENT: ["listing:create", "listing:edit_own", "listing:delete_own", "company:manage_own", "review:write"],
  CAR_SHOWROOM: ["listing:create", "listing:edit_own", "listing:delete_own", "company:manage_own", "review:write"],
  CONTENT_MODERATOR: ["listing:moderate", "review:moderate", "report:review"],
  SYSTEM_ADMIN: [
    "listing:moderate",
    "review:moderate",
    "report:review",
    "user:ban",
    "admin:categories:manage",
    "admin:geography:manage",
    "admin:users:manage",
    "admin:plans:manage",
    "admin:ai:manage",
    "admin:audit:view",
  ],
  SUPER_ADMIN: PERMISSIONS.map((p) => p.code) as PermissionCode[],
};
