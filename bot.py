import asyncio
import csv
import hashlib
import hmac
import json
import logging
import os
import random
import re
import sqlite3
from contextlib import closing
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import parse_qsl
from zoneinfo import ZoneInfo

from aiohttp import web
from telegram import Bot, ChatInviteLink, InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.constants import ChatMemberStatus
from telegram.error import BadRequest, Forbidden, TelegramError
from telegram.ext import (
    Application,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
)
from dotenv import load_dotenv


load_dotenv()

DB_PATH = os.getenv("DB_PATH", "invites.sqlite3")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
WEBAPP_URL = os.getenv("WEBAPP_URL", "").strip()
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "127.0.0.1")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", "8080"))
WEB_DIR = Path(__file__).parent / "web"
SNAPSHOT_DIR = Path(os.getenv("SNAPSHOT_DIR", "snapshots"))
SNAPSHOT_TZ = ZoneInfo(os.getenv("SNAPSHOT_TZ", "Europe/Warsaw"))
WEEKLY_RESET_WEEKDAY = 6
WEEKLY_RESET_TIME = time(23, 59)
DEFAULT_WEEKLY_PRIZES = [
    os.getenv("WEEKLY_PRIZE_1", "8 часов игры"),
    os.getenv("WEEKLY_PRIZE_2", "5 часов игры"),
    os.getenv("WEEKLY_PRIZE_3", "3 часа игры"),
]
INVITE_COIN_REWARD = 20
STREAK_BONUSES = {
    3: 50,
    7: 150,
    14: 300,
    30: 500,
}
CLAN_LEVELS = [
    {"level": 1, "slots": 5, "xp": 0},
    {"level": 2, "slots": 7, "xp": 500},
    {"level": 3, "slots": 10, "xp": 1500},
    {"level": 4, "slots": 15, "xp": 4000},
    {"level": 5, "slots": 20, "xp": 8000},
    {"level": 6, "slots": 25, "xp": 15000},
    {"level": 7, "slots": 30, "xp": 25000},
    {"level": 8, "slots": 40, "xp": 45000},
    {"level": 9, "slots": 50, "xp": 75000},
    {"level": 10, "slots": 75, "xp": 120000},
]
CLAN_CHESTS = [
    {"key": "common", "title": "Common Chest", "xp": 500, "members": 5, "hours": 1},
    {"key": "rare", "title": "Rare Chest", "xp": 1500, "members": 20, "hours": 2},
    {"key": "epic", "title": "Epic Chest", "xp": 3500, "members": 40, "hours": 3},
]
CLAN_CHECKIN_XP = 10
CLAN_DAILY_GOAL_MEMBERS = 3
CLAN_DAILY_GOAL_XP = 50
CLAN_CHEST_ACTIVE_XP = 50
LEAGUE_GAMES = {
    "cs2": "CS2",
}
LEAGUE_FORMATS = {
    "2x2": {"title": "2×2", "min": 2, "max": 2},
    "5x5": {"title": "5×5", "min": 5, "max": 6},
}
LEAGUE_ADMIN_IDS = {
    int(value.strip())
    for value in os.getenv("LEAGUE_ADMIN_IDS", "").split(",")
    if value.strip().isdigit()
}
RANKS = [
    {"title": "Recruit", "icon": "🥉", "minScore": 0},
    {"title": "Rookie", "icon": "🥈", "minScore": 10},
    {"title": "Grinder", "icon": "🥇", "minScore": 20},
    {"title": "Veteran", "icon": "💠", "minScore": 30},
    {"title": "Elite", "icon": "🔥", "minScore": 40},
    {"title": "Legend", "icon": "👑", "minScore": 50},
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def utc_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds")


def db() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with closing(db()) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS invite_links (
                invite_link TEXT PRIMARY KEY,
                owner_id INTEGER NOT NULL,
                owner_username TEXT,
                owner_full_name TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS invited_members (
                chat_id INTEGER NOT NULL,
                invited_user_id INTEGER NOT NULL,
                invite_link TEXT NOT NULL,
                owner_id INTEGER NOT NULL,
                joined_at TEXT NOT NULL,
                PRIMARY KEY (chat_id, invited_user_id)
            );

            CREATE TABLE IF NOT EXISTS app_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS weekly_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period_start TEXT NOT NULL,
                period_end TEXT NOT NULL,
                file_path TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                club_login TEXT NOT NULL DEFAULT '',
                coins INTEGER NOT NULL DEFAULT 0,
                visits INTEGER NOT NULL DEFAULT 0,
                last_daily_reward_date TEXT NOT NULL DEFAULT '',
                last_visit_reward_date TEXT NOT NULL DEFAULT '',
                visit_streak INTEGER NOT NULL DEFAULT 0,
                instagram_reward_claimed INTEGER NOT NULL DEFAULT 0,
                discord_reward_claimed INTEGER NOT NULL DEFAULT 0,
                instagram_reward_requested_at TEXT NOT NULL DEFAULT '',
                discord_reward_requested_at TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS clans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                code TEXT NOT NULL UNIQUE,
                leader_id INTEGER NOT NULL,
                is_public INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS clan_members (
                user_id INTEGER PRIMARY KEY,
                clan_id INTEGER NOT NULL,
                role TEXT NOT NULL DEFAULT 'member',
                username TEXT NOT NULL DEFAULT '',
                full_name TEXT NOT NULL DEFAULT '',
                joined_at TEXT NOT NULL,
                FOREIGN KEY (clan_id) REFERENCES clans(id)
            );

            CREATE TABLE IF NOT EXISTS clan_xp_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clan_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                kind TEXT NOT NULL,
                day_key TEXT NOT NULL,
                week_start TEXT NOT NULL,
                month_key TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (clan_id) REFERENCES clans(id)
            );

            CREATE TABLE IF NOT EXISTS clan_daily_goals (
                clan_id INTEGER NOT NULL,
                day_key TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (clan_id, day_key)
            );

            CREATE TABLE IF NOT EXISTS league_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER NOT NULL UNIQUE,
                username TEXT NOT NULL DEFAULT '',
                game_nick_cs2 TEXT NOT NULL DEFAULT '',
                role TEXT NOT NULL DEFAULT 'player',
                xp INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS league_seasons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game TEXT NOT NULL,
                format TEXT,
                name TEXT NOT NULL DEFAULT '',
                start_date TEXT NOT NULL DEFAULT '',
                end_date TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'registration',
                winner_team_id INTEGER
            );

            CREATE TABLE IF NOT EXISTS league_teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                game TEXT NOT NULL,
                format TEXT,
                captain_id INTEGER NOT NULL,
                season_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                invite_token TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                FOREIGN KEY (captain_id) REFERENCES league_users(id),
                FOREIGN KEY (season_id) REFERENCES league_seasons(id)
            );

            CREATE TABLE IF NOT EXISTS league_team_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                season_id INTEGER,
                joined_at TEXT NOT NULL,
                UNIQUE (team_id, user_id),
                FOREIGN KEY (team_id) REFERENCES league_teams(id),
                FOREIGN KEY (user_id) REFERENCES league_users(id)
            );

            CREATE TABLE IF NOT EXISTS league_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                season_id INTEGER NOT NULL,
                team1_id INTEGER NOT NULL,
                team2_id INTEGER NOT NULL,
                scheduled_at TEXT NOT NULL DEFAULT '',
                score1 INTEGER,
                score2 INTEGER,
                status TEXT NOT NULL DEFAULT 'scheduled',
                winner_id INTEGER,
                FOREIGN KEY (season_id) REFERENCES league_seasons(id),
                FOREIGN KEY (team1_id) REFERENCES league_teams(id),
                FOREIGN KEY (team2_id) REFERENCES league_teams(id)
            );

            CREATE TABLE IF NOT EXISTS league_match_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                reported_by INTEGER NOT NULL,
                score_own INTEGER NOT NULL,
                score_opponent INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE (match_id, reported_by),
                FOREIGN KEY (match_id) REFERENCES league_matches(id),
                FOREIGN KEY (reported_by) REFERENCES league_users(id)
            );

            CREATE TABLE IF NOT EXISTS league_standings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                season_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL,
                rank INTEGER NOT NULL,
                prev_rank INTEGER,
                played INTEGER NOT NULL DEFAULT 0,
                wins INTEGER NOT NULL DEFAULT 0,
                losses INTEGER NOT NULL DEFAULT 0,
                points INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (season_id) REFERENCES league_seasons(id),
                FOREIGN KEY (team_id) REFERENCES league_teams(id)
            );
            """
        )
        ensure_user_profile_columns(connection)
        ensure_league_format_columns(connection)
        ensure_league_member_columns(connection)
        ensure_weekly_period_start(connection)
        ensure_default_league_seasons(connection)
        connection.commit()


def ensure_user_profile_columns(connection: sqlite3.Connection) -> None:
    columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(user_profiles)").fetchall()
    }
    if "coins" not in columns:
        connection.execute("ALTER TABLE user_profiles ADD COLUMN coins INTEGER NOT NULL DEFAULT 0")
    if "visits" not in columns:
        connection.execute("ALTER TABLE user_profiles ADD COLUMN visits INTEGER NOT NULL DEFAULT 0")
    if "last_daily_reward_date" not in columns:
        connection.execute("ALTER TABLE user_profiles ADD COLUMN last_daily_reward_date TEXT NOT NULL DEFAULT ''")
    if "last_visit_reward_date" not in columns:
        connection.execute("ALTER TABLE user_profiles ADD COLUMN last_visit_reward_date TEXT NOT NULL DEFAULT ''")
    if "visit_streak" not in columns:
        connection.execute("ALTER TABLE user_profiles ADD COLUMN visit_streak INTEGER NOT NULL DEFAULT 0")
    if "instagram_reward_claimed" not in columns:
        connection.execute("ALTER TABLE user_profiles ADD COLUMN instagram_reward_claimed INTEGER NOT NULL DEFAULT 0")
    if "discord_reward_claimed" not in columns:
        connection.execute("ALTER TABLE user_profiles ADD COLUMN discord_reward_claimed INTEGER NOT NULL DEFAULT 0")
    if "instagram_reward_requested_at" not in columns:
        connection.execute("ALTER TABLE user_profiles ADD COLUMN instagram_reward_requested_at TEXT NOT NULL DEFAULT ''")
    if "discord_reward_requested_at" not in columns:
        connection.execute("ALTER TABLE user_profiles ADD COLUMN discord_reward_requested_at TEXT NOT NULL DEFAULT ''")


def ensure_league_format_columns(connection: sqlite3.Connection) -> None:
    season_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(league_seasons)").fetchall()
    }
    if "format" not in season_columns:
        connection.execute("ALTER TABLE league_seasons ADD COLUMN format TEXT")
    if "name" not in season_columns:
        connection.execute("ALTER TABLE league_seasons ADD COLUMN name TEXT NOT NULL DEFAULT ''")
    connection.execute("UPDATE league_seasons SET format = '5x5' WHERE game = 'cs2' AND (format IS NULL OR format = '')")
    connection.execute(
        """
        UPDATE league_seasons
        SET name = CASE
            WHEN game = 'cs2' THEN 'CS2 · ' || COALESCE(format, '5x5')
            ELSE game || ' · Сезон'
        END
        WHERE name = ''
        """
    )

    team_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(league_teams)").fetchall()
    }
    if "format" not in team_columns:
        connection.execute("ALTER TABLE league_teams ADD COLUMN format TEXT")
    connection.execute("UPDATE league_teams SET format = '5x5' WHERE game = 'cs2' AND (format IS NULL OR format = '')")
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_seasons_game_format_status
        ON league_seasons (game, format, status)
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_teams_season_format
        ON league_teams (season_id, format)
        """
    )
    connection.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_standings_season_team
        ON league_standings (season_id, team_id)
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_standings_rank
        ON league_standings (season_id, rank ASC)
        """
    )


def ensure_league_member_columns(connection: sqlite3.Connection) -> None:
    columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(league_team_members)").fetchall()
    }
    if "season_id" not in columns:
        connection.execute("ALTER TABLE league_team_members ADD COLUMN season_id INTEGER")
        connection.execute(
            """
            UPDATE league_team_members
            SET season_id = (
                SELECT season_id
                FROM league_teams
                WHERE league_teams.id = league_team_members.team_id
            )
            WHERE season_id IS NULL
            """
        )
    connection.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_league_member_season
        ON league_team_members (user_id, season_id)
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_league_team_code
        ON league_teams (invite_token)
        """
    )


