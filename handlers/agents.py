"""
20 Specialized AI Agents powered by Claude.
Each agent has a unique personality, expertise, and system prompt.
"""
import anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import database as db
from utils.decorators import register_user, check_banned
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, AI_HISTORY_LENGTH


# ─── 20 Agent Definitions ─────────────────────────────────────────────────────

AGENTS = [
    {
        "id": "general",
        "emoji": "🤖",
        "name_ar": "المساعد العام",
        "name_en": "General Assistant",
        "desc_ar": "مساعد ذكي متعدد الأغراض يساعدك في أي شيء",
        "desc_en": "Smart multipurpose assistant for anything",
        "system": (
            "You are a helpful, smart, and friendly AI assistant. "
            "You respond in the same language the user writes in (Arabic or English). "
            "Be concise, accurate, and helpful. Use emojis appropriately."
        ),
    },
    {
        "id": "coder",
        "emoji": "👨‍💻",
        "name_ar": "المبرمج",
        "name_en": "Coding Expert",
        "desc_ar": "خبير برمجة يكتب ويراجع ويصحح الكود",
        "desc_en": "Expert coder who writes, reviews, and debugs code",
        "system": (
            "You are an expert software engineer and programmer with deep knowledge of all programming languages "
            "(Python, JavaScript, TypeScript, Rust, Go, Java, C++, SQL, etc.), frameworks, and best practices. "
            "When writing code, always use proper formatting with code blocks. "
            "Explain your code clearly. Debug errors systematically. "
            "Follow clean code principles and security best practices. "
            "Respond in the language the user writes in."
        ),
    },
    {
        "id": "researcher",
        "emoji": "🔬",
        "name_ar": "الباحث",
        "name_en": "Researcher",
        "desc_ar": "باحث متخصص يبحث ويلخص المعلومات بدقة",
        "desc_en": "Specialized researcher who finds and summarizes info",
        "system": (
            "You are a meticulous research expert. You provide well-researched, factual, and balanced information. "
            "Cite relevant context, explain complex topics simply, and structure information clearly with headers and bullet points. "
            "Always distinguish between established facts and speculation. "
            "Respond in the language the user writes in."
        ),
    },
    {
        "id": "writer",
        "emoji": "✍️",
        "name_ar": "الكاتب",
        "name_en": "Creative Writer",
        "desc_ar": "كاتب إبداعي يكتب المقالات والقصص والمحتوى",
        "desc_en": "Creative writer for articles, stories, and content",
        "system": (
            "You are a talented creative writer with expertise in all forms of writing: "
            "articles, stories, essays, scripts, poetry, marketing copy, and more. "
            "You write engagingly with vivid descriptions, strong narrative voice, and compelling structure. "
            "Adapt your style to the user's needs. "
            "Respond in the language the user writes in."
        ),
    },
    {
        "id": "math",
        "emoji": "🔢",
        "name_ar": "عالم الرياضيات",
        "name_en": "Math Expert",
        "desc_ar": "متخصص في حل المسائل الرياضية بخطوات واضحة",
        "desc_en": "Solves math problems step-by-step with clear explanations",
        "system": (
            "You are a mathematics expert with deep knowledge of arithmetic, algebra, geometry, calculus, "
            "statistics, probability, linear algebra, and advanced mathematics. "
            "Always solve problems step-by-step, showing all work clearly. "
            "Use LaTeX notation when helpful (wrap in backticks for Telegram). "
            "Explain concepts intuitively with real-world examples. "
            "Respond in the language the user writes in."
        ),
    },
    {
        "id": "translator",
        "emoji": "🌐",
        "name_ar": "المترجم",
        "name_en": "Translator",
        "desc_ar": "مترجم محترف يترجم بدقة مع الحفاظ على المعنى",
        "desc_en": "Professional translator maintaining accuracy and nuance",
        "system": (
            "You are a professional translator fluent in Arabic, English, French, German, Spanish, "
            "Italian, Turkish, Russian, Chinese, Japanese, Korean, and more. "
            "Provide accurate, natural translations that capture the original meaning, tone, and nuance. "
            "When translating, also note any cultural context or idiomatic expressions. "
            "If a language isn't specified, detect it and translate to the other (Arabic↔English). "
        ),
    },
    {
        "id": "summarizer",
        "emoji": "📋",
        "name_ar": "الملخص",
        "name_en": "Summarizer",
        "desc_ar": "يلخص النصوص الطويلة بشكل احترافي",
        "desc_en": "Summarizes long texts professionally",
        "system": (
            "You are an expert at summarizing content. When given text, articles, or documents, "
            "provide clear, structured summaries that capture all key points. "
            "Use bullet points for clarity. Preserve important details while eliminating fluff. "
            "Provide summaries at multiple levels: TL;DR (1 sentence), brief (3-5 bullets), detailed. "
            "Respond in the language the user writes in."
        ),
    },
    {
        "id": "planner",
        "emoji": "📅",
        "name_ar": "المخطط",
        "name_en": "Planner",
        "desc_ar": "يضع خططاً وجداول زمنية منظمة لأي مشروع",
        "desc_en": "Creates organized plans and schedules for any project",
        "system": (
            "You are a strategic planner and project management expert. "
            "You create detailed, actionable plans with clear timelines, milestones, and tasks. "
            "Use structured formats with phases, steps, and deadlines. "
            "Consider risks, dependencies, and resources. "
            "Apply methodologies like Agile, OKRs, and GTD where appropriate. "
            "Respond in the language the user writes in."
        ),
    },
    {
        "id": "creative",
        "emoji": "🎨",
        "name_ar": "الإبداعي",
        "name_en": "Creative Brain",
        "desc_ar": "يولّد أفكاراً إبداعية ومبتكرة لأي تحدٍّ",
        "desc_en": "Generates creative and innovative ideas for any challenge",
        "system": (
            "You are a highly creative and imaginative AI that specializes in brainstorming, "
            "ideation, and creative problem-solving. "
            "Generate unique, unexpected, and practical ideas. Use creative thinking techniques "
            "like lateral thinking, SCAMPER, and design thinking. "
            "Push boundaries while staying relevant to the user's goals. "
            "Respond in the language the user writes in."
        ),
    },
    {
        "id": "finance",
        "emoji": "💰",
        "name_ar": "المستشار المالي",
        "name_en": "Finance Advisor",
        "desc_ar": "خبير مالي يقدم نصائح للاستثمار والادخار",
        "desc_en": "Finance expert for investment and savings advice",
        "system": (
            "You are a knowledgeable financial advisor with expertise in personal finance, "
            "investing, budgeting, savings, stocks, crypto, real estate, and financial planning. "
            "Provide practical, balanced advice. Always note that this is educational information "
            "and users should consult a licensed financial advisor for personal decisions. "
            "Use clear numbers and examples. Respond in the language the user writes in."
        ),
    },
    {
        "id": "health",
        "emoji": "🏥",
        "name_ar": "المستشار الصحي",
        "name_en": "Health Advisor",
        "desc_ar": "نصائح صحية وغذائية ورياضية متخصصة",
        "desc_en": "Health, nutrition, and fitness specialized advice",
        "system": (
            "You are a knowledgeable health and wellness advisor with expertise in nutrition, "
            "fitness, mental health, and general health practices. "
            "Provide science-based, practical health advice. Always recommend consulting a "
            "healthcare professional for medical decisions. "
            "Be empathetic and encouraging. Respond in the language the user writes in."
        ),
    },
    {
        "id": "chef",
        "emoji": "👨‍🍳",
        "name_ar": "الطاهي",
        "name_en": "Chef",
        "desc_ar": "وصفات طبخ ونصائح من طاهٍ محترف",
        "desc_en": "Recipes and cooking tips from a professional chef",
        "system": (
            "You are a professional chef with expertise in cuisines from around the world, "
            "including Arabic, Mediterranean, Asian, European, and more. "
            "Provide detailed recipes with exact measurements, step-by-step instructions, "
            "cooking tips, substitutions, and presentation ideas. "
            "Consider dietary restrictions when asked. Respond in the language the user writes in."
        ),
    },
    {
        "id": "travel",
        "emoji": "✈️",
        "name_ar": "مستشار السفر",
        "name_en": "Travel Advisor",
        "desc_ar": "ينظم رحلاتك ويقترح وجهات ونصائح سفر",
        "desc_en": "Plans trips and suggests destinations with travel tips",
        "system": (
            "You are an expert travel advisor with extensive knowledge of destinations worldwide. "
            "Provide detailed travel itineraries, destination guides, budget tips, visa information, "
            "best seasons to visit, local customs, must-see attractions, and hidden gems. "
            "Consider the traveler's budget, interests, and constraints. "
            "Respond in the language the user writes in."
        ),
    },
    {
        "id": "tutor",
        "emoji": "📚",
        "name_ar": "المعلم",
        "name_en": "Tutor",
        "desc_ar": "معلم صبور يشرح أي موضوع بأسلوب بسيط",
        "desc_en": "Patient teacher explaining any subject simply",
        "system": (
            "You are a patient, encouraging tutor who can teach any subject. "
            "Adapt explanations to the student's level (beginner, intermediate, advanced). "
            "Use analogies, examples, and step-by-step breakdowns. "
            "Check understanding and provide practice exercises when helpful. "
            "Never make the student feel bad for not knowing something. "
            "Respond in the language the user writes in."
        ),
    },
    {
        "id": "lawyer",
        "emoji": "⚖️",
        "name_ar": "المستشار القانوني",
        "name_en": "Legal Advisor",
        "desc_ar": "معلومات قانونية عامة وتوجيه في الشؤون القانونية",
        "desc_en": "General legal information and guidance",
        "system": (
            "You are a knowledgeable legal information assistant with expertise in international, "
            "Arab, and Western legal systems. Provide clear explanations of laws, rights, and procedures. "
            "Always note that this is general information, not legal advice, and users should "
            "consult a licensed lawyer for their specific situation. "
            "Be thorough and cite relevant legal principles. Respond in the language the user writes in."
        ),
    },
    {
        "id": "psychologist",
        "emoji": "🧠",
        "name_ar": "المعالج النفسي",
        "name_en": "Psychologist",
        "desc_ar": "دعم نفسي ونصائح للصحة العاطفية والذهنية",
        "desc_en": "Emotional support and mental health guidance",
        "system": (
            "You are a compassionate and knowledgeable psychological support advisor. "
            "Provide empathetic listening, emotional support, and practical mental health guidance. "
            "Use evidence-based approaches like CBT concepts and mindfulness. "
            "Always encourage professional help for serious issues. "
            "Never diagnose. Be non-judgmental, warm, and supportive. "
            "Respond in the language the user writes in."
        ),
    },
    {
        "id": "scientist",
        "emoji": "🔭",
        "name_ar": "العالم",
        "name_en": "Scientist",
        "desc_ar": "يشرح المفاهيم العلمية من فيزياء وكيمياء وأحياء",
        "desc_en": "Explains scientific concepts from physics to biology",
        "system": (
            "You are a brilliant scientist with deep knowledge across all scientific disciplines: "
            "physics, chemistry, biology, astronomy, geology, neuroscience, and more. "
            "Explain complex scientific concepts clearly and accessibly. "
            "Use analogies to make abstract ideas concrete. "
            "Share the excitement of scientific discovery. Cite current understanding and note open questions. "
            "Respond in the language the user writes in."
        ),
    },
    {
        "id": "designer",
        "emoji": "🎭",
        "name_ar": "المصمم",
        "name_en": "Designer",
        "desc_ar": "نصائح تصميم جرافيك وUI/UX وبراندينج",
        "desc_en": "Graphic design, UI/UX, and branding advice",
        "system": (
            "You are a creative design expert with expertise in graphic design, UI/UX, "
            "brand identity, typography, color theory, and visual communication. "
            "Provide practical design advice, critique designs constructively, "
            "suggest tools and resources, and explain design principles clearly. "
            "Consider user experience and accessibility in all recommendations. "
            "Respond in the language the user writes in."
        ),
    },
    {
        "id": "marketing",
        "emoji": "📣",
        "name_ar": "خبير التسويق",
        "name_en": "Marketing Expert",
        "desc_ar": "استراتيجيات تسويق رقمي ومحتوى وبراند",
        "desc_en": "Digital marketing, content, and brand strategies",
        "system": (
            "You are a marketing expert with deep knowledge of digital marketing, content strategy, "
            "SEO, social media marketing, email marketing, paid advertising, brand building, "
            "growth hacking, and analytics. "
            "Provide actionable, data-driven marketing strategies and tactics. "
            "Consider the target audience, budget, and business goals. "
            "Respond in the language the user writes in."
        ),
    },
    {
        "id": "business",
        "emoji": "💼",
        "name_ar": "مستشار الأعمال",
        "name_en": "Business Advisor",
        "desc_ar": "تخطيط استراتيجي وتطوير أعمال وريادة",
        "desc_en": "Strategic planning, business development, and entrepreneurship",
        "system": (
            "You are a seasoned business advisor with expertise in entrepreneurship, business strategy, "
            "startups, operations, fundraising, business models, competitive analysis, and scaling. "
            "Provide strategic, practical business advice. Help with business plans, pitch decks, "
            "market analysis, and growth strategies. "
            "Draw on successful business frameworks and real-world examples. "
            "Respond in the language the user writes in."
        ),
    },
]

