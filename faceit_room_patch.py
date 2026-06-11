#!/usr/bin/env python3
"""Patch bot.py — adds POST /api/bracket/create-faceit-room endpoint."""

with open('/home/ubuntu/hardpoint-bot/bot.py', 'r') as f:
    content = f.read()

changes = []

# 1. Add faceit_create_match function after faceit_get_match_detail
create_match_fn = '''

async def faceit_create_match_for_bracket(team1_nicks: List[str], team2_nicks: List[str]) -> Optional[Dict]:
    """Create a match in FACEIT Hub using player nicknames."""
    if not FACEIT_HUB_ID or not FACEIT_API_KEY:
        return None

    async def resolve_player_id(nick: str) -> Optional[str]:
        data = await faceit_get(f"/players?nickname={nick}")
        return data.get("player_id") if data else None

    team1_ids = [pid for pid in [await resolve_player_id(n) for n in team1_nicks if n] if pid]
    team2_ids = [pid for pid in [await resolve_player_id(n) for n in team2_nicks if n] if pid]

    if not team1_ids or not team2_ids:
        logging.warning("faceit_create_match: could not resolve player IDs t1=%s t2=%s", team1_nicks, team2_nicks)
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
                    logging.info("FACEIT match created: %s", data.get("match_id"))
                    return data
                logging.warning("FACEIT create match failed %s: %s", resp.status, data)
                return None
    except Exception:
        logging.exception("FACEIT create match error")
        return None

'''

if 'faceit_create_match_for_bracket' not in content:
    content = content.replace(
        'async def faceit_get_match_detail(match_id: str) -> Optional[Dict]:\n    return await faceit_get(f"/matches/{match_id}")',
        'async def faceit_get_match_detail(match_id: str) -> Optional[Dict]:\n    return await faceit_get(f"/matches/{match_id}")' + create_match_fn
    )
    changes.append('faceit_create_match_for_bracket function')

