from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import database as db
from utils.decorators import register_user, check_banned, admin_only
from config import ADMIN_IDS
import humanize


@register_user
@check_banned
@admin_only
async def stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    s = await db.get_stats()
    text = (
        "📊 **إحصائيات البوت**\n\n"
        f"👥 إجمالي المستخدمين: `{s['total_users']:,}`\n"
        f"🚫 المحظورون: `{s['banned']}`\n"
        f"📝 الملاحظات: `{s['notes']:,}`\n"
        f"⏰ التذكيرات النشطة: `{s['active_reminders']}`\n"
        f"💬 إجمالي الرسائل: `{s['total_messages']:,}`\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


@register_user
@check_banned
@admin_only
async def broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("❌ الاستخدام: /broadcast [الرسالة]")
        return
    text = " ".join(ctx.args)
    users = await db.get_all_users()
    sent = 0
    failed = 0
    msg = await update.message.reply_text(f"⏳ إرسال إلى {len(users)} مستخدم...")
    for user in users:
        try:
            await ctx.bot.send_message(user["user_id"], f"📢 **إعلان:**\n\n{text}", parse_mode="Markdown")
            sent += 1
        except Exception:
            failed += 1
    await msg.edit_text(f"✅ تم الإرسال!\n\n✅ ناجح: {sent}\n❌ فشل: {failed}")


@register_user
@check_banned
@admin_only
async def ban_user(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("❌ الاستخدام: /ban [user_id]")
        return
    try:
        uid = int(ctx.args[0])
    except ValueError:
        await update.message.reply_text("❌ معرف غير صحيح.")
        return
    if uid in ADMIN_IDS:
        await update.message.reply_text("❌ لا يمكن حظر مدير.")
        return
    await db.ban_user(uid)
    await update.message.reply_text(f"🚫 تم حظر المستخدم `{uid}`.", parse_mode="Markdown")


@register_user
@check_banned
@admin_only
async def unban_user(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("❌ الاستخدام: /unban [user_id]")
        return
    try:
        uid = int(ctx.args[0])
    except ValueError:
        await update.message.reply_text("❌ معرف غير صحيح.")
        return
    await db.unban_user(uid)
    await update.message.reply_text(f"✅ تم رفع الحظر عن `{uid}`.", parse_mode="Markdown")


@register_user
@check_banned
@admin_only
async def add_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("❌ الاستخدام: /addadmin [user_id]")
        return
    try:
        uid = int(ctx.args[0])
    except ValueError:
        await update.message.reply_text("❌ معرف غير صحيح.")
        return
    await db.set_admin(uid, True)
    await update.message.reply_text(f"✅ تم تعيين `{uid}` مديراً.", parse_mode="Markdown")


@register_user
@check_banned
@admin_only
async def remove_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("❌ الاستخدام: /removeadmin [user_id]")
        return
    try:
        uid = int(ctx.args[0])
    except ValueError:
        await update.message.reply_text("❌ معرف غير صحيح.")
        return
    if uid in ADMIN_IDS:
        await update.message.reply_text("❌ لا يمكن إزالة مدير رئيسي.")
        return
    await db.set_admin(uid, False)
    await update.message.reply_text(f"✅ تم إزالة صلاحيات المدير عن `{uid}`.", parse_mode="Markdown")


@register_user
@check_banned
@admin_only
async def users_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    users = await db.get_all_users()
    if not users:
        await update.message.reply_text("لا يوجد مستخدمون.")
        return
    lines = ["👥 **قائمة المستخدمين** (أول 20)\n"]
    for u in users[:20]:
        name = u.get("first_name") or "مجهول"
        uname = f"@{u['username']}" if u.get("username") else "-"
        lines.append(f"• `{u['user_id']}` — {name} ({uname})")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


def register(app):
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("addadmin", add_admin))
    app.add_handler(CommandHandler("removeadmin", remove_admin))
    app.add_handler(CommandHandler("users", users_list))
