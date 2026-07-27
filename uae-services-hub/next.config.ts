import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./i18n/request.ts");

const nextConfig: NextConfig = {
  output: "standalone", // لبناء Docker إنتاج خفيف — راجع docker/web.Dockerfile
  images: {
    remotePatterns: [
      { protocol: "http", hostname: "localhost" },
      { protocol: "http", hostname: "minio", port: "9000" },
    ],
  },
};

export default withNextIntl(nextConfig);
