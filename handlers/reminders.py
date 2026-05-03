from datetime import datetime, timezone, timedelta
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import database as db
from utils.decorators import register_user, check_banned
from utils.helpers import parse_time
from config import MAX_REMINDERS


@register_user
@check_banned
async def remind_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    lang = await db.get_user_language(user.id)

    if len(ctx.args) < 2:
        msg = (
            "❌ الاستخدام: `/remind [وقت] [النص]`\n\n"
            "أمثلة:\n"
            "• `/remind 10m اجتماع مهم`\n"
            "• `/remind 1h اتصل بالعميل`\n"
            "• `/remind 2d تجديد الاشتراك`"
        ) if lang == "ar" else (
            "❌ Usage: `/remind [time] [text]`\n\n"
            "Examples:\n"
            "• `/remind 10m important meeting`\n"
            "• `/remind 1h call client`\n"
            "• `/remind 2d renew subscription`"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    delta = parse_time(ctx.args[0])
    if not delta:
        err = "❌ صيغة الوقت غير صحيحة. استخدم: 30s, 10m, 2h, 1d" if lang == "ar" else "❌ Invalid time format. Use: 30s, 10m, 2h, 1d"
        await update.message.reply_text(err)
        return

    if delta < timedelta(seconds=30):
        err = "❌ الحد الأدنى 30 ثانية." if lang == "ar" else "❌ Minimum time is 30 seconds."
        await update.message.reply_text(err)
        return

    if delta > timedelta(days=365):
        err = "❌ الحد الأقصى سنة واحدة." if lang == "ar" else "❌ Maximum time is 1 year."
        await update.message.reply_text(err)
        return

    count = await db.count_reminders(user.id, chat.id)
    if count >= MAX_REMINDERS:
        err = f"❌ وصلت الحد الأقصى ({MAX_REMINDERS} تذكيرات)." if lang == "ar" else f"❌ You've reached the limit ({MAX_REMINDERS} reminders)."
        await update.message.reply_text(err)
        return

    text = " ".join(ctx.args[1:])
    remind_at = datetime.utcnow() + delta
    rid = await db.add_reminder(user.id, chat.id, text, remind_at)

    # Format the time in a readable way
    minutes = int(delta.total_seconds() / 60)
    if minutes < 60:
        time_str = f"{minutes} دقيقة" if lang == "ar" else f"{minutes} minutes"
    elif minutes < 1440:
        hours = minutes // 60
        time_str = f"{hours} ساعة" if lang == "ar" else f"{hours} hours"
    else:
        days = minutes // 1440
        time_str = f"{days} يوم" if lang == "ar" else f"{days} days"

    msg = f"⏰ تم ضبط التذكير!\n\n📌 ID: `{rid}`\n⏱️ بعد: {time_str}\n📝 النص: {text}" if lang == "ar" else f"⏰ Reminder set!\n\n📌 ID: `{rid}`\n⏱️ In: {time_str}\n📝 Text: {text}"
    await update.message.reply_text(msg, parse_mode="Markdown")


@register_user
@check_banned
async def list_reminders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    lang = await db.get_user_language(user.id)

    reminders = await db.list_reminders(user.id, chat.id)
    if not reminders:
        msg = "⏰ لا توجد تذكيرات نشطة." if lang == "ar" else "⏰ No active reminders."
        await update.message.reply_text(msg)
        return

    header = f"⏰ **تذكيراتك ({len(reminders)}):**\n\n" if lang == "ar" else f"⏰ **Your Reminders ({len(reminders)}):**\n\n"
    lines = []
    for r in reminders:
        rid = r["id"]
        text = r["text"][:50]
        remind_at = r["remind_at"][:16]
        lines.append(f"• `#{rid}` — {text}\n  ⏱️ {remind_at}")
    footer = "\n\nاستخدم `/cancel [id]` لإلغاء تذكير." if lang == "ar" else "\n\nUse `/cancel [id]` to cancel."
    await update.message.reply_text(header + "\n".join(lines) + footer, parse_mode="Markdown")


@register_user
@check_banned
async def cancel_reminder(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)

    if not ctx.args:
        msg = "❌ الاستخدام: `/cancel [id]`" if lang == "ar" else "❌ Usage: `/cancel [id]`"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    try:
        rid = int(ctx.args[0])
    except ValueError:
        err = "❌ معرف غير صحيح." if lang == "ar" else "❌ Invalid ID."
        await update.message.reply_text(err)
        return

    deleted = await db.cancel_reminder(user.id, rid)
    if deleted:
        text = f"✅ تم إلغاء التذكير `#{rid}`." if lang == "ar" else f"✅ Reminder `#{rid}` cancelled."
    else:
        text = f"❌ لم أجد تذكيراً بالمعرف `#{rid}`." if lang == "ar" else f"❌ Reminder `#{rid}` not found."
    await update.message.reply_text(text, parse_mode="Markdown")


async def check_reminders(ctx: ContextTypes.DEFAULT_TYPE):
    """Job that fires every minute to send due reminders."""
    pending = await db.get_pending_reminders()
    for r in pending:
        try:
            await ctx.bot.send_message(
                r["chat_id"],
                f"⏰ **تذكير!**\n\n{r['text']}",
                parse_mode="Markdown"
            )
            await db.mark_reminder_done(r["id"])
        except Exception:
            await db.mark_reminder_done(r["id"])


def register(app):
    app.add_handler(CommandHandler("remind", remind_cmd))
    app.add_handler(CommandHandler("reminders", list_reminders))
    app.add_handler(CommandHandler("cancel", cancel_reminder))
    app.job_queue.run_repeating(check_reminders, interval=30, first=10)
