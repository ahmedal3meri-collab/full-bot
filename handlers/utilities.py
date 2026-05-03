import io
import random
import aiohttp
import qrcode
from PIL import Image
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import database as db
from utils.decorators import register_user, check_banned
from utils.helpers import (
    safe_eval, hash_text, b64_encode, b64_decode, gen_password, gen_uuid,
    get_city_time, JOKES_AR, JOKES_EN, QUOTES_AR, QUOTES_EN, FACTS_AR, FACTS_EN
)
from config import OPENWEATHER_API_KEY


@register_user
@check_banned
async def calc_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    if not ctx.args:
        msg = "❌ الاستخدام: `/calc 2+2` أو `/calc sqrt(16)`" if lang == "ar" else "❌ Usage: `/calc 2+2` or `/calc sqrt(16)`"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return
    expr = " ".join(ctx.args)
    result = safe_eval(expr)
    if result is None:
        err = "❌ تعبير غير صالح." if lang == "ar" else "❌ Invalid expression."
        await update.message.reply_text(err)
        return
    text = f"🧮 `{expr}` = **{result}**" if lang == "ar" else f"🧮 `{expr}` = **{result}**"
    await update.message.reply_text(text, parse_mode="Markdown")


@register_user
@check_banned
async def weather_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    if not ctx.args:
        msg = "❌ الاستخدام: `/weather الرياض`" if lang == "ar" else "❌ Usage: `/weather London`"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return
    city = " ".join(ctx.args)

    if not OPENWEATHER_API_KEY:
        # Simulate weather if no API key
        import random
        temp = random.randint(15, 45)
        desc = random.choice(["مشمس ☀️", "غائم ⛅", "ممطر 🌧️"] if lang == "ar" else ["Sunny ☀️", "Cloudy ⛅", "Rainy 🌧️"])
        text = (f"🌤️ **طقس {city}**\n\n🌡️ الحرارة: {temp}°C\n☁️ الحالة: {desc}\n\n"
                f"_⚠️ بيانات تجريبية — أضف OPENWEATHER_API_KEY_") if lang == "ar" else \
               (f"🌤️ **Weather: {city}**\n\n🌡️ Temp: {temp}°C\n☁️ Condition: {desc}\n\n"
                f"_⚠️ Demo data — add OPENWEATHER_API_KEY_")
        await update.message.reply_text(text, parse_mode="Markdown")
        return

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang={'ar' if lang == 'ar' else 'en'}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    err = "❌ المدينة غير موجودة." if lang == "ar" else "❌ City not found."
                    await update.message.reply_text(err)
                    return
                data = await resp.json()
        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        desc = data["weather"][0]["description"]
        wind = data["wind"]["speed"]
        city_name = data["name"]
        if lang == "ar":
            text = (
                f"🌤️ **طقس {city_name}**\n\n"
                f"🌡️ الحرارة: {temp:.1f}°C (يبدو {feels:.1f}°C)\n"
                f"💧 الرطوبة: {humidity}%\n"
                f"💨 الرياح: {wind} م/ث\n"
                f"☁️ الحالة: {desc}\n"
            )
        else:
            text = (
                f"🌤️ **Weather: {city_name}**\n\n"
                f"🌡️ Temp: {temp:.1f}°C (Feels {feels:.1f}°C)\n"
                f"💧 Humidity: {humidity}%\n"
                f"💨 Wind: {wind} m/s\n"
                f"☁️ Condition: {desc}\n"
            )
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("❌ خطأ في جلب الطقس." if lang == "ar" else "❌ Error fetching weather.")


