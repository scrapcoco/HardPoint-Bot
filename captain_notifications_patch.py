#!/usr/bin/env python3
"""Patch bot.py — captain group notifications when team is accepted."""

with open('/home/ubuntu/hardpoint-bot/bot.py', 'r') as f:
    content = f.read()

changes = []

# 1. Add faceit_match_id columns to tournament_bracket_matches
old_schema = '''                thread_id INTEGER,
                scheduled_at TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY (tournament_id) REFERENCES tournaments(id)'''

new_schema = '''                thread_id INTEGER,
                scheduled_at TEXT NOT NULL DEFAULT '',
                faceit_match_id TEXT NOT NULL DEFAULT '',
                faceit_match_url TEXT NOT NULL DEFAULT '',
                faceit_match_status TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY (tournament_id) REFERENCES tournaments(id)'''

if 'faceit_match_id TEXT NOT NULL DEFAULT' not in content:
    content = content.replace(old_schema, new_schema)
    changes.append('faceit columns in tournament_bracket_matches schema')

# 2. Add ensure_faceit_bracket_columns function
ensure_fn = '''

def ensure_faceit_bracket_columns(connection: sqlite3.Connection) -> None:
    columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(tournament_bracket_matches)").fetchall()
    }
    for col, default in [
        ("faceit_match_id", "''"),
        ("faceit_match_url", "''"),
        ("faceit_match_status", "''"),
    ]:
        if col not in columns:
            connection.execute(
                f"ALTER TABLE tournament_bracket_matches ADD COLUMN {col} TEXT NOT NULL DEFAULT {default}"
            )

'''

if 'ensure_faceit_bracket_columns' not in content:
    content = content.replace(
        'def ensure_tournament_indexes',
        ensure_fn + 'def ensure_tournament_indexes'
    )
    changes.append('ensure_faceit_bracket_columns function')

# 3. Call ensure_faceit_bracket_columns in init_db
old_init = '        ensure_tournament_indexes(connection)'
new_init = '        ensure_tournament_indexes(connection)\n        ensure_faceit_bracket_columns(connection)'
if 'ensure_faceit_bracket_columns(connection)' not in content:
    content = content.replace(old_init, new_init)
    changes.append('call ensure_faceit_bracket_columns in init_db')

# 4. Notify captain group when team is accepted
old_update = '''        data = serialize_league(connection, user)
        connection.commit()
        return web.json_response({"ok": True, "league": data})


async def api_league_report_match'''

new_update = '''        # Get team info for notification
        team_row = connection.execute("SELECT * FROM league_teams WHERE id = ?", (team_id,)).fetchone()
        captain_tg_id = 0
        if team_row:
            cap = connection.execute(
                "SELECT lu.tg_id, lu.username FROM league_users lu WHERE lu.id = ?",
                (int(team_row["captain_id"]),)
            ).fetchone()
            if cap:
                captain_tg_id = int(cap["tg_id"])
        data = serialize_league(connection, user)
        connection.commit()

    # Notify captain and group
    application: Application = request.app["telegram_application"]
    if team_row and status == "active":
        team_name = str(team_row["name"])
        fmt = str(team_row["format"] or "5x5")
        # Notify captain in DM with invite link to captain group
        if captain_tg_id:
            dm_msg = (
                f"✅ Команда «{team_name}» принята в турнир HardPoint Series {fmt}!\\n\\n"
            )
            if CAPTAIN_GROUP_ID:
                try:
                    invite = await application.bot.create_chat_invite_link(
                        chat_id=CAPTAIN_GROUP_ID,
                        name=f"captain:{captain_tg_id}",
                        member_limit=1,
                    )
                    dm_msg += (
                        f"Вступи в группу капитанов — там будут уведомления о матчах:\\n"
                        f"🔗 {invite.invite_link}"
                    )
                except TelegramError:
                    logging.exception("Failed to create captain group invite")
                    dm_msg += "Следи за уведомлениями в боте."
            try:
                await application.bot.send_message(chat_id=captain_tg_id, text=dm_msg)
            except TelegramError:
                logging.exception("Failed to DM captain %s", captain_tg_id)
        # Notify captain group
        if CAPTAIN_GROUP_ID:
            cap_username = ""
            if captain_tg_id:
                cap_row = connection.execute(
                    "SELECT username FROM league_users WHERE tg_id = ?", (captain_tg_id,)
                ).fetchone() if False else None  # already have it above
            group_msg = (
                f"✅ Новая команда в турнире!\\n\\n"
                f"🏆 «{team_name}» · {fmt}\\n"
                f"Капитан получил приглашение в группу."
            )
            try:
                await application.bot.send_message(chat_id=CAPTAIN_GROUP_ID, text=group_msg)
            except TelegramError:
                logging.exception("Failed to notify captain group about new team")

    return web.json_response({"ok": True, "league": data})


async def api_league_report_match'''

