from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import database as db
from utils.decorators import register_user, check_banned
from config import MAX_NOTES


@register_user
@check_banned
async def save_note(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    lang = await db.get_user_language(user.id)

    if len(ctx.args) < 2:
        msg = "❌ الاستخدام: `/save [الاسم] [المحتوى]`" if lang == "ar" else "❌ Usage: `/save [name] [content]`"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    name = ctx.args[0].lower()
    content = " ".join(ctx.args[1:])

    count = await db.count_notes(user.id, chat.id)
    if count >= MAX_NOTES:
        err = f"❌ وصلت الحد الأقصى ({MAX_NOTES} ملاحظة). احذف ملاحظات قديمة أولاً." if lang == "ar" else f"❌ You've reached the limit ({MAX_NOTES} notes). Delete some first."
        await update.message.reply_text(err)
        return

    await db.save_note(user.id, chat.id, name, content)
    text = f"✅ تم حفظ الملاحظة: **{name}**" if lang == "ar" else f"✅ Note saved: **{name}**"
    await update.message.reply_text(text, parse_mode="Markdown")


@register_user
@check_banned
async def get_note(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    lang = await db.get_user_language(user.id)

    if not ctx.args:
        msg = "❌ الاستخدام: `/get [الاسم]`" if lang == "ar" else "❌ Usage: `/get [name]`"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    name = ctx.args[0].lower()
    content = await db.get_note(user.id, chat.id, name)
    if content is None:
        err = f"❌ لم أجد ملاحظة بالاسم: **{name}**" if lang == "ar" else f"❌ No note found: **{name}**"
        await update.message.reply_text(err, parse_mode="Markdown")
        return

    header = f"📝 **{name}:**\n\n" if lang == "ar" else f"📝 **{name}:**\n\n"
    await update.message.reply_text(header + content, parse_mode="Markdown")


@register_user
@check_banned
async def list_notes(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    lang = await db.get_user_language(user.id)

    notes = await db.list_notes(user.id, chat.id)
    if not notes:
        msg = "📝 لا توجد ملاحظات محفوظة." if lang == "ar" else "📝 No notes saved."
        await update.message.reply_text(msg)
        return

    header = f"📝 **ملاحظات ({len(notes)}):**\n\n" if lang == "ar" else f"📝 **Notes ({len(notes)}):**\n\n"
    lines = []
    for name, date, is_private, note_user_id in notes:
        icon = "🔒" if is_private else "🌐"
        if note_user_id == user.id:
            lines.append(f"{icon} `{name}` — _{date[:10]}_")
        else:
            label = "(عامة)" if lang == "ar" else "(public)"
            lines.append(f"{icon} `{name}` — _{label}_")
    footer_ar = (
        "\n\nاستخدم `/get [الاسم]` لقراءة ملاحظة."
        "\nاستخدم `/noteprivacy [الاسم] public|private` لتغيير الخصوصية."
    )
    footer_en = (
        "\n\nUse `/get [name]` to read a note."
        "\nUse `/noteprivacy [name] public|private` to change privacy."
    )
    footer = footer_ar if lang == "ar" else footer_en
    await update.message.reply_text(header + "\n".join(lines) + footer, parse_mode="Markdown")


@register_user
@check_banned
async def del_note(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    lang = await db.get_user_language(user.id)

    if not ctx.args:
        msg = "❌ الاستخدام: `/delnote [الاسم]`" if lang == "ar" else "❌ Usage: `/delnote [name]`"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    name = ctx.args[0].lower()
    deleted = await db.delete_note(user.id, chat.id, name)
    if deleted:
        text = f"✅ تم حذف الملاحظة: **{name}**" if lang == "ar" else f"✅ Note deleted: **{name}**"
    else:
        text = f"❌ لم أجد ملاحظة بالاسم: **{name}**" if lang == "ar" else f"❌ Note not found: **{name}**"
    await update.message.reply_text(text, parse_mode="Markdown")


@register_user
@check_banned
async def note_privacy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    lang = await db.get_user_language(user.id)

    if len(ctx.args) < 2:
        msg = (
            "❌ الاستخدام: `/noteprivacy [الاسم] [public/private]`\n\n"
            "• `public` — الملاحظة مرئية للجميع في المجموعة 🌐\n"
            "• `private` — الملاحظة خاصة بك فقط 🔒"
        ) if lang == "ar" else (
            "❌ Usage: `/noteprivacy [name] [public/private]`\n\n"
            "• `public` — note visible to everyone in the group 🌐\n"
            "• `private` — note visible only to you 🔒"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    name = ctx.args[0].lower()
    visibility = ctx.args[1].lower()

    if visibility in ("public", "عام", "عامة"):
        is_private = 0
        status = "عامة 🌐" if lang == "ar" else "public 🌐"
    elif visibility in ("private", "خاص", "خاصة"):
        is_private = 1
        status = "خاصة 🔒" if lang == "ar" else "private 🔒"
    else:
        msg = "❌ استخدم `public` أو `private`" if lang == "ar" else "❌ Use `public` or `private`"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    updated = await db.set_note_privacy(user.id, chat.id, name, is_private)
    if updated:
        text = (
            f"✅ تم تغيير خصوصية الملاحظة **{name}** إلى {status}"
        ) if lang == "ar" else (
            f"✅ Note **{name}** is now {status}"
        )
    else:
        text = (
            f"❌ لم أجد ملاحظة بالاسم: **{name}**"
        ) if lang == "ar" else (
            f"❌ Note not found: **{name}**"
        )
    await update.message.reply_text(text, parse_mode="Markdown")


def register(app):
    app.add_handler(CommandHandler("save", save_note))
    app.add_handler(CommandHandler("get", get_note))
    app.add_handler(CommandHandler("notes", list_notes))
    app.add_handler(CommandHandler("delnote", del_note))
    app.add_handler(CommandHandler("noteprivacy", note_privacy))