def previous_weekly_reset(now: Optional[datetime] = None) -> datetime:
    local_now = (now or datetime.now(timezone.utc)).astimezone(SNAPSHOT_TZ)
    candidate = datetime.combine(local_now.date(), WEEKLY_RESET_TIME, tzinfo=SNAPSHOT_TZ)
    days_since_reset_day = (local_now.weekday() - WEEKLY_RESET_WEEKDAY) % 7
    candidate -= timedelta(days=days_since_reset_day)
    if candidate > local_now:
        candidate -= timedelta(days=7)
    return candidate.astimezone(timezone.utc)


def next_weekly_reset(now: Optional[datetime] = None) -> datetime:
    local_now = (now or datetime.now(timezone.utc)).astimezone(SNAPSHOT_TZ)
    candidate = datetime.combine(local_now.date(), WEEKLY_RESET_TIME, tzinfo=SNAPSHOT_TZ)
    days_until_reset_day = (WEEKLY_RESET_WEEKDAY - local_now.weekday()) % 7
    candidate += timedelta(days=days_until_reset_day)
    if candidate <= local_now:
        candidate += timedelta(days=7)
    return candidate.astimezone(timezone.utc)


def ensure_weekly_period_start(connection: sqlite3.Connection) -> None:
    row = connection.execute("SELECT value FROM app_state WHERE key = 'weekly_period_start'").fetchone()
    if row:
        return

    connection.execute(
        "INSERT INTO app_state (key, value) VALUES ('weekly_period_start', ?)",
        (utc_iso(previous_weekly_reset()),),
    )


def ensure_default_league_seasons(connection: sqlite3.Connection) -> None:
    today = datetime.now(SNAPSHOT_TZ).date().isoformat()
    defaults = [
        ("cs2", "5x5", "CS2 · 5×5 · Регистрация"),
        ("cs2", "2x2", "CS2 · 2×2 · Регистрация"),
    ]
    for game, league_format, name in defaults:
        row = connection.execute(
            """
            SELECT id FROM league_seasons
            WHERE game = ?
              AND (format IS ? OR format = ?)
              AND status IN ('registration', 'active')
            LIMIT 1
            """,
            (game, league_format, league_format),
        ).fetchone()
        if row:
            continue
        connection.execute(
            """
            INSERT INTO league_seasons (game, format, name, start_date, end_date, status, winner_team_id)
            VALUES (?, ?, ?, ?, '', 'registration', NULL)
            """,
            (game, league_format, name, today),
        )


def get_state(key: str) -> Optional[str]:
    with closing(db()) as connection:
        row = connection.execute("SELECT value FROM app_state WHERE key = ?", (key,)).fetchone()
        return str(row["value"]) if row else None