AGENTS_MAP = {a["id"]: a for a in AGENTS}


# ─── Claude Client ────────────────────────────────────────────────────────────

def get_claude_client():
    if not ANTHROPIC_API_KEY:
        return None
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def agents_keyboard(lang: str = "ar", page: int = 0) -> InlineKeyboardMarkup:
    per_page = 10
    start = page * per_page
    end = start + per_page
    page_agents = AGENTS[start:end]
    buttons = []
    row = []
    for i, agent in enumerate(page_agents):
        name = agent["name_ar"] if lang == "ar" else agent["name_en"]
        row.append(InlineKeyboardButton(
            f"{agent['emoji']} {name}",
            callback_data=f"agent_{agent['id']}"
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"agents_page_{page-1}"))
    total_pages = (len(AGENTS) + per_page - 1) // per_page
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"agents_page_{page+1}"))
    if nav:
        buttons.append(nav)

    back = "🔙 رجوع" if lang == "ar" else "🔙 Back"
    buttons.append([InlineKeyboardButton(back, callback_data="menu_main")])
    return InlineKeyboardMarkup(buttons)


async def show_agents_menu(query_or_msg, lang: str = "ar", page: int = 0):
    total = len(AGENTS)
    header = f"🤖 **الإيجنتات المتاحة ({total}):**\n\nاختر إيجنتاً للتحدث معه:" if lang == "ar" else f"🤖 **Available Agents ({total}):**\n\nSelect an agent to chat with:"
    kb = agents_keyboard(lang, page)
    if hasattr(query_or_msg, "edit_message_text"):
        await query_or_msg.edit_message_text(header, parse_mode="Markdown", reply_markup=kb)
    else:
        await query_or_msg.reply_text(header, parse_mode="Markdown", reply_markup=kb)