if 'create_chat_invite_link' not in content or 'captain_tg_id = 0' not in content:
    content = content.replace(old_update, new_update)
    changes.append('captain group notification on team accept')

# 5. Add faceit_match_url to serialize_bracket
old_serialize = '''            "status": match["status"],
            "scheduledAt": match["scheduled_at"],
        })'''
new_serialize = '''            "status": match["status"],
            "scheduledAt": match["scheduled_at"],
            "faceitMatchId": match["faceit_match_id"] if "faceit_match_id" in match.keys() else "",
            "faceitMatchUrl": match["faceit_match_url"] if "faceit_match_url" in match.keys() else "",
        })'''
if 'faceitMatchUrl' not in content:
    content = content.replace(old_serialize, new_serialize)
    changes.append('faceitMatchUrl in serialize_bracket')

# 6. Add _get_team_faceit_nicks helper
nicks_fn = '''

def _get_team_faceit_nicks(connection: sqlite3.Connection, team_id: int) -> List[str]:
    """Get FACEIT nicknames for all team members."""
    rows = connection.execute(
        """
        SELECT lu.faceit_nickname
        FROM league_team_members ltm
        JOIN league_users lu ON lu.id = ltm.user_id
        WHERE ltm.team_id = ? AND lu.faceit_nickname != ''
        """,
        (team_id,),
    ).fetchall()
    return [str(row["faceit_nickname"]) for row in rows if row["faceit_nickname"]]

'''

if '_get_team_faceit_nicks' not in content:
    content = content.replace(
        'def advance_winner',
        nicks_fn + 'def advance_winner'
    )
    changes.append('_get_team_faceit_nicks helper')

# 7. Add faceit create match function
create_match_fn = '''

async def faceit_create_match_for_bracket(team1_nicks: List[str], team2_nicks: List[str]) -> Optional[Dict]:
    """Create a match in FACEIT Hub."""
    if not FACEIT_HUB_ID or not FACEIT_API_KEY:
        return None

    async def resolve_player_id(nick: str) -> Optional[str]:
        data = await faceit_get_player(nick)
        return data.get("player_id") if data else None

    team1_ids = [pid for pid in [await resolve_player_id(n) for n in team1_nicks if n] if pid]
    team2_ids = [pid for pid in [await resolve_player_id(n) for n in team2_nicks if n] if pid]

    if not team1_ids or not team2_ids:
        return None

    headers = {
        "Authorization": f"Bearer {FACEIT_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "type": "hub",
        "game": "cs2",
        "region": "EU",
        "organized": {"hub_id": FACEIT_HUB_ID},
        "teams": {
            "faction1": {"roster": [{"player_id": pid} for pid in team1_ids]},
            "faction2": {"roster": [{"player_id": pid} for pid in team2_ids]},
        },
    }
    try:
        async with aiohttp_client.ClientSession() as session:
            async with session.post(
                "https://open.faceit.com/data/v4/matches",
                headers=headers,
                json=payload,
                timeout=aiohttp_client.ClientTimeout(total=20),
            ) as resp:
                data = await resp.json()
                if resp.status in (200, 201):
                    return data
                return None
    except Exception:
        logging.exception("FACEIT create match error")
        return None

'''

if 'faceit_create_match_for_bracket' not in content:
    content = content.replace(
        'async def api_faceit_verify',
        create_match_fn + 'async def api_faceit_verify'
    )
    changes.append('faceit_create_match_for_bracket function')

