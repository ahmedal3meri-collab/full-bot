"""Inline mode: @botname [query]"""
import uuid
import random
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes, InlineQueryHandler
from utils.helpers import safe_eval, b64_encode, JOKES_AR, QUOTES_AR


async def inline_query(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query
    if not query:
        return

    text = query.query.strip()
    results = []

    # ── Calculator ──
    if text.startswith("calc ") or text.startswith("حساب "):
        expr = text.split(" ", 1)[1]
        result = safe_eval(expr)
        if result:
            results.append(InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"🧮 {expr} = {result}",
                description="انقر للإرسال",
                input_message_content=InputTextMessageContent(f"🧮 `{expr}` = **{result}**", parse_mode="Markdown"),
            ))

    # ── Translate ──
    elif text.startswith("tr ") or text.startswith("ترجم "):
        to_translate = text.split(" ", 1)[1]
        try:
            from deep_translator import GoogleTranslator
            en_result = GoogleTranslator(source="auto", target="en").translate(to_translate)
            ar_result = GoogleTranslator(source="auto", target="ar").translate(to_translate)
            results.append(InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"🌐 EN: {en_result[:50]}",
                description=f"Translate to English",
                input_message_content=InputTextMessageContent(f"🌐 **Translation (EN):**\n{en_result}"),
            ))
            results.append(InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"🌐 AR: {ar_result[:50]}",
                description=f"Translate to Arabic",
                input_message_content=InputTextMessageContent(f"🌐 **الترجمة (AR):**\n{ar_result}"),
            ))
        except Exception:
            pass

    # ── Hash ──
    elif text.startswith("hash "):
        from utils.helpers import hash_text
        content = text[5:]
        hashes = hash_text(content)
        for name, value in hashes.items():
            results.append(InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"🔒 {name}: {value[:20]}...",
                description=f"Hash of: {content[:30]}",
                input_message_content=InputTextMessageContent(f"🔒 **{name}:**\n`{value}`", parse_mode="Markdown"),
            ))

    # ── Base64 ──
    elif text.startswith("encode "):
        content = text[7:]
        encoded = b64_encode(content)
        results.append(InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title=f"🔐 Base64: {encoded[:30]}...",
            description="Base64 Encode",
            input_message_content=InputTextMessageContent(f"🔐 **Base64:**\n`{encoded}`", parse_mode="Markdown"),
        ))

    # ── Random joke ──
    elif text in ("joke", "نكتة"):
        joke = random.choice(JOKES_AR)
        results.append(InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title="😂 نكتة عشوائية",
            description=joke[:50],
            input_message_content=InputTextMessageContent(f"😂 {joke}"),
        ))

    # ── Random quote ──
    elif text in ("quote", "اقتباس"):
        quote = random.choice(QUOTES_AR)
        results.append(InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title="💭 اقتباس",
            description=quote[:50],
            input_message_content=InputTextMessageContent(f"💭 _{quote}_", parse_mode="Markdown"),
        ))

    # ── UUID ──
    elif text in ("uuid", "id"):
        uid = str(uuid.uuid4())
        results.append(InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title=f"🆔 {uid}",
            description="Random UUID",
            input_message_content=InputTextMessageContent(f"`{uid}`", parse_mode="Markdown"),
        ))

    # ── Help ──
    else:
        results.append(InlineQueryResultArticle(
            id="help",
            title="💡 استخدامات الـ Inline",
            description="calc, tr, hash, encode, joke, quote, uuid",
            input_message_content=InputTextMessageContent(
                "💡 **استخدامات Inline:**\n\n"
                "• `@bot calc 2+2`\n"
                "• `@bot tr مرحبا`\n"
                "• `@bot hash نص`\n"
                "• `@bot encode نص`\n"
                "• `@bot joke`\n"
                "• `@bot quote`\n"
                "• `@bot uuid`\n",
                parse_mode="Markdown"
            ),
        ))

    await query.answer(results, cache_time=10, is_personal=True)


def register(app):
    app.add_handler(InlineQueryHandler(inline_query))
