// مصدر مركزي واحد لاسم المشروع/الشعار/الألوان — كما طُلب صراحة، تعديله هنا يكفي
// (لوحة إدارة لتعديل هذه القيم من واجهة بدل الكود هي مهمة المرحلة 4، غير مبنية بعد)

export const siteConfig = {
  nameAr: "مركز الخدمات الإماراتي",
  nameEn: "UAE Services Hub",
  shortNameAr: "الخدمات",
  shortNameEn: "USH",
  descriptionAr: "منصة إماراتية موحّدة للبيع والشراء والإيجار والخدمات المحلية",
  descriptionEn: "A unified UAE platform for buying, selling, renting and local services",
  defaultLocale: "ar" as const,
  locales: ["ar", "en"] as const,
  logoText: "USH",
  colors: {
    brand950: "#16210f",
    brand900: "#1f2b1a",
    brand700: "#3a4d2c",
    sand100: "#f2ead9",
    sand50: "#faf7ef",
    gold500: "#b8925a",
    gold600: "#9c7743",
  },
  currency: "AED",
};

export type SiteConfig = typeof siteConfig;
