#!/usr/bin/env python3
"""Patch bot.py — adds FACEIT sync integration."""

with open('/home/ubuntu/hardpoint-bot/bot.py', 'r') as f:
    content = f.read()

changes = []

# 1. Add FACEIT_SYNC_INTERVAL constant
old = 'FACEIT_HUB_URL = f"https://www.faceit.com/ru/hub/{FACEIT_HUB_ID}" if FACEIT_HUB_ID else ""'
new = 'FACEIT_HUB_URL = f"https://www.faceit.com/ru/hub/{FACEIT_HUB_ID}" if FACEIT_HUB_ID else ""\nFACEIT_SYNC_INTERVAL = 300  # 5 minutes'
if 'FACEIT_SYNC_INTERVAL' not in content:
    content = content.replace(old, new)
    changes.append('FACEIT_SYNC_INTERVAL constant')

# 2. Add ensure_bracket_match_faceit_columns function
ensure_fn = '''
def ensure_bracket_match_faceit_columns(connection: sqlite3.Connection) -> None:
    columns = {r["name"] for r in connection.execute("PRAGMA table_info(tournament_bracket_matches)").fetchall()}
    if "faceit_match_id" not in columns:
        connection.execute("ALTER TABLE tournament_bracket_matches ADD COLUMN faceit_match_id TEXT NOT NULL DEFAULT ''")
    if "faceit_match_url" not in columns:
        connection.execute("ALTER TABLE tournament_bracket_matches ADD COLUMN faceit_match_url TEXT NOT NULL DEFAULT ''")
    if "faceit_match_status" not in columns:
        connection.execute("ALTER TABLE tournament_bracket_matches ADD COLUMN faceit_match_status TEXT NOT NULL DEFAULT ''")


'''
if 'ensure_bracket_match_faceit_columns' not in content:
    content = content.replace('def ensure_tournament_indexes', ensure_fn + 'def ensure_tournament_indexes')
    changes.append('ensure_bracket_match_faceit_columns function')

# 3. Call it in init_db
if 'ensure_bracket_match_faceit_columns(connection)' not in content:
    content = content.replace(
        'ensure_league_user_faceit_column(connection)\n        ensure_tournament_indexes(connection)',
        'ensure_league_user_faceit_column(connection)\n        ensure_bracket_match_faceit_columns(connection)\n        ensure_tournament_indexes(connection)'
    )
    changes.append('ensure_bracket_match_faceit_columns call in init_db')

