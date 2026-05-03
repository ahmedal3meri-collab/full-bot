from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, ChatMemberHandler, filters
import database as db
from utils.decorators import register_user, check_banned, group_admin_only


@register_user
@check_banned
@group_admin_only
async def set_welcome(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text("❌ هذا الأمر للمجموعات فقط.")
        return
    if not ctx.args:
        await update.message.reply_text(
            "❌ الاستخدام: `/setwelcome [الرسالة]`\n\nيمكنك استخدام:\n"
            "• `{name}` — اسم المستخدم\n"
            "• `{username}` — يوزر المستخدم\n"
            "• `{group}` — اسم المجموعة",
            parse_mode="Markdown"
        )
        return
    msg = " ".join(ctx.args)
    await db.update_group_settings(update.effective_chat.id, welcome_msg=msg)
    await update.message.reply_text(f"✅ تم تعيين رسالة الترحيب:\n\n_{msg}_", parse_mode="Markdown")


@register_user
@check_banned
@group_admin_only
async def set_goodbye(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text("❌ هذا الأمر للمجموعات فقط.")
        return
    if not ctx.args:
        await update.message.reply_text("❌ الاستخدام: `/setgoodbye [الرسالة]`", parse_mode="Markdown")
        return
    msg = " ".join(ctx.args)
    await db.update_group_settings(update.effective_chat.id, goodbye_msg=msg)
    await update.message.reply_text(f"✅ تم تعيين رسالة الوداع:\n\n_{msg}_", parse_mode="Markdown")


@register_user
@check_banned
@group_admin_only
async def antiflood_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text("❌ هذا الأمر للمجموعات فقط.")
        return
    if not ctx.args:
        settings = await db.get_group_settings(update.effective_chat.id)
        status = "مفعّل ✅" if settings["antiflood"] else "معطّل ❌"
        await update.message.reply_text(f"🛡️ حالة Anti-flood: {status}")
        return
    val = ctx.args[0].lower()
    if val in ("on", "1", "true", "نعم"):
        await db.update_group_settings(update.effective_chat.id, antiflood=1)
        await update.message.reply_text("✅ تم تفعيل Anti-flood.")
    elif val in ("off", "0", "false", "لا"):
        await db.update_group_settings(update.effective_chat.id, antiflood=0)
        await update.message.reply_text("❌ تم تعطيل Anti-flood.")
    else:
        await update.message.reply_text("❌ استخدم: `/antiflood on` أو `/antiflood off`", parse_mode="Markdown")


@register_user
@check_banned
@group_admin_only
async def pin_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ رد على الرسالة التي تريد تثبيتها.")
        return
    try:
        await update.message.reply_to_message.pin()
        await update.message.reply_text("📌 تم تثبيت الرسالة.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")


@register_user
@check_banned
@group_admin_only
async def unpin_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        await update.effective_chat.unpin_all_messages()
        await update.message.reply_text("📌 تم إلغاء تثبيت جميع الرسائل.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")


async def welcome_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handles new members joining groups."""
    if not update.message or not update.message.new_chat_members:
        return
    chat = update.effective_chat
    settings = await db.get_group_settings(chat.id)
    welcome_msg = settings.get("welcome_msg")
    if not welcome_msg:
        return
    for member in update.message.new_chat_members:
        if member.is_bot:
            continue
        name = member.first_name or "مستخدم"
        username = f"@{member.username}" if member.username else name
        msg = welcome_msg.replace("{name}", name).replace("{username}", username).replace("{group}", chat.title or "")
        await update.message.reply_text(msg)


async def goodbye_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handles members leaving groups."""
    if not update.message or not update.message.left_chat_member:
        return
    chat = update.effective_chat
    member = update.message.left_chat_member
    if member.is_bot:
        return
    settings = await db.get_group_settings(chat.id)
    goodbye_msg = settings.get("goodbye_msg")
    if not goodbye_msg:
        return
    name = member.first_name or "مستخدم"
    username = f"@{member.username}" if member.username else name
    msg = goodbye_msg.replace("{name}", name).replace("{username}", username).replace("{group}", chat.title or "")
    await update.message.reply_text(msg)


async def flood_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Anti-flood: mute users who send too many messages."""
    if not update.effective_chat or update.effective_chat.type == "private":
        return
    if not update.effective_user:
        return
    chat = update.effective_chat
    user = update.effective_user

    settings = await db.get_group_settings(chat.id)
    if not settings["antiflood"]:
        return

    limit = settings["antiflood_limit"]
    window = settings["antiflood_secs"]

    is_flood = await db.check_flood(user.id, chat.id, limit, window)
    if is_flood:
        try:
            from datetime import timedelta
            await chat.restrict_member(
                user.id,
                ChatPermissions(can_send_messages=False),
                until_date=60
            )
            await update.message.reply_text(
                f"⚠️ {user.first_name} تم كتمك لمدة دقيقة بسبب الإرسال المتكرر!"
            )
        except Exception:
            pass


def register(app):
    app.add_handler(CommandHandler("setwelcome", set_welcome))
    app.add_handler(CommandHandler("setgoodbye", set_goodbye))
    app.add_handler(CommandHandler("antiflood", antiflood_cmd))
    app.add_handler(CommandHandler("pin", pin_cmd))
    app.add_handler(CommandHandler("unpin", unpin_cmd))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, goodbye_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, flood_handler), group=5)
