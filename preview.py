from pathlib import Path
from datetime import datetime, timedelta, timezone
import random

from aiohttp import web


WEB_DIR = Path(__file__).parent / "web"
preview_profile = {
    "clubLogin": "hardpoint_player",
    "bonusCoins": 0,
    "visits": 0,
    "dailyClaimed": False,
    "visitClaimed": False,
    "instagramClaimed": False,
    "discordClaimed": False,
    "instagramRequestedAt": "",
    "discordRequestedAt": "",
    "visitStreak": 6,
    "clanJoined": False,
    "clanCheckedToday": False,
}

preview_clan = {
    "id": 1,
    "name": "HardPoint Alpha",
    "code": "HP-A7K2",
    "isPublic": True,
    "leaderId": 99,
    "weeklyXp": 840,
    "monthlyXp": 1880,
    "totalXp": 2600,
    "membersCount": 8,
}

preview_league = {
    "cs2Nick": "HP_Player",
    "teamCreated": False,
    "teamStatus": "pending",
    "joinedTeam": False,
    "teamFormat": "5x5",
}


def preview_progress() -> dict:
    invites = 28
    return {
        "invites": invites,
        "coins": invites * 20 + preview_profile["bonusCoins"],
        "visits": preview_profile["visits"],
        "score": invites,
        "inviteCoinReward": 20,
    }


def preview_clan_payload(current: bool = False) -> dict:
    clan = {
        **preview_clan,
        "level": {
            "level": 3,
            "slots": 10,
            "xp": 1500,
            "nextLevel": 4,
            "nextXp": 4000,
            "remaining": 1400,
            "isMax": False,
        },
        "chest": {
            "reached": {"key": "common", "title": "Common Chest", "xp": 500, "members": 5, "hours": 1},
            "next": {"key": "rare", "title": "Rare Chest", "xp": 1500, "members": 20, "hours": 2},
            "missingXp": 660,
            "missingMembers": 12,
            "activeXpRequired": 50,
            "chests": [
                {"key": "common", "title": "Common Chest", "xp": 500, "members": 5, "hours": 1},
                {"key": "rare", "title": "Rare Chest", "xp": 1500, "members": 20, "hours": 2},
                {"key": "epic", "title": "Epic Chest", "xp": 3500, "members": 40, "hours": 3},
            ],
        },
        "dailyGoal": {"checked": 2 if not preview_profile["clanCheckedToday"] else 3, "target": 3, "reward": 50},
        "checkedToday": preview_profile["clanCheckedToday"],
        "me": {
            "userId": 1,
            "name": preview_profile["clubLogin"],
            "role": "member",
            "weeklyXp": 40 if not preview_profile["clanCheckedToday"] else 50,
            "totalXp": 120,
            "checkins": 4,
            "isChestActive": preview_profile["clanCheckedToday"],
            "needsForChest": 10 if not preview_profile["clanCheckedToday"] else 0,
        },
        "members": [
            {"userId": 2, "name": "Nama", "role": "leader", "weeklyXp": 320, "totalXp": 800, "checkins": 6, "isChestActive": True, "needsForChest": 0},
            {"userId": 3, "name": "Alex", "role": "member", "weeklyXp": 140, "totalXp": 400, "checkins": 5, "isChestActive": True, "needsForChest": 0},
            {"userId": 1, "name": preview_profile["clubLogin"], "role": "member", "weeklyXp": 40 if not preview_profile["clanCheckedToday"] else 50, "totalXp": 120, "checkins": 4, "isChestActive": preview_profile["clanCheckedToday"], "needsForChest": 10 if not preview_profile["clanCheckedToday"] else 0},
        ],
    }
    return clan


def preview_clans_response() -> dict:
    clan = preview_clan_payload()
    return {
        "access": {
            "canJoin": True,
            "canCreate": False,
            "invites": 28,
            "rank": {"title": "Grinder", "icon": "🥇"},
        },
        "currentClan": preview_clan_payload(True) if preview_profile["clanJoined"] else None,
        "publicClans": [clan],
        "weeklyTop": [{**clan, "place": 1, "periodXp": clan["weeklyXp"]}],
        "monthlyTop": [{**clan, "place": 1, "periodXp": clan["monthlyXp"]}],
    }


