"""Bilingual strings: Arabic (default) and English."""

STRINGS = {
    "ar": {
        # General
        "start_msg": (
            "🤖 **أهلاً {name}!**\n\n"
            "أنا بوت متكامل يضم:\n"
            "🎮 ألعاب متنوعة\n"
            "🛠️ أدوات مفيدة\n"
            "🤖 20 إيجنت ذكاء اصطناعي متخصص\n"
            "📝 ملاحظات وتذكيرات\n"
            "👥 إدارة المجموعات\n"
            "🎭 ترفيه وألعاب\n\n"
            "اضغط /help لرؤية كل الأوامر"
        ),
        "help_msg": (
            "📖 **قائمة الأوامر**\n\n"
            "**🤖 الإيجنتات**\n"
            "/agents — عرض وتحديد إيجنت\n"
            "/agent [id] — تفعيل إيجنت معين\n"
            "/chat [نص] — محادثة مع الإيجنت النشط\n"
            "/reset — إعادة تعيين المحادثة\n\n"
            "**🎮 الألعاب**\n"
            "/dice — رمي النرد\n"
            "/flip — رمي العملة\n"
            "/rps — حجر ورقة مقص\n"
            "/trivia — أسئلة ثقافية\n"
            "/8ball [سؤال] — الكرة السحرية\n"
            "/slot — ماكينة الحظ\n"
            "/guess — لعبة تخمين الرقم\n\n"
            "**🛠️ الأدوات**\n"
            "/calc [عملية] — حاسبة\n"
            "/weather [مدينة] — الطقس\n"
            "/translate [لغة] [نص] — ترجمة\n"
            "/qr [نص] — إنشاء QR Code\n"
            "/password [طول] — توليد كلمة مرور\n"
            "/hash [نص] — تحويل إلى هاش\n"
            "/encode [نص] — تشفير Base64\n"
            "/decode [نص] — فك تشفير Base64\n"
            "/uuid — توليد UUID\n"
            "/time [مدينة] — الوقت الحالي\n"
            "/wiki [موضوع] — بحث ويكيبيديا\n\n"
            "**📝 الملاحظات**\n"
            "/save [اسم] [محتوى] — حفظ ملاحظة (خاصة)\n"
            "/get [اسم] — جلب ملاحظة\n"
            "/notes — عرض ملاحظاتي\n"
            "/delnote [اسم] — حذف ملاحظة\n"
            "/noteprivacy [اسم] public|private — تغيير خصوصية ملاحظة\n\n"
            "**⏰ التذكيرات**\n"
            "/remind [وقت] [نص] — ضبط تذكير\n"
            "/reminders — عرض تذكيراتي\n"
            "/cancel [id] — إلغاء تذكير\n\n"
            "**🎭 الترفيه**\n"
            "/joke — نكتة عشوائية\n"
            "/quote — اقتباس ملهم\n"
            "/fact — معلومة مثيرة\n"
            "/ascii [نص] — فن ASCII\n\n"
            "**👤 الحساب**\n"
            "/profile — ملفي الشخصي\n"
            "/language — تغيير اللغة\n\n"
            "**👥 المجموعات** _(للمدراء)_\n"
            "/setwelcome [نص] — رسالة ترحيب\n"
            "/setgoodbye [نص] — رسالة وداع\n"
            "/antiflood [on/off] — مكافحة الفيضان\n"
            "/pin — تثبيت رسالة\n"
            "/unpin — إلغاء التثبيت\n"
        ),
        "banned": "🚫 أنت محظور من استخدام هذا البوت.",
        "admin_only": "⛔ هذا الأمر للمدراء فقط.",
        "group_admin_only": "⛔ هذا الأمر لمدراء المجموعة فقط.",
        "error": "❌ حدث خطأ. حاول مجدداً.",
        "rate_limit": "⚠️ تباطأ قليلاً! أرسلت الكثير من الرسائل.",
        "done": "✅ تم!",
        "cancelled": "❌ تم الإلغاء.",
        "not_found": "❌ لم يُعثر على شيء.",
    },
    "en": {
        "start_msg": (
            "🤖 **Hello {name}!**\n\n"
            "I'm a full-featured bot with:\n"
            "🎮 Various games\n"
            "🛠️ Useful tools\n"
            "🤖 20 specialized AI agents\n"
            "📝 Notes & reminders\n"
            "👥 Group management\n"
            "🎭 Entertainment\n\n"
            "Press /help to see all commands"
        ),
        "help_msg": (
            "📖 **Commands List**\n\n"
            "**🤖 Agents**\n"
            "/agents — View & select an agent\n"
            "/agent [id] — Activate a specific agent\n"
            "/chat [text] — Chat with active agent\n"
            "/reset — Reset conversation\n\n"
            "**🎮 Games**\n"
            "/dice — Roll dice\n"
            "/flip — Flip a coin\n"
            "/rps — Rock paper scissors\n"
            "/trivia — Trivia questions\n"
            "/8ball [question] — Magic 8-ball\n"
            "/slot — Slot machine\n"
            "/guess — Number guessing game\n\n"
            "**🛠️ Tools**\n"
            "/calc [expr] — Calculator\n"
            "/weather [city] — Weather\n"
            "/translate [lang] [text] — Translate\n"
            "/qr [text] — Generate QR Code\n"
            "/password [len] — Generate password\n"
            "/hash [text] — Hash text\n"
            "/encode [text] — Base64 encode\n"
            "/decode [text] — Base64 decode\n"
            "/uuid — Generate UUID\n"
            "/time [city] — Current time\n"
            "/wiki [topic] — Wikipedia search\n\n"
            "**📝 Notes**\n"
            "/save [name] [content] — Save note (private)\n"
            "/get [name] — Get note\n"
            "/notes — List my notes\n"
            "/delnote [name] — Delete note\n"
            "/noteprivacy [name] public|private — Change note privacy\n\n"
            "**⏰ Reminders**\n"
            "/remind [time] [text] — Set reminder\n"
            "/reminders — List reminders\n"
            "/cancel [id] — Cancel reminder\n\n"
            "**🎭 Entertainment**\n"
            "/joke — Random joke\n"
            "/quote — Inspirational quote\n"
            "/fact — Interesting fact\n"
            "/ascii [text] — ASCII art\n\n"
            "**👤 Account**\n"
            "/profile — My profile\n"
            "/language — Change language\n\n"
            "**👥 Groups** _(admins)_\n"
            "/setwelcome [text] — Welcome message\n"
            "/setgoodbye [text] — Goodbye message\n"
            "/antiflood [on/off] — Anti-flood\n"
            "/pin — Pin message\n"
            "/unpin — Unpin message\n"
        ),
        "banned": "🚫 You are banned from using this bot.",
        "admin_only": "⛔ This command is for admins only.",
        "group_admin_only": "⛔ This command is for group admins only.",
        "error": "❌ An error occurred. Please try again.",
        "rate_limit": "⚠️ Slow down! You're sending too many messages.",
        "done": "✅ Done!",
        "cancelled": "❌ Cancelled.",
        "not_found": "❌ Nothing found.",
    }
}


def t(key: str, lang: str = "ar", **kwargs) -> str:
    text = STRINGS.get(lang, STRINGS["ar"]).get(key) or STRINGS["ar"].get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text
