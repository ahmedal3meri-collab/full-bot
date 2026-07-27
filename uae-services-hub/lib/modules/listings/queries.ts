import { prisma } from "@/lib/db/client";
import type { Prisma } from "@prisma/client";

const listingCardInclude = {
  images: { orderBy: { sortOrder: "asc" as const }, take: 1 },
  category: true,
  emirate: true,
} satisfies Prisma.ListingInclude;

export function getFeaturedListings(limit = 8) {
  return prisma.listing.findMany({
    where: { status: "PUBLISHED", isFeatured: true },
    orderBy: { createdAt: "desc" },
    take: limit,
    include: listingCardInclude,
  });
}

export function getLatestListings(limit = 12) {
  return prisma.listing.findMany({
    where: { status: "PUBLISHED" },
    orderBy: { createdAt: "desc" },
    take: limit,
    include: listingCardInclude,
  });
}

export function getListingsByCategorySlug(
  categorySlug: string,
  opts: { emirateSlug?: string; minPrice?: number; maxPrice?: number; page?: number; pageSize?: number } = {}
) {
  const { emirateSlug, minPrice, maxPrice, page = 1, pageSize = 20 } = opts;
  const where: Prisma.ListingWhereInput = {
    status: "PUBLISHED",
    category: { slug: categorySlug },
    ...(emirateSlug ? { emirate: { slug: emirateSlug } } : {}),
    ...(minPrice != null || maxPrice != null
      ? { price: { gte: minPrice ?? undefined, lte: maxPrice ?? undefined } }
      : {}),
  };
  return prisma.$transaction([
    prisma.listing.findMany({
      where,
      orderBy: [{ isFeatured: "desc" }, { createdAt: "desc" }],
      skip: (page - 1) * pageSize,
      take: pageSize,
      include: listingCardInclude,
    }),
    prisma.listing.count({ where }),
  ]);
}

export async function getListingById(id: string) {
  const listing = await prisma.listing.findUnique({
    where: { id },
    include: {
      images: { orderBy: { sortOrder: "asc" } },
      videos: true,
      category: true,
      emirate: true,
      city: true,
      region: true,
      owner: { select: { id: true, fullName: true, avatarUrl: true } },
      company: true,
      attributes: { include: { attributeDefinition: true } },
    },
  });
  if (listing) {
    prisma.listing.update({ where: { id }, data: { viewsCount: { increment: 1 } } }).catch(() => {});
  }
  return listing;
}
