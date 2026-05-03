from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
import database as db
from locales.strings import t
from utils.keyboards import main_menu_kb, language_kb, back_kb
from utils.decorators import register_user, check_banned
from config import ADMIN_IDS


@register_user
@check_banned
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    name = user.first_name or "مستخدم"
    text = t("start_msg", lang, name=name)
    await update.message.reply_text(
        text, parse_mode="Markdown", reply_markup=main_menu_kb(lang)
    )


@register_user
@check_banned
async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    await update.message.reply_text(t("help_msg", lang), parse_mode="Markdown")


@register_user
@check_banned
async def profile(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    db_user = await db.get_user(user.id)
    if not db_user:
        await update.message.reply_text("❌")
        return

    agent_id = await db.get_user_agent(user.id)
    is_admin = user.id in ADMIN_IDS or db_user.get("is_admin")

    if lang == "ar":
        text = (
            f"👤 **ملفك الشخصي**\n\n"
            f"🆔 المعرف: `{user.id}`\n"
            f"📛 الاسم: {user.first_name or '-'} {user.last_name or ''}\n"
            f"🔖 اليوزر: @{user.username or '-'}\n"
            f"🌐 اللغة: {'العربية' if lang == 'ar' else 'English'}\n"
            f"🤖 الإيجنت النشط: {agent_id}\n"
            f"💬 إجمالي الرسائل: {db_user['total_msgs']:,}\n"
            f"📅 تاريخ الانضمام: {db_user['joined_at'][:10]}\n"
            f"⏰ آخر ظهور: {db_user['last_seen'][:10]}\n"
            f"👑 مدير: {'نعم' if is_admin else 'لا'}\n"
        )
    else:
        text = (
            f"👤 **Your Profile**\n\n"
            f"🆔 ID: `{user.id}`\n"
            f"📛 Name: {user.first_name or '-'} {user.last_name or ''}\n"
            f"🔖 Username: @{user.username or '-'}\n"
            f"🌐 Language: {'Arabic' if lang == 'ar' else 'English'}\n"
            f"🤖 Active Agent: {agent_id}\n"
            f"💬 Total Messages: {db_user['total_msgs']:,}\n"
            f"📅 Joined: {db_user['joined_at'][:10]}\n"
            f"⏰ Last Seen: {db_user['last_seen'][:10]}\n"
            f"👑 Admin: {'Yes' if is_admin else 'No'}\n"
        )
    await update.message.reply_text(text, parse_mode="Markdown")


@register_user
@check_banned
async def language_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    label = "🌐 اختر لغتك:" if lang == "ar" else "🌐 Choose your language:"
    await update.message.reply_text(label, reply_markup=language_kb())


async def menu_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    lang = await db.get_user_language(user.id)
    data = query.data

    if data == "menu_main":
        name = user.first_name or "مستخدم"
        await query.edit_message_text(
            t("start_msg", lang, name=name),
            parse_mode="Markdown",
            reply_markup=main_menu_kb(lang)
        )

    elif data == "menu_games":
        if lang == "ar":
            text = (
                "🎮 **الألعاب**\n\n"
                "/dice — رمي النرد\n"
                "/flip — رمي العملة\n"
                "/rps — حجر ورقة مقص\n"
                "/trivia — أسئلة ثقافية\n"
                "/8ball [سؤال] — الكرة السحرية\n"
                "/slot — ماكينة الحظ\n"
                "/guess — تخمين الرقم\n"
            )
        else:
            text = (
                "🎮 **Games**\n\n"
                "/dice — Roll dice\n"
                "/flip — Flip coin\n"
                "/rps — Rock Paper Scissors\n"
                "/trivia — Trivia\n"
                "/8ball [question] — Magic 8-ball\n"
                "/slot — Slot machine\n"
                "/guess — Number guessing\n"
            )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_kb("main", lang))

    elif data == "menu_tools":
        if lang == "ar":
            text = (
                "🛠️ **الأدوات**\n\n"
                "/calc [عملية] — حاسبة\n"
                "/weather [مدينة] — الطقس\n"
                "/translate [لغة] [نص] — ترجمة\n"
                "/qr [نص] — QR Code\n"
                "/password [طول] — كلمة مرور\n"
                "/hash [نص] — هاش\n"
                "/encode [نص] — Base64\n"
                "/decode [نص] — فك Base64\n"
                "/uuid — UUID\n"
                "/time [مدينة] — الوقت\n"
                "/wiki [موضوع] — ويكيبيديا\n"
            )
        else:
            text = (
                "🛠️ **Tools**\n\n"
                "/calc [expr] — Calculator\n"
                "/weather [city] — Weather\n"
                "/translate [lang] [text] — Translate\n"
                "/qr [text] — QR Code\n"
                "/password [len] — Password\n"
                "/hash [text] — Hash\n"
                "/encode [text] — Base64\n"
                "/decode [text] — Decode Base64\n"
                "/uuid — UUID\n"
                "/time [city] — Time\n"
                "/wiki [topic] — Wikipedia\n"
            )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_kb("main", lang))

    elif data == "menu_fun":
        if lang == "ar":
            text = "🎭 **الترفيه**\n\n/joke — نكتة\n/quote — اقتباس\n/fact — معلومة\n/ascii [نص] — ASCII"
        else:
            text = "🎭 **Fun**\n\n/joke — Joke\n/quote — Quote\n/fact — Fact\n/ascii [text] — ASCII"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_kb("main", lang))

    elif data == "menu_notes":
        if lang == "ar":
            text = "📝 **الملاحظات**\n\n/save [اسم] [محتوى]\n/get [اسم]\n/notes\n/delnote [اسم]"
        else:
            text = "📝 **Notes**\n\n/save [name] [content]\n/get [name]\n/notes\n/delnote [name]"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_kb("main", lang))

    elif data == "menu_reminders":
        if lang == "ar":
            text = "⏰ **التذكيرات**\n\n/remind [10m/1h/2d] [نص]\n/reminders\n/cancel [id]"
        else:
            text = "⏰ **Reminders**\n\n/remind [10m/1h/2d] [text]\n/reminders\n/cancel [id]"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_kb("main", lang))

    elif data == "menu_profile":
        db_user = await db.get_user(user.id)
        agent_id = await db.get_user_agent(user.id)
        is_admin = user.id in ADMIN_IDS or (db_user and db_user.get("is_admin"))
        if lang == "ar":
            text = (
                f"👤 **ملفك الشخصي**\n\n"
                f"🆔 `{user.id}`\n"
                f"📛 {user.first_name or '-'}\n"
                f"🌐 {'العربية' if lang == 'ar' else 'English'}\n"
                f"🤖 الإيجنت: {agent_id}\n"
                f"💬 رسائل: {db_user['total_msgs'] if db_user else 0:,}\n"
                f"👑 {'مدير ✅' if is_admin else 'مستخدم'}\n"
            )
        else:
            text = (
                f"👤 **Your Profile**\n\n"
                f"🆔 `{user.id}`\n"
                f"📛 {user.first_name or '-'}\n"
                f"🌐 {'Arabic' if lang == 'ar' else 'English'}\n"
                f"🤖 Agent: {agent_id}\n"
                f"💬 Messages: {db_user['total_msgs'] if db_user else 0:,}\n"
                f"👑 {'Admin ✅' if is_admin else 'User'}\n"
            )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_kb("main", lang))

    elif data == "menu_settings":
        label = "⚙️ الإعدادات\n\nاختر لغتك:" if lang == "ar" else "⚙️ Settings\n\nChoose your language:"
        await query.edit_message_text(label, reply_markup=language_kb())

    elif data == "lang_ar":
        await db.set_user_language(user.id, "ar")
        await query.edit_message_text(
            "✅ تم تغيير اللغة إلى العربية!",
            reply_markup=back_kb("main", "ar")
        )

    elif data == "lang_en":
        await db.set_user_language(user.id, "en")
        await query.edit_message_text(
            "✅ Language changed to English!",
            reply_markup=back_kb("main", "en")
        )

    elif data == "menu_agents":
        from handlers.agents import show_agents_menu
        await show_agents_menu(query, lang)


def register(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("language", language_cmd))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern=r"^menu_|^lang_"))