def preview_league_team() -> dict:
    return {
        "id": 1,
        "name": "HardPoint Red" if not preview_league["teamCreated"] else "Preview Team",
        "game": "cs2",
        "gameTitle": "CS2",
        "format": preview_league["teamFormat"],
        "formatTitle": "5×5" if preview_league["teamFormat"] == "5x5" else "2×2",
        "captainId": 1,
        "captainName": "@hardpoint_player",
        "seasonId": 1,
        "status": preview_league["teamStatus"],
        "inviteToken": "HL-PREVIEW",
        "maxMembers": 6 if preview_league["teamFormat"] == "5x5" else 2,
        "members": [
            {"id": 1, "tgId": 1, "username": "hardpoint_player", "nick": preview_league["cs2Nick"]},
        ],
    }


def preview_league_response() -> dict:
    team = preview_league_team()
    my_teams = [team] if preview_league["teamCreated"] or preview_league["joinedTeam"] else []
    teams = [
        team,
        {
            "id": 2,
            "name": "Noname",
            "game": "cs2",
            "gameTitle": "CS2",
            "format": "5x5",
            "formatTitle": "5×5",
            "captainId": 2,
            "captainName": "@noname",
            "seasonId": 1,
            "status": "active",
            "inviteToken": "HL-NONAME",
            "maxMembers": 6,
            "members": [{"id": 2, "tgId": 2, "username": "noname", "nick": "Noname"}],
        },
    ]
    standing_tabs = [
        {
            "key": "cs2-5x5",
            "title": "CS2 5×5",
            "season": {"id": 1, "game": "cs2", "gameTitle": "CS2", "format": "5x5", "formatTitle": "5×5", "name": "CS2 · 5×5 · Регистрация", "startDate": "2026-06-10", "endDate": "", "status": "registration", "teamsRegistered": 1},
            "standings": [
                {"place": 1, "teamId": 2, "name": "Noname", "played": 2, "wins": 2, "losses": 0, "points": 6, "trend": "0", "isCurrentUserTeam": False},
                {"place": 2, "teamId": 1, "name": team["name"], "played": 0, "wins": 0, "losses": 0, "points": 0, "trend": "new", "isCurrentUserTeam": bool(my_teams)},
            ],
        },
        {
            "key": "cs2-2x2",
            "title": "CS2 2×2",
            "season": {"id": 2, "game": "cs2", "gameTitle": "CS2", "format": "2x2", "formatTitle": "2×2", "name": "CS2 · 2×2 · Регистрация", "startDate": "2026-06-17", "endDate": "", "status": "registration", "teamsRegistered": 0},
            "standings": [],
        },
    ]
    return {
        "user": {
            "id": 1,
            "tgId": 1,
            "username": "hardpoint_player",
            "role": "admin" if preview_league["teamCreated"] else "player",
            "xp": 120,
            "gameNickCs2": preview_league["cs2Nick"],
            "isAdmin": True,
        },
        "seasons": [
            {"id": 1, "game": "cs2", "gameTitle": "CS2", "format": "5x5", "formatTitle": "5×5", "name": "CS2 · 5×5 · Регистрация", "startDate": "2026-06-10", "endDate": "", "status": "registration"},
            {"id": 2, "game": "cs2", "gameTitle": "CS2", "format": "2x2", "formatTitle": "2×2", "name": "CS2 · 2×2 · Регистрация", "startDate": "2026-06-17", "endDate": "", "status": "registration"},
        ],
        "selectedSeasonId": 1,
        "myTeams": my_teams,
        "teams": teams,
        "pendingTeams": [team] if team["status"] == "pending" else [],
        "standings": standing_tabs[0]["standings"],
        "standingTabs": standing_tabs,
        "defaultStandingTab": "cs2-5x5",
        "games": [{"key": "cs2", "title": "CS2"}],
    }