def set_state(key: str, value: str) -> None:
    with closing(db()) as connection:
        connection.execute(
            "INSERT INTO app_state (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        connection.commit()


def weekly_period_start() -> str:
    value = get_state("weekly_period_start")
    if value:
        return value

    start = utc_iso(previous_weekly_reset())
    set_state("weekly_period_start", start)
    return start


def save_invite_link(link: ChatInviteLink, owner_id: int, username: Optional[str], full_name: str) -> None:
    with closing(db()) as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO invite_links
                (invite_link, owner_id, owner_username, owner_full_name, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (link.invite_link, owner_id, username, full_name, utc_now()),
        )
        connection.commit()


def find_link_owner(invite_link: str) -> Optional[sqlite3.Row]:
    with closing(db()) as connection:
        return connection.execute(
            "SELECT * FROM invite_links WHERE invite_link = ?",
            (invite_link,),
        ).fetchone()


def latest_invite_for_owner(owner_id: int) -> Optional[sqlite3.Row]:
    with closing(db()) as connection:
        return connection.execute(
            """
            SELECT * FROM invite_links
            WHERE owner_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (owner_id,),
        ).fetchone()


def record_join(chat_id: int, invited_user_id: int, invite_link: str, owner_id: int) -> bool:
    with closing(db()) as connection:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO invited_members
                (chat_id, invited_user_id, invite_link, owner_id, joined_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (chat_id, invited_user_id, invite_link, owner_id, utc_now()),
        )
        connection.commit()
        return cursor.rowcount == 1


def stats_for_owner(owner_id: int) -> int:
    with closing(db()) as connection:
        row = connection.execute(
            "SELECT COUNT(*) AS total FROM invited_members WHERE owner_id = ?",
            (owner_id,),
        ).fetchone()
        return int(row["total"])


def weekly_stats_for_owner(owner_id: int) -> int:
    with closing(db()) as connection:
        row = connection.execute(
            "SELECT COUNT(*) AS total FROM invited_members WHERE owner_id = ? AND joined_at >= ?",
            (owner_id, weekly_period_start()),
        ).fetchone()
        return int(row["total"])


def normalize_club_login(value: object) -> str:
    login = str(value or "").strip()
    login = " ".join(login.split())
    if len(login) > 40:
        raise web.HTTPBadRequest(reason="Логин слишком длинный")
    return login


def local_day_key(offset_days: int = 0) -> str:
    local_now = datetime.now(timezone.utc).astimezone(SNAPSHOT_TZ)
    return (local_now.date() + timedelta(days=offset_days)).isoformat()


def hours_since(value: str) -> Optional[float]:
    if not value:
        return None
    try:
        created_at = datetime.fromisoformat(value)
    except ValueError:
        return None
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - created_at.astimezone(timezone.utc)
    return max(0, delta.total_seconds() / 3600)


def social_mission_state(claimed: bool, requested_at: str, url: str) -> Dict[str, object]:
    elapsed_hours = hours_since(requested_at)
    is_pending = bool(requested_at) and not claimed and (elapsed_hours is None or elapsed_hours < 24)
    is_ready = bool(requested_at) and not claimed and elapsed_hours is not None and elapsed_hours >= 24
    hours_left = max(0, 24 - int(elapsed_hours or 0)) if is_pending else 0
    return {
        "reward": 500,
        "status": "claimed" if claimed else "ready" if is_ready else "pending" if is_pending else "new",
        "canClaim": not claimed and not is_pending,
        "canReceive": is_ready,
        "requestedAt": requested_at,
        "hoursLeft": hours_left,
        "url": url,
    }


def ensure_user_profile(user_id: int, connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        INSERT INTO user_profiles (user_id, updated_at)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO NOTHING
        """,
        (user_id, utc_now()),
    )


def save_club_login(user_id: int, club_login: str) -> None:
    with closing(db()) as connection:
        connection.execute(
            """
            INSERT INTO user_profiles (user_id, club_login, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                club_login = excluded.club_login,
                updated_at = excluded.updated_at
            """,
            (user_id, club_login, utc_now()),
        )
        connection.commit()


def club_login_for_user(user_id: int) -> str:
    with closing(db()) as connection:
        row = connection.execute(
            "SELECT club_login FROM user_profiles WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return str(row["club_login"]) if row else ""


def profile_progress_for_user(user_id: int) -> Dict[str, int]:
    with closing(db()) as connection:
        row = connection.execute(
            "SELECT coins, visits FROM user_profiles WHERE user_id = ?",
            (user_id,),
        ).fetchone()

    invites = stats_for_owner(user_id)
    bonus_coins = int(row["coins"]) if row else 0
    visits = int(row["visits"]) if row else 0
    return {
        "invites": invites,
        "coins": invites * INVITE_COIN_REWARD + bonus_coins,
        "visits": visits,
        "score": invites,
        "inviteCoinReward": INVITE_COIN_REWARD,
    }


def missions_for_user(user_id: int) -> Dict[str, object]:
    today = local_day_key()
    with closing(db()) as connection:
        ensure_user_profile(user_id, connection)
        row = connection.execute(
            """
            SELECT
                last_daily_reward_date,
                last_visit_reward_date,
                visit_streak,
                instagram_reward_claimed,
                discord_reward_claimed,
                instagram_reward_requested_at,
                discord_reward_requested_at
            FROM user_profiles
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()
        connection.commit()

    last_daily = str(row["last_daily_reward_date"] or "") if row else ""
    last_visit = str(row["last_visit_reward_date"] or "") if row else ""
    streak = int(row["visit_streak"] or 0) if row else 0
    instagram_claimed = bool(row["instagram_reward_claimed"]) if row else False
    discord_claimed = bool(row["discord_reward_claimed"]) if row else False
    instagram_requested_at = str(row["instagram_reward_requested_at"] or "") if row else ""
    discord_requested_at = str(row["discord_reward_requested_at"] or "") if row else ""
    return {
        "dailyReward": {
            "rewardMin": 10,
            "rewardMax": 50,
            "canClaim": last_daily != today,
            "lastClaimDate": last_daily,
        },
        "visitReward": {
            "reward": 5,
            "canClaim": last_visit != today,
            "lastClaimDate": last_visit,
        },
        "streak": {
            "days": streak,
            "milestones": [
                {"days": days, "reward": reward}
                for days, reward in STREAK_BONUSES.items()
            ],
        },
        "social": {
            "instagram": social_mission_state(
                instagram_claimed,
                instagram_requested_at,
                "https://www.instagram.com/hardpoint_szczecin",
            ),
            "discord": social_mission_state(
                discord_claimed,
                discord_requested_at,
                "https://discord.gg/8zJUFdjA",
            ),
        },
    }


def claim_mission_reward(user_id: int, mission: str) -> Dict[str, object]:
    today = local_day_key()
    yesterday = local_day_key(-1)
    now = utc_now()

    with closing(db()) as connection:
        ensure_user_profile(user_id, connection)
        row = connection.execute(
            """
            SELECT
                coins,
                last_daily_reward_date,
                last_visit_reward_date,
                visit_streak,
                instagram_reward_claimed,
                discord_reward_claimed,
                instagram_reward_requested_at,
                discord_reward_requested_at
            FROM user_profiles
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

        if not row:
            raise web.HTTPInternalServerError(reason="Профиль не найден")

        coins = int(row["coins"] or 0)
        awarded = 0
        bonus = 0
        message = ""

        if mission == "daily":
            if str(row["last_daily_reward_date"] or "") == today:
                raise web.HTTPBadRequest(reason="Daily Reward уже получен сегодня")
            awarded = random.randint(10, 50)
            connection.execute(
                """
                UPDATE user_profiles
                SET coins = ?, last_daily_reward_date = ?, updated_at = ?
                WHERE user_id = ?
                """,
                (coins + awarded, today, now, user_id),
            )
            message = f"Daily Reward: +{awarded} HP Coins"
        elif mission == "visit":
            last_visit = str(row["last_visit_reward_date"] or "")
            if last_visit == today:
                raise web.HTTPBadRequest(reason="Награда за вход уже получена сегодня")

            previous_streak = int(row["visit_streak"] or 0)
            streak = previous_streak + 1 if last_visit == yesterday else 1
            awarded = 5
            bonus = STREAK_BONUSES.get(streak, 0)

            connection.execute(
                """
                UPDATE user_profiles
                SET coins = ?, visits = visits + 1, last_visit_reward_date = ?, visit_streak = ?, updated_at = ?
                WHERE user_id = ?
                """,
                (coins + awarded + bonus, today, streak, now, user_id),
            )
            message = f"Вход в бота: +{awarded + bonus} HP Coins"
        elif mission == "instagram":
            if int(row["instagram_reward_claimed"] or 0):
                raise web.HTTPBadRequest(reason="Награда за Instagram уже получена")
            requested_at = str(row["instagram_reward_requested_at"] or "")
            elapsed_hours = hours_since(requested_at)
            if not requested_at:
                connection.execute(
                    """
                    UPDATE user_profiles
                    SET instagram_reward_requested_at = ?, updated_at = ?
                    WHERE user_id = ?
                    """,
                    (now, now, user_id),
                )
                message = "Instagram отправлен на проверку. Награда будет доступна через 24 часа."
            elif elapsed_hours is not None and elapsed_hours >= 24:
                awarded = 500
                connection.execute(
                    """
                    UPDATE user_profiles
                    SET coins = ?, instagram_reward_claimed = 1, updated_at = ?
                    WHERE user_id = ?
                    """,
                    (coins + awarded, now, user_id),
                )
                message = "Instagram проверен: +500 HP Coins"
            else:
                raise web.HTTPBadRequest(reason="Instagram ещё на проверке")
        elif mission == "discord":
            if int(row["discord_reward_claimed"] or 0):
                raise web.HTTPBadRequest(reason="Награда за Discord уже получена")
            requested_at = str(row["discord_reward_requested_at"] or "")
            elapsed_hours = hours_since(requested_at)
            if not requested_at:
                connection.execute(
                    """
                    UPDATE user_profiles
                    SET discord_reward_requested_at = ?, updated_at = ?
                    WHERE user_id = ?
                    """,
                    (now, now, user_id),
                )
                message = "Discord отправлен на проверку. Награда будет доступна через 24 часа."
            elif elapsed_hours is not None and elapsed_hours >= 24:
                awarded = 500
                connection.execute(
                    """
                    UPDATE user_profiles
                    SET coins = ?, discord_reward_claimed = 1, updated_at = ?
                    WHERE user_id = ?
                    """,
                    (coins + awarded, now, user_id),
                )
                message = "Discord проверен: +500 HP Coins"
            else:
                raise web.HTTPBadRequest(reason="Discord ещё на проверке")
        else:
            raise web.HTTPBadRequest(reason="Неизвестная миссия")

        connection.commit()

    progress = profile_progress_for_user(user_id)
    return {
        "ok": True,
        "message": message,
        "awardedCoins": awarded,
        "bonusCoins": bonus,
        "totalAwardedCoins": awarded + bonus,
        "missions": missions_for_user(user_id),
        "user": {
            "progress": progress,
            "rank": rank_for_score(progress["score"]),
        },
    }


def rank_for_score(score: int) -> Dict[str, object]:
    current = RANKS[0]
    next_rank: Optional[Dict[str, object]] = None
    for index, rank in enumerate(RANKS):
        if score >= int(rank["minScore"]):
            current = rank
            next_rank = RANKS[index + 1] if index + 1 < len(RANKS) else None

    next_score = int(next_rank["minScore"]) if next_rank else int(current["minScore"])
    remaining = max(0, next_score - score) if next_rank else 0
    return {
        "title": current["title"],
        "icon": current["icon"],
        "score": score,
        "nextTitle": next_rank["title"] if next_rank else "",
        "nextIcon": next_rank["icon"] if next_rank else "",
        "nextScore": next_score,
        "remaining": remaining,
        "isMax": next_rank is None,
    }


def month_key(offset_months: int = 0) -> str:
    local_now = datetime.now(timezone.utc).astimezone(SNAPSHOT_TZ)
    year = local_now.year
    month = local_now.month + offset_months
    while month < 1:
        month += 12
        year -= 1
    while month > 12:
        month -= 12
        year += 1
    return f"{year:04d}-{month:02d}"


def normalize_clan_name(value: object) -> str:
    name = " ".join(str(value or "").strip().split())
    if len(name) < 3:
        raise web.HTTPBadRequest(reason="Название клана слишком короткое")
    if len(name) > 28:
        raise web.HTTPBadRequest(reason="Название клана слишком длинное")
    return name


def generate_clan_code(connection: sqlite3.Connection) -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    while True:
        code = "HP-" + "".join(random.choice(alphabet) for _ in range(4))
        row = connection.execute("SELECT id FROM clans WHERE code = ?", (code,)).fetchone()
        if not row:
            return code


def clan_level_for_xp(total_xp: int) -> Dict[str, object]:
    current = CLAN_LEVELS[0]
    next_level: Optional[Dict[str, int]] = None
    for index, level in enumerate(CLAN_LEVELS):
        if total_xp >= int(level["xp"]):
            current = level
            next_level = CLAN_LEVELS[index + 1] if index + 1 < len(CLAN_LEVELS) else None

    next_xp = int(next_level["xp"]) if next_level else int(current["xp"])
    return {
        "level": int(current["level"]),
        "slots": int(current["slots"]),
        "xp": int(current["xp"]),
        "nextLevel": int(next_level["level"]) if next_level else 0,
        "nextXp": next_xp,
        "remaining": max(0, next_xp - total_xp) if next_level else 0,
        "isMax": next_level is None,
    }


def clan_xp_sum(connection: sqlite3.Connection, clan_id: int, period: str) -> int:
    if period == "weekly":
        condition = "week_start = ?"
        value = weekly_period_start()
    elif period == "monthly":
        condition = "month_key = ?"
        value = month_key()
    else:
        condition = "1 = ?"
        value = 1
    row = connection.execute(
        f"SELECT COALESCE(SUM(amount), 0) AS total FROM clan_xp_events WHERE clan_id = ? AND {condition}",
        (clan_id, value),
    ).fetchone()
    return int(row["total"] or 0)


def user_clan_xp_sum(connection: sqlite3.Connection, clan_id: int, user_id: int, period: str) -> int:
    if period == "weekly":
        condition = "week_start = ?"
        value = weekly_period_start()
    elif period == "monthly":
        condition = "month_key = ?"
        value = month_key()
    else:
        condition = "1 = ?"
        value = 1
    row = connection.execute(
        f"""
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM clan_xp_events
        WHERE clan_id = ? AND user_id = ? AND {condition}
        """,
        (clan_id, user_id, value),
    ).fetchone()
    return int(row["total"] or 0)


def clan_member_count(connection: sqlite3.Connection, clan_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM clan_members WHERE clan_id = ?",
        (clan_id,),
    ).fetchone()
    return int(row["total"] or 0)


def clan_today_checkins(connection: sqlite3.Connection, clan_id: int) -> int:
    row = connection.execute(
        """
        SELECT COUNT(DISTINCT user_id) AS total
        FROM clan_xp_events
        WHERE clan_id = ? AND day_key = ? AND kind = 'checkin'
        """,
        (clan_id, local_day_key()),
    ).fetchone()
    return int(row["total"] or 0)


def clan_user_checked_today(connection: sqlite3.Connection, clan_id: int, user_id: int) -> bool:
    row = connection.execute(
        """
        SELECT id FROM clan_xp_events
        WHERE clan_id = ? AND user_id = ? AND day_key = ? AND kind = 'checkin'
        LIMIT 1
        """,
        (clan_id, user_id, local_day_key()),
    ).fetchone()
    return row is not None


def clan_chest_state(weekly_xp: int, members_count: int) -> Dict[str, object]:
    reached: Optional[Dict[str, object]] = None
    for chest in CLAN_CHESTS:
        if weekly_xp >= int(chest["xp"]) and members_count >= int(chest["members"]):
            reached = chest

    next_chest = next((chest for chest in CLAN_CHESTS if reached is None or int(chest["xp"]) > int(reached["xp"])), None)
    if not next_chest and reached:
        next_chest = reached

    missing_xp = max(0, int(next_chest["xp"]) - weekly_xp) if next_chest else 0
    missing_members = max(0, int(next_chest["members"]) - members_count) if next_chest else 0
    return {
        "reached": reached,
        "next": next_chest,
        "missingXp": missing_xp,
        "missingMembers": missing_members,
        "activeXpRequired": CLAN_CHEST_ACTIVE_XP,
        "chests": CLAN_CHESTS,
    }


def clan_member_name(row: sqlite3.Row) -> str:
    if row["club_login"]:
        return str(row["club_login"])
    if row["username"]:
        return f"@{row['username']}"
    return str(row["full_name"] or row["user_id"])


def serialize_clan_member(connection: sqlite3.Connection, row: sqlite3.Row, clan_id: int) -> Dict[str, object]:
    weekly_xp = user_clan_xp_sum(connection, clan_id, int(row["user_id"]), "weekly")
    total_xp = user_clan_xp_sum(connection, clan_id, int(row["user_id"]), "total")
    checkins_row = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM clan_xp_events
        WHERE clan_id = ? AND user_id = ? AND week_start = ? AND kind = 'checkin'
        """,
        (clan_id, int(row["user_id"]), weekly_period_start()),
    ).fetchone()
    return {
        "userId": int(row["user_id"]),
        "name": clan_member_name(row),
        "role": str(row["role"]),
        "weeklyXp": weekly_xp,
        "totalXp": total_xp,
        "checkins": int(checkins_row["total"] or 0),
        "isChestActive": weekly_xp >= CLAN_CHEST_ACTIVE_XP,
        "needsForChest": max(0, CLAN_CHEST_ACTIVE_XP - weekly_xp),
    }


def serialize_clan(connection: sqlite3.Connection, clan: sqlite3.Row, user_id: Optional[int] = None) -> Dict[str, object]:
    clan_id = int(clan["id"])
    weekly_xp = clan_xp_sum(connection, clan_id, "weekly")
    monthly_xp = clan_xp_sum(connection, clan_id, "monthly")
    total_xp = clan_xp_sum(connection, clan_id, "total")
    members_count = clan_member_count(connection, clan_id)
    level = clan_level_for_xp(total_xp)
    members = connection.execute(
        """
        SELECT members.*, COALESCE(profiles.club_login, '') AS club_login
        FROM clan_members members
        LEFT JOIN user_profiles profiles ON profiles.user_id = members.user_id
        WHERE members.clan_id = ?
        ORDER BY members.role = 'leader' DESC, members.joined_at ASC
        """,
        (clan_id,),
    ).fetchall()
    serialized_members = [serialize_clan_member(connection, row, clan_id) for row in members]
    serialized_members.sort(key=lambda item: int(item["weeklyXp"]), reverse=True)
    my_member = next((item for item in serialized_members if user_id and int(item["userId"]) == user_id), None)
    return {
        "id": clan_id,
        "name": str(clan["name"]),
        "code": str(clan["code"]),
        "isPublic": bool(clan["is_public"]),
        "leaderId": int(clan["leader_id"]),
        "level": level,
        "membersCount": members_count,
        "weeklyXp": weekly_xp,
        "monthlyXp": monthly_xp,
        "totalXp": total_xp,
        "chest": clan_chest_state(weekly_xp, members_count),
        "dailyGoal": {
            "checked": clan_today_checkins(connection, clan_id),
            "target": CLAN_DAILY_GOAL_MEMBERS,
            "reward": CLAN_DAILY_GOAL_XP,
        },
        "checkedToday": clan_user_checked_today(connection, clan_id, user_id) if user_id else False,
        "members": serialized_members[:30],
        "me": my_member,
    }


def current_user_clan(connection: sqlite3.Connection, user_id: int) -> Optional[sqlite3.Row]:
    return connection.execute(
        """
        SELECT clans.*
        FROM clan_members members
        JOIN clans ON clans.id = members.clan_id
        WHERE members.user_id = ?
        """,
        (user_id,),
    ).fetchone()


def public_clans(connection: sqlite3.Connection, limit: int = 20) -> List[Dict[str, object]]:
    rows = connection.execute(
        """
        SELECT * FROM clans
        WHERE is_public = 1
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [serialize_clan(connection, row) for row in rows]


def clan_top(connection: sqlite3.Connection, period: str, limit: int = 10) -> List[Dict[str, object]]:
    if period == "monthly":
        condition = "events.month_key = ?"
        value = month_key()
    else:
        condition = "events.week_start = ?"
        value = weekly_period_start()
    rows = connection.execute(
        f"""
        SELECT clans.*, COALESCE(SUM(events.amount), 0) AS period_xp
        FROM clans
        LEFT JOIN clan_xp_events events ON events.clan_id = clans.id AND {condition}
        GROUP BY clans.id
        ORDER BY period_xp DESC, clans.created_at ASC
        LIMIT ?
        """,
        (value, limit),
    ).fetchall()
    result = []
    for index, row in enumerate(rows, start=1):
        item = serialize_clan(connection, row)
        item["place"] = index
        item["periodXp"] = int(row["period_xp"] or 0)
        result.append(item)
    return result


def add_clan_xp(connection: sqlite3.Connection, clan_id: int, user_id: int, amount: int, kind: str) -> None:
    connection.execute(
        """
        INSERT INTO clan_xp_events
            (clan_id, user_id, amount, kind, day_key, week_start, month_key, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (clan_id, user_id, amount, kind, local_day_key(), weekly_period_start(), month_key(), utc_now()),
    )


def normalize_league_game(value: object) -> str:
    game = str(value or "").strip().lower()
    if game not in LEAGUE_GAMES:
        raise web.HTTPBadRequest(reason="Выберите дисциплину CS2")
    return game


def normalize_league_format(value: object, game: str) -> Optional[str]:
    league_format = str(value or "").strip().lower().replace("×", "x")
    if not league_format:
        raise web.HTTPBadRequest(reason="Выберите формат CS2")
    if league_format not in LEAGUE_FORMATS:
        raise web.HTTPBadRequest(reason="Неверный формат CS2")
    return league_format


def league_format_title(value: Optional[str]) -> str:
    return LEAGUE_FORMATS.get(value, {}).get("title", value)


def league_team_limit(row: sqlite3.Row) -> int:
    return int(LEAGUE_FORMATS.get(str(row["format"] or "5x5"), LEAGUE_FORMATS["5x5"])["max"])


def normalize_league_name(value: object, label: str = "Название") -> str:
    name = " ".join(str(value or "").strip().split())
    if len(name) < 2:
        raise web.HTTPBadRequest(reason=f"{label} слишком короткое")
    if len(name) > 40:
        raise web.HTTPBadRequest(reason=f"{label} слишком длинное")
    return name


def normalize_league_invite_code(value: object) -> str:
    clean = re.sub(r"[^A-Z0-9]", "", str(value or "").upper())
    if clean.startswith("HL"):
        clean = clean[2:]
    if len(clean) != 6:
        raise ValueError("invalid_code")
    return f"HL-{clean}"


def league_error(error: str, message: str, status: int) -> web.Response:
    return web.json_response({"ok": False, "error": error, "message": message}, status=status)


def league_invite_token(connection: sqlite3.Connection) -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    for _ in range(30):
        token = "HL-" + "".join(random.choice(alphabet) for _ in range(6))
        row = connection.execute("SELECT id FROM league_teams WHERE invite_token = ?", (token,)).fetchone()
        if not row:
            return token
    raise web.HTTPInternalServerError(reason="Не удалось создать invite token")


def league_public_user(user: Dict[str, object]) -> Dict[str, str]:
    full_name = " ".join(filter(None, [user.get("first_name"), user.get("last_name")])) or str(user["id"])
    username = str(user.get("username") or "")
    return {"fullName": full_name, "username": username}


def is_league_admin(connection: sqlite3.Connection, tg_id: int) -> bool:
    if tg_id in LEAGUE_ADMIN_IDS:
        return True
    row = connection.execute("SELECT role FROM league_users WHERE tg_id = ?", (tg_id,)).fetchone()
    return bool(row and str(row["role"]) == "admin")


def ensure_league_user(connection: sqlite3.Connection, user: Dict[str, object]) -> sqlite3.Row:
    tg_id = int(user["id"])
    username = str(user.get("username") or "")
    existing = connection.execute("SELECT * FROM league_users WHERE tg_id = ?", (tg_id,)).fetchone()
    if existing:
        role = "admin" if tg_id in LEAGUE_ADMIN_IDS else str(existing["role"] or "player")
        connection.execute(
            "UPDATE league_users SET username = ?, role = ? WHERE tg_id = ?",
            (username, role, tg_id),
        )
    else:
        role = "admin" if tg_id in LEAGUE_ADMIN_IDS else "player"
        connection.execute(
            """
            INSERT INTO league_users (tg_id, username, role, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (tg_id, username, role, utc_now()),
        )
    return connection.execute("SELECT * FROM league_users WHERE tg_id = ?", (tg_id,)).fetchone()


def league_seasons(connection: sqlite3.Connection) -> List[sqlite3.Row]:
    ensure_default_league_seasons(connection)
    return connection.execute(
        "SELECT * FROM league_seasons WHERE game = 'cs2' ORDER BY status = 'active' DESC, status = 'registration' DESC, id DESC"
    ).fetchall()


def league_season_for_game(connection: sqlite3.Connection, game: str, league_format: Optional[str] = None) -> sqlite3.Row:
    ensure_default_league_seasons(connection)
    row = connection.execute(
        """
        SELECT * FROM league_seasons
        WHERE game = ?
          AND (format IS ? OR format = ?)
          AND status IN ('registration', 'active')
        ORDER BY status = 'active' DESC, id DESC
        LIMIT 1
        """,
        (game, league_format, league_format),
    ).fetchone()
    if not row:
        if game == "cs2" and league_format:
            raise web.HTTPBadRequest(reason=f"Сейчас регистрация на {league_format_title(league_format)} закрыта")
        raise web.HTTPBadRequest(reason="Для этой дисциплины нет активного сезона")
    return row


def league_user_team(connection: sqlite3.Connection, league_user_id: int, season_id: int) -> Optional[sqlite3.Row]:
    return connection.execute(
        """
        SELECT teams.*
        FROM league_team_members members
        JOIN league_teams teams ON teams.id = members.team_id
        WHERE members.user_id = ? AND teams.season_id = ?
        LIMIT 1
        """,
        (league_user_id, season_id),
    ).fetchone()


def serialize_league_team(connection: sqlite3.Connection, row: sqlite3.Row) -> Dict[str, object]:
    captain = connection.execute("SELECT * FROM league_users WHERE id = ?", (int(row["captain_id"]),)).fetchone()
    members = connection.execute(
        """
        SELECT users.*
        FROM league_team_members members
        JOIN league_users users ON users.id = members.user_id
        WHERE members.team_id = ?
        ORDER BY members.joined_at ASC
        """,
        (int(row["id"]),),
    ).fetchall()
    return {
        "id": int(row["id"]),
        "name": row["name"],
        "game": row["game"],
        "gameTitle": LEAGUE_GAMES.get(str(row["game"]), str(row["game"]).upper()),
        "format": row["format"],
        "formatTitle": league_format_title(row["format"]),
        "captainId": int(row["captain_id"]),
        "captainName": f"@{captain['username']}" if captain and captain["username"] else str(captain["tg_id"]) if captain else "",
        "seasonId": int(row["season_id"]),
        "status": row["status"],
        "inviteToken": row["invite_token"],
        "maxMembers": league_team_limit(row),
        "members": [
            {
                "id": int(member["id"]),
                "tgId": int(member["tg_id"]),
                "username": member["username"],
                "nick": member["game_nick_cs2"],
            }
            for member in members
        ],
    }


def league_team_rows(connection: sqlite3.Connection, season_id: Optional[int] = None) -> List[sqlite3.Row]:
    if season_id:
        return connection.execute(
            "SELECT * FROM league_teams WHERE season_id = ? AND game = 'cs2' ORDER BY status = 'pending' DESC, created_at DESC",
            (season_id,),
        ).fetchall()
    return connection.execute(
        "SELECT * FROM league_teams WHERE game = 'cs2' ORDER BY status = 'pending' DESC, created_at DESC"
    ).fetchall()


def league_standings(connection: sqlite3.Connection, season_id: int, league_user_id: Optional[int] = None) -> List[Dict[str, object]]:
    teams = connection.execute(
        "SELECT * FROM league_teams WHERE season_id = ? AND status = 'active' ORDER BY created_at ASC",
        (season_id,),
    ).fetchall()
    current_team = league_user_team(connection, league_user_id, season_id) if league_user_id else None
    current_team_id = int(current_team["id"]) if current_team else 0
    result = []
    for team in teams:
        team_id = int(team["id"])
        matches = connection.execute(
            """
            SELECT * FROM league_matches
            WHERE season_id = ? AND status = 'played' AND (team1_id = ? OR team2_id = ?)
            """,
            (season_id, team_id, team_id),
        ).fetchall()
        wins = 0
        losses = 0
        for match in matches:
            if int(match["winner_id"] or 0) == team_id:
                wins += 1
            else:
                losses += 1
        points = wins * 3
        result.append(
            {
                "teamId": team_id,
                "name": team["name"],
                "played": len(matches),
                "wins": wins,
                "losses": losses,
                "points": points,
                "trend": "new" if not matches else "0",
                "isCurrentUserTeam": team_id == current_team_id,
            }
        )
    result.sort(key=lambda item: (-int(item["points"]), -int(item["wins"]), str(item["name"])))
    for index, item in enumerate(result, start=1):
        item["place"] = index
    return result


def league_standing_tabs(connection: sqlite3.Connection, league_user_id: int) -> List[Dict[str, object]]:
    tabs = [
        ("cs2-5x5", "CS2 5×5", "cs2", "5x5"),
        ("cs2-2x2", "CS2 2×2", "cs2", "2x2"),
    ]
    result = []
    for key, title, game, league_format in tabs:
        season = connection.execute(
            """
            SELECT *
            FROM league_seasons
            WHERE game = ?
              AND (format IS ? OR format = ?)
              AND status IN ('registration', 'active', 'finished')
            ORDER BY status = 'active' DESC, status = 'registration' DESC, id DESC
            LIMIT 1
            """,
            (game, league_format, league_format),
        ).fetchone()
        if not season:
            result.append({"key": key, "title": title, "season": None, "standings": []})
            continue
        teams_registered = connection.execute(
            "SELECT COUNT(*) AS total FROM league_teams WHERE season_id = ? AND status = 'active'",
            (int(season["id"]),),
        ).fetchone()["total"]
        result.append(
            {
                "key": key,
                "title": title,
                "season": {
                    "id": int(season["id"]),
                    "game": season["game"],
                    "gameTitle": LEAGUE_GAMES.get(str(season["game"]), str(season["game"]).upper()),
                    "format": season["format"],
                    "formatTitle": league_format_title(season["format"]),
                    "name": season["name"],
                    "startDate": season["start_date"],
                    "endDate": season["end_date"],
                    "status": season["status"],
                    "teamsRegistered": int(teams_registered or 0),
                },
                "standings": league_standings(connection, int(season["id"]), league_user_id),
            }
        )
    return result


def serialize_league(connection: sqlite3.Connection, user: Dict[str, object]) -> Dict[str, object]:
    league_user = ensure_league_user(connection, user)
    tg_id = int(user["id"])
    seasons = league_seasons(connection)
    selected = seasons[0] if seasons else None
    my_teams = []
    for season in seasons:
        team = league_user_team(connection, int(league_user["id"]), int(season["id"]))
        if team:
            my_teams.append(serialize_league_team(connection, team))
    teams = [serialize_league_team(connection, row) for row in league_team_rows(connection)]
    pending = [team for team in teams if team["status"] == "pending"]
    standing_tabs = league_standing_tabs(connection, int(league_user["id"]))
    preferred_key = "cs2-5x5"
    if my_teams:
        first_team = my_teams[0]
        preferred_key = f"cs2-{first_team.get('format') or '5x5'}"
    return {
        "user": {
            "id": int(league_user["id"]),
            "tgId": int(league_user["tg_id"]),
            "username": league_user["username"],
            "role": "admin" if is_league_admin(connection, tg_id) else league_user["role"],
            "xp": int(league_user["xp"]),
            "gameNickCs2": league_user["game_nick_cs2"],
            "isAdmin": is_league_admin(connection, tg_id),
        },
        "seasons": [
            {
                "id": int(season["id"]),
                "game": season["game"],
                "gameTitle": LEAGUE_GAMES.get(str(season["game"]), str(season["game"]).upper()),
                "format": season["format"],
                "formatTitle": league_format_title(season["format"]),
                "name": season["name"],
                "startDate": season["start_date"],
                "endDate": season["end_date"],
                "status": season["status"],
            }
            for season in seasons
        ],
        "selectedSeasonId": int(selected["id"]) if selected else None,
        "myTeams": my_teams,
        "teams": teams,
        "pendingTeams": pending,
        "standings": league_standings(connection, int(selected["id"]), int(league_user["id"])) if selected else [],
        "standingTabs": standing_tabs,
        "defaultStandingTab": preferred_key,
        "games": [{"key": key, "title": title} for key, title in LEAGUE_GAMES.items()],
    }


def top_inviters(limit: int = 10) -> List[sqlite3.Row]:
    return top_inviters_since(None, limit)


def weekly_top_inviters(limit: int = 10) -> List[sqlite3.Row]:
    return top_inviters_since(weekly_period_start(), limit)


def top_inviters_since(period_start: Optional[str], limit: int = 10) -> List[sqlite3.Row]:
    join_filter = "AND m.joined_at >= ?" if period_start else ""
    params: List[object] = [period_start, limit] if period_start else [limit]
    with closing(db()) as connection:
        return connection.execute(
            f"""
            SELECT
                owners.owner_id,
                COALESCE(owners.owner_username, '') AS username,
                owners.owner_full_name,
                COALESCE(profiles.club_login, '') AS club_login,
                COALESCE(profiles.coins, 0) AS coins,
                COALESCE(profiles.visits, 0) AS visits,
                COUNT(DISTINCT m.chat_id || ':' || m.invited_user_id) AS total
            FROM (
                SELECT owner_id, owner_username, owner_full_name, MAX(created_at) AS created_at
                FROM invite_links
                GROUP BY owner_id
            ) owners
            LEFT JOIN invited_members m ON m.owner_id = owners.owner_id {join_filter}
            LEFT JOIN user_profiles profiles ON profiles.user_id = owners.owner_id
            GROUP BY owners.owner_id
            ORDER BY total DESC, owners.created_at ASC
            LIMIT ?
            """,
            params,
        ).fetchall()


def weekly_snapshot_files(limit: int = 12) -> List[sqlite3.Row]:
    with closing(db()) as connection:
        return connection.execute(
            """
            SELECT * FROM weekly_snapshots
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()


def prize_for_place(place: int) -> str:
    if 1 <= place <= len(DEFAULT_WEEKLY_PRIZES):
        return DEFAULT_WEEKLY_PRIZES[place - 1]
    return ""


def public_label(row: sqlite3.Row) -> str:
    return f"@{row['username']}" if row["username"] else str(row["owner_full_name"])


def award_label(row: sqlite3.Row) -> str:
    club_login = str(row["club_login"] or "").strip()
    if club_login:
        return f"{public_label(row)} ({club_login})"
    return public_label(row)


def serialize_top_rows(rows: List[sqlite3.Row]) -> List[Dict[str, object]]:
    return [
        {
            "place": index,
            "name": row["owner_full_name"],
            "username": row["username"],
            "clubLogin": row["club_login"],
            "total": row["total"],
            "rank": rank_for_score(int(row["total"])),
            "prize": prize_for_place(index),
        }
        for index, row in enumerate(rows, start=1)
    ]


def weekly_results_message(rows: List[sqlite3.Row]) -> str:
    if not rows:
        return (
            "Итоги недели HardPoint\n\n"
            "На этой неделе пока нет приглашений. Новая неделя уже началась."
        )

    lines = [
        "Итоги недели HardPoint",
        "",
        "Топ приглашений:",
    ]
    for index, row in enumerate(rows[:10], start=1):
        prize = prize_for_place(index)
        prize_text = f" - приз: {prize}" if prize else ""
        lines.append(f"{index}. {award_label(row)} - {row['total']}{prize_text}")

    lines.extend(
        [
            "",
            "Недельный рейтинг обнулён. Общий рейтинг за всё время сохраняется.",
            "Откройте мини-приложение, чтобы проверить новую неделю и общий топ.",
        ]
    )
    return "\n".join(lines)


def save_weekly_snapshot(period_end: Optional[datetime] = None) -> Dict[str, object]:
    end = period_end or datetime.now(timezone.utc)
    period_start = weekly_period_start()
    rows = top_inviters_since(period_start, limit=1000)
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    local_end = end.astimezone(SNAPSHOT_TZ)
    file_path = SNAPSHOT_DIR / f"weekly-rating-{local_end:%Y-%m-%d-%H%M}.csv"
    with file_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["period_start", period_start])
        writer.writerow(["period_end", utc_iso(end)])
        writer.writerow([])
        writer.writerow(["place", "user_id", "username", "name", "club_login", "invites"])
        for index, row in enumerate(rows, start=1):
            writer.writerow([
                index,
                row["owner_id"],
                row["username"],
                row["owner_full_name"],
                row["club_login"],
                row["total"],
            ])

    with closing(db()) as connection:
        connection.execute(
            """
            INSERT INTO weekly_snapshots (period_start, period_end, file_path, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (period_start, utc_iso(end), str(file_path), utc_now()),
        )
        connection.commit()

    set_state("weekly_period_start", utc_iso(end))
    logging.info("Weekly rating snapshot saved to %s", file_path)
    return {
        "file_path": file_path,
        "period_start": period_start,
        "period_end": utc_iso(end),
        "rows": rows,
    }


async def get_or_create_invite_link(
    bot: Bot,
    owner_id: int,
    username: Optional[str],
    full_name: str,
) -> str:
    existing = latest_invite_for_owner(owner_id)
    if existing:
        return str(existing["invite_link"])

    if not GROUP_ID:
        raise RuntimeError("GROUP_ID is not configured")

    invite_link = await bot.create_chat_invite_link(
        chat_id=GROUP_ID,
        name=f"invite:{owner_id}",
        creates_join_request=False,
    )
    save_invite_link(invite_link, owner_id, username, full_name)
    return invite_link.invite_link


async def ensure_invite_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return

    user = update.effective_user
    full_name = user.full_name or str(user.id)

    if not GROUP_ID:
        await update.message.reply_text(
            "Сначала укажите GROUP_ID в настройках бота. "
            "Добавьте меня в группу администратором и отправьте там /chatid."
        )
        return

    try:
        invite_link = await get_or_create_invite_link(
            bot=context.bot,
            owner_id=user.id,
            username=user.username,
            full_name=full_name,
        )
    except Forbidden:
        await update.message.reply_text(
            "Бот не может создать ссылку. Добавьте его администратором группы и дайте право приглашать пользователей."
        )
        return
    except BadRequest as error:
        await update.message.reply_text(f"Telegram не дал создать ссылку: {error.message}")
        return
    except TelegramError:
        logging.exception("Failed to create invite link")
        await update.message.reply_text("Не получилось создать ссылку. Проверьте токен, GROUP_ID и права бота.")
        return

    await update.message.reply_text(
        "Ваша персональная ссылка для приглашений:\n"
        f"{invite_link}\n\n"
        "Я буду считать людей, которые вступят именно по этой ссылке."
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return

    weekly_total = weekly_stats_for_owner(update.effective_user.id)
    total = stats_for_owner(update.effective_user.id)
    await update.message.reply_text(
        f"За эту неделю: {weekly_total}\n"
        f"За всё время: {total}"
    )


async def week(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    rows = weekly_top_inviters()
    if not rows:
        await update.message.reply_text("За эту неделю пока нет приглашений.")
        return

    lines = ["Топ этой недели:"]
    for index, row in enumerate(rows, start=1):
        prize = prize_for_place(index)
        prize_text = f" - приз: {prize}" if prize else ""
        lines.append(f"{index}. {award_label(row)}: {row['total']}{prize_text}")

    await update.message.reply_text("\n".join(lines))


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    rows = top_inviters()
    if not rows:
        await update.message.reply_text("Пока нет созданных ссылок.")
        return

    lines = ["Топ за всё время:"]
    for index, row in enumerate(rows, start=1):
        lines.append(f"{index}. {public_label(row)}: {row['total']}")

    await update.message.reply_text("\n".join(lines))


async def snapshots(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    rows = weekly_snapshot_files()
    if not rows:
        await update.message.reply_text("Снимков недельного рейтинга пока нет.")
        return

    lines = ["Последние снимки рейтинга:"]
    for row in rows:
        lines.append(f"{row['period_end']}: {row['file_path']}")

    await update.message.reply_text("\n".join(lines))


async def whats_new(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    await update.message.reply_text(
        "Что нового в HardPoint Invites:\n\n"
        "- Появился недельный рейтинг приглашений.\n"
        "- Общий рейтинг теперь хранится отдельно и не обнуляется.\n"
        "- Каждое воскресенье недельный рейтинг сохраняется, после этого неделя начинается заново.\n"
        "- В мини-приложении можно переключаться между вкладками «Неделя» и «За всё время».\n"
        "- Можно сохранить логин клуба, чтобы награды было проще начислять победителям.\n"
        "- Личная ссылка, счетчики и топ теперь собраны в одном удобном экране.\n\n"
        "Команды:\n"
        "/link - получить персональную ссылку\n"
        "/stats - мои счетчики\n"
        "/week - топ недели\n"
        "/top - топ за всё время\n"
        "/app - открыть мини-приложение"
    )


async def track_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_member = update.chat_member
    if not chat_member:
        return

    old_status = chat_member.old_chat_member.status
    new_status = chat_member.new_chat_member.status
    joined = old_status in {ChatMemberStatus.LEFT, ChatMemberStatus.BANNED} and new_status in {
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.RESTRICTED,
    }

    if not joined or not chat_member.invite_link:
        return

    invite_link = chat_member.invite_link.invite_link
    owner = find_link_owner(invite_link)
    if not owner:
        return

    invited_user = chat_member.new_chat_member.user
    if invited_user.id == owner["owner_id"]:
        return

    was_new = record_join(
        chat_id=chat_member.chat.id,
        invited_user_id=invited_user.id,
        invite_link=invite_link,
        owner_id=owner["owner_id"],
    )

    if was_new:
        logging.info(
            "User %s joined chat %s via invite owned by %s",
            invited_user.id,
            chat_member.chat.id,
            owner["owner_id"],
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    await update.message.reply_text(
        "/link - получить персональную ссылку\n"
        "/stats - мой счетчик за неделю и за всё время\n"
        "/week - топ этой недели\n"
        "/top - топ за всё время\n"
        "/snapshots - последние файлы недельных снимков\n"
        "/new - что нового в боте\n"
        "/chatid - показать ID текущего чата"
    )


async def chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.message:
        return

    await update.message.reply_text(f"ID этого чата: {update.effective_chat.id}")


async def app_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    if not WEBAPP_URL:
        await update.message.reply_text(
            "Мини-приложение уже собрано, но для Telegram нужна публичная HTTPS-ссылка. "
            "Укажите WEBAPP_URL в .env после публикации."
        )
        return

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Открыть приглашения HardPoint", web_app=WebAppInfo(WEBAPP_URL))]]
    )
    await update.message.reply_text("Откройте личный кабинет приглашений HardPoint.", reply_markup=keyboard)


def verify_init_data(init_data: str) -> Dict[str, str]:
    if not BOT_TOKEN:
        raise web.HTTPUnauthorized(reason="Bot token is not configured")

    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", "")
    if not received_hash:
        raise web.HTTPUnauthorized(reason="Telegram hash is missing")

    check_string = "\n".join(f"{key}={value}" for key, value in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise web.HTTPUnauthorized(reason="Telegram auth check failed")

    return parsed


def user_from_init_data(request: web.Request) -> Dict[str, object]:
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    parsed = verify_init_data(init_data)
    user_raw = parsed.get("user")
    if not user_raw:
        raise web.HTTPUnauthorized(reason="Telegram user is missing")

    return json.loads(user_raw)


async def api_me(request: web.Request) -> web.Response:
    user = user_from_init_data(request)
    application: Application = request.app["telegram_application"]
    username = user.get("username")
    full_name = " ".join(filter(None, [user.get("first_name"), user.get("last_name")])) or str(user["id"])

    try:
        invite_link = await get_or_create_invite_link(
            bot=application.bot,
            owner_id=int(user["id"]),
            username=str(username) if username else None,
            full_name=full_name,
        )
    except TelegramError as error:
        raise web.HTTPBadGateway(reason=f"Telegram error: {error}") from error

    progress = profile_progress_for_user(int(user["id"]))

    return web.json_response(
        {
            "user": {
                "id": user["id"],
                "name": full_name,
                "username": username,
                "clubLogin": club_login_for_user(int(user["id"])),
                "progress": progress,
                "rank": rank_for_score(progress["score"]),
            },
            "inviteLink": invite_link,
            "weeklyInvitedCount": weekly_stats_for_owner(int(user["id"])),
            "allTimeInvitedCount": stats_for_owner(int(user["id"])),
            "weeklyPeriodStart": weekly_period_start(),
            "missions": missions_for_user(int(user["id"])),
        }
    )


async def api_save_club_login(request: web.Request) -> web.Response:
    user = user_from_init_data(request)
    try:
        payload = await request.json()
    except json.JSONDecodeError as error:
        raise web.HTTPBadRequest(reason="Неверный формат данных") from error

    club_login = normalize_club_login(payload.get("clubLogin", ""))
    save_club_login(int(user["id"]), club_login)
    return web.json_response({"ok": True, "clubLogin": club_login})


async def api_missions(request: web.Request) -> web.Response:
    user = user_from_init_data(request)
    return web.json_response({"missions": missions_for_user(int(user["id"]))})


async def api_claim_mission(request: web.Request) -> web.Response:
    user = user_from_init_data(request)
    try:
        payload = await request.json()
    except json.JSONDecodeError as error:
        raise web.HTTPBadRequest(reason="Неверный формат данных") from error

    return web.json_response(claim_mission_reward(int(user["id"]), str(payload.get("mission", ""))))


def user_display(user: Dict[str, object]) -> Dict[str, str]:
    full_name = " ".join(filter(None, [user.get("first_name"), user.get("last_name")])) or str(user["id"])
    username = str(user.get("username") or "")
    return {"fullName": full_name, "username": username}


def clan_access_for_user(user_id: int) -> Dict[str, object]:
    progress = profile_progress_for_user(user_id)
    return {
        "canJoin": int(progress["score"]) >= 10,
        "canCreate": int(progress["score"]) >= 50,
        "invites": int(progress["score"]),
        "rank": rank_for_score(int(progress["score"])),
    }


async def api_clans(request: web.Request) -> web.Response:
    user = user_from_init_data(request)
    user_id = int(user["id"])
    access = clan_access_for_user(user_id)
    with closing(db()) as connection:
        clan = current_user_clan(connection, user_id)
        current = serialize_clan(connection, clan, user_id) if clan else None
        return web.json_response(
            {
                "access": access,
                "currentClan": current,
                "publicClans": public_clans(connection),
                "weeklyTop": clan_top(connection, "weekly"),
                "monthlyTop": clan_top(connection, "monthly"),
            }
        )


async def api_create_clan(request: web.Request) -> web.Response:
    user = user_from_init_data(request)
    user_id = int(user["id"])
    if not clan_access_for_user(user_id)["canCreate"]:
        raise web.HTTPForbidden(reason="Создание клана доступно с ранга Legend")

    try:
        payload = await request.json()
    except json.JSONDecodeError as error:
        raise web.HTTPBadRequest(reason="Неверный формат данных") from error

    name = normalize_clan_name(payload.get("name", ""))
    is_public = 1 if bool(payload.get("isPublic", True)) else 0
    display = user_display(user)
    with closing(db()) as connection:
        if current_user_clan(connection, user_id):
            raise web.HTTPBadRequest(reason="Вы уже состоите в клане")
        code = generate_clan_code(connection)
        try:
            cursor = connection.execute(
                """
                INSERT INTO clans (name, code, leader_id, is_public, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, code, user_id, is_public, utc_now()),
            )
        except sqlite3.IntegrityError as error:
            raise web.HTTPBadRequest(reason="Такое название клана уже занято") from error
        clan_id = int(cursor.lastrowid)
        connection.execute(
            """
            INSERT INTO clan_members (user_id, clan_id, role, username, full_name, joined_at)
            VALUES (?, ?, 'leader', ?, ?, ?)
            """,
            (user_id, clan_id, display["username"], display["fullName"], utc_now()),
        )
        connection.commit()
        clan = connection.execute("SELECT * FROM clans WHERE id = ?", (clan_id,)).fetchone()
        return web.json_response({"ok": True, "clans": serialize_clan(connection, clan, user_id)})


async def api_join_clan(request: web.Request) -> web.Response:
    user = user_from_init_data(request)
    user_id = int(user["id"])
    if not clan_access_for_user(user_id)["canJoin"]:
        raise web.HTTPForbidden(reason="Вступление в клан доступно с ранга Rookie")

    try:
        payload = await request.json()
    except json.JSONDecodeError as error:
        raise web.HTTPBadRequest(reason="Неверный формат данных") from error

    clan_id = payload.get("clanId")
    code = str(payload.get("code", "")).strip().upper()
    display = user_display(user)
    with closing(db()) as connection:
        if current_user_clan(connection, user_id):
            raise web.HTTPBadRequest(reason="Вы уже состоите в клане")
        if clan_id:
            clan = connection.execute("SELECT * FROM clans WHERE id = ?", (int(clan_id),)).fetchone()
        else:
            clan = connection.execute("SELECT * FROM clans WHERE code = ?", (code,)).fetchone()
        if not clan:
            raise web.HTTPBadRequest(reason="Клан не найден")

        serialized = serialize_clan(connection, clan)
        if int(serialized["membersCount"]) >= int(serialized["level"]["slots"]):
            raise web.HTTPBadRequest(reason="В клане нет свободных мест")

        connection.execute(
            """
            INSERT INTO clan_members (user_id, clan_id, role, username, full_name, joined_at)
            VALUES (?, ?, 'member', ?, ?, ?)
            """,
            (user_id, int(clan["id"]), display["username"], display["fullName"], utc_now()),
        )
        connection.commit()
        clan = connection.execute("SELECT * FROM clans WHERE id = ?", (int(clan["id"]),)).fetchone()
        return web.json_response({"ok": True, "clan": serialize_clan(connection, clan, user_id)})


async def api_clan_checkin(request: web.Request) -> web.Response:
    user = user_from_init_data(request)
    user_id = int(user["id"])
    with closing(db()) as connection:
        clan = current_user_clan(connection, user_id)
        if not clan:
            raise web.HTTPBadRequest(reason="Сначала вступите в клан")
        clan_id = int(clan["id"])
        if clan_user_checked_today(connection, clan_id, user_id):
            raise web.HTTPBadRequest(reason="Сегодня вы уже отметились за клан")

        add_clan_xp(connection, clan_id, user_id, CLAN_CHECKIN_XP, "checkin")
        checked = clan_today_checkins(connection, clan_id)
        goal_bonus = False
        if checked >= CLAN_DAILY_GOAL_MEMBERS:
            try:
                connection.execute(
                    "INSERT INTO clan_daily_goals (clan_id, day_key, created_at) VALUES (?, ?, ?)",
                    (clan_id, local_day_key(), utc_now()),
                )
                add_clan_xp(connection, clan_id, 0, CLAN_DAILY_GOAL_XP, "daily_goal")
                goal_bonus = True
            except sqlite3.IntegrityError:
                goal_bonus = False
        connection.commit()
        clan = connection.execute("SELECT * FROM clans WHERE id = ?", (clan_id,)).fetchone()
        message = f"Отметка принята: +{CLAN_CHECKIN_XP} Clan XP"
        if goal_bonus:
            message += f". Цель дня закрыта: +{CLAN_DAILY_GOAL_XP} XP клану"
        return web.json_response(
            {
                "ok": True,
                "message": message,
                "clan": serialize_clan(connection, clan, user_id),
            }
        )


async def api_league(request: web.Request) -> web.Response:
    user = user_from_init_data(request)
    with closing(db()) as connection:
        data = serialize_league(connection, user)
        connection.commit()
        return web.json_response(data)


async def api_league_active_seasons(request: web.Request) -> web.Response:
    user_from_init_data(request)
    with closing(db()) as connection:
        seasons = league_seasons(connection)
        payload = [
            {
                "id": int(season["id"]),
                "game": season["game"],
                "gameTitle": LEAGUE_GAMES.get(str(season["game"]), str(season["game"]).upper()),
                "format": season["format"],
                "formatTitle": league_format_title(season["format"]),
                "status": season["status"],
                "name": season["name"],
                "start_date": season["start_date"],
                "end_date": season["end_date"],
            }
            for season in seasons
            if season["status"] in {"registration", "active"} and season["game"] == "cs2"
        ]
        connection.commit()
        return web.json_response({"seasons": payload})


async def api_league_standings(request: web.Request) -> web.Response:
    user = user_from_init_data(request)
    game = normalize_league_game(request.match_info.get("game"))
    league_format = normalize_league_format(request.query.get("format"), game)
    with closing(db()) as connection:
        league_user = ensure_league_user(connection, user)
        try:
            season = league_season_for_game(connection, game, league_format)
        except web.HTTPBadRequest:
            return web.json_response({"season": None, "standings": []})
        teams_registered = connection.execute(
            "SELECT COUNT(*) AS total FROM league_teams WHERE season_id = ? AND status = 'active'",
            (int(season["id"]),),
        ).fetchone()["total"]
        payload = {
            "season": {
                "id": int(season["id"]),
                "game": season["game"],
                "status": season["status"],
                "name": season["name"],
                "format": season["format"],
                "formatTitle": league_format_title(season["format"]),
                "teamsRegistered": int(teams_registered or 0),
            },
            "standings": league_standings(connection, int(season["id"]), int(league_user["id"])),
        }
        connection.commit()
        return web.json_response(payload)


async def api_league_register(request: web.Request) -> web.Response:
    user = user_from_init_data(request)
    try:
        payload = await request.json()
    except json.JSONDecodeError as error:
        raise web.HTTPBadRequest(reason="Неверный формат данных") from error

    game = normalize_league_game(payload.get("game"))
    nick = normalize_league_name(payload.get("nick"), "Ник")
    with closing(db()) as connection:
        league_user = ensure_league_user(connection, user)
        connection.execute(
            "UPDATE league_users SET game_nick_cs2 = ? WHERE id = ?",
            (nick, int(league_user["id"])),
        )
        data = serialize_league(connection, user)
        connection.commit()
        return web.json_response({"ok": True, "league": data})


async def api_league_create_team(request: web.Request) -> web.Response:
    user = user_from_init_data(request)
    try:
        payload = await request.json()
    except json.JSONDecodeError as error:
        raise web.HTTPBadRequest(reason="Неверный формат данных") from error

    game = normalize_league_game(payload.get("game"))
    league_format = normalize_league_format(payload.get("format"), game)
    name = normalize_league_name(payload.get("name"), "Название команды")
    with closing(db()) as connection:
        league_user = ensure_league_user(connection, user)
        season = league_season_for_game(connection, game, league_format)
        if league_user_team(connection, int(league_user["id"]), int(season["id"])):
            raise web.HTTPBadRequest(reason="В этом сезоне у вас уже есть команда")
        if not str(league_user["game_nick_cs2"] or "").strip():
            raise web.HTTPBadRequest(reason="Сначала укажите игровой ник для этой дисциплины")
        token = league_invite_token(connection)
        cursor = connection.execute(
            """
            INSERT INTO league_teams (name, game, format, captain_id, season_id, status, invite_token, created_at)
            VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)
            """,
            (name, game, league_format, int(league_user["id"]), int(season["id"]), token, utc_now()),
        )
        team_id = int(cursor.lastrowid)
        connection.execute(
            "INSERT INTO league_team_members (team_id, user_id, season_id, joined_at) VALUES (?, ?, ?, ?)",
            (team_id, int(league_user["id"]), int(season["id"]), utc_now()),
        )
        if str(league_user["role"]) == "player":
            connection.execute("UPDATE league_users SET role = 'captain' WHERE id = ?", (int(league_user["id"]),))
        data = serialize_league(connection, user)
        connection.commit()
        return web.json_response({"ok": True, "league": data})


async def api_league_join_team(request: web.Request) -> web.Response:
    user = user_from_init_data(request)
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        return league_error("bad_request", "Неверный формат данных", 400)

    try:
        invite_code = normalize_league_invite_code(payload.get("invite_code") or payload.get("code"))
    except ValueError:
        return league_error("team_not_found", "Команда не найдена. Проверь код", 404)

    captain_tg_id = 0
    captain_message = ""
    with closing(db()) as connection:
        league_user = ensure_league_user(connection, user)
        has_cs2_nick = bool(str(league_user["game_nick_cs2"] or "").strip())
        if not has_cs2_nick:
            return league_error("no_nick", "Сначала укажи игровой ник", 400)

        team = connection.execute(
            "SELECT * FROM league_teams WHERE invite_token = ?",
            (invite_code,),
        ).fetchone()
        if not team:
            return league_error("team_not_found", "Команда не найдена. Проверь код", 404)
        if str(team["status"]) not in {"pending", "active"}:
            return league_error("team_rejected", "Эта команда не принята в лигу", 403)

        if str(team["game"]) != "cs2" or not str(league_user["game_nick_cs2"] or "").strip():
            return league_error("wrong_discipline", "Этот код для другой дисциплины", 409)

        existing_team = league_user_team(connection, int(league_user["id"]), int(team["season_id"]))
        if existing_team:
            return league_error("already_in_team", "Ты уже в команде этого сезона", 409)

        member_count_row = connection.execute(
            "SELECT COUNT(*) AS total FROM league_team_members WHERE team_id = ?",
            (int(team["id"]),),
        ).fetchone()
        member_count = int(member_count_row["total"] or 0)
        if member_count >= league_team_limit(team):
            return league_error("team_full", "Состав команды заполнен", 409)

        try:
            connection.execute(
                "INSERT INTO league_team_members (team_id, user_id, season_id, joined_at) VALUES (?, ?, ?, ?)",
                (int(team["id"]), int(league_user["id"]), int(team["season_id"]), utc_now()),
            )
        except sqlite3.IntegrityError:
            return league_error("already_in_team", "Ты уже в команде этого сезона", 409)

        captain = connection.execute(
            "SELECT * FROM league_users WHERE id = ?",
            (int(team["captain_id"]),),
        ).fetchone()
        member_count = connection.execute(
            "SELECT COUNT(*) AS total FROM league_team_members WHERE team_id = ?",
            (int(team["id"]),),
        ).fetchone()["total"]
        captain_tg_id = int(captain["tg_id"]) if captain else 0
        username = str(league_user["username"] or "").strip()
        player_name = f"@{username}" if username else f"id {league_user['tg_id']}"
        captain_message = (
            "🎮 Новый игрок в команде!\n"
            f"{player_name} вступил в твою команду «{team['name']}».\n"
            f"Текущий состав: {member_count} игроков."
        )
        data = serialize_league(connection, user)
        response_team = serialize_league_team(connection, team)
        connection.commit()

    if captain_tg_id and captain_tg_id != int(user["id"]):
        try:
            telegram_application = request.app.get("telegram_application")
            if telegram_application:
                await telegram_application.bot.send_message(chat_id=captain_tg_id, text=captain_message)
        except TelegramError:
            logging.info("Could not notify league captain %s", captain_tg_id)

    return web.json_response(
        {
            "ok": True,
            "team": {
                "id": response_team["id"],
                "name": response_team["name"],
                "game": response_team["game"],
                "members_count": len(response_team["members"]),
            },
            "league": data,
        }
    )


async def api_league_update_team(request: web.Request) -> web.Response:
    user = user_from_init_data(request)
    try:
        payload = await request.json()
    except json.JSONDecodeError as error:
        raise web.HTTPBadRequest(reason="Неверный формат данных") from error

    status = str(payload.get("status", "")).strip().lower()
    if status not in {"active", "rejected"}:
        raise web.HTTPBadRequest(reason="Неверный статус заявки")
    team_id = int(payload.get("teamId") or 0)
    with closing(db()) as connection:
        ensure_league_user(connection, user)
        if not is_league_admin(connection, int(user["id"])):
            raise web.HTTPForbidden(reason="Доступно только админу")
        row = connection.execute("SELECT id FROM league_teams WHERE id = ?", (team_id,)).fetchone()
        if not row:
            raise web.HTTPBadRequest(reason="Команда не найдена")
        connection.execute("UPDATE league_teams SET status = ? WHERE id = ?", (status, team_id))
        data = serialize_league(connection, user)
        connection.commit()
        return web.json_response({"ok": True, "league": data})


async def api_league_report_match(request: web.Request) -> web.Response:
    user = user_from_init_data(request)
    try:
        payload = await request.json()
    except json.JSONDecodeError as error:
        raise web.HTTPBadRequest(reason="Неверный формат данных") from error

    match_id = int(payload.get("matchId") or 0)
    score_own = int(payload.get("scoreOwn") or 0)
    score_opponent = int(payload.get("scoreOpponent") or 0)
    with closing(db()) as connection:
        league_user = ensure_league_user(connection, user)
        match = connection.execute("SELECT * FROM league_matches WHERE id = ?", (match_id,)).fetchone()
        if not match:
            raise web.HTTPBadRequest(reason="Матч не найден")
        captain_team = connection.execute(
            """
            SELECT * FROM league_teams
            WHERE captain_id = ? AND id IN (?, ?)
            """,
            (int(league_user["id"]), int(match["team1_id"]), int(match["team2_id"])),
        ).fetchone()
        if not captain_team:
            raise web.HTTPForbidden(reason="Результат может внести только капитан команды")
        connection.execute(
            """
            INSERT INTO league_match_reports (match_id, reported_by, score_own, score_opponent, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(match_id, reported_by) DO UPDATE SET
                score_own = excluded.score_own,
                score_opponent = excluded.score_opponent,
                created_at = excluded.created_at
            """,
            (match_id, int(league_user["id"]), score_own, score_opponent, utc_now()),
        )
        reports = connection.execute(
            "SELECT * FROM league_match_reports WHERE match_id = ? ORDER BY created_at ASC",
            (match_id,),
        ).fetchall()
        if len(reports) >= 2:
            first, second = reports[0], reports[1]
            if int(first["score_own"]) == int(second["score_opponent"]) and int(first["score_opponent"]) == int(second["score_own"]):
                team1_score = score_own if int(captain_team["id"]) == int(match["team1_id"]) else score_opponent
                team2_score = score_opponent if int(captain_team["id"]) == int(match["team1_id"]) else score_own
                winner_id = int(match["team1_id"]) if team1_score > team2_score else int(match["team2_id"])
                connection.execute(
                    "UPDATE league_matches SET score1 = ?, score2 = ?, winner_id = ?, status = 'played' WHERE id = ?",
                    (team1_score, team2_score, winner_id, match_id),
                )
            else:
                connection.execute("UPDATE league_matches SET status = 'disputed' WHERE id = ?", (match_id,))
        data = serialize_league(connection, user)
        connection.commit()
        return web.json_response({"ok": True, "league": data})


async def api_weekly_top(request: web.Request) -> web.Response:
    user_from_init_data(request)
    rows = weekly_top_inviters()
    return web.json_response(
        {
            "periodStart": weekly_period_start(),
            "top": serialize_top_rows(rows),
        }
    )


async def api_all_time_top(request: web.Request) -> web.Response:
    user_from_init_data(request)
    rows = top_inviters()
    return web.json_response(
        {
            "top": serialize_top_rows(rows),
        }
    )


async def web_index(request: web.Request) -> web.FileResponse:
    return web.FileResponse(WEB_DIR / "index.html")


async def start_web_server(application: Application) -> web.AppRunner:
    web_app = web.Application()
    web_app["telegram_application"] = application
    web_app.router.add_get("/", web_index)
    web_app.router.add_get("/api/me", api_me)
    web_app.router.add_post("/api/club-login", api_save_club_login)
    web_app.router.add_get("/api/missions", api_missions)
    web_app.router.add_post("/api/missions/claim", api_claim_mission)
    web_app.router.add_get("/api/clans", api_clans)
    web_app.router.add_post("/api/clans/create", api_create_clan)
    web_app.router.add_post("/api/clans/join", api_join_clan)
    web_app.router.add_post("/api/clans/check-in", api_clan_checkin)
    web_app.router.add_get("/api/league", api_league)
    web_app.router.add_get("/api/league/seasons/active", api_league_active_seasons)
    web_app.router.add_get("/league/seasons/active", api_league_active_seasons)
    web_app.router.add_get("/api/league/standings/{game}", api_league_standings)
    web_app.router.add_get("/league/standings/{game}", api_league_standings)
    web_app.router.add_post("/api/league/register", api_league_register)
    web_app.router.add_post("/api/league/team", api_league_create_team)
    web_app.router.add_post("/api/league/team/join", api_league_join_team)
    web_app.router.add_post("/league/teams/join", api_league_join_team)
    web_app.router.add_post("/api/league/team/status", api_league_update_team)
    web_app.router.add_post("/api/league/match/report", api_league_report_match)
    web_app.router.add_get("/api/top", api_weekly_top)
    web_app.router.add_get("/api/weekly-top", api_weekly_top)
    web_app.router.add_get("/api/all-time-top", api_all_time_top)
    web_app.router.add_static("/assets", WEB_DIR / "assets")
    web_app.router.add_static("/", WEB_DIR)

    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
    await site.start()
    logging.info("Web server is running on http://%s:%s", WEBAPP_HOST, WEBAPP_PORT)
    return runner


async def announce_weekly_results(bot: Bot, rows: List[sqlite3.Row]) -> None:
    if not GROUP_ID:
        logging.warning("GROUP_ID is not configured; weekly results were not announced")
        return

    try:
        await bot.send_message(chat_id=GROUP_ID, text=weekly_results_message(rows))
        logging.info("Weekly results were announced in chat %s", GROUP_ID)
    except TelegramError:
        logging.exception("Failed to announce weekly results")


async def weekly_snapshot_scheduler(bot: Bot) -> None:
    while True:
        reset_at = next_weekly_reset()
        delay = max(1, (reset_at - datetime.now(timezone.utc)).total_seconds())
        logging.info("Next weekly rating snapshot is scheduled for %s", utc_iso(reset_at))
        await asyncio.sleep(delay)
        try:
            snapshot = save_weekly_snapshot(reset_at)
            await announce_weekly_results(bot, snapshot["rows"])  # type: ignore[arg-type]
        except Exception:
            logging.exception("Failed to save weekly rating snapshot")


def build_application() -> Application:
    if not BOT_TOKEN:
        raise RuntimeError("Set BOT_TOKEN in environment or .env file")

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler(["start", "link"], ensure_invite_link))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("week", week))
    application.add_handler(CommandHandler("top", top))
    application.add_handler(CommandHandler("snapshots", snapshots))
    application.add_handler(CommandHandler(["new", "changes"], whats_new))
    application.add_handler(CommandHandler("chatid", chat_id))
    application.add_handler(CommandHandler("app", app_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(ChatMemberHandler(track_join, ChatMemberHandler.CHAT_MEMBER))
    return application


async def main() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    init_db()
    application = build_application()
    web_runner: Optional[web.AppRunner] = None
    snapshot_task: Optional[asyncio.Task[None]] = None
    await application.initialize()
    await application.start()
    snapshot_task = asyncio.create_task(weekly_snapshot_scheduler(application.bot))
    web_runner = await start_web_server(application)
    await application.updater.start_polling(allowed_updates=["message", "channel_post", "chat_member"])
    logging.info("Invite counter bot is running")

    try:
        await asyncio.Event().wait()
    finally:
        await application.updater.stop()
        if snapshot_task:
            snapshot_task.cancel()
        if web_runner:
            await web_runner.cleanup()
        await application.stop()
        await application.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
