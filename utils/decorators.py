from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
import database as db
from config import ADMIN_IDS
from locales.strings import t


def check_banned(func):
    @wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not update.effective_user:
            return
        if await db.is_banned(update.effective_user.id):
            lang = await db.get_user_language(update.effective_user.id)
            await update.effective_message.reply_text(t("banned", lang))
            return
        return await func(update, ctx, *args, **kwargs)
    return wrapper


def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not update.effective_user:
            return
        user = update.effective_user
        lang = await db.get_user_language(user.id)
        db_user = await db.get_user(user.id)
        is_admin = user.id in ADMIN_IDS or (db_user and db_user.get("is_admin"))
        if not is_admin:
            await update.effective_message.reply_text(t("admin_only", lang))
            return
        return await func(update, ctx, *args, **kwargs)
    return wrapper


def group_admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not update.effective_user or not update.effective_chat:
            return
        user = update.effective_user
        chat = update.effective_chat
        lang = await db.get_user_language(user.id)
        if chat.type == "private":
            return await func(update, ctx, *args, **kwargs)
        member = await chat.get_member(user.id)
        if member.status not in ("administrator", "creator"):
            await update.effective_message.reply_text(t("group_admin_only", lang))
            return
        return await func(update, ctx, *args, **kwargs)
    return wrapper


def register_user(func):
    @wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if update.effective_user:
            await db.upsert_user(update.effective_user)
        return await func(update, ctx, *args, **kwargs)
    return wrapper


def private_only(func):
    @wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if update.effective_chat and update.effective_chat.type != "private":
            await update.effective_message.reply_text("هذا الأمر يعمل في المحادثة الخاصة فقط.")
            return
        return await func(update, ctx, *args, **kwargs)
    return wrapper