def preview_missions() -> dict:
    def social_state(claimed: bool, requested_at: str, url: str) -> dict:
        if claimed:
            status = "claimed"
        elif requested_at:
            status = "pending"
        else:
            status = "new"
        return {
            "reward": 500,
            "status": status,
            "canClaim": status == "new",
            "canReceive": status == "ready",
            "requestedAt": requested_at,
            "hoursLeft": 24 if status == "pending" else 0,
            "url": url,
        }

    return {
        "dailyReward": {
            "rewardMin": 10,
            "rewardMax": 50,
            "canClaim": not preview_profile["dailyClaimed"],
            "lastClaimDate": "preview" if preview_profile["dailyClaimed"] else "",
        },
        "visitReward": {
            "reward": 5,
            "canClaim": not preview_profile["visitClaimed"],
            "lastClaimDate": "preview" if preview_profile["visitClaimed"] else "",
        },
        "streak": {
            "days": preview_profile["visitStreak"],
            "milestones": [
                {"days": 3, "reward": 50},
                {"days": 7, "reward": 150},
                {"days": 14, "reward": 300},
                {"days": 30, "reward": 500},
            ],
        },
        "social": {
            "instagram": {
                **social_state(
                    preview_profile["instagramClaimed"],
                    preview_profile["instagramRequestedAt"],
                    "https://www.instagram.com/hardpoint_szczecin",
                ),
            },
            "discord": {
                **social_state(
                    preview_profile["discordClaimed"],
                    preview_profile["discordRequestedAt"],
                    "https://discord.gg/8zJUFdjA",
                ),
            },
        },
    }


async def index(request: web.Request) -> web.FileResponse:
    return web.FileResponse(WEB_DIR / "index.html")


async def api_me(request: web.Request) -> web.Response:
    return web.json_response(
        {
            "user": {
                "id": 1,
                "name": "Игрок HardPoint",
                "username": "hardpoint_player",
                "clubLogin": preview_profile["clubLogin"],
                "progress": preview_progress(),
                "rank": {
                    "title": "Grinder",
                    "icon": "🥇",
                    "score": 28,
                    "nextTitle": "Veteran",
                    "nextIcon": "💠",
                    "nextScore": 30,
                    "remaining": 2,
                    "isMax": False,
                },
            },
            "inviteLink": "https://t.me/+hardpoint-preview",
            "weeklyInvitedCount": 3,
            "allTimeInvitedCount": 28,
            "weeklyPeriodStart": "preview",
            "missions": preview_missions(),
        }
    )


async def api_weekly_top(request: web.Request) -> web.Response:
    return web.json_response(
        {
            "periodStart": "preview",
            "top": [
                {
                    "place": 1,
                    "name": "Игрок HardPoint",
                    "username": "hardpoint_player",
                    "clubLogin": preview_profile["clubLogin"],
                    "total": 28,
                    "rank": {"title": "Grinder", "icon": "🥇"},
                    "prize": "8 часов игры",
                },
                {
                    "place": 2,
                    "name": "Cyber Friend",
                    "username": "cyber_friend",
                    "clubLogin": "cf_21",
                    "total": 18,
                    "rank": {"title": "Rookie", "icon": "🥈"},
                    "prize": "5 часов игры",
                },
                {
                    "place": 3,
                    "name": "Новый игрок",
                    "username": "",
                    "clubLogin": "rookie77",
                    "total": 6,
                    "rank": {"title": "Recruit", "icon": "🥉"},
                    "prize": "3 часа игры",
                },
            ],
        }
    )


async def api_all_time_top(request: web.Request) -> web.Response:
    return web.json_response(
        {
            "top": [
                {
                    "place": 1,
                    "name": "Игрок HardPoint",
                    "username": "hardpoint_player",
                    "clubLogin": preview_profile["clubLogin"],
                    "total": 28,
                    "rank": {"title": "Grinder", "icon": "🥇"},
                    "prize": "8 часов игры",
                },
                {
                    "place": 2,
                    "name": "Veteran Player",
                    "username": "veteran_player",
                    "clubLogin": "veteran",
                    "total": 11,
                    "rank": {"title": "Rookie", "icon": "🥈"},
                    "prize": "5 часов игры",
                },
            ],
        }
    )


