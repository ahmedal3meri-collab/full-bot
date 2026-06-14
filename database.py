import aiosqlite
import json
from datetime import datetime
from config import DATABASE_PATH


async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                first_name  TEXT,
                last_name   TEXT,
                language    TEXT DEFAULT 'ar',
                is_banned   INTEGER DEFAULT 0,
                is_admin    INTEGER DEFAULT 0,
                joined_at   TEXT DEFAULT CURRENT_TIMESTAMP,
                last_seen   TEXT DEFAULT CURRENT_TIMESTAMP,
                total_msgs  INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS notes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                chat_id     INTEGER,
                name        TEXT,
                content     TEXT,
                is_private  INTEGER DEFAULT 1,
                created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, chat_id, name)
            );

            CREATE TABLE IF NOT EXISTS reminders (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                chat_id     INTEGER,
                text        TEXT,
                remind_at   TEXT,
                is_done     INTEGER DEFAULT 0,
                created_at  TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS group_settings (
                chat_id         INTEGER PRIMARY KEY,
                welcome_msg     TEXT,
                goodbye_msg     TEXT,
                antiflood       INTEGER DEFAULT 1,
                antiflood_limit INTEGER DEFAULT 5,
                antiflood_secs  INTEGER DEFAULT 5,
                language        TEXT DEFAULT 'ar'
            );

            CREATE TABLE IF NOT EXISTS ai_conversations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                agent_id    TEXT DEFAULT 'general',
                role        TEXT,
                content     TEXT,
                created_at  TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS user_agents (
                user_id     INTEGER PRIMARY KEY,
                agent_id    TEXT DEFAULT 'general',
                updated_at  TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS bot_stats (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                event       TEXT,
                value       INTEGER DEFAULT 1,
                recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS flood_control (
                user_id     INTEGER,
                chat_id     INTEGER,
                msg_times   TEXT DEFAULT '[]',
                PRIMARY KEY (user_id, chat_id)
            );
        """)
        await db.commit()
        # Migration: add is_private column to existing notes tables
        try:
            await db.execute("ALTER TABLE notes ADD COLUMN is_private INTEGER DEFAULT 1")
            await db.commit()
        except Exception:
            pass


# ─── Users ────────────────────────────────────────────────────────────────────

async def upsert_user(user):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, username, first_name, last_name, last_seen, total_msgs)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, 1)
            ON CONFLICT(user_id) DO UPDATE SET
                username   = excluded.username,
                first_name = excluded.first_name,
                last_name  = excluded.last_name,
                last_seen  = CURRENT_TIMESTAMP,
                total_msgs = total_msgs + 1
        """, (user.id, user.username, user.first_name, user.last_name))
        await db.commit()


async def get_user(user_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_all_users():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE is_banned = 0") as cur:
            return [dict(r) for r in await cur.fetchall()]


async def set_user_language(user_id: int, lang: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))
        await db.commit()


async def get_user_language(user_id: int) -> str:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT language FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else "ar"


async def ban_user(user_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
        await db.commit()


async def unban_user(user_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
        await db.commit()


async def is_banned(user_id: int) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return bool(row[0]) if row else False


async def set_admin(user_id: int, is_admin: bool):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE users SET is_admin = ? WHERE user_id = ?", (int(is_admin), user_id))
        await db.commit()


async def get_stats():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            total = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1") as cur:
            banned = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM notes") as cur:
            notes = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM reminders WHERE is_done = 0") as cur:
            reminders = (await cur.fetchone())[0]
        async with db.execute("SELECT SUM(total_msgs) FROM users") as cur:
            msgs = (await cur.fetchone())[0] or 0
    return {"total_users": total, "banned": banned, "notes": notes,
            "active_reminders": reminders, "total_messages": msgs}


# ─── Notes ────────────────────────────────────────────────────────────────────

async def save_note(user_id: int, chat_id: int, name: str, content: str, is_private: int = 1):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO notes (user_id, chat_id, name, content, is_private)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, chat_id, name) DO UPDATE SET content = excluded.content, is_private = excluded.is_private
        """, (user_id, chat_id, name, content, is_private))
        await db.commit()


async def get_note(user_id: int, chat_id: int, name: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Try user's own note first
        async with db.execute(
            "SELECT content FROM notes WHERE user_id=? AND chat_id=? AND name=?",
            (user_id, chat_id, name)
        ) as cur:
            row = await cur.fetchone()
            if row:
                return row[0]
        # Fall back to any public note with that name in the same chat
        async with db.execute(
            "SELECT content FROM notes WHERE chat_id=? AND name=? AND is_private=0 LIMIT 1",
            (chat_id, name)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else None


async def list_notes(user_id: int, chat_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            """SELECT name, created_at, is_private, user_id
               FROM notes
               WHERE chat_id=? AND (user_id=? OR is_private=0)
               ORDER BY user_id=? DESC, name""",
            (chat_id, user_id, user_id)
        ) as cur:
            return await cur.fetchall()


async def set_note_privacy(user_id: int, chat_id: int, name: str, is_private: int) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute(
            "UPDATE notes SET is_private=? WHERE user_id=? AND chat_id=? AND name=?",
            (is_private, user_id, chat_id, name)
        )
        await db.commit()
        return cur.rowcount > 0


async def delete_note(user_id: int, chat_id: int, name: str) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute(
            "DELETE FROM notes WHERE user_id=? AND chat_id=? AND name=?",
            (user_id, chat_id, name)
        )
        await db.commit()
        return cur.rowcount > 0


async def count_notes(user_id: int, chat_id: int) -> int:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM notes WHERE user_id=? AND chat_id=?", (user_id, chat_id)
        ) as cur:
            return (await cur.fetchone())[0]


# ─── Reminders ────────────────────────────────────────────────────────────────

async def add_reminder(user_id: int, chat_id: int, text: str, remind_at: datetime):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("""
            INSERT INTO reminders (user_id, chat_id, text, remind_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, chat_id, text, remind_at.isoformat()))
        await db.commit()
        return cur.lastrowid


async def get_pending_reminders():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        now = datetime.utcnow().isoformat()
        async with db.execute(
            "SELECT * FROM reminders WHERE is_done=0 AND remind_at <= ?", (now,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def mark_reminder_done(reminder_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE reminders SET is_done=1 WHERE id=?", (reminder_id,))
        await db.commit()


async def list_reminders(user_id: int, chat_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM reminders WHERE user_id=? AND chat_id=? AND is_done=0 ORDER BY remind_at",
            (user_id, chat_id)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def cancel_reminder(user_id: int, reminder_id: int) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute(
            "DELETE FROM reminders WHERE id=? AND user_id=?", (reminder_id, user_id)
        )
        await db.commit()
        return cur.rowcount > 0


async def count_reminders(user_id: int, chat_id: int) -> int:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM reminders WHERE user_id=? AND chat_id=? AND is_done=0",
            (user_id, chat_id)
        ) as cur:
            return (await cur.fetchone())[0]


# ─── Group Settings ───────────────────────────────────────────────────────────

async def get_group_settings(chat_id: int) -> dict:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM group_settings WHERE chat_id=?", (chat_id,)) as cur:
            row = await cur.fetchone()
            if row:
                return dict(row)
            return {"chat_id": chat_id, "welcome_msg": None, "goodbye_msg": None,
                    "antiflood": 1, "antiflood_limit": 5, "antiflood_secs": 5, "language": "ar"}


async def update_group_settings(chat_id: int, **kwargs):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        fields = ", ".join(f"{k}=?" for k in kwargs)
        values = list(kwargs.values()) + [chat_id]
        await db.execute(f"""
            INSERT INTO group_settings (chat_id) VALUES (?)
            ON CONFLICT(chat_id) DO UPDATE SET {fields}
        """.replace("INSERT INTO group_settings (chat_id) VALUES (?)",
                     f"INSERT INTO group_settings (chat_id, {', '.join(kwargs.keys())}) VALUES (?, {', '.join('?' for _ in kwargs)})"),
            [chat_id] + list(kwargs.values()))
        await db.commit()


# ─── AI Conversations ─────────────────────────────────────────────────────────

async def add_message(user_id: int, agent_id: str, role: str, content: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO ai_conversations (user_id, agent_id, role, content) VALUES (?,?,?,?)",
            (user_id, agent_id, role, content)
        )
        await db.commit()


async def get_conversation(user_id: int, agent_id: str, limit: int = 20):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT role, content FROM (
                SELECT role, content, created_at FROM ai_conversations
                WHERE user_id=? AND agent_id=?
                ORDER BY created_at DESC LIMIT ?
            ) ORDER BY created_at ASC
        """, (user_id, agent_id, limit)) as cur:
            return [{"role": r["role"], "content": r["content"]} for r in await cur.fetchall()]


async def clear_conversation(user_id: int, agent_id: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "DELETE FROM ai_conversations WHERE user_id=? AND agent_id=?", (user_id, agent_id)
        )
        await db.commit()


async def get_user_agent(user_id: int) -> str:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT agent_id FROM user_agents WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else "general"


async def set_user_agent(user_id: int, agent_id: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO user_agents (user_id, agent_id) VALUES (?,?)
            ON CONFLICT(user_id) DO UPDATE SET agent_id=excluded.agent_id, updated_at=CURRENT_TIMESTAMP
        """, (user_id, agent_id))
        await db.commit()


# ─── Flood Control ────────────────────────────────────────────────────────────

async def check_flood(user_id: int, chat_id: int, limit: int, window: int) -> bool:
    """Returns True if user is flooding."""
    import time
    now = time.time()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT msg_times FROM flood_control WHERE user_id=? AND chat_id=?", (user_id, chat_id)
        ) as cur:
            row = await cur.fetchone()
        times = json.loads(row[0]) if row else []
        times = [t for t in times if now - t < window]
        times.append(now)
        is_flood = len(times) > limit
        await db.execute("""
            INSERT INTO flood_control (user_id, chat_id, msg_times) VALUES (?,?,?)
            ON CONFLICT(user_id, chat_id) DO UPDATE SET msg_times=excluded.msg_times
        """, (user_id, chat_id, json.dumps(times)))
        await db.commit()
    return is_flood