@register_user
@check_banned
async def translate_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    if not ctx.args or len(ctx.args) < 2:
        msg = "❌ الاستخدام: `/translate en مرحبا`\nاللغات: ar, en, fr, de, es, it, tr, ru, zh, ja" if lang == "ar" else "❌ Usage: `/translate ar Hello`\nLangs: ar, en, fr, de, es, it, tr, ru, zh, ja"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return
    target_lang = ctx.args[0]
    text_to_translate = " ".join(ctx.args[1:])
    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source="auto", target=target_lang).translate(text_to_translate)
        result = f"🌐 **الترجمة:**\n\n{translated}" if lang == "ar" else f"🌐 **Translation:**\n\n{translated}"
        await update.message.reply_text(result, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في الترجمة: {e}" if lang == "ar" else f"❌ Translation error: {e}")


@register_user
@check_banned
async def qr_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    if not ctx.args:
        msg = "❌ الاستخدام: `/qr [النص أو الرابط]`" if lang == "ar" else "❌ Usage: `/qr [text or URL]`"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return
    content = " ".join(ctx.args)
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    caption = f"✅ QR Code جاهز!" if lang == "ar" else f"✅ QR Code ready!"
    await update.message.reply_photo(photo=buf, caption=caption)


@register_user
@check_banned
async def password_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    length = 16
    if ctx.args:
        try:
            length = int(ctx.args[0])
        except ValueError:
            pass
    pwd = gen_password(length)
    text = f"🔐 **كلمة مرور عشوائية ({length} حرف):**\n\n`{pwd}`" if lang == "ar" else f"🔐 **Random Password ({length} chars):**\n\n`{pwd}`"
    await update.message.reply_text(text, parse_mode="Markdown")


@register_user
@check_banned
async def hash_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    if not ctx.args:
        msg = "❌ الاستخدام: `/hash [النص]`" if lang == "ar" else "❌ Usage: `/hash [text]`"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return
    text = " ".join(ctx.args)
    hashes = hash_text(text)
    result = "🔒 **الهاشات:**\n\n"
    for name, value in hashes.items():
        result += f"**{name}:**\n`{value}`\n\n"
    await update.message.reply_text(result, parse_mode="Markdown")


@register_user
@check_banned
async def encode_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    if not ctx.args:
        msg = "❌ الاستخدام: `/encode [النص]`" if lang == "ar" else "❌ Usage: `/encode [text]`"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return
    text = " ".join(ctx.args)
    encoded = b64_encode(text)
    result = f"🔐 **Base64:**\n\n`{encoded}`"
    await update.message.reply_text(result, parse_mode="Markdown")


@register_user
@check_banned
async def decode_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    if not ctx.args:
        msg = "❌ الاستخدام: `/decode [النص المشفر]`" if lang == "ar" else "❌ Usage: `/decode [encoded text]`"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return
    text = " ".join(ctx.args)
    decoded = b64_decode(text)
    if decoded is None:
        err = "❌ نص Base64 غير صالح." if lang == "ar" else "❌ Invalid Base64 text."
        await update.message.reply_text(err)
        return
    result = f"🔓 **فك التشفير:**\n\n`{decoded}`" if lang == "ar" else f"🔓 **Decoded:**\n\n`{decoded}`"
    await update.message.reply_text(result, parse_mode="Markdown")


@register_user
@check_banned
async def uuid_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    uid = gen_uuid()
    text = f"🆔 **UUID:**\n\n`{uid}`"
    await update.message.reply_text(text, parse_mode="Markdown")


@register_user
@check_banned
async def time_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    if not ctx.args:
        msg = "❌ الاستخدام: `/time الرياض`\nالمدن: الرياض، دبي، القاهرة، بغداد، لندن، باريس..." if lang == "ar" else "❌ Usage: `/time London`\nCities: riyadh, dubai, cairo, baghdad, london, paris..."
        await update.message.reply_text(msg, parse_mode="Markdown")
        return
    city = " ".join(ctx.args)
    time_str = get_city_time(city)
    if not time_str:
        err = f"❌ لم أجد المدينة: {city}" if lang == "ar" else f"❌ City not found: {city}"
        await update.message.reply_text(err)
        return
    text = f"🕐 **الوقت في {city}:**\n\n`{time_str}`" if lang == "ar" else f"🕐 **Time in {city}:**\n\n`{time_str}`"
    await update.message.reply_text(text, parse_mode="Markdown")


@register_user
@check_banned
async def wiki_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    if not ctx.args:
        msg = "❌ الاستخدام: `/wiki [الموضوع]`" if lang == "ar" else "❌ Usage: `/wiki [topic]`"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return
    topic = " ".join(ctx.args)
    try:
        import wikipediaapi
        wiki = wikipediaapi.Wikipedia(
            language="ar" if lang == "ar" else "en",
            user_agent="TelegramBot/1.0"
        )
        page = wiki.page(topic)
        if not page.exists():
            err = f"❌ لم أجد نتائج لـ: {topic}" if lang == "ar" else f"❌ No results for: {topic}"
            await update.message.reply_text(err)
            return
        summary = page.summary[:1000]
        if len(page.summary) > 1000:
            summary += "..."
        header = f"📚 **{page.title}**\n\n" if lang == "ar" else f"📚 **{page.title}**\n\n"
        footer = f"\n\n🔗 [اقرأ المزيد]({page.fullurl})" if lang == "ar" else f"\n\n🔗 [Read more]({page.fullurl})"
        await update.message.reply_text(header + summary + footer, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("❌ خطأ في البحث." if lang == "ar" else "❌ Search error.")


@register_user
@check_banned
async def joke_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    joke = random.choice(JOKES_AR if lang == "ar" else JOKES_EN)
    await update.message.reply_text(f"😂 {joke}")


@register_user
@check_banned
async def quote_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    quote = random.choice(QUOTES_AR if lang == "ar" else QUOTES_EN)
    await update.message.reply_text(f"💭 _{quote}_", parse_mode="Markdown")


@register_user
@check_banned
async def fact_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    fact = random.choice(FACTS_AR if lang == "ar" else FACTS_EN)
    await update.message.reply_text(f"🔬 **معلومة:**\n\n{fact}" if lang == "ar" else f"🔬 **Fact:**\n\n{fact}", parse_mode="Markdown")


@register_user
@check_banned
async def ascii_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    if not ctx.args:
        msg = "❌ الاستخدام: `/ascii [نص]`" if lang == "ar" else "❌ Usage: `/ascii [text]`"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return
    text = " ".join(ctx.args)[:20]
    try:
        import pyfiglet
        art = pyfiglet.figlet_format(text, font="standard")
        await update.message.reply_text(f"```\n{art}\n```", parse_mode="Markdown")
    except ImportError:
        # Simple ascii fallback
        art = " ".join(f"[{c.upper()}]" for c in text)
        await update.message.reply_text(f"```\n{art}\n```", parse_mode="Markdown")


def register(app):
    app.add_handler(CommandHandler("calc", calc_cmd))
    app.add_handler(CommandHandler("weather", weather_cmd))
    app.add_handler(CommandHandler("translate", translate_cmd))
    app.add_handler(CommandHandler("tr", translate_cmd))
    app.add_handler(CommandHandler("qr", qr_cmd))
    app.add_handler(CommandHandler("password", password_cmd))
    app.add_handler(CommandHandler("hash", hash_cmd))
    app.add_handler(CommandHandler("encode", encode_cmd))
    app.add_handler(CommandHandler("decode", decode_cmd))
    app.add_handler(CommandHandler("uuid", uuid_cmd))
    app.add_handler(CommandHandler("time", time_cmd))
    app.add_handler(CommandHandler("wiki", wiki_cmd))
    app.add_handler(CommandHandler("joke", joke_cmd))
    app.add_handler(CommandHandler("quote", quote_cmd))
    app.add_handler(CommandHandler("fact", fact_cmd))
    app.add_handler(CommandHandler("ascii", ascii_cmd))
