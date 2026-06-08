const tg = window.Telegram?.WebApp;
const state = {
  inviteLink: "",
  weeklyTop: [],
  allTimeTop: [],
  clanWeeklyTop: [],
  clanMonthlyTop: [],
  clans: null,
  league: null,
  activeView: null,
  previousView: null,
  leagueStandingTab: "",
  selectedLeagueFormat: "5x5",
  liveFmt: "5x5",
  liveRefreshTimer: null,
};

const inviteLinkNode = document.querySelector("#invite-link");
const weeklyCountNode = document.querySelector("#weekly-count");
const allTimeCountNode = document.querySelector("#all-time-count");
const headerCoinBalance = document.querySelector("#header-coin-balance");
const homeUsernameNode = document.querySelector("#home-username");
const homeAvatarButton = document.querySelector("#home-avatar-button");
const profileDropdown = document.querySelector("#profile-dropdown");
const dropdownProfileButton = document.querySelector("#dropdown-profile-button");
const dropdownSettingsButton = document.querySelector("#dropdown-settings-button");
const profileClanBadge = document.querySelector("#profile-clan-badge");
const homeMissionsCard = document.querySelector("#home-missions-card");
const homeSeriesCard = document.querySelector("#home-series-card");
const homeClansCard = document.querySelector("#home-clans-card");
const homeLiveCard = document.querySelector("#home-live-card");
const rankHintText = document.querySelector("#rank-hint-text");
const topListNode = document.querySelector("#top-list");
const topTitleNode = document.querySelector("#top-title");
const statusNode = document.querySelector("#status");
const copyButton = document.querySelector("#copy-button");
const shareButton = document.querySelector("#share-button");
const weeklyTab = document.querySelector("#weekly-tab");
const allTimeTab = document.querySelector("#all-time-tab");
const clubLoginInput = document.querySelector("#club-login");
const saveLoginButton = document.querySelector("#save-login-button");
const homeView = document.querySelector("#home-view");
const profileView = document.querySelector("#profile-view");
const missionsView = document.querySelector("#missions-view");
const clansView = document.querySelector("#clans-view");
const leagueView = document.querySelector("#league-view");
const liveView = document.querySelector("#live-view");
const esportView = document.querySelector("#esport-view");
const liveContent = document.querySelector("#live-content");
const liveTab5x5 = document.querySelector("#live-tab-5x5");
const liveTab2x2 = document.querySelector("#live-tab-2x2");
const profileMenuButton = document.querySelector("#profile-menu-button");
const profileMissionsButton = document.querySelector("#profile-missions-button");
const profileClansButton = document.querySelector("#profile-clans-button");
const backButton = document.querySelector("#back-button");
const navHome = document.querySelector("#nav-home");
const navSeries = document.querySelector("#nav-series");
const navLive = document.querySelector("#nav-live");
const navEsport = document.querySelector("#nav-esport");
const rankTitleNode = document.querySelector("#rank-title");
const rankScoreNode = document.querySelector("#rank-score");
const rankMeterFillNode = document.querySelector("#rank-meter-fill");
const rankNextNode = document.querySelector("#rank-next");
const coinNoteNode = document.querySelector("#coin-note");
const rankInvitesNode = document.querySelector("#rank-invites");
const rankCoinsNode = document.querySelector("#rank-coins");
const rankVisitsNode = document.querySelector("#rank-visits");
const dailyRewardButton = document.querySelector("#daily-reward-button");
const visitRewardButton = document.querySelector("#visit-reward-button");
const dailyRewardStatus = document.querySelector("#daily-reward-status");
const visitRewardStatus = document.querySelector("#visit-reward-status");
const missionStreakNode = document.querySelector("#mission-streak");
const instagramRewardButton = document.querySelector("#instagram-reward-button");
const discordRewardButton = document.querySelector("#discord-reward-button");
const instagramRewardStatus = document.querySelector("#instagram-reward-status");
const discordRewardStatus = document.querySelector("#discord-reward-status");
const profileStreakDaysNode = document.querySelector("#profile-streak-days");
const profileStreakFillNode = document.querySelector("#profile-streak-fill");
const profileStreakMarkers = document.querySelectorAll(".streak-marker");
const clanGate = document.querySelector("#clan-gate");
const clanCurrent = document.querySelector("#clan-current");
const clanJoin = document.querySelector("#clan-join");
const clanNameNode = document.querySelector("#clan-name");
const clanLevelNode = document.querySelector("#clan-level");
const clanSlotsNode = document.querySelector("#clan-slots");
const clanWeeklyXpNode = document.querySelector("#clan-weekly-xp");
const clanMonthlyXpNode = document.querySelector("#clan-monthly-xp");
const clanTotalXpNode = document.querySelector("#clan-total-xp");
const clanLevelFillNode = document.querySelector("#clan-level-fill");
const clanNextLevelNode = document.querySelector("#clan-next-level");
const clanChestTitleNode = document.querySelector("#clan-chest-title");
const clanChestXpNode = document.querySelector("#clan-chest-xp");
const clanChestFillNode = document.querySelector("#clan-chest-fill");
const clanChestNoteNode = document.querySelector("#clan-chest-note");
const clanChestMarkers = document.querySelectorAll(".clan-chest-marker");
const clanDailyGoalNode = document.querySelector("#clan-daily-goal");
const clanCheckinButton = document.querySelector("#clan-checkin-button");
const clanCheckinStatus = document.querySelector("#clan-checkin-status");
const clanMyRoleNode = document.querySelector("#clan-my-role");
const clanMyWeeklyNode = document.querySelector("#clan-my-weekly");
const clanMyTotalNode = document.querySelector("#clan-my-total");
const clanMyCheckinsNode = document.querySelector("#clan-my-checkins");
const clanMyActiveNode = document.querySelector("#clan-my-active");
const clanCodeNode = document.querySelector("#clan-code");
const copyClanCodeButton = document.querySelector("#copy-clan-code-button");
const clanMembersList = document.querySelector("#clan-members-list");
const newClanNameInput = document.querySelector("#new-clan-name");
const newClanPublicInput = document.querySelector("#new-clan-public");
const createClanButton = document.querySelector("#create-clan-button");
const createClanNote = document.querySelector("#create-clan-note");
const joinClanCodeInput = document.querySelector("#join-clan-code");
const joinClanCodeButton = document.querySelector("#join-clan-code-button");
const publicClansList = document.querySelector("#public-clans-list");
const clanWeeklyTab = document.querySelector("#clan-weekly-tab");
const clanMonthlyTab = document.querySelector("#clan-monthly-tab");
const clanTopTitleNode = document.querySelector("#clan-top-title");
const clanTopList = document.querySelector("#clan-top-list");
const leagueRoleNode = document.querySelector("#league-role");
const leagueXpNode = document.querySelector("#league-xp");
const leagueNextTitle = document.querySelector("#league-next-title");
const leagueNextNote = document.querySelector("#league-next-note");
const leagueNextButton = document.querySelector("#league-next-button");
const leagueActionJoin = document.querySelector("#league-action-join");
const leagueActionCreate = document.querySelector("#league-action-create");
const leagueActionTable = document.querySelector("#league-action-table");
const leagueTabs = document.querySelectorAll(".league-tabs button");
const leagueSections = document.querySelectorAll(".league-section");
const leagueSeasonsNode = document.querySelector("#league-seasons");
const leagueMyTeamNode = document.querySelector("#league-my-team");
const leagueTeamsList = document.querySelector("#league-teams-list");
const leagueStandingsTabs = document.querySelector("#league-standings-tabs");
const leagueStandingsMeta = document.querySelector("#league-standings-meta");
const leagueStandingsList = document.querySelector("#league-standings-list");
const leaguePendingList = document.querySelector("#league-pending-list");
const leagueAdminPanel = document.querySelector("#league-admin-panel");
const leagueAdminEmpty = document.querySelector("#league-admin-empty");
const leagueRegisterFaceit = document.querySelector("#league-register-faceit");
const faceitVerifyStatus = document.querySelector("#faceit-verify-status");
const leagueRegisterButton = document.querySelector("#league-register-button");
const leagueJoinCard = document.querySelector("#league-join-card");
const leagueJoinForm = document.querySelector("#league-join-form");
const leagueJoinCodeInput = document.querySelector("#league-join-code");
const leagueJoinButton = document.querySelector("#league-join-button");
const leagueJoinNote = document.querySelector("#league-join-note");
const leagueTeamFormatWrap = document.querySelector("#league-team-format-wrap");
const leagueTeamFormat = document.querySelector("#league-team-format");
const leagueTeamName = document.querySelector("#league-team-name");
const leagueCreateTeamButton = document.querySelector("#league-create-team-button");
const leagueInviteSheet = document.querySelector("#league-invite-sheet");
const leagueInviteClose = document.querySelector("#league-invite-close");
const leagueInviteCodeNode = document.querySelector("#league-invite-code");
const leagueCopyCodeButton = document.querySelector("#league-copy-code-button");
const leagueShareCodeButton = document.querySelector("#league-share-code-button");
const seriesFormatButtons = document.querySelectorAll("[data-series-format]");
const seriesBackToFormats = document.querySelector("#series-back-to-formats");
const seriesSelectedTitle = document.querySelector("#series-selected-title");
const seriesSelectedBadge = document.querySelector("#series-selected-badge");
const faceitHubBanner = document.querySelector("#faceit-hub-banner");
const faceitHubLink = document.querySelector("#faceit-hub-link");
const teamFinalsButton = document.querySelector("#team-finals-button");
const teamFinalsPanel = document.querySelector("#team-finals-panel");
const namaIconButton = document.querySelector("#nama-icon-button");
const namaProfilePanel = document.querySelector("#nama-profile-panel");

