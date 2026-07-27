// يُحقَن كـ inline script قبل الرسم لمنع وميض التبديل بين الوضعين (FOUC)
export const themeInitScript = `
(function () {
  try {
    var stored = localStorage.getItem("ush-theme");
    if (stored === "dark" || stored === "light") {
      document.documentElement.setAttribute("data-theme", stored);
    }
  } catch (e) {}
})();
`;
