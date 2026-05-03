from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def main_menu_kb(lang: str = "ar") -> InlineKeyboardMarkup:
    if lang == "ar":
        buttons = [
            [InlineKeyboardButton("🤖 الإيجنتات", callback_data="menu_agents"),
             InlineKeyboardButton("🎮 الألعاب", callback_data="menu_games")],
            [InlineKeyboardButton("🛠️ الأدوات", callback_data="menu_tools"),
             InlineKeyboardButton("🎭 الترفيه", callback_data="menu_fun")],
            [InlineKeyboardButton("📝 الملاحظات", callback_data="menu_notes"),
             InlineKeyboardButton("⏰ التذكيرات", callback_data="menu_reminders")],
            [InlineKeyboardButton("👤 ملفي", callback_data="menu_profile"),
             InlineKeyboardButton("⚙️ الإعدادات", callback_data="menu_settings")],
        ]
    else:
        buttons = [
            [InlineKeyboardButton("🤖 Agents", callback_data="menu_agents"),
             InlineKeyboardButton("🎮 Games", callback_data="menu_games")],
            [InlineKeyboardButton("🛠️ Tools", callback_data="menu_tools"),
             InlineKeyboardButton("🎭 Fun", callback_data="menu_fun")],
            [InlineKeyboardButton("📝 Notes", callback_data="menu_notes"),
             InlineKeyboardButton("⏰ Reminders", callback_data="menu_reminders")],
            [InlineKeyboardButton("👤 Profile", callback_data="menu_profile"),
             InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")],
        ]
    return InlineKeyboardMarkup(buttons)


def language_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ])


def back_kb(target: str = "main", lang: str = "ar") -> InlineKeyboardMarkup:
    label = "🔙 رجوع" if lang == "ar" else "🔙 Back"
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data=f"menu_{target}")]])


def yes_no_kb(yes_data: str, no_data: str, lang: str = "ar") -> InlineKeyboardMarkup:
    yes = "✅ نعم" if lang == "ar" else "✅ Yes"
    no = "❌ لا" if lang == "ar" else "❌ No"
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(yes, callback_data=yes_data),
        InlineKeyboardButton(no, callback_data=no_data),
    ]])


def rps_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🪨 حجر", callback_data="rps_rock"),
        InlineKeyboardButton("📄 ورقة", callback_data="rps_paper"),
        InlineKeyboardButton("✂️ مقص", callback_data="rps_scissors"),
    ]])


def agents_kb(agents: list, lang: str = "ar") -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for i, agent in enumerate(agents):
        row.append(InlineKeyboardButton(
            f"{agent['emoji']} {agent['name_ar'] if lang == 'ar' else agent['name_en']}",
            callback_data=f"agent_{agent['id']}"
        ))
        if len(row) == 2 or i == len(agents) - 1:
            buttons.append(row)
            row = []
    back = "🔙 رجوع" if lang == "ar" else "🔙 Back"
    buttons.append([InlineKeyboardButton(back, callback_data="menu_main")])
    return InlineKeyboardMarkup(buttons)


def trivia_kb(choices: list, correct_idx: int) -> InlineKeyboardMarkup:
    buttons = []
    for i, choice in enumerate(choices):
        buttons.append([InlineKeyboardButton(
            f"{'ABCD'[i]}. {choice}",
            callback_data=f"trivia_{i}_{correct_idx}"
        )])
    return InlineKeyboardMarkup(buttons)