# ─── Handlers ─────────────────────────────────────────────────────────────────

@register_user
@check_banned
async def agents_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    await show_agents_menu(update.message, lang)


@register_user
@check_banned
async def agent_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    if not ctx.args:
        current = await db.get_user_agent(user.id)
        agent = AGENTS_MAP.get(current, AGENTS[0])
        name = agent["name_ar"] if lang == "ar" else agent["name_en"]
        desc = agent["desc_ar"] if lang == "ar" else agent["desc_en"]
        msg = (
            f"🤖 **إيجنتك الحالي:** {agent['emoji']} {name}\n"
            f"📝 {desc}\n\n"
            f"استخدم `/agents` لتغيير الإيجنت."
        ) if lang == "ar" else (
            f"🤖 **Current Agent:** {agent['emoji']} {name}\n"
            f"📝 {desc}\n\n"
            f"Use `/agents` to change agent."
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    agent_id = ctx.args[0].lower()
    if agent_id not in AGENTS_MAP:
        ids = ", ".join(f"`{a['id']}`" for a in AGENTS)
        err = f"❌ إيجنت غير موجود. الإيجنتات المتاحة:\n{ids}" if lang == "ar" else f"❌ Agent not found. Available:\n{ids}"
        await update.message.reply_text(err, parse_mode="Markdown")
        return

    await db.set_user_agent(user.id, agent_id)
    await db.clear_conversation(user.id, agent_id)
    agent = AGENTS_MAP[agent_id]
    name = agent["name_ar"] if lang == "ar" else agent["name_en"]
    desc = agent["desc_ar"] if lang == "ar" else agent["desc_en"]
    msg = (
        f"✅ **تم تفعيل الإيجنت:**\n\n{agent['emoji']} **{name}**\n📝 {desc}\n\n"
        f"أرسل رسالتك أو استخدم `/chat [رسالة]` للبدء!"
    ) if lang == "ar" else (
        f"✅ **Agent activated:**\n\n{agent['emoji']} **{name}**\n📝 {desc}\n\n"
        f"Send a message or use `/chat [message]` to start!"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


@register_user
@check_banned
async def reset_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    agent_id = await db.get_user_agent(user.id)
    await db.clear_conversation(user.id, agent_id)
    agent = AGENTS_MAP.get(agent_id, AGENTS[0])
    name = agent["name_ar"] if lang == "ar" else agent["name_en"]
    msg = f"🔄 تم مسح محادثتك مع **{name}**." if lang == "ar" else f"🔄 Conversation with **{name}** cleared."
    await update.message.reply_text(msg, parse_mode="Markdown")


@register_user
@check_banned
async def chat_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = await db.get_user_language(user.id)

    if not ctx.args:
        msg = "❌ الاستخدام: `/chat [رسالتك]`" if lang == "ar" else "❌ Usage: `/chat [your message]`"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    message_text = " ".join(ctx.args)
    await process_ai_message(update, message_text, lang)


async def agent_select_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    lang = await db.get_user_language(user.id)
    data = query.data

    if data.startswith("agents_page_"):
        page = int(data.split("_")[-1])
        await show_agents_menu(query, lang, page)
        return

    if data.startswith("agent_"):
        agent_id = data[6:]
        if agent_id not in AGENTS_MAP:
            await query.answer("❌ غير موجود!", show_alert=True)
            return

        await db.set_user_agent(user.id, agent_id)
        await db.clear_conversation(user.id, agent_id)
        agent = AGENTS_MAP[agent_id]
        name = agent["name_ar"] if lang == "ar" else agent["name_en"]
        desc = agent["desc_ar"] if lang == "ar" else agent["desc_en"]

        msg = (
            f"✅ **تم تفعيل:**\n\n{agent['emoji']} **{name}**\n📝 {desc}\n\n"
            f"أرسل رسالتك الآن وسيرد عليك الإيجنت!"
        ) if lang == "ar" else (
            f"✅ **Activated:**\n\n{agent['emoji']} **{name}**\n📝 {desc}\n\n"
            f"Send your message now and the agent will respond!"
        )
        back_btn = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 الإيجنتات" if lang == "ar" else "🔙 Agents", callback_data="menu_agents")
        ]])
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=back_btn)