# 8. Add api_bracket_create_faceit_room endpoint
create_room_endpoint = '''

async def api_bracket_create_faceit_room(request: web.Request) -> web.Response:
    """Captain creates FACEIT room for bracket match."""
    user = user_from_init_data(request)
    try:
        payload = await request.json()
    except json.JSONDecodeError as error:
        raise web.HTTPBadRequest(reason="Неверный формат") from error

    match_id = int(payload.get("matchId") or 0)
    if not match_id:
        raise web.HTTPBadRequest(reason="matchId обязателен")

    with closing(db()) as connection:
        league_user = ensure_league_user(connection, user)
        match = connection.execute(
            "SELECT * FROM tournament_bracket_matches WHERE id = ?", (match_id,)
        ).fetchone()
        if not match:
            raise web.HTTPBadRequest(reason="Матч не найден")

        if str(match["faceit_match_id"] or ""):
            return web.json_response({
                "ok": True, "already": True,
                "faceitMatchUrl": match["faceit_match_url"],
            })

        captain_team = None
        for tid in [match["team1_id"], match["team2_id"]]:
            if not tid:
                continue
            team = connection.execute(
                "SELECT * FROM league_teams WHERE id = ? AND captain_id = ?",
                (int(tid), int(league_user["id"])),
            ).fetchone()
            if team:
                captain_team = team
                break

        if not captain_team and not is_league_admin(connection, int(user["id"])):
            raise web.HTTPForbidden(reason="Только капитан может создать комнату")

        t1_nicks = _get_team_faceit_nicks(connection, int(match["team1_id"])) if match["team1_id"] else []
        t2_nicks = _get_team_faceit_nicks(connection, int(match["team2_id"])) if match["team2_id"] else []
        t1 = _team_brief(connection, match["team1_id"])
        t2 = _team_brief(connection, match["team2_id"])
        caps = []
        for tid in [match["team1_id"], match["team2_id"]]:
            if not tid:
                continue
            cap = connection.execute(
                "SELECT lu.tg_id FROM league_teams lt JOIN league_users lu ON lu.id = lt.captain_id WHERE lt.id = ?",
                (int(tid),),
            ).fetchone()
            if cap:
                caps.append(int(cap["tg_id"]))
        connection.commit()

    if not t1_nicks or not t2_nicks:
        return web.json_response({
            "ok": False, "fallback": True,
            "faceitHubUrl": FACEIT_HUB_URL,
            "message": "Не удалось найти FACEIT ники игроков",
        })

    faceit_match = await faceit_create_match_for_bracket(t1_nicks, t2_nicks)

    if not faceit_match:
        return web.json_response({
            "ok": False, "fallback": True,
            "faceitHubUrl": FACEIT_HUB_URL,
            "message": "Не удалось создать автоматически. Создайте вручную через Hub.",
        })

    faceit_id = str(faceit_match.get("match_id", ""))
    faceit_url = str(faceit_match.get("faceit_url", "")).replace("{lang}", "ru")
    faceit_status = str(faceit_match.get("status", "SCHEDULED"))

    with closing(db()) as connection:
        connection.execute(
            "UPDATE tournament_bracket_matches SET faceit_match_id=?, faceit_match_url=?, faceit_match_status=? WHERE id=?",
            (faceit_id, faceit_url, faceit_status, match_id),
        )
        connection.commit()

    application: Application = request.app["telegram_application"]
    t1_name = t1["name"] if t1 else "?"
    t2_name = t2["name"] if t2 else "?"
    msg = f"🎮 FACEIT комната создана!\\n\\n{t1_name} vs {t2_name}\\n\\n🔗 {faceit_url}"

    # Notify both captains in DM
    for tg_id in caps:
        try:
            await application.bot.send_message(chat_id=tg_id, text=msg)
        except TelegramError:
            pass

    # Notify captain group
    if CAPTAIN_GROUP_ID:
        try:
            await application.bot.send_message(chat_id=CAPTAIN_GROUP_ID, text=msg)
        except TelegramError:
            pass

    return web.json_response({
        "ok": True,
        "faceitMatchId": faceit_id,
        "faceitMatchUrl": faceit_url,
        "message": "Комната создана! Капитаны получили ссылку.",
    })

'''

if 'api_bracket_create_faceit_room' not in content:
    content = content.replace(
        'async def api_faceit_verify',
        create_room_endpoint + 'async def api_faceit_verify'
    )
    changes.append('api_bracket_create_faceit_room endpoint')

# 9. Register route
old_route = '    web_app.router.add_get("/api/faceit/verify", api_faceit_verify)'
new_route = '    web_app.router.add_post("/api/bracket/create-faceit-room", api_bracket_create_faceit_room)\n    web_app.router.add_get("/api/faceit/verify", api_faceit_verify)'
if '/api/bracket/create-faceit-room' not in content:
    content = content.replace(old_route, new_route)
    changes.append('route /api/bracket/create-faceit-room registered')

with open('/home/ubuntu/hardpoint-bot/bot.py', 'w') as f:
    f.write(content)

print(f"✅ Patched! Changes: {len(changes)}")
for c in changes:
    print(f"  ✓ {c}")
print(f"Total lines: {content.count(chr(10))}")
