import random
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
import database as db
from utils.decorators import register_user, check_banned
from utils.keyboards import rps_kb, trivia_kb
from utils.helpers import TRIVIA_QUESTIONS

EIGHT_BALL_AR = [
    "🎱 نعم، بالتأكيد!", "🎱 الأمور تبدو جيدة!", "🎱 كل المؤشرات تقول نعم!",
    "🎱 الجواب مبهم، حاول لاحقاً.", "🎱 لا تعتمد عليه.", "🎱 من المستبعد جداً.",
    "🎱 لا تحسب عليه!", "🎱 الجواب لا.", "🎱 مصادري تقول لا.",
    "🎱 الآفاق تبدو جيدة!", "🎱 نعم!", "🎱 المستقبل ضبابي، اسأل مرة أخرى.",
]

EIGHT_BALL_EN = [
    "🎱 It is certain!", "🎱 Outlook good!", "🎱 All signs point to yes!",
    "🎱 Reply hazy, try again.", "🎱 Don't count on it.", "🎱 Very doubtful.",
    "🎱 My reply is no.", "🎱 Outlook not so good.", "🎱 Sources say no.",
    "🎱 Signs point to yes!", "🎱 Yes!", "🎱 Cannot predict now.",
]

SLOT_SYMBOLS = ["🍒", "🍋", "🍊", "🍇", "⭐", "💎", "🔔", "🎰"]

# Active guessing games: {user_id: {"number": int, "attempts": int}}
guess_games: dict[int, dict] = {}


@register_user
@check_banned
async def dice_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    result = random.randint(1, 6)
    faces = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
    if lang == "ar":
        text = f"🎲 رميت النرد!\n\nالنتيجة: {faces[result-1]} **{result}**"
    else:
        text = f"🎲 You rolled the dice!\n\nResult: {faces[result-1]} **{result}**"
    await update.message.reply_text(text, parse_mode="Markdown")


@register_user
@check_banned
async def flip_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    result = random.choice(["heads", "tails"])
    if lang == "ar":
        label = "صورة 🟡" if result == "heads" else "كتابة 📀"
        text = f"🪙 رميت العملة!\n\nالنتيجة: **{label}**"
    else:
        label = "Heads 🟡" if result == "heads" else "Tails 📀"
        text = f"🪙 You flipped a coin!\n\nResult: **{label}**"
    await update.message.reply_text(text, parse_mode="Markdown")


@register_user
@check_banned
async def rps_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    if lang == "ar":
        text = "✊ اختر: حجر، ورقة، أو مقص؟"
    else:
        text = "✊ Choose: Rock, Paper, or Scissors?"
    await update.message.reply_text(text, reply_markup=rps_kb())


async def rps_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    lang = await db.get_user_language(user.id)
    choice_map = {"rps_rock": "🪨", "rps_paper": "📄", "rps_scissors": "✂️"}
    name_ar = {"rps_rock": "حجر", "rps_paper": "ورقة", "rps_scissors": "مقص"}
    name_en = {"rps_rock": "Rock", "rps_paper": "Paper", "rps_scissors": "Scissors"}

    player = query.data
    bot_choice = random.choice(["rps_rock", "rps_paper", "rps_scissors"])

    beats = {"rps_rock": "rps_scissors", "rps_paper": "rps_rock", "rps_scissors": "rps_paper"}

    if player == bot_choice:
        result_ar, result_en = "🤝 تعادل!", "🤝 It's a tie!"
    elif beats[player] == bot_choice:
        result_ar, result_en = "🎉 فزت!", "🎉 You win!"
    else:
        result_ar, result_en = "😔 خسرت!", "😔 You lost!"

    if lang == "ar":
        text = (
            f"أنت: {choice_map[player]} {name_ar[player]}\n"
            f"البوت: {choice_map[bot_choice]} {name_ar[bot_choice]}\n\n"
            f"{result_ar}"
        )
    else:
        text = (
            f"You: {choice_map[player]} {name_en[player]}\n"
            f"Bot: {choice_map[bot_choice]} {name_en[bot_choice]}\n\n"
            f"{result_en}"
        )
    await query.edit_message_text(text)


@register_user
@check_banned
async def trivia_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    q = random.choice(TRIVIA_QUESTIONS)
    choices = q["choices"][:]
    correct_original = q["answer"]

    # Shuffle choices
    indexed = list(enumerate(choices))
    random.shuffle(indexed)
    new_correct = next(i for i, (orig, _) in enumerate(indexed) if orig == correct_original)
    shuffled = [c for _, c in indexed]

    question = q["q_ar"] if lang == "ar" else q["q_en"]
    header = "❓ **سؤال ثقافي:**\n\n" if lang == "ar" else "❓ **Trivia Question:**\n\n"
    await update.message.reply_text(
        header + question,
        parse_mode="Markdown",
        reply_markup=trivia_kb(shuffled, new_correct)
    )