async def api_club_login(request: web.Request) -> web.Response:
    payload = await request.json()
    preview_profile["clubLogin"] = str(payload.get("clubLogin", "")).strip()[:40]
    return web.json_response({"ok": True, "clubLogin": preview_profile["clubLogin"]})


async def api_clans(request: web.Request) -> web.Response:
    return web.json_response(preview_clans_response())


async def api_create_clan(request: web.Request) -> web.Response:
    payload = await request.json()
    preview_clan["name"] = str(payload.get("name") or "New Clan").strip()[:28]
    preview_profile["clanJoined"] = True
    return web.json_response({"ok": True, "clan": preview_clan_payload(True)})


async def api_join_clan(request: web.Request) -> web.Response:
    await request.json()
    preview_profile["clanJoined"] = True
    return web.json_response({"ok": True, "clan": preview_clan_payload(True)})


async def api_clan_checkin(request: web.Request) -> web.Response:
    preview_profile["clanCheckedToday"] = True
    preview_clan["weeklyXp"] += 60
    preview_clan["monthlyXp"] += 60
    preview_clan["totalXp"] += 60
    return web.json_response({"ok": True, "message": "Отметка принята. Цель дня закрыта: +50 XP клану", "clan": preview_clan_payload(True)})


async def api_league(request: web.Request) -> web.Response:
    return web.json_response(preview_league_response())


async def api_league_active_seasons(request: web.Request) -> web.Response:
    return web.json_response({"seasons": preview_league_response()["seasons"]})


async def api_league_standings(request: web.Request) -> web.Response:
    game = request.match_info.get("game", "cs2")
    fmt = request.query.get("format")
    key = f"cs2-{fmt or '5x5'}"
    tab = next((item for item in preview_league_response()["standingTabs"] if item["key"] == key), None)
    return web.json_response(tab or {"season": None, "standings": []})


async def api_league_register(request: web.Request) -> web.Response:
    payload = await request.json()
    game = str(payload.get("game", "cs2")).lower()
    nick = str(payload.get("nick", "")).strip()[:40]
    preview_league["cs2Nick"] = nick
    return web.json_response({"ok": True, "league": preview_league_response()})


async def api_league_create_team(request: web.Request) -> web.Response:
    payload = await request.json()
    preview_league["teamCreated"] = True
    preview_league["teamStatus"] = "pending"
    preview_league["teamFormat"] = str(payload.get("format") or "5x5")
    return web.json_response({"ok": True, "league": preview_league_response()})


async def api_league_join_team(request: web.Request) -> web.Response:
    payload = await request.json()
    code = str(payload.get("invite_code") or payload.get("code") or "").upper().replace("-", "").strip()
    if not preview_league["cs2Nick"]:
        return web.json_response({"ok": False, "error": "no_nick", "message": "Сначала укажи игровой ник"}, status=400)
    if not code.startswith("HL"):
        return web.json_response({"ok": False, "error": "team_not_found", "message": "Команда не найдена. Проверь код"}, status=404)
    preview_league["joinedTeam"] = True
    return web.json_response({
        "ok": True,
        "team": {"id": 1, "name": "HardPoint Red", "game": "cs2", "members_count": 2},
        "league": preview_league_response(),
    })


async def api_league_update_team(request: web.Request) -> web.Response:
    payload = await request.json()
    preview_league["teamStatus"] = str(payload.get("status", "active"))
    return web.json_response({"ok": True, "league": preview_league_response()})


async def api_league_report_match(request: web.Request) -> web.Response:
    await request.json()
    return web.json_response({"ok": True, "league": preview_league_response()})


async def api_missions(request: web.Request) -> web.Response:
    return web.json_response({"missions": preview_missions()})