# 4. Add FACEIT sync functions after faceit_get_player
faceit_functions = '''

async def faceit_get(path: str) -> Optional[Dict]:
    if not FACEIT_API_KEY:
        return None
    url = f"https://open.faceit.com/data/v4{path}"
    headers = {"Authorization": f"Bearer {FACEIT_API_KEY}"}
    try:
        async with aiohttp_client.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp_client.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    return await resp.json()
                logging.warning("FACEIT GET %s -> %s", path, resp.status)
                return None
    except Exception:
        logging.exception("FACEIT GET error: %s", path)
        return None


async def faceit_get_hub_matches(limit: int = 20) -> List[Dict]:
    if not FACEIT_HUB_ID:
        return []
    data = await faceit_get(f"/hubs/{FACEIT_HUB_ID}/matches?type=ongoing&limit={limit}")
    items = data.get("items", []) if data else []
    if not items:
        data2 = await faceit_get(f"/hubs/{FACEIT_HUB_ID}/matches?type=scheduled&limit={limit}")
        items = data2.get("items", []) if data2 else []
    return items


async def faceit_get_match_detail(match_id: str) -> Optional[Dict]:
    return await faceit_get(f"/matches/{match_id}")


def _get_team_faceit_nicks(connection: sqlite3.Connection, team_id: int) -> List[str]:
    rows = connection.execute(
        """
        SELECT lu.faceit_nickname
        FROM league_team_members ltm
        JOIN league_users lu ON lu.id = ltm.user_id
        WHERE ltm.team_id = ? AND lu.faceit_nickname != ''
        """,
        (team_id,),
    ).fetchall()
    return [str(r["faceit_nickname"]) for r in rows]


def _match_confidence(faceit_players: List[str], team1_nicks: List[str], team2_nicks: List[str]) -> float:
    if not faceit_players:
        return 0.0
    faceit_set = {n.lower() for n in faceit_players}
    all_known = [n.lower() for n in team1_nicks + team2_nicks if n]
    if not all_known:
        return 0.0
    hits_t1 = sum(1 for n in team1_nicks if n.lower() in faceit_set)
    hits_t2 = sum(1 for n in team2_nicks if n.lower() in faceit_set)
    if hits_t1 == 0 or hits_t2 == 0:
        return 0.0
    hits = sum(1 for n in all_known if n in faceit_set)
    return hits / len(all_known)


async def faceit_sync_match(bot: Bot, connection: sqlite3.Connection, bracket_match: sqlite3.Row, faceit_match: Dict) -> None:
    faceit_id = str(faceit_match.get("match_id", ""))
    faceit_url = str(faceit_match.get("faceit_url", "")).replace("{lang}", "ru")
    faceit_status = str(faceit_match.get("status", ""))
    match_id = int(bracket_match["id"])
    tournament_id = int(bracket_match["tournament_id"])
    connection.execute(
        "UPDATE tournament_bracket_matches SET faceit_match_id=?, faceit_match_url=?, faceit_match_status=? WHERE id=?",
        (faceit_id, faceit_url, faceit_status, match_id),
    )
    if not str(bracket_match["faceit_match_id"] or ""):
        t1 = _team_brief(connection, bracket_match["team1_id"])
        t2 = _team_brief(connection, bracket_match["team2_id"])
        caps = []
        for tid in [bracket_match["team1_id"], bracket_match["team2_id"]]:
            cap = connection.execute(
                "SELECT lu.tg_id FROM league_teams lt JOIN league_users lu ON lu.id = lt.captain_id WHERE lt.id = ?",
                (tid,),
            ).fetchone()
            if cap:
                caps.append(int(cap["tg_id"]))
        link = faceit_url or FACEIT_HUB_URL
        msg = (
            f"\\U0001f3ae FACEIT \\u043a\\u043e\\u043c\\u043d\\u0430\\u0442\\u0430 \\u043f\\u0440\\u0438\\u043a\\u0440\\u0435\\u043f\\u043b\\u0435\\u043d\\u0430!\\n\\n"
            f"{t1['name'] if t1 else '?'} vs {t2['name'] if t2 else '?'}\\n\\n"
            f"\\U0001f517 {link}"
        )
        for tg_id in caps:
            try:
                await bot.send_message(chat_id=tg_id, text=msg)
            except Exception:
                pass
    if faceit_status in ("FINISHED", "finished") and str(bracket_match["status"]) == "pending":
        results = faceit_match.get("results", {})
        score = results.get("score", {})
        s1 = int(score.get("faction1", 0))
        s2 = int(score.get("faction2", 0))
        winner_faction = results.get("winner", "")
        if winner_faction and bracket_match["team1_id"] and bracket_match["team2_id"]:
            winner_id = int(bracket_match["team1_id"]) if winner_faction == "faction1" else int(bracket_match["team2_id"])
            connection.execute(
                "UPDATE tournament_bracket_matches SET score1=?, score2=?, winner_id=?, status=\\'played\\', faceit_match_status=? WHERE id=?",
                (s1, s2, winner_id, faceit_status, match_id),
            )
            advance_winner(connection, tournament_id, match_id)
            logging.info("FACEIT result: match %s winner %s (%s:%s)", match_id, winner_id, s1, s2)


async def faceit_sync_hub(bot: Bot) -> None:
    if not FACEIT_HUB_ID or not FACEIT_API_KEY:
        return
    faceit_matches = await faceit_get_hub_matches(limit=30)
    if not faceit_matches:
        return
    with closing(db()) as connection:
        pending = connection.execute(
            """
            SELECT * FROM tournament_bracket_matches
            WHERE status IN ('pending', 'played')
              AND team1_id IS NOT NULL AND team2_id IS NOT NULL
              AND (faceit_match_id = '' OR faceit_match_status NOT IN ('FINISHED','finished'))
            ORDER BY created_at DESC LIMIT 50
            """
        ).fetchall()
        for bm in pending:
            if str(bm["faceit_match_id"] or "") and bm["faceit_match_status"] in ("FINISHED", "finished"):
                continue
            if str(bm["faceit_match_id"] or ""):
                fm = await faceit_get_match_detail(bm["faceit_match_id"])
                if fm:
                    await faceit_sync_match(bot, connection, bm, fm)
                continue
            t1_nicks = _get_team_faceit_nicks(connection, int(bm["team1_id"]))
            t2_nicks = _get_team_faceit_nicks(connection, int(bm["team2_id"]))
            best_match = None
            best_score = 0.0
            for fm in faceit_matches:
                fm_id = str(fm.get("match_id", ""))
                if connection.execute(
                    "SELECT id FROM tournament_bracket_matches WHERE faceit_match_id=? AND id!=?",
                    (fm_id, int(bm["id"])),
                ).fetchone():
                    continue
                teams_data = fm.get("teams", {})
                fm_players: List[str] = []
                for faction in ["faction1", "faction2"]:
                    fm_players.extend(p.get("nickname", "") for p in teams_data.get(faction, {}).get("roster", []))
                score = _match_confidence(fm_players, t1_nicks, t2_nicks)
                if score > best_score:
                    best_score = score
                    best_match = fm
            if best_match and best_score >= 0.6:
                logging.info("Auto-attaching FACEIT %s to bracket match %s (%.0f%%)",
                             best_match.get("match_id"), bm["id"], best_score * 100)
                await faceit_sync_match(bot, connection, bm, best_match)
            elif best_match and best_score >= 0.3 and GROUP_ID:
                t1 = _team_brief(connection, bm["team1_id"])
                t2 = _team_brief(connection, bm["team2_id"])
                fm_url = str(best_match.get("faceit_url", "")).replace("{lang}", "ru")
                try:
                    await bot.send_message(
                        chat_id=GROUP_ID,
                        text=(
                            f"\\u2753 FACEIT \\u043d\\u0430\\u0439\\u0434\\u0435\\u043d\\u0430, "
                            f"\\u043d\\u0443\\u0436\\u043d\\u043e \\u043f\\u043e\\u0434\\u0442\\u0432\\u0435\\u0440\\u0436\\u0434\\u0435\\u043d\\u0438\\u0435 ({best_score:.0%})\\n\\n"
                            f"{t1['name'] if t1 else '?'} vs {t2['name'] if t2 else '?'}\\n{fm_url}"
                        ),
                    )
                except Exception:
                    pass
        connection.commit()


async def faceit_sync_scheduler(bot: Bot) -> None:
    logging.info("FACEIT sync scheduler started (interval=%ds)", FACEIT_SYNC_INTERVAL)
    while True:
        await asyncio.sleep(FACEIT_SYNC_INTERVAL)
        try:
            await faceit_sync_hub(bot)
        except Exception:
            logging.exception("FACEIT sync error")

'''

