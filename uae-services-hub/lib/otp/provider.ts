import "server-only";

// طبقة OTP قابلة لربط مزود SMS حقيقي لاحقًا (Unifonic/Twilio/Etisalat) — راجع REQUIRED_USER_INPUT.md #2
// الوضع الحالي: "console" — يطبع الكود في اللوغ بدل الإرسال الفعلي، حتى تعمل رحلة التحقق كاملة أثناء التطوير.

export interface OtpProvider {
  send(destination: string, code: string): Promise<void>;
}

class ConsoleOtpProvider implements OtpProvider {
  async send(destination: string, code: string): Promise<void> {
    // eslint-disable-next-line no-console
    console.log(`[OTP:console] ${destination} → ${code}`);
  }
}

// نقطة التوسّع: أضف Twilio/Unifonic هنا واقرأ OTP_PROVIDER من env لاختيار المزود
export function getOtpProvider(): OtpProvider {
  const provider = process.env.OTP_PROVIDER ?? "console";
  switch (provider) {
    case "console":
    default:
      return new ConsoleOtpProvider();
  }
}

export function generateOtpCode(): string {
  return String(Math.floor(100000 + Math.random() * 900000));
}