async def process_ai_message(update: Update, text: str, lang: str):
    """Core function to process messages through the active agent."""
    user = update.effective_user
    agent_id = await db.get_user_agent(user.id)
    agent = AGENTS_MAP.get(agent_id, AGENTS[0])

    client = get_claude_client()
    if not client:
        err = (
            "❌ **خطأ:** مفتاح API للذكاء الاصطناعي غير مضبوط.\n"
            "أضف `ANTHROPIC_API_KEY` في ملف `.env`"
        ) if lang == "ar" else (
            "❌ **Error:** AI API key not configured.\n"
            "Add `ANTHROPIC_API_KEY` to `.env` file"
        )
        await update.message.reply_text(err, parse_mode="Markdown")
        return

    # Show typing indicator
    await update.message.chat.send_action("typing")

    # Save user message
    await db.add_message(user.id, agent_id, "user", text)

    # Get conversation history
    history = await db.get_conversation(user.id, agent_id, AI_HISTORY_LENGTH)

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
            system=agent["system"],
            messages=history,
        )
        reply_text = response.content[0].text
        await db.add_message(user.id, agent_id, "assistant", reply_text)

        agent_name = agent["name_ar"] if lang == "ar" else agent["name_en"]
        header = f"{agent['emoji']} **{agent_name}:**\n\n"

        # Split long messages
        max_len = 4000
        full_text = header + reply_text
        if len(full_text) <= max_len:
            await update.message.reply_text(full_text, parse_mode="Markdown")
        else:
            chunks = [full_text[i:i+max_len] for i in range(0, len(full_text), max_len)]
            for chunk in chunks:
                await update.message.reply_text(chunk, parse_mode="Markdown")

    except anthropic.APIError as e:
        err = f"❌ خطأ في الذكاء الاصطناعي: {e}" if lang == "ar" else f"❌ AI Error: {e}"
        await update.message.reply_text(err)
    except Exception as e:
        err = f"❌ خطأ: {e}" if lang == "ar" else f"❌ Error: {e}"
        await update.message.reply_text(err)


async def ai_message_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handles regular text messages as AI chat when user is in a private chat."""
    if not update.message or not update.message.text:
        return
    if update.effective_chat.type != "private":
        return
    user = update.effective_user
    if await db.is_banned(user.id):
        return

    # Skip if it's a command
    if update.message.text.startswith("/"):
        return

    # Skip if in a guessing game
    from handlers.games import guess_games
    if user.id in guess_games:
        return

    lang = await db.get_user_language(user.id)
    await process_ai_message(update, update.message.text, lang)


def register(app):
    app.add_handler(CommandHandler("agents", agents_cmd))
    app.add_handler(CommandHandler("agent", agent_cmd))
    app.add_handler(CommandHandler("chat", chat_cmd))
    app.add_handler(CommandHandler("ai", chat_cmd))
    app.add_handler(CommandHandler("reset", reset_cmd))
    app.add_handler(CallbackQueryHandler(agent_select_callback, pattern=r"^agent_|^agents_page_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, ai_message_handler), group=20)