async def trivia_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    lang = await db.get_user_language(user.id)
    _, chosen, correct = query.data.split("_")
    chosen, correct = int(chosen), int(correct)
    if chosen == correct:
        text = "✅ **إجابة صحيحة!** 🎉" if lang == "ar" else "✅ **Correct!** 🎉"
    else:
        text = f"❌ **إجابة خاطئة!** الصحيح هو الخيار {correct + 1}" if lang == "ar" else f"❌ **Wrong!** The correct answer was option {correct + 1}"
    await query.edit_message_text(text, parse_mode="Markdown")


@register_user
@check_banned
async def eightball_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    question = " ".join(ctx.args) if ctx.args else None
    if not question:
        msg = "❓ اسألني سؤالاً: `/8ball [سؤالك]`" if lang == "ar" else "❓ Ask me a question: `/8ball [question]`"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return
    answer = random.choice(EIGHT_BALL_AR if lang == "ar" else EIGHT_BALL_EN)
    header = f"🎱 **الكرة السحرية**\n\n❓ {question}\n\n" if lang == "ar" else f"🎱 **Magic 8-Ball**\n\n❓ {question}\n\n"
    await update.message.reply_text(header + answer, parse_mode="Markdown")


@register_user
@check_banned
async def slot_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    s1, s2, s3 = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
    display = f"[ {s1} | {s2} | {s3} ]"
    if s1 == s2 == s3:
        result_ar = "🎰 **جاك بوت! فزت بالجائزة الكبرى!** 🎉🎉🎉"
        result_en = "🎰 **JACKPOT! You hit the grand prize!** 🎉🎉🎉"
    elif s1 == s2 or s2 == s3 or s1 == s3:
        result_ar = "✨ **زوج! لديك حظ جيد!**"
        result_en = "✨ **A pair! Nice luck!**"
    else:
        result_ar = "😔 حظاً أوفر المرة القادمة!"
        result_en = "😔 Better luck next time!"
    text = f"🎰 **ماكينة الحظ**\n\n{display}\n\n" if lang == "ar" else f"🎰 **Slot Machine**\n\n{display}\n\n"
    text += result_ar if lang == "ar" else result_en
    await update.message.reply_text(text, parse_mode="Markdown")


@register_user
@check_banned
async def guess_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    number = random.randint(1, 100)
    guess_games[user.id] = {"number": number, "attempts": 0}
    if lang == "ar":
        text = "🎯 **لعبة التخمين!**\n\nفكرت بعدد بين 1 و 100.\nخمّن الرقم! أرسل رقماً أو /stopguess للخروج."
    else:
        text = "🎯 **Number Guessing Game!**\n\nI'm thinking of a number between 1 and 100.\nGuess it! Send a number or /stopguess to quit."
    await update.message.reply_text(text, parse_mode="Markdown")


@register_user
@check_banned
async def stopguess_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    if user.id in guess_games:
        num = guess_games.pop(user.id)["number"]
        text = f"🛑 انتهت اللعبة. كان الرقم **{num}**." if lang == "ar" else f"🛑 Game over. The number was **{num}**."
    else:
        text = "❌ لا توجد لعبة نشطة." if lang == "ar" else "❌ No active game."
    await update.message.reply_text(text, parse_mode="Markdown")


async def guess_message_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not update.message or not update.message.text:
        return
    if user.id not in guess_games:
        return
    text = update.message.text.strip()
    if not text.lstrip("-").isdigit():
        return

    lang = await db.get_user_language(user.id)
    game = guess_games[user.id]
    guess = int(text)
    game["attempts"] += 1

    if guess == game["number"]:
        attempts = game["attempts"]
        guess_games.pop(user.id)
        if lang == "ar":
            reply = f"🎉 **صحيح!** الرقم كان **{guess}**!\nعدد المحاولات: {attempts}"
        else:
            reply = f"🎉 **Correct!** The number was **{guess}**!\nAttempts: {attempts}"
    elif guess < game["number"]:
        reply = "📈 أعلى من ذلك!" if lang == "ar" else "📈 Higher!"
    else:
        reply = "📉 أقل من ذلك!" if lang == "ar" else "📉 Lower!"
    await update.message.reply_text(reply, parse_mode="Markdown")


def register(app):
    from telegram.ext import MessageHandler, filters
    app.add_handler(CommandHandler("dice", dice_cmd))
    app.add_handler(CommandHandler("flip", flip_cmd))
    app.add_handler(CommandHandler("rps", rps_cmd))
    app.add_handler(CommandHandler("trivia", trivia_cmd))
    app.add_handler(CommandHandler("8ball", eightball_cmd))
    app.add_handler(CommandHandler("slot", slot_cmd))
    app.add_handler(CommandHandler("guess", guess_cmd))
    app.add_handler(CommandHandler("stopguess", stopguess_cmd))
    app.add_handler(CallbackQueryHandler(rps_callback, pattern=r"^rps_"))
    app.add_handler(CallbackQueryHandler(trivia_callback, pattern=r"^trivia_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess_message_handler), group=10)
