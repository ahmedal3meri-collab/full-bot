import { prisma } from "@/lib/db/client";

export function getVerifiedCompanies(limit = 6) {
  return prisma.company.findMany({
    where: { status: "ACTIVE", isVerified: true },
    orderBy: { createdAt: "desc" },
    take: limit,
  });
}

export function getCompanyBySlug(slug: string) {
  return prisma.company.findUnique({
    where: { slug },
    include: {
      coverage: { include: { emirate: true } },
      services: { include: { category: true } },
      portfolio: true,
      listings: { where: { status: "PUBLISHED" }, include: { images: { take: 1 } } },
      reviews: { orderBy: { createdAt: "desc" }, take: 10, include: { author: { select: { fullName: true } } } },
    },
  });
}
