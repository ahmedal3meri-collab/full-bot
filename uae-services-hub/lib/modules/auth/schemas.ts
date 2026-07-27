import { z } from "zod";

export const registerSchema = z
  .object({
    fullName: z.string().trim().min(2).max(120),
    email: z.string().trim().toLowerCase().email().optional().or(z.literal("")),
    phone: z
      .string()
      .trim()
      .regex(/^\+971[0-9]{8,9}$/, "رقم إماراتي يجب أن يبدأ بـ +971")
      .optional()
      .or(z.literal("")),
    password: z.string().min(8).max(72),
    emirateId: z.string().optional(),
  })
  .refine((d) => d.email || d.phone, { message: "أدخل بريدًا إلكترونيًا أو رقم هاتف", path: ["email"] });

export const loginSchema = z.object({
  identifier: z.string().trim().min(3), // email or phone
  password: z.string().min(1),
});

export type RegisterInput = z.infer<typeof registerSchema>;
export type LoginInput = z.infer<typeof loginSchema>;