# 2. Add api_bracket_create_faceit_room endpoint
create_room_endpoint = '''

async def api_bracket_create_faceit_room(request: web.Request) -> web.Response:
    """Captain creates FACEIT room for their bracket match."""
    user = user_from_init_data(request)
    try:
        payload = await request.json()
    except json.JSONDecodeError as error:
        raise web.HTTPBadRequest(reason="\\u041d\\u0435\\u0432\\u0435\\u0440\\u043d\\u044b\\u0439 \\u0444\\u043e\\u0440\\u043c\\u0430\\u0442") from error

    match_id = int(payload.get("matchId") or 0)
    if not match_id:
        raise web.HTTPBadRequest(reason="matchId \\u043e\\u0431\\u044f\\u0437\\u0430\\u0442\\u0435\\u043b\\u0435\\u043d")

    with closing(db()) as connection:
        league_user = ensure_league_user(connection, user)

        # Get bracket match
        match = connection.execute(
            "SELECT * FROM tournament_bracket_matches WHERE id = ?", (match_id,)
        ).fetchone()
        if not match:
            raise web.HTTPBadRequest(reason="\\u041c\\u0430\\u0442\\u0447 \\u043d\\u0435 \\u043d\\u0430\\u0439\\u0434\\u0435\\u043d")

        # Check match already has FACEIT room
        if str(match["faceit_match_id"] or ""):
            return web.json_response({
                "ok": True,
                "already": True,
                "faceitMatchUrl": match["faceit_match_url"],
                "message": "\\u041a\\u043e\\u043c\\u043d\\u0430\\u0442\\u0430 \\u0443\\u0436\\u0435 \\u0441\\u043e\\u0437\\u0434\\u0430\\u043d\\u0430",
            })

        # Check user is captain of one of the teams
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
            raise web.HTTPForbidden(reason="\\u0422\\u043e\\u043b\\u044c\\u043a\\u043e \\u043a\\u0430\\u043f\\u0438\\u0442\\u0430\\u043d \\u043c\\u043e\\u0436\\u0435\\u0442 \\u0441\\u043e\\u0437\\u0434\\u0430\\u0442\\u044c \\u043a\\u043e\\u043c\\u043d\\u0430\\u0442\\u0443")

        # Get FACEIT nicks for both teams
        t1_nicks = _get_team_faceit_nicks(connection, int(match["team1_id"])) if match["team1_id"] else []
        t2_nicks = _get_team_faceit_nicks(connection, int(match["team2_id"])) if match["team2_id"] else []

        if not t1_nicks or not t2_nicks:
            raise web.HTTPBadRequest(reason="\\u041d\\u0435 \\u0443\\u0434\\u0430\\u043b\\u043e\\u0441\\u044c \\u043d\\u0430\\u0439\\u0442\\u0438 FACEIT \\u043d\\u0438\\u043a\\u0438 \\u0438\\u0433\\u0440\\u043e\\u043a\\u043e\\u0432")

        connection.commit()

    # Create FACEIT match (outside DB connection)
    faceit_match = await faceit_create_match_for_bracket(t1_nicks, t2_nicks)

    if not faceit_match:
        # Fallback — return Hub URL so captain can create manually
        return web.json_response({
            "ok": False,
            "fallback": True,
            "faceitHubUrl": FACEIT_HUB_URL,
            "message": "\\u041d\\u0435 \\u0443\\u0434\\u0430\\u043b\\u043e\\u0441\\u044c \\u0441\\u043e\\u0437\\u0434\\u0430\\u0442\\u044c \\u0430\\u0432\\u0442\\u043e\\u043c\\u0430\\u0442\\u0438\\u0447\\u0435\\u0441\\u043a\\u0438. \\u0421\\u043e\\u0437\\u0434\\u0430\\u0439\\u0442\\u0435 \\u0432\\u0440\\u0443\\u0447\\u043d\\u0443\\u044e \\u0447\\u0435\\u0440\\u0435\\u0437 Hub.",
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

        # Notify both captains
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

    msg = (
        f"\\U0001f3ae FACEIT \\u043a\\u043e\\u043c\\u043d\\u0430\\u0442\\u0430 \\u0441\\u043e\\u0437\\u0434\\u0430\\u043d\\u0430!\\n\\n"
        f"{t1['name'] if t1 else '?'} vs {t2['name'] if t2 else '?'}\\n\\n"
        f"\\U0001f517 {faceit_url}"
    )
    application: Application = request.app["telegram_application"]
    for tg_id in caps:
        try:
            await application.bot.send_message(chat_id=tg_id, text=msg)
        except TelegramError:
            pass

    return web.json_response({
        "ok": True,
        "faceitMatchId": faceit_id,
        "faceitMatchUrl": faceit_url,
        "message": "\\u041a\\u043e\\u043c\\u043d\\u0430\\u0442\\u0430 \\u0441\\u043e\\u0437\\u0434\\u0430\\u043d\\u0430! \\u041a\\u0430\\u043f\\u0438\\u0442\\u0430\\u043d\\u044b \\u043f\\u043e\\u043b\\u0443\\u0447\\u0438\\u043b\\u0438 \\u0441\\u0441\\u044b\\u043b\\u043a\\u0443.",
    })

'''

if 'api_bracket_create_faceit_room' not in content:
    content = content.replace(
        'async def api_faceit_verify',
        create_room_endpoint + 'async def api_faceit_verify'
    )
    changes.append('api_bracket_create_faceit_room endpoint')

# 3. Register route in start_web_server
old_route = 'web_app.router.add_get("/api/faceit/verify", api_faceit_verify)'
new_route = (
    'web_app.router.add_post("/api/bracket/create-faceit-room", api_bracket_create_faceit_room)\n'
    '    web_app.router.add_get("/api/faceit/verify", api_faceit_verify)'
)
if 'create-faceit-room' not in content:
    content = content.replace(old_route, new_route)
    changes.append('route /api/bracket/create-faceit-room registered')

with open('/home/ubuntu/hardpoint-bot/bot.py', 'w') as f:
    f.write(content)

print(f"✅ Patched! Changes: {len(changes)}")
for c in changes:
    print(f"  ✓ {c}")
print(f"Total lines: {content.count(chr(10))}")
