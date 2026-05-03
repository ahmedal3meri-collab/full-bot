"""
Full-Featured Telegram Bot
==========================
Features:
  • 20 Specialized AI Agents (Claude-powered)
  • Games: Dice, Flip, RPS, Trivia, 8-Ball, Slots, Guessing
  • Tools: Calc, Weather, Translate, QR, Password, Hash, Base64, UUID, Time, Wiki
  • Notes & Reminders system
  • Group management: Welcome/Goodbye, Anti-flood, Pin
  • Admin panel: Stats, Ban/Unban, Broadcast, Manage Admins
  • Inline mode
  • Arabic/English bilingual support
"""

import asyncio
import logging
import sys
from telegram import BotCommand
from telegram.ext import Application, ApplicationBuilder

from config import BOT_TOKEN
import database as db
import handlers.start as start_h
import handlers.admin as admin_h
import handlers.games as games_h
import handlers.utilities as utilities_h
import handlers.notes as notes_h
import handlers.reminders as reminders_h
import handlers.group as group_h
import handlers.agents as agents_h
import handlers.inline as inline_h

logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s: %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


BOT_COMMANDS = [
    # AI Agents
    BotCommand("agents", "🤖 عرض وتفعيل إيجنت ذكاء اصطناعي"),
    BotCommand("agent", "🤖 تفعيل إيجنت محدد"),
    BotCommand("chat", "💬 محادثة مع الإيجنت النشط"),
    BotCommand("reset", "🔄 إعادة تعيين المحادثة"),
    # Games
    BotCommand("dice", "🎲 رمي النرد"),
    BotCommand("flip", "🪙 رمي العملة"),
    BotCommand("rps", "✊ حجر ورقة مقص"),
    BotCommand("trivia", "❓ أسئلة ثقافية"),
    BotCommand("8ball", "🎱 الكرة السحرية"),
    BotCommand("slot", "🎰 ماكينة الحظ"),
    BotCommand("guess", "🎯 تخمين الرقم"),
    # Tools
    BotCommand("calc", "🧮 حاسبة"),
    BotCommand("weather", "🌤️ الطقس"),
    BotCommand("translate", "🌐 ترجمة"),
    BotCommand("qr", "📷 QR Code"),
    BotCommand("password", "🔐 كلمة مرور"),
    BotCommand("hash", "🔒 هاش"),
    BotCommand("encode", "📤 Base64"),
    BotCommand("decode", "📥 فك Base64"),
    BotCommand("uuid", "🆔 UUID"),
    BotCommand("time", "🕐 الوقت"),
    BotCommand("wiki", "📚 ويكيبيديا"),
    # Fun
    BotCommand("joke", "😂 نكتة"),
    BotCommand("quote", "💭 اقتباس"),
    BotCommand("fact", "🔬 معلومة"),
    BotCommand("ascii", "🔤 ASCII Art"),
    # Notes
    BotCommand("save", "📝 حفظ ملاحظة"),
    BotCommand("get", "📖 جلب ملاحظة"),
    BotCommand("notes", "📋 ملاحظاتي"),
    BotCommand("delnote", "🗑️ حذف ملاحظة"),
    # Reminders
    BotCommand("remind", "⏰ تذكير"),
    BotCommand("reminders", "📅 تذكيراتي"),
    BotCommand("cancel", "❌ إلغاء تذكير"),
    # Account
    BotCommand("profile", "👤 ملفي الشخصي"),
    BotCommand("language", "🌐 تغيير اللغة"),
    # Group
    BotCommand("setwelcome", "👋 رسالة ترحيب"),
    BotCommand("setgoodbye", "👋 رسالة وداع"),
    BotCommand("antiflood", "🛡️ مكافحة الفيضان"),
    BotCommand("pin", "📌 تثبيت رسالة"),
    BotCommand("unpin", "📌 إلغاء التثبيت"),
    # Admin
    BotCommand("stats", "📊 الإحصائيات"),
    BotCommand("broadcast", "📢 بث رسالة"),
    BotCommand("ban", "🚫 حظر مستخدم"),
    BotCommand("unban", "✅ رفع الحظر"),
    BotCommand("addadmin", "👑 إضافة مدير"),
    BotCommand("removeadmin", "👑 إزالة مدير"),
    BotCommand("users", "👥 قائمة المستخدمين"),
    # Help
    BotCommand("start", "🏠 الشاشة الرئيسية"),
    BotCommand("help", "📖 قائمة الأوامر"),
]


async def post_init(app: Application):
    await db.init_db()
    await app.bot.set_my_commands(BOT_COMMANDS)
    me = await app.bot.get_me()
    logger.info(f"✅ Bot started: @{me.username} (ID: {me.id})")
    logger.info(f"📦 Loaded handlers: start, admin, games, utilities, notes, reminders, group, agents, inline")


def main():
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN is not set! Add it to .env file.")
        sys.exit(1)

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Register all handlers
    start_h.register(app)
    admin_h.register(app)
    games_h.register(app)
    utilities_h.register(app)
    notes_h.register(app)
    reminders_h.register(app)
    group_h.register(app)
    agents_h.register(app)
    inline_h.register(app)

    logger.info("🚀 Starting bot polling...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