const ALL_VIEWS = [homeView, profileView, missionsView, clansView, leagueView, liveView, esportView];
state.activeView = homeView;

function setStatus(msg) { statusNode.textContent = msg || ""; }
function authHeaders() { return { "X-Telegram-Init-Data": tg?.initData || "" }; }

async function api(path) {
  const r = await fetch(path, { headers: authHeaders() });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
async function postApi(path, payload) {
  const r = await fetch(path, { method: "POST", headers: { ...authHeaders(), "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
function errorMessage(error, fallback) {
  try { return JSON.parse(error.message).message || fallback; } catch { return fallback; }
}
function initialsFor(v) {
  const c = String(v || "HP").replace("@", "").trim();
  const p = c.split(/\s+/).filter(Boolean);
  return p.length >= 2 ? `${p[0][0]}${p[1][0]}`.toUpperCase() : c.slice(0, 2).toUpperCase() || "HP";
}
function escapeHtml(v) {
  return String(v).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[c]));
}

// ── NAV ──
function showView(view, options = {}) {
  if (state.activeView && state.activeView !== view && !options.skipHistory) state.previousView = state.activeView;
  state.activeView = view;
  ALL_VIEWS.forEach(v => v.classList.toggle("is-active", v === view));
  navHome.classList.toggle("is-current", view === homeView);
  navSeries.classList.toggle("is-current", view === leagueView);
  navLive.classList.toggle("is-current", view === liveView);
  navEsport.classList.toggle("is-current", view === esportView);
  backButton.classList.toggle("is-visible", view !== homeView);
  closeProfileDropdown();
  if (view === liveView) loadLiveBracket();
  else stopLiveRefresh();
}
function goBack() {
  const target = state.previousView && state.previousView !== state.activeView ? state.previousView : homeView;
  state.previousView = homeView;
  showView(target, { skipHistory: true });
}
function closeProfileDropdown() {
  profileDropdown.classList.remove("is-open");
  profileDropdown.setAttribute("aria-hidden", "true");
  profileMenuButton.setAttribute("aria-expanded", "false");
}
function toggleProfileDropdown() {
  const open = !profileDropdown.classList.contains("is-open");
  profileDropdown.classList.toggle("is-open", open);
  profileDropdown.setAttribute("aria-hidden", String(!open));
  profileMenuButton.setAttribute("aria-expanded", String(open));
}

// ── LIVE BRACKET ──
function roundLabel(rnd, total) {
  if (rnd === total) return "Финал";
  if (rnd === total - 1) return "1/2";
  if (rnd === total - 2) return "1/4";
  if (rnd === total - 3) return "1/8";
  return `Р${rnd}`;
}

function renderLiveBracket(data) {
  if (!data.bracket) {
    liveContent.innerHTML = `
      <div class="live-reg-state">
        <div class="live-reg-icon">📋</div>
        <h3>Идёт регистрация</h3>
        <p>Сетка будет сгенерирована в понедельник в 04:00</p>
        <div class="live-reg-count">${data.registeredTeams || 0} команд зарегистрировано</div>
      </div>`;
    return;
  }
  const b = data.bracket;
  const rounds = b.rounds || {};
  const roundNums = Object.keys(rounds).map(Number).sort((a, z) => a - z);
  const total = roundNums.length;
  const played = b.playedMatches || 0;
  const totalM = b.totalMatches || 0;
  let html = `<div class="live-stats-bar"><div><strong>${b.registeredTeams || 0}</strong><small>Команд</small></div><div><strong>${played}/${totalM}</strong><small>Матчей</small></div><div><strong>${total}</strong><small>Раундов</small></div></div>`;
  html += `<div class="live-bracket-scroll"><div class="live-bracket">`;
  roundNums.forEach(rnd => {
    const matches = rounds[rnd] || [];
    html += `<div class="live-round"><div class="live-round-label">${roundLabel(rnd, total)}</div>`;
    matches.forEach(m => { html += renderLiveMatch(m); });
    html += `</div>`;
  });
  if (b.status === "finished" && b.winnerId) {
    const winnerName = findTeamName(rounds, b.winnerId);
    html += `<div class="live-round"><div class="live-round-label">Чемпион</div><div class="live-champion"><div>🏆</div><div>${escapeHtml(winnerName || "??")}</div></div></div>`;
  }
  html += `</div></div>`;
  liveContent.innerHTML = html;
}

function findTeamName(rounds, winnerId) {
  for (const matches of Object.values(rounds)) {
    for (const m of matches) {
      if (m.team1?.id === winnerId) return m.team1.name;
      if (m.team2?.id === winnerId) return m.team2.name;
    }
  }
  return null;
}

function renderLiveMatch(m) {
  const t1 = m.team1; const t2 = m.team2; const w = m.winner;
  let barClass = "live-match-bar pending", barText = "Ожидается";
  if (m.status === "played") { barClass = "live-match-bar done"; barText = "Завершён"; }
  else if (m.status === "bye") { barClass = "live-match-bar bye"; barText = "BYE"; }
  const t1cls = w ? (w.id === t1?.id ? "winner" : "loser") : (t1 ? "" : "tbd");
  const t2cls = w ? (w.id === t2?.id ? "winner" : "loser") : (t2 ? "" : "tbd");
  const s1 = m.score1 !== null && m.score1 !== undefined ? m.score1 : "—";
  const s2 = m.score2 !== null && m.score2 !== undefined ? m.score2 : "—";
  return `<div class="live-match">
    <div class="${barClass}">${barText}</div>
    <div class="live-team ${t1cls}"><span>${escapeHtml(t1?.name || "TBD")}</span><b>${s1}</b></div>
    <div class="live-divider"></div>
    <div class="live-team ${t2cls}"><span>${escapeHtml(t2?.name || "TBD")}</span><b>${s2}</b></div>
  </div>`;
}

function stopLiveRefresh() {
  if (state.liveRefreshTimer) { clearTimeout(state.liveRefreshTimer); state.liveRefreshTimer = null; }
}

async function loadLiveBracket() {
  stopLiveRefresh();
  liveContent.innerHTML = `<div class="live-loading">Загрузка...</div>`;
  try {
    const data = await fetch(`/api/bracket?format=${state.liveFmt}`).then(r => r.json());
    renderLiveBracket(data);
    if (data.bracket?.status === "active") {
      state.liveRefreshTimer = setTimeout(loadLiveBracket, 30000);
    }
  } catch {
    liveContent.innerHTML = `<div class="live-error">⚠️ Не удалось загрузить. Попробуй позже.</div>`;
  }
}

function switchLiveFormat(fmt) {
  state.liveFmt = fmt;
  liveTab5x5.classList.toggle("is-active", fmt === "5x5");
  liveTab2x2.classList.toggle("is-active", fmt === "2x2");
  loadLiveBracket();
}

// ── RENDER ──
function renderTop(items) {
  if (!items.length) { topListNode.innerHTML = "<li>Пока нет приглашений</li>"; return; }
  topListNode.innerHTML = items.map((item, i) => {
    const name = item.username ? `@${item.username}` : item.name;
    const prize = item.prize ? `<small>Приз: ${escapeHtml(item.prize)}</small>` : "";
    const club = item.clubLogin ? `<small>${escapeHtml(item.clubLogin)}</small>` : "";
    const rank = item.rank ? `<small>${escapeHtml(item.rank.icon)} ${escapeHtml(item.rank.title)}</small>` : "";
    return `<li><strong>${i + 1}. ${escapeHtml(name)}${rank}${club}${prize}</strong><span>${item.total}</span></li>`;
  }).join("");
}

function renderRank(user) {
  const rank = user.rank || {}; const progress = user.progress || {};
  const score = Number(progress.score || rank.score || 0);
  const nextScore = Number(rank.nextScore || score);
  const minScore = Math.max(0, nextScore - Number(rank.remaining || 0));
  const pct = rank.isMax ? 100 : Math.min(100, Math.round((Math.max(0, score - minScore) / Math.max(1, nextScore - minScore)) * 100));
  rankTitleNode.textContent = `${rank.icon || "🥉"} ${rank.title || "Recruit"}`;
  rankScoreNode.textContent = String(score);
  rankMeterFillNode.style.width = `${pct}%`;
  rankNextNode.textContent = rank.isMax ? "Максимальный ранг." : `До ${rank.nextIcon || ""} ${rank.nextTitle || ""}: ${rank.remaining || 0}`;
  rankInvitesNode.textContent = String(progress.invites || 0);
  rankCoinsNode.textContent = String(progress.coins || 0);
  rankVisitsNode.textContent = String(progress.visits || 0);
  headerCoinBalance.textContent = String(progress.coins || 0);
  coinNoteNode.textContent = `За каждого приглашённого: ${progress.inviteCoinReward || 20} монет.`;
  rankHintText.textContent = rank.isMax ? "Максимальный ранг." : `Пригласи ещё ${rank.remaining || 0} и стань ${rank.nextTitle || ""}.`;
}

function renderMissions(missions) {
  const daily = missions.dailyReward || {}; const visit = missions.visitReward || {};
  const streak = missions.streak || {}; const social = missions.social || {};
  dailyRewardButton.disabled = !daily.canClaim;
  dailyRewardButton.textContent = daily.canClaim ? "Забрать" : "Забрано";
  dailyRewardStatus.textContent = daily.canClaim ? "Доступно сегодня." : "Завтра.";
  visitRewardButton.disabled = !visit.canClaim;
  visitRewardButton.textContent = visit.canClaim ? "Забрать" : "Забрано";
  visitRewardStatus.textContent = visit.canClaim ? "Доступно сегодня." : "До завтра.";
  missionStreakNode.textContent = String(streak.days || 0);
  renderProfileStreak(streak);
  renderSocialMission(instagramRewardButton, instagramRewardStatus, social.instagram || {}, "Instagram");
  renderSocialMission(discordRewardButton, discordRewardStatus, social.discord || {}, "Discord");
}

function renderProfileStreak(streak) {
  const days = Math.max(0, Number(streak.days || 0));
  profileStreakDaysNode.textContent = String(days);
  profileStreakFillNode.style.width = `${Math.min(100, (days / 30) * 100)}%`;
  profileStreakMarkers.forEach(m => m.classList.toggle("is-reached", days >= Number(m.dataset.day || 0)));
}

function renderSocialMission(button, node, mission, title) {
  const s = mission.status || "new";
  button.disabled = s === "pending" || s === "claimed";
  if (s === "claimed") { button.textContent = "Получено"; node.textContent = `Награда за ${title} получена.`; }
  else if (s === "pending") { button.textContent = "На проверке"; node.textContent = `~${mission.hoursLeft || 24} ч.`; }
  else if (s === "ready") { button.textContent = "Получить 500"; node.textContent = "Можно забрать."; }
  else { button.textContent = "Отправить"; node.textContent = "После подписки отправь."; }
}

function formatXp(v) { return `${Number(v || 0)} XP`; }

function renderClans(data) {
  state.clans = data || {};
  state.clanWeeklyTop = state.clans.weeklyTop || [];
  state.clanMonthlyTop = state.clans.monthlyTop || [];
  const access = state.clans.access || {}; const clan = state.clans.currentClan;
  const canJoin = Boolean(access.canJoin); const canCreate = Boolean(access.canCreate);
  profileClanBadge.textContent = clan?.name || (canJoin ? "Доступно" : "С Rookie");
  clanGate.hidden = canJoin; clanCurrent.hidden = !clan; clanJoin.hidden = Boolean(clan);
  createClanButton.disabled = !canCreate;
  createClanNote.textContent = canCreate ? "Можно создать." : "С ранга Legend.";
  joinClanCodeButton.disabled = !canJoin;
  if (clan) renderCurrentClan(clan);
  renderPublicClans(state.clans.publicClans || [], canJoin);
  showClanWeeklyTop();
}

function renderCurrentClan(clan) {
  clanNameNode.textContent = clan.name || "Клан";
  clanLevelNode.textContent = `LVL ${clan.level?.level || 1}`;
  clanSlotsNode.textContent = `${clan.membersCount || 0}/${clan.level?.slots || 5}`;
  clanWeeklyXpNode.textContent = formatXp(clan.weeklyXp);
  clanMonthlyXpNode.textContent = formatXp(clan.monthlyXp);
  clanTotalXpNode.textContent = formatXp(clan.totalXp);
  const lv = clan.level || {};
  const pct = lv.isMax ? 100 : Math.min(100, ((Number(clan.totalXp || 0) - Number(lv.xp || 0)) / Math.max(1, Number(lv.nextXp || lv.xp || 1) - Number(lv.xp || 0))) * 100);
  clanLevelFillNode.style.width = `${pct}%`;
  clanNextLevelNode.textContent = lv.isMax ? "Макс." : `До ${lv.nextLevel}: ${lv.remaining || 0} XP`;
  renderClanChest(clan); renderClanContribution(clan); renderClanMembers(clan.members || []);
  clanCodeNode.textContent = clan.code || "";
}

function renderClanChest(clan) {
  const chest = clan.chest || {}; const reached = chest.reached; const next = chest.next;
  clanChestTitleNode.textContent = reached ? `Достигнут ${reached.title}` : "Сундук ещё не достигнут";
  clanChestXpNode.textContent = formatXp(clan.weeklyXp);
  clanChestFillNode.style.width = `${Math.min(100, (Number(clan.weeklyXp || 0) / 3500) * 100)}%`;
  clanChestMarkers.forEach(m => {
    const c = (chest.chests || []).find(i => i.key === m.dataset.chest);
    m.classList.toggle("is-reached", Boolean(c && Number(clan.weeklyXp || 0) >= Number(c.xp) && Number(clan.membersCount || 0) >= Number(c.members)));
  });
  if (next) {
    const parts = [];
    if (chest.missingXp) parts.push(`${chest.missingXp} XP`);
    if (chest.missingMembers) parts.push(`${chest.missingMembers} уч.`);
    clanChestNoteNode.textContent = parts.length ? `До ${next.title}: ${parts.join(" и ")}.` : `Достигнут ${next.title}.`;
  } else clanChestNoteNode.textContent = "Копите XP.";
}

function renderClanContribution(clan) {
  const daily = clan.dailyGoal || {}; const me = clan.me || {};
  clanDailyGoalNode.textContent = `${Math.min(Number(daily.checked || 0), Number(daily.target || 3))}/${daily.target || 3}`;
  clanCheckinButton.disabled = Boolean(clan.checkedToday);
  clanCheckinButton.textContent = clan.checkedToday ? "Готово" : "Отметиться";
  clanCheckinStatus.textContent = clan.checkedToday ? "Уже отмечен." : `+10 XP. Цель: ${daily.target || 3} уч. = +${daily.reward || 50} XP.`;
  clanMyRoleNode.textContent = me.role === "leader" ? "Лидер" : "Участник";
  clanMyWeeklyNode.textContent = formatXp(me.weeklyXp);
  clanMyTotalNode.textContent = formatXp(me.totalXp);
  clanMyCheckinsNode.textContent = String(me.checkins || 0);
  clanMyActiveNode.textContent = me.isChestActive ? "Активен" : `+${me.needsForChest || 50} XP`;
}

function renderClanMembers(members) {
  if (!members.length) { clanMembersList.innerHTML = "<li>Пока нет</li>"; return; }
  clanMembersList.innerHTML = members.map((m, i) =>
    `<li><strong>${i + 1}. ${escapeHtml(m.name)}</strong><span>${formatXp(m.weeklyXp)} · ${m.checkins || 0} check-in</span></li>`
  ).join("");
}

function renderPublicClans(clans, canJoin) {
  if (!clans.length) { publicClansList.innerHTML = "<p class=\"panel-note\">Публичных кланов нет.</p>"; return; }
  publicClansList.innerHTML = clans.map(c => {
    const full = Number(c.membersCount || 0) >= Number(c.level?.slots || 5);
    const dis = !canJoin || full ? "disabled" : "";
    const txt = !canJoin ? "С Rookie" : full ? "Нет мест" : "Вступить";
    return `<article class="public-clan-card"><div><strong>${escapeHtml(c.name)}</strong><span>LVL ${c.level?.level || 1} · ${c.membersCount || 0}/${c.level?.slots || 5} · ${formatXp(c.weeklyXp)}</span></div><button type="button" data-clan-id="${c.id}" ${dis}>${txt}</button></article>`;
  }).join("");
}

function renderClanTop(items) {
  if (!items.length) { clanTopList.innerHTML = "<li>Пока нет</li>"; return; }
  clanTopList.innerHTML = items.map((c, i) =>
    `<li><strong>${i + 1}. ${escapeHtml(c.name)}<small>LVL ${c.level?.level || 1} · ${c.membersCount || 0} уч.</small></strong><span>${formatXp(c.periodXp || c.weeklyXp)}</span></li>`
  ).join("");
}

function renderLeague(data) {
  state.league = data || {};
  const user = state.league.user || {};
  leagueRoleNode.textContent = user.isAdmin ? "Админ" : user.role === "captain" ? "Капитан" : "Игрок";
  leagueXpNode.textContent = `${Number(user.xp || 0)} XP`;
  leagueRegisterFaceit.value = user.faceitNickname || "";
  document.body.classList.toggle("has-league-admin", Boolean(user.isAdmin));
  if (user.faceitHubUrl) { faceitHubBanner.hidden = false; faceitHubLink.href = user.faceitHubUrl; }
  else faceitHubBanner.hidden = true;
  renderLeagueNextStep(user, state.league.myTeams || []);
  renderLeagueJoinAccess(user);
  renderLeagueSeasons(state.league.seasons || []);
  renderLeagueMyTeam(state.league.myTeams || []);
  renderLeagueTeams(state.league.teams || []);
  renderLeagueStandings();
  renderLeaguePending(state.league.pendingTeams || [], Boolean(user.isAdmin));
  selectSeriesFormat(state.selectedLeagueFormat);
  syncLeagueTeamFormat();
}

function renderLeagueNextStep(user, teams) {
  const hasFaceit = Boolean((user.faceitNickname || "").trim());
  const hasTeam = Boolean(teams.length);
  if (!hasFaceit) {
    leagueNextTitle.textContent = "Укажи FACEIT nickname";
    leagueNextNote.textContent = "Матчи турнира проходят через FACEIT Hub.";
    leagueNextButton.textContent = "Указать"; leagueNextButton.dataset.target = "register"; return;
  }
  if (!hasTeam) {
    leagueNextTitle.textContent = "Вступи или создай команду";
    leagueNextNote.textContent = "Есть код капитана? Введи его. Хочешь собрать состав — создай заявку.";
    leagueNextButton.textContent = "Открыть заявку"; leagueNextButton.dataset.target = "register"; return;
  }
  leagueNextTitle.textContent = "Команда готова";
  leagueNextNote.textContent = "Проверь состав, пригласи игроков или смотри таблицу.";
  leagueNextButton.textContent = "Таблица"; leagueNextButton.dataset.target = "table";
}

function renderLeagueJoinAccess(user) {
  const hasFaceit = Boolean((user.faceitNickname || "").trim());
  leagueJoinForm.hidden = !hasFaceit;
  leagueJoinNote.textContent = hasFaceit ? "Введи код капитана." : "Сначала укажи FACEIT nickname.";
}

function showLeagueSection(name) {
  leagueTabs.forEach(b => b.classList.toggle("is-current", b.dataset.leagueSection === name));
  leagueSections.forEach(s => s.classList.toggle("is-active", s.id === `league-${name}-section`));
}

function selectSeriesFormat(format) {
  state.selectedLeagueFormat = format === "2x2" ? "2x2" : "5x5";
  leagueTeamFormat.value = state.selectedLeagueFormat;
  const isDuo = state.selectedLeagueFormat === "2x2";
  seriesSelectedTitle.textContent = isDuo ? "Duo Strike" : "Full Squad Challenge";
  seriesSelectedBadge.textContent = isDuo ? "⚡ 2×2" : "🛡️ 5×5";
  document.body.classList.toggle("series-duo", isDuo);
  syncLeagueTeamFormat();
}

function openSeriesRegistration(format) { selectSeriesFormat(format); showLeagueSection("register"); }

function leagueStatusLabel(s) {
  return { registration: "Набор", active: "Идёт", finished: "Завершён", pending: "На проверке", rejected: "Отклонена", played: "Сыгран" }[s] || s || "—";
}

function renderLeagueSeasons(seasons) {
  if (!seasons.length) { leagueSeasonsNode.innerHTML = "<span><strong>Скоро</strong></span>"; return; }
  leagueSeasonsNode.innerHTML = seasons.map(s =>
    `<span><strong>${escapeHtml(s.formatTitle || s.gameTitle)}</strong><small>${escapeHtml(leagueStatusLabel(s.status))}</small></span>`
  ).join("");
}

function renderLeagueMyTeam(teams) {
  if (!teams.length) { leagueMyTeamNode.innerHTML = "<p class=\"panel-note\">Нет команды.</p>"; return; }
  leagueMyTeamNode.innerHTML = teams.map(team => {
    const full = (team.members?.length || 0) >= Number(team.maxMembers || 99);
    return `<article class="league-row league-team-row"><div><strong>${escapeHtml(team.name)}</strong><span>${escapeHtml(team.formatTitle || team.gameTitle)} · ${escapeHtml(leagueStatusLabel(team.status))} · ${team.members?.length || 0}/${team.maxMembers || "?"}</span></div><button class="league-invite-button" type="button" data-team-id="${team.id}" ${full ? "disabled" : ""}>${full ? "Заполнено" : "Пригласить"}</button></article>`;
  }).join("");
}

function renderLeagueTeams(teams) {
  if (!teams.length) { leagueTeamsList.innerHTML = "<p class=\"panel-note\">Команд нет.</p>"; return; }
  leagueTeamsList.innerHTML = teams.map(t =>
    `<article class="league-row"><div><strong>${escapeHtml(t.name)}</strong><span>${escapeHtml(t.formatTitle || t.gameTitle)} · ${escapeHtml(leagueStatusLabel(t.status))}</span></div><small>${t.members?.length || 0}</small></article>`
  ).join("");
}

function renderLeagueStandings() {
  const tabs = state.league?.standingTabs || [];
  if (!tabs.length) { leagueStandingsTabs.innerHTML = ""; leagueStandingsMeta.innerHTML = ""; leagueStandingsList.innerHTML = ""; return; }
  if (!state.leagueStandingTab || !tabs.some(t => t.key === state.leagueStandingTab)) state.leagueStandingTab = state.league?.defaultStandingTab || tabs[0].key;
  leagueStandingsTabs.innerHTML = tabs.map(t =>
    `<button type="button" data-standing-tab="${escapeHtml(t.key)}" class="${t.key === state.leagueStandingTab ? "is-current" : ""}">${escapeHtml(t.title)}</button>`
  ).join("");
  const active = tabs.find(t => t.key === state.leagueStandingTab) || tabs[0];
  const season = active.season;
  if (!season) { leagueStandingsMeta.innerHTML = ""; leagueStandingsList.innerHTML = ""; return; }
  leagueStandingsMeta.innerHTML = `<strong>${escapeHtml(season.name || active.title)}</strong><span>${escapeHtml(leagueStatusLabel(season.status))} · команд: ${season.teamsRegistered || 0}</span>`;
  const items = active.standings || [];
  if (!items.length || season.status === "registration") { leagueStandingsList.innerHTML = `<li>🎮 Зарегистрировано: ${season.teamsRegistered || 0}</li>`; return; }
  leagueStandingsList.innerHTML = items.map(item => {
    const trend = item.trend === "new" ? "NEW" : item.trend === "0" ? "—" : Number(item.trend || 0) > 0 ? `▲${item.trend}` : `▼${Math.abs(Number(item.trend))}`;
    return `<li class="${item.isCurrentUserTeam ? "is-current-team" : ""}"><strong>${item.place}. ${escapeHtml(item.name)}<small>${trend} · И ${item.played} В ${item.wins} П ${item.losses}</small></strong><span>${item.points}</span></li>`;
  }).join("");
}

function renderLeaguePending(items, isAdmin) {
  leagueAdminPanel.hidden = !isAdmin; leagueAdminEmpty.hidden = isAdmin;
  if (!isAdmin) return;
  if (!items.length) { leaguePendingList.innerHTML = "<p class=\"panel-note\">Нет заявок.</p>"; return; }
  leaguePendingList.innerHTML = items.map(t =>
    `<article class="league-row league-admin-row"><div><strong>${escapeHtml(t.name)}</strong><span>${escapeHtml(t.formatTitle || t.gameTitle)} · ${escapeHtml(t.captainName || "-")}</span></div><div class="league-admin-actions"><button type="button" data-team-id="${t.id}" data-status="active">Принять</button><button type="button" data-team-id="${t.id}" data-status="rejected">Отклонить</button></div></article>`
  ).join("");
}

async function leagueRegister() {
  leagueRegisterButton.disabled = true;
  const faceitNick = leagueRegisterFaceit.value.trim();
  if (faceitNick) {
    faceitVerifyStatus.textContent = "Проверяем FACEIT...";
    try {
      const r = await api(`/api/faceit/verify?nickname=${encodeURIComponent(faceitNick)}`);
      if (!r.ok) { faceitVerifyStatus.textContent = `❌ Ник «${faceitNick}» не найден`; leagueRegisterButton.disabled = false; return; }
      faceitVerifyStatus.textContent = `✅ ${r.player.nickname} · Level ${r.player.skillLevel} · ELO ${r.player.faceitElo}`;
    } catch { faceitVerifyStatus.textContent = "⚠️ Не удалось проверить"; }
  } else faceitVerifyStatus.textContent = "";
  try {
    const result = await postApi("/api/league/register", { game: "cs2", nick: faceitNick, faceitNick });
    renderLeague(result.league || {}); setStatus("Данные сохранены.");
  } catch { setStatus("Не удалось сохранить."); }
  finally { leagueRegisterButton.disabled = false; }
}

async function leagueCreateTeam() {
  leagueCreateTeamButton.disabled = true;
  try {
    const result = await postApi("/api/league/team", { game: "cs2", format: leagueTeamFormat.value, name: leagueTeamName.value.trim() });
    leagueTeamName.value = ""; renderLeague(result.league || {}); setStatus("Заявка отправлена.");
  } catch { setStatus("Не удалось."); }
  finally { syncLeagueTeamFormat(); }
}

function syncLeagueTeamFormat() {
  leagueTeamFormatWrap.hidden = false;
  leagueCreateTeamButton.disabled = !leagueTeamFormat.value;
}

async function leagueUpdateTeam(teamId, status) {
  try {
    const result = await postApi("/api/league/team/status", { teamId, status });
    renderLeague(result.league || {}); setStatus(status === "active" ? "Принята." : "Отклонена.");
  } catch { setStatus("Не удалось."); }
}

function openLeagueInvite(teamId) {
  const team = (state.league?.myTeams || []).find(t => Number(t.id) === Number(teamId));
  if (!team) return;
  leagueInviteCodeNode.textContent = team.inviteToken;
  leagueCopyCodeButton.textContent = "Скопировать";
  leagueInviteSheet.hidden = false;
}
function closeLeagueInvite() { leagueInviteSheet.hidden = true; }
async function copyLeagueInviteCode() {
  await navigator.clipboard.writeText(leagueInviteCodeNode.textContent.trim());
  leagueCopyCodeButton.textContent = "Скопировано ✓";
  setTimeout(() => { leagueCopyCodeButton.textContent = "Скопировать"; }, 2000);
}
function shareLeagueInviteCode() {
  const code = leagueInviteCodeNode.textContent.trim();
  const msg = `Вступай в команду HardPoint Series!\nКод: ${code}`;
  const url = `https://t.me/share/url?url=&text=${encodeURIComponent(msg)}`;
  if (tg?.openTelegramLink) tg.openTelegramLink(url); else window.open(url, "_blank");
}

async function leagueJoinTeam() {
  leagueJoinButton.disabled = true; leagueJoinButton.textContent = "Проверяем...";
  try {
    const result = await postApi("/api/league/team/join", { invite_code: leagueJoinCodeInput.value.trim() });
    leagueJoinCodeInput.value = ""; renderLeague(result.league || {});
    setStatus(`Ты в команде ${result.team?.name || ""}!`); showLeagueSection("overview");
  } catch (err) { leagueJoinNote.textContent = errorMessage(err, "Не удалось."); }
  finally { leagueJoinButton.disabled = false; leagueJoinButton.textContent = "Вступить"; }
}

// ── LOAD ──
async function load() {
  try {
    tg?.ready(); tg?.expand();
    const [me, weeklyTop, allTimeTop, clans, league] = await Promise.all([
      api("/api/me"), api("/api/weekly-top"), api("/api/all-time-top"), api("/api/clans"), api("/api/league")
    ]);
    state.inviteLink = me.inviteLink;
    state.weeklyTop = weeklyTop.top;
    state.allTimeTop = allTimeTop.top;
    inviteLinkNode.textContent = me.inviteLink;
    weeklyCountNode.textContent = me.weeklyInvitedCount;
    allTimeCountNode.textContent = me.allTimeInvitedCount;
    clubLoginInput.value = me.user.clubLogin || "";
    const displayName = me.user.username ? `@${me.user.username}` : (me.user.name || "Игрок");
    homeUsernameNode.textContent = displayName;
    homeAvatarButton.textContent = initialsFor(me.user.name || me.user.username || "HP");
    renderRank(me.user); renderMissions(me.missions || {}); renderClans(clans); renderLeague(league);
    showWeeklyTop();
  } catch {
    inviteLinkNode.textContent = "Откройте из Telegram.";
    weeklyCountNode.textContent = "0"; allTimeCountNode.textContent = "0";
    homeUsernameNode.textContent = "@hardpoint"; homeAvatarButton.textContent = "HP";
    renderRank({ progress: {}, rank: {} }); renderMissions({}); renderClans({}); renderLeague({}); renderTop([]);
    setStatus("Откройте из Telegram.");
  }
}

async function refreshClans() { const c = await api("/api/clans"); renderClans(c); return c; }

async function claimMission(mission) {
  const buttons = { daily: dailyRewardButton, visit: visitRewardButton, instagram: instagramRewardButton, discord: discordRewardButton };
  const button = buttons[mission]; button.disabled = true;
  try {
    const result = await postApi("/api/missions/claim", { mission });
    renderMissions(result.missions || {}); renderRank(result.user || {});
    tg?.HapticFeedback?.notificationOccurred("success");
    setStatus(result.message || `+${result.totalAwardedCoins || 0} HP Coins.`);
  } catch {
    tg?.HapticFeedback?.notificationOccurred("error"); setStatus("Недоступно.");
  } finally {
    if (!["Забрано", "Получено", "На проверке"].includes(button.textContent)) button.disabled = false;
  }
}

function activateTab(active) {
  [weeklyTab, allTimeTab].forEach(b => {
    const on = b === active;
    b.classList.toggle("is-active", on);
    b.setAttribute("aria-selected", String(on));
    b.style.color = on ? "#171714" : "var(--muted)";
    b.style.background = on ? "var(--yellow)" : "transparent";
  });
}
function showWeeklyTop() { activateTab(weeklyTab); topTitleNode.textContent = "Топ недели"; renderTop(state.weeklyTop); }
function showAllTimeTop() { activateTab(allTimeTab); topTitleNode.textContent = "Топ за всё время"; renderTop(state.allTimeTop); }

function activateClanTab(active) {
  [clanWeeklyTab, clanMonthlyTab].forEach(b => {
    const on = b === active; b.classList.toggle("is-active", on);
    b.setAttribute("aria-selected", String(on));
    b.style.color = on ? "#171714" : "var(--muted)";
    b.style.background = on ? "var(--yellow)" : "transparent";
  });
}
function showClanWeeklyTop() { activateClanTab(clanWeeklyTab); clanTopTitleNode.textContent = "Топ недели"; renderClanTop(state.clanWeeklyTop); }
function showClanMonthlyTop() { activateClanTab(clanMonthlyTab); clanTopTitleNode.textContent = "Топ месяца"; renderClanTop(state.clanMonthlyTop); }

async function createClan() {
  createClanButton.disabled = true;
  try { await postApi("/api/clans/create", { name: newClanNameInput.value.trim(), isPublic: newClanPublicInput.checked }); newClanNameInput.value = ""; await refreshClans(); setStatus("Клан создан."); }
  catch { setStatus("Не удалось."); }
  finally { createClanButton.disabled = !(state.clans?.access?.canCreate); }
}
async function joinClan(payload) {
  joinClanCodeButton.disabled = true;
  try { await postApi("/api/clans/join", payload); await refreshClans(); setStatus("Ты в клане."); }
  catch { setStatus("Не удалось."); }
  finally { joinClanCodeButton.disabled = !(state.clans?.access?.canJoin); }
}
async function clanCheckIn() {
  clanCheckinButton.disabled = true;
  try { const r = await postApi("/api/clans/check-in", {}); await refreshClans(); setStatus(r.message || "Отметка."); }
  catch { setStatus("Уже отметился."); }
}

// ── EVENTS ──
copyButton.addEventListener("click", async () => {
  if (!state.inviteLink) return;
  await navigator.clipboard.writeText(state.inviteLink);
  tg?.HapticFeedback?.notificationOccurred("success"); setStatus("Ссылка скопирована.");
});
shareButton.addEventListener("click", () => {
  if (!state.inviteLink) return;
  tg?.openTelegramLink(`https://t.me/share/url?url=${encodeURIComponent(state.inviteLink)}&text=${encodeURIComponent("Заходи в HardPoint")}`);
});
saveLoginButton.addEventListener("click", async () => {
  saveLoginButton.disabled = true;
  try { const r = await postApi("/api/club-login", { clubLogin: clubLoginInput.value.trim() }); clubLoginInput.value = r.clubLogin || ""; setStatus("Логин сохранён."); }
  catch { setStatus("Не удалось."); }
  finally { saveLoginButton.disabled = false; }
});

navHome.addEventListener("click", () => showView(homeView));
navSeries.addEventListener("click", () => showView(leagueView));
navLive.addEventListener("click", () => showView(liveView));
navEsport.addEventListener("click", () => showView(esportView));

backButton.addEventListener("click", goBack);
profileMenuButton.addEventListener("click", toggleProfileDropdown);
homeAvatarButton.addEventListener("click", () => showView(profileView));
dropdownProfileButton.addEventListener("click", () => showView(profileView));
dropdownSettingsButton.addEventListener("click", () => showView(profileView));
profileMissionsButton.addEventListener("click", () => showView(missionsView));
profileClansButton.addEventListener("click", () => showView(clansView));
document.addEventListener("click", e => {
  if (!profileDropdown.contains(e.target) && !profileMenuButton.contains(e.target)) closeProfileDropdown();
});

homeMissionsCard.addEventListener("click", () => showView(missionsView));
homeSeriesCard.addEventListener("click", () => showView(leagueView));
homeClansCard.addEventListener("click", () => showView(clansView));
homeLiveCard.addEventListener("click", () => showView(liveView));

weeklyTab.addEventListener("click", showWeeklyTop);
allTimeTab.addEventListener("click", showAllTimeTop);
clanWeeklyTab.addEventListener("click", showClanWeeklyTop);
clanMonthlyTab.addEventListener("click", showClanMonthlyTop);
liveTab5x5.addEventListener("click", () => switchLiveFormat("5x5"));
liveTab2x2.addEventListener("click", () => switchLiveFormat("2x2"));

leagueTabs.forEach(b => b.addEventListener("click", () => showLeagueSection(b.dataset.leagueSection)));
leagueNextButton.addEventListener("click", () => showLeagueSection(leagueNextButton.dataset.target || "register"));
leagueActionJoin.addEventListener("click", () => showLeagueSection("register"));
leagueActionCreate.addEventListener("click", () => showLeagueSection("register"));
leagueActionTable.addEventListener("click", () => showLeagueSection("table"));
seriesFormatButtons.forEach(b => b.addEventListener("click", () => openSeriesRegistration(b.dataset.seriesFormat)));
seriesBackToFormats.addEventListener("click", () => showLeagueSection("overview"));
leagueRegisterButton.addEventListener("click", leagueRegister);
leagueJoinCodeInput.addEventListener("input", () => { leagueJoinCodeInput.value = leagueJoinCodeInput.value.toUpperCase(); });
leagueJoinButton.addEventListener("click", leagueJoinTeam);
leagueTeamFormat.addEventListener("change", syncLeagueTeamFormat);
leagueCreateTeamButton.addEventListener("click", leagueCreateTeam);
leagueStandingsTabs.addEventListener("click", e => {
  const b = e.target.closest("button[data-standing-tab]"); if (!b) return;
  state.leagueStandingTab = b.dataset.standingTab; renderLeagueStandings();
});
leagueMyTeamNode.addEventListener("click", e => {
  const b = e.target.closest("button[data-team-id]"); if (!b) return;
  openLeagueInvite(Number(b.dataset.teamId));
});
leagueInviteClose.addEventListener("click", closeLeagueInvite);
leagueInviteSheet.addEventListener("click", e => { if (e.target === leagueInviteSheet) closeLeagueInvite(); });
leagueCopyCodeButton.addEventListener("click", copyLeagueInviteCode);
leagueShareCodeButton.addEventListener("click", shareLeagueInviteCode);
leaguePendingList.addEventListener("click", e => {
  const b = e.target.closest("button[data-team-id]"); if (!b) return;
  leagueUpdateTeam(Number(b.dataset.teamId), b.dataset.status);
});

createClanButton.addEventListener("click", createClan);
joinClanCodeButton.addEventListener("click", () => joinClan({ code: joinClanCodeInput.value.trim() }));
clanCheckinButton.addEventListener("click", clanCheckIn);
copyClanCodeButton.addEventListener("click", async () => { await navigator.clipboard.writeText(clanCodeNode.textContent.trim()); setStatus("Код скопирован."); });
publicClansList.addEventListener("click", e => {
  const b = e.target.closest("button[data-clan-id]"); if (!b) return;
  joinClan({ clanId: Number(b.dataset.clanId) });
});

dailyRewardButton.addEventListener("click", () => claimMission("daily"));
visitRewardButton.addEventListener("click", () => claimMission("visit"));
instagramRewardButton.addEventListener("click", () => claimMission("instagram"));
discordRewardButton.addEventListener("click", () => claimMission("discord"));

teamFinalsButton.addEventListener("click", () => {
  const open = !teamFinalsPanel.classList.contains("is-open");
  teamFinalsPanel.classList.toggle("is-open", open);
  teamFinalsPanel.setAttribute("aria-hidden", String(!open));
  teamFinalsButton.classList.toggle("is-active", open);
  teamFinalsButton.setAttribute("aria-expanded", String(open));
});
namaIconButton.addEventListener("click", () => {
  const open = !namaProfilePanel.classList.contains("is-open");
  namaProfilePanel.classList.toggle("is-open", open);
  namaProfilePanel.setAttribute("aria-hidden", String(!open));
  namaIconButton.classList.toggle("is-active", open);
  namaIconButton.setAttribute("aria-expanded", String(open));
});

// ── CANVAS ──
const canvas = document.querySelector("#arena");
const context = canvas.getContext("2d");
let width = 0, height = 0, points = [];
function resize() {
  const ratio = window.devicePixelRatio || 1;
  width = window.innerWidth; height = window.innerHeight;
  canvas.width = Math.floor(width * ratio); canvas.height = Math.floor(height * ratio);
  canvas.style.width = `${width}px`; canvas.style.height = `${height}px`;
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  points = Array.from({ length: 34 }, () => ({ x: Math.random() * width, y: Math.random() * height, vx: (Math.random() - .5) * .28, vy: (Math.random() - .5) * .28 }));
}
function draw() {
  context.clearRect(0, 0, width, height);
  context.strokeStyle = "rgba(255,221,61,0.12)"; context.lineWidth = 1;
  points.forEach((p, i) => {
    p.x += p.vx; p.y += p.vy;
    if (p.x < 0 || p.x > width) p.vx *= -1;
    if (p.y < 0 || p.y > height) p.vy *= -1;
    for (let j = i + 1; j < points.length; j++) {
      const o = points[j]; const d = Math.hypot(p.x - o.x, p.y - o.y);
      if (d < 115) { context.globalAlpha = 1 - d / 115; context.beginPath(); context.moveTo(p.x, p.y); context.lineTo(o.x, o.y); context.stroke(); }
    }
  });
  context.globalAlpha = 1; requestAnimationFrame(draw);
}
window.addEventListener("resize", resize);
resize(); draw(); load();