async def api_claim_mission(request: web.Request) -> web.Response:
    payload = await request.json()
    mission = str(payload.get("mission", ""))
    awarded = 0
    bonus = 0

    if mission == "daily":
        if preview_profile["dailyClaimed"]:
            raise web.HTTPBadRequest(reason="Daily Reward уже получен сегодня")
        awarded = random.randint(10, 50)
        preview_profile["dailyClaimed"] = True
    elif mission == "visit":
        if preview_profile["visitClaimed"]:
            raise web.HTTPBadRequest(reason="Награда за вход уже получена сегодня")
        awarded = 5
        preview_profile["visitClaimed"] = True
        preview_profile["visitStreak"] += 1
        preview_profile["visits"] += 1
        bonus = {
            3: 50,
            7: 150,
            14: 300,
            30: 500,
        }.get(preview_profile["visitStreak"], 0)
    elif mission == "instagram":
        if preview_profile["instagramClaimed"]:
            raise web.HTTPBadRequest(reason="Награда за Instagram уже получена")
        if not preview_profile["instagramRequestedAt"]:
            preview_profile["instagramRequestedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        else:
            requested_at = datetime.fromisoformat(preview_profile["instagramRequestedAt"])
            if datetime.now(timezone.utc) - requested_at < timedelta(hours=24):
                raise web.HTTPBadRequest(reason="Instagram ещё на проверке")
            awarded = 500
            preview_profile["instagramClaimed"] = True
    elif mission == "discord":
        if preview_profile["discordClaimed"]:
            raise web.HTTPBadRequest(reason="Награда за Discord уже получена")
        if not preview_profile["discordRequestedAt"]:
            preview_profile["discordRequestedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        else:
            requested_at = datetime.fromisoformat(preview_profile["discordRequestedAt"])
            if datetime.now(timezone.utc) - requested_at < timedelta(hours=24):
                raise web.HTTPBadRequest(reason="Discord ещё на проверке")
            awarded = 500
            preview_profile["discordClaimed"] = True
    else:
        raise web.HTTPBadRequest(reason="Неизвестная миссия")

    preview_profile["bonusCoins"] += awarded + bonus
    return web.json_response(
        {
            "ok": True,
            "message": f"Начислено: +{awarded + bonus} HP Coins",
            "awardedCoins": awarded,
            "bonusCoins": bonus,
            "totalAwardedCoins": awarded + bonus,
            "missions": preview_missions(),
            "user": {
                "progress": preview_progress(),
                "rank": {
                    "title": "Grinder",
                    "icon": "🥇",
                    "score": 28,
                    "nextTitle": "Veteran",
                    "nextIcon": "💠",
                    "nextScore": 30,
                    "remaining": 2,
                    "isMax": False,
                },
            },
        }
    )


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/api/me", api_me)
    app.router.add_get("/api/top", api_weekly_top)
    app.router.add_get("/api/weekly-top", api_weekly_top)
    app.router.add_get("/api/all-time-top", api_all_time_top)
    app.router.add_post("/api/club-login", api_club_login)
    app.router.add_get("/api/clans", api_clans)
    app.router.add_post("/api/clans/create", api_create_clan)
    app.router.add_post("/api/clans/join", api_join_clan)
    app.router.add_post("/api/clans/check-in", api_clan_checkin)
    app.router.add_get("/api/league", api_league)
    app.router.add_get("/api/league/seasons/active", api_league_active_seasons)
    app.router.add_get("/league/seasons/active", api_league_active_seasons)
    app.router.add_get("/api/league/standings/{game}", api_league_standings)
    app.router.add_get("/league/standings/{game}", api_league_standings)
    app.router.add_post("/api/league/register", api_league_register)
    app.router.add_post("/api/league/team", api_league_create_team)
    app.router.add_post("/api/league/team/join", api_league_join_team)
    app.router.add_post("/league/teams/join", api_league_join_team)
    app.router.add_post("/api/league/team/status", api_league_update_team)
    app.router.add_post("/api/league/match/report", api_league_report_match)
    app.router.add_get("/api/missions", api_missions)
    app.router.add_post("/api/missions/claim", api_claim_mission)
    app.router.add_static("/assets", WEB_DIR / "assets")
    app.router.add_static("/", WEB_DIR)
    return app


if __name__ == "__main__":
    web.run_app(create_app(), host="127.0.0.1", port=5173)
