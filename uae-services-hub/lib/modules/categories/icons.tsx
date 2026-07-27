import { Car, Hash, Building2, Wrench, Truck, Home, Briefcase, type LucideIcon } from "lucide-react";

export const CATEGORY_ICONS: Record<string, LucideIcon> = {
  car: Car,
  hash: Hash,
  building: Building2,
  wrench: Wrench,
  truck: Truck,
  home: Home,
  briefcase: Briefcase,
};

export function CategoryIcon({ icon, className }: { icon: string | null; className?: string }) {
  const Icon = (icon && CATEGORY_ICONS[icon]) || Briefcase;
  return <Icon className={className} />;
}