marker = '        logging.exception("FACEIT API error for nickname %s", nickname)\n        return None\n'
if 'faceit_sync_scheduler' not in content:
    content = content.replace(marker, marker + faceit_functions)
    changes.append('FACEIT sync functions (faceit_get, faceit_sync_hub, faceit_sync_scheduler, etc)')

# 5. Add faceit fields to serialize_bracket
old_item = '            "status": match["status"],\n            "scheduledAt": match["scheduled_at"],\n        })'
new_item = (
    '            "status": match["status"],\n'
    '            "scheduledAt": match["scheduled_at"],\n'
    '            "faceitMatchId": match["faceit_match_id"] if "faceit_match_id" in match.keys() else "",\n'
    '            "faceitMatchUrl": match["faceit_match_url"] if "faceit_match_url" in match.keys() else "",\n'
    '            "faceitMatchStatus": match["faceit_match_status"] if "faceit_match_status" in match.keys() else "",\n'
    '        })'
)
if 'faceitMatchId' not in content:
    content = content.replace(old_item, new_item)
    changes.append('faceit fields in serialize_bracket')

# 6. Add faceit_sync_task in main()
old_main = '    bracket_task = asyncio.create_task(bracket_scheduler(application.bot))\n    web_runner = await start_web_server'
new_main = (
    '    bracket_task = asyncio.create_task(bracket_scheduler(application.bot))\n'
    '    faceit_sync_task: Optional[asyncio.Task[None]] = None\n'
    '    faceit_sync_task = asyncio.create_task(faceit_sync_scheduler(application.bot))\n'
    '    web_runner = await start_web_server'
)
if 'faceit_sync_task' not in content:
    content = content.replace(old_main, new_main)
    changes.append('faceit_sync_task in main()')

# 7. Cancel faceit_sync_task in finally
old_cancel = '        if bracket_task:\n            bracket_task.cancel()\n        if web_runner:'
new_cancel = (
    '        if bracket_task:\n'
    '            bracket_task.cancel()\n'
    '        if faceit_sync_task:\n'
    '            faceit_sync_task.cancel()\n'
    '        if web_runner:'
)
if 'faceit_sync_task.cancel()' not in content:
    content = content.replace(old_cancel, new_cancel)
    changes.append('faceit_sync_task.cancel() in finally')

with open('/home/ubuntu/hardpoint-bot/bot.py', 'w') as f:
    f.write(content)

print(f"✅ Patched successfully! Changes: {len(changes)}")
for c in changes:
    print(f"  ✓ {c}")
print(f"Total lines: {content.count(chr(10))}")
