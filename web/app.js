const tg = window.Telegram?.WebApp;
const state = {
  league: null,
  activeView: null,
  previousView: null,
  leagueStandingTab: "",
  selectedLeagueFormat: "5x5",
  liveFmt: "5x5",
  liveRefreshTimer: null,
  myLeagueTeamIds: [],
  liveViewer: { isAdmin: false, captainTeamIds: [] },
  lastInGroup: {},
  myTgId: null,
};

const homeUsernameNode = document.querySelector("#home-username");
const homeSeriesCard = document.querySelector("#home-series-card");
const homeLiveCard = document.querySelector("#home-live-card");
const statusNode = document.querySelector("#status");
const clubLoginInput = document.querySelector("#club-login");
const saveLoginButton = document.querySelector("#save-login-button");
const homeView = document.querySelector("#home-view");
const leagueView = document.querySelector("#league-view");
const liveView = document.querySelector("#live-view");
const clubView = document.querySelector("#club-view");
const navClub = document.querySelector("#nav-club");
const homeClubCard = document.querySelector("#home-club-card");
const liveContent = document.querySelector("#live-content");
const liveTab5x5 = document.querySelector("#live-tab-5x5");
const liveTab2x2 = document.querySelector("#live-tab-2x2");
const navHome = document.querySelector("#nav-home");
const navSeries = document.querySelector("#nav-series");
const subnav = document.querySelector("#subnav");
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
const leagueJoinCodeInput = document.querySelector("#league-join-code");
const leagueJoinButton = document.querySelector("#league-join-button");
const leagueJoinNote = document.querySelector("#league-join-note");
const leagueTeamName = document.querySelector("#league-team-name");
const leagueCreateTeamButton = document.querySelector("#league-create-team-button");
const leagueInviteSheet = document.querySelector("#league-invite-sheet");
const leagueInviteClose = document.querySelector("#league-invite-close");
const leagueInviteCodeNode = document.querySelector("#league-invite-code");
const leagueCopyCodeButton = document.querySelector("#league-copy-code-button");
const leagueShareCodeButton = document.querySelector("#league-share-code-button");
const seriesFormatButtons = document.querySelectorAll("[data-series-format]");
const faceitHubBanner = document.querySelector("#faceit-hub-banner");
const faceitHubLink = document.querySelector("#faceit-hub-link");

const ALL_VIEWS = [homeView, clubView, leagueView, liveView];
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
  const text = String(error?.message || "");
  try { return JSON.parse(text).message || fallback; } catch { /* not JSON */ }
  const m = text.match(/^\d{3}: (.+)$/s);
  return m && !/^(Bad Request|Internal Server Error)$/.test(m[1].trim()) ? m[1].trim() : fallback;
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
  ALL_VIEWS.forEach(v => v && v.classList.toggle("is-active", v === view));
  const group = groupOf(view);
  state.lastInGroup[group.key] = view;
  document.body.dataset.section = group.key;
  document.querySelectorAll(".bottom-nav .nav-btn").forEach(b => b.classList.toggle("is-current", b.dataset.group === group.key));
  renderSubnav(group, view);
  window.scrollTo({ top: 0 });
  if (view === liveView) loadLiveBracket();
  else stopLiveRefresh();
}
// ── NAV GROUPS: 4 bottom tabs, sub-tabs inside Турниры and Профиль ──
const NAV_GROUPS = [
  { key: "home", views: [[homeView, "Главная"]] },
  { key: "club", views: [[clubView, "Клуб"]] },
  { key: "tournaments", views: [[leagueView, "Турнир", "overview"], [leagueView, "Регистрация", "register"], [liveView, "Сетка LIVE"], [leagueView, "Таблица", "table"], [leagueView, "Админ", "admin", "admin"]] },
];
function groupOf(view) { return NAV_GROUPS.find(g => g.views.some(([v]) => v === view)) || NAV_GROUPS[0]; }
function renderSubnav(group, active) {
  if (!subnav) return;
  if (group.views.length < 2) { subnav.hidden = true; subnav.innerHTML = ""; return; }
  subnav.hidden = false;
  const isAdmin = document.body.classList.contains("has-league-admin");
  subnav.innerHTML = group.views.map(([v, label, sec, only], i) => {
    if (only === "admin" && !isAdmin) return "";
    const current = v === active && (!sec || sec === (state.leagueSection || "overview"));
    return `<button type="button" class="subnav-btn${current ? " is-current" : ""}" data-subview="${i}">${label}</button>`;
  }).join("");
  subnav.querySelector(".is-current")?.scrollIntoView({ block: "nearest", inline: "center" });
  subnav.onclick = e => {
    const b = e.target.closest("[data-subview]"); if (!b) return;
    const [v, , sec] = group.views[Number(b.dataset.subview)];
    if (sec) state.leagueSection = sec;
    showView(v);
    if (sec) showLeagueSection(sec);
    tg?.HapticFeedback?.selectionChanged();
  };
}
function openGroup(key) {
  const group = NAV_GROUPS.find(g => g.key === key);
  showView(state.lastInGroup[key] || group.views[0][0]);
}

// Bot buttons open the app with ?view=series / ?view=live etc.
function initialViewFromLocation() {
  const params = new URLSearchParams(window.location.search);
  const view = String(params.get("view") || tg?.initDataUnsafe?.start_param || "").toLowerCase();
  const map = { club: clubView, prices: clubView, series: leagueView, league: leagueView, live: liveView };
  return map[view] || null;
}
function showInitialView() {
  const view = initialViewFromLocation();
  if (view) showView(view, { skipHistory: true });
}

// ── CLUB (prices, hours, contacts) ──
const clubState = { data: null, tab: 0 };
function openExternal(url) {
  if (!url) return;
  if (/^https:\/\/t\.me\//.test(url) && tg?.openTelegramLink) tg.openTelegramLink(url);
  else if (tg?.openLink) tg.openLink(url);
  else window.open(url, "_blank", "noopener");
}
function clubStatusText(status) {
  if (!status || !status.known) return { open: false, title: "Клуб HardPoint", sub: "Цены, часы работы, адрес" };
  if (status.openNow) return { open: true, title: `Открыто до ${status.closesAt}`, sub: "Цены, часы работы, адрес" };
  if (status.opensAt) return { open: false, title: `Откроемся в ${status.opensAt}`, sub: `Сегодня ${status.today}` };
  return { open: false, title: "Сейчас закрыто", sub: status.today ? `Сегодня ${status.today}` : "Цены, часы работы, адрес" };
}
function priceChips(price) {
  // "STD 45 zł · VIP 50 zł" -> two chips; plain "17 zł" -> one chip
  return String(price || "").split("·").map(p => p.trim()).filter(Boolean).map((part, i) => {
    const m = part.match(/^(STD|VIP)\s+(.+)$/i);
    const main = i === 0 ? " is-main" : "";
    return m ? `<span class="club-price${main}"><b>${escapeHtml(m[1].toUpperCase())}</b>${escapeHtml(m[2])}</span>`
             : `<span class="club-price${main}">${escapeHtml(part)}</span>`;
  }).join("") || `<span class="club-price">уточняйте</span>`;
}
function renderClubPrices() {
  const sections = clubState.data?.priceSections || [];
  const tabs = document.querySelector("#club-price-tabs");
  const list = document.querySelector("#club-price-list");
  if (!sections.length) { tabs.innerHTML = ""; list.innerHTML = `<p class="club-section-note">Цены скоро появятся</p>`; return; }
  if (clubState.tab >= sections.length) clubState.tab = 0;
  tabs.innerHTML = sections.map((s, i) => `<button class="club-tab${i === clubState.tab ? " is-active" : ""}" type="button" role="tab" data-club-tab="${i}">${escapeHtml(s.title)}</button>`).join("");
  const section = sections[clubState.tab];
  list.innerHTML = (section.note ? `<p class="club-section-note">${escapeHtml(section.note)}</p>` : "") +
    section.items.map(item => `<div class="club-price-row"><span>${escapeHtml(item.title)}${item.note ? `<small>${escapeHtml(item.note)}</small>` : ""}</span><span class="club-price-values">${priceChips(item.unit ? `${item.price}/${item.unit === "час" ? "ч" : item.unit}` : item.price)}</span></div>`).join("");
}
function renderClub(data) {
  clubState.data = data;
  const st = clubStatusText(data.status);
  const dot = document.querySelector("#home-club-status");
  dot?.classList.toggle("is-open", st.open);
  document.querySelector("#home-club-title").textContent = st.title;
  document.querySelector("#home-club-sub").textContent = st.sub;
  document.querySelector("#club-name").textContent = data.name || "HardPoint";
  document.querySelector("#club-tagline").textContent = data.tagline || "";
  const badge = document.querySelector("#club-open-badge");
  badge.textContent = data.status?.known ? (data.status.openNow ? "● Открыто" : "Закрыто") : "";
  badge.classList.toggle("is-open", Boolean(data.status?.openNow));
  document.querySelector("#club-promos").innerHTML = (data.promos || []).map(p => `<div class="club-promo">${escapeHtml(p)}</div>`).join("");
  const homePromos = document.querySelector("#home-promos");
  if (homePromos) {
    homePromos.innerHTML = (data.promos || []).map(p => `<button class="home-row" type="button" data-color="peach" data-go-club><span class="home-row-icon"><svg viewBox="0 0 24 24"><path d="M20 12 12 20 4 12V4h8z"/><circle cx="8.5" cy="8.5" r="1.5"/></svg></span><span class="home-row-text"><strong>${escapeHtml(p.includes(": ") ? p.slice(0, p.indexOf(": ")) : p)}</strong><small>${escapeHtml(p.includes(": ") ? p.slice(p.indexOf(": ") + 2) : "Подробнее в разделе Клуб")}</small></span><span class="home-row-arrow" aria-hidden="true">›</span></button>`).join("");
    homePromos.hidden = !(data.promos || []).length;
    document.querySelector("#home-promos-label").hidden = homePromos.hidden;
    homePromos.onclick = e => { if (e.target.closest("[data-go-club]")) showView(clubView); };
  }
  renderClubPrices();
  document.querySelector("#club-hours").innerHTML = (data.hours || []).map(h => {
    const today = Array.isArray(h.weekdays) && h.weekdays.includes(data.today);
    return `<div class="club-hours-row${today ? " is-today" : ""}"><span>${escapeHtml(h.days)}${today ? " · сегодня" : ""}</span><strong>${escapeHtml(h.time)}</strong></div>`;
  }).join("") + (data.hoursNote ? `<p class="club-section-note">${escapeHtml(data.hoursNote)}</p>` : "");
  const contacts = [];
  if (data.address) contacts.push(`<span>📍 ${escapeHtml(data.address)}</span>`);
  if (data.phone) contacts.push(`<a class="club-phone" href="tel:${escapeHtml(data.phone.replace(/\s+/g, ""))}">☎️ ${escapeHtml(data.phone)}</a>`);
  document.querySelector("#club-contacts").innerHTML = contacts.join("");
  const actions = [];
  if (data.bookingUrl) actions.push(["📅 Забронировать место", data.bookingUrl, true]);
  if (data.mapUrl) actions.push(["🗺 Как добраться", data.mapUrl, false]);
  if (data.instagram) actions.push(["Instagram", data.instagram, false]);
  if (data.discord) actions.push(["Discord", data.discord, false]);
  if (data.website) actions.push(["Сайт клуба", data.website, false]);
  document.querySelector("#club-actions").innerHTML = actions.map(([label, url, primary]) => `<button class="club-action${primary ? " is-primary" : ""}" type="button" data-club-link="${escapeHtml(url)}">${escapeHtml(label)}</button>`).join("");
}
async function loadClub() {
  try { renderClub(await api("/api/club")); }
  catch { const list = document.querySelector("#club-price-list"); if (list) list.innerHTML = `<p class="club-section-note">Не удалось загрузить цены</p>`; }
}
document.querySelector("#club-price-tabs")?.addEventListener("click", e => {
  const b = e.target.closest("[data-club-tab]"); if (!b) return;
  clubState.tab = Number(b.dataset.clubTab) || 0; renderClubPrices(); tg?.HapticFeedback?.selectionChanged();
});
document.querySelector("#club-actions")?.addEventListener("click", e => {
  const b = e.target.closest("[data-club-link]"); if (b) openExternal(b.dataset.clubLink);
});

// ── LIVE BRACKET ──
function roundLabel(rnd, total) {
  if (rnd === total) return "Финал";
  if (rnd === total - 1) return "1/2";
  if (rnd === total - 2) return "1/4";
  if (rnd === total - 3) return "1/8";
  return `Р${rnd}`;
}
function renderLiveBracket(data) {
  state.liveViewer = data.viewer || { isAdmin: false, captainTeamIds: [] };
  state.faceitHubUrl = data.faceitHubUrl || "";
  if (!data.bracket) {
    liveContent.innerHTML = `<div class="live-reg-state"><div class="live-reg-icon">📋</div><h3>Идёт регистрация</h3><p>Сетка будет сгенерирована в понедельник в 04:00</p><div class="live-reg-count">${data.registeredTeams || 0} команд зарегистрировано</div></div>`;
    return;
  }
  const b = data.bracket;
  const rounds = b.rounds || {};
  const roundNums = Object.keys(rounds).map(Number).sort((a, z) => a - z);
  const total = roundNums.length;
  let html = `<div class="live-stats-bar"><div><strong>${b.registeredTeams || 0}</strong><small>Команд</small></div><div><strong>${b.playedMatches || 0}/${b.totalMatches || 0}</strong><small>Матчей</small></div><div><strong>${total}</strong><small>Раундов</small></div></div>`;
  html += `<div class="live-bracket-scroll"><div class="live-bracket">`;
  roundNums.forEach(rnd => {
    html += `<div class="live-round"><div class="live-round-label">${roundLabel(rnd, total)}</div>`;
    (rounds[rnd] || []).forEach(m => { html += renderLiveMatch(m); });
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
  else if (m.status === "disputed") { barClass = "live-match-bar disputed"; barText = "Спор · решает админ"; }
  else if (m.status === "bye") { barClass = "live-match-bar bye"; barText = "BYE"; }
  const t1cls = w ? (w.id === t1?.id ? "winner" : "loser") : (t1 ? "" : "tbd");
  const t2cls = w ? (w.id === t2?.id ? "winner" : "loser") : (t2 ? "" : "tbd");
  const s1 = m.score1 != null ? m.score1 : "—";
  const s2 = m.score2 != null ? m.score2 : "—";
  let faceitBtn = "";
  if (["pending", "disputed"].includes(m.status) && t1 && t2) {
    const canEdit = Boolean(myCaptainTeamInMatch(m) || state.liveViewer.isAdmin);
    if (m.faceitMatchUrl) faceitBtn = `<button class="live-faceit-link" type="button" data-open-url="${escapeHtml(m.faceitMatchUrl)}">🔗 Открыть комнату FACEIT</button>`;
    else if (canEdit) faceitBtn = `<button class="live-faceit-btn" type="button" data-match-id="${m.id}">🎮 Комната FACEIT</button>`;
  }
  return `<div class="live-match" data-match-id="${m.id}"><div class="${barClass}">${barText}</div><div class="live-team ${t1cls}"><span>${escapeHtml(t1?.name || "TBD")}</span><b>${s1}</b></div><div class="live-divider"></div><div class="live-team ${t2cls}"><span>${escapeHtml(t2?.name || "TBD")}</span><b>${s2}</b></div>${faceitBtn}${renderScoreControls(m)}</div>`;
}
// Score: both captains must report the same result; admin can set it directly.
function myCaptainTeamInMatch(m) {
  const ids = state.liveViewer.captainTeamIds || [];
  if (m.team1?.id && ids.includes(m.team1.id)) return m.team1.id;
  if (m.team2?.id && ids.includes(m.team2.id)) return m.team2.id;
  return null;
}
function renderScoreControls(m) {
  if (!["pending", "disputed"].includes(m.status) || !m.team1 || !m.team2) return "";
  const myTeam = myCaptainTeamInMatch(m);
  const admin = Boolean(state.liveViewer.isAdmin);
  if (!myTeam && !admin) return "";
  const reported = (m.reportedTeamIds || []);
  let hint = "";
  if (myTeam && reported.includes(myTeam) && m.status === "pending") hint = `<p class="live-score-hint">✓ Ваш счёт отправлен · ждём соперника</p>`;
  const label = myTeam ? (reported.includes(myTeam) ? "✏️ Изменить счёт" : "📝 Внести счёт") : "🛡 Засчитать счёт (админ)";
  const adminExtra = myTeam && admin ? `<button class="live-score-btn is-admin" type="button" data-score-match="${m.id}" data-as-admin="1">🛡 Как админ</button>` : "";
  return `${hint}<div class="live-score-actions"><button class="live-score-btn" type="button" data-score-match="${m.id}" data-as-admin="${myTeam ? "" : "1"}">${label}</button>${adminExtra}</div>`;
}
function openScoreForm(btn) {
  const card = btn.closest(".live-match");
  const names = [...card.querySelectorAll(".live-team span")].map(n => n.textContent);
  card.querySelector(".live-score-form")?.remove();
  const form = document.createElement("form");
  form.className = "live-score-form";
  form.innerHTML = `<label><span>${escapeHtml(names[0] || "Команда 1")}</span><input type="number" inputmode="numeric" min="0" max="99" name="s1" required></label><label><span>${escapeHtml(names[1] || "Команда 2")}</span><input type="number" inputmode="numeric" min="0" max="99" name="s2" required></label><button type="submit">Отправить</button>`;
  form.addEventListener("submit", async e => {
    e.preventDefault();
    const submit = form.querySelector("button"); submit.disabled = true; submit.textContent = "...";
    try {
      const result = await postApi("/api/bracket/result", { matchId: Number(btn.dataset.scoreMatch), score1: Number(form.s1.value), score2: Number(form.s2.value), asAdmin: btn.dataset.asAdmin === "1" });
      tg?.HapticFeedback?.notificationOccurred("success");
      setStatus(result.message || "Готово.");
      loadLiveBracket();
    } catch (err) {
      tg?.HapticFeedback?.notificationOccurred("error");
      setStatus(errorMessage(err, "Не удалось отправить счёт."));
      submit.disabled = false; submit.textContent = "Отправить";
    }
  });
  card.appendChild(form);
  form.s1.focus();
}
function stopLiveRefresh() {
  if (state.liveRefreshTimer) { clearTimeout(state.liveRefreshTimer); state.liveRefreshTimer = null; }
}
async function loadLiveBracket() {
  stopLiveRefresh();
  liveContent.innerHTML = `<div class="live-loading">Загрузка...</div>`;
  try {
    const data = await fetch(`/api/bracket?format=${state.liveFmt}`, { headers: authHeaders() }).then(r => r.json());
    renderLiveBracket(data);
    if (data.bracket?.status === "active") state.liveRefreshTimer = setTimeout(loadLiveBracket, 30000);
  } catch { liveContent.innerHTML = `<div class="live-error">⚠️ Не удалось загрузить.</div>`; }
}
function switchLiveFormat(fmt) {
  state.liveFmt = fmt;
  liveTab5x5.classList.toggle("is-active", fmt === "5x5");
  liveTab2x2.classList.toggle("is-active", fmt === "2x2");
  loadLiveBracket();
}
// FACEIT room: created by hand in the Hub, then the link is saved so both teams see it.
function openFaceitRoomForm(btn) {
  const card = btn.closest(".live-match");
  card.querySelector(".live-score-form")?.remove();
  const form = document.createElement("form");
  form.className = "live-score-form";
  form.innerHTML = `${state.faceitHubUrl ? `<button type="button" class="live-faceit-hub" data-open-url="${escapeHtml(state.faceitHubUrl)}">1. Создать матч в Hub FACEIT ↗</button>` : ""}<input type="url" name="url" placeholder="2. Вставьте ссылку на комнату" required><button type="submit">Сохранить ссылку</button>`;
  form.addEventListener("submit", async e => {
    e.preventDefault();
    const submit = form.querySelector("button[type=submit]"); submit.disabled = true;
    try {
      const result = await postApi("/api/bracket/faceit-room", { matchId: Number(btn.dataset.matchId), url: form.url.value.trim() });
      tg?.HapticFeedback?.notificationOccurred("success"); setStatus(result.message || "Сохранено."); loadLiveBracket();
    } catch (err) { setStatus(errorMessage(err, "Не удалось сохранить ссылку.")); submit.disabled = false; }
  });
  card.appendChild(form);
}

// ── RENDER ──
function renderLeague(data) {
  state.league = data || {};
  const user = state.league.user || {};
  if (leagueRoleNode) leagueRoleNode.textContent = user.isAdmin ? "Админ" : user.role === "captain" ? "Капитан" : "Игрок";
  if (leagueXpNode) leagueXpNode.textContent = `${Number(user.xp || 0)} XP`;
  if (leagueRegisterFaceit) leagueRegisterFaceit.value = user.faceitNickname || "";
  document.body.classList.toggle("has-league-admin", Boolean(user.isAdmin));
  if (faceitHubBanner) { faceitHubBanner.hidden = !user.faceitHubUrl; if (user.faceitHubUrl && faceitHubLink) faceitHubLink.href = user.faceitHubUrl; }
  state.myLeagueTeamIds = (state.league.myTeams || []).filter(t => t.status === "active").map(t => Number(t.id));
  renderLeagueNextStep(user, state.league.myTeams || []);
  renderLeagueSeasons(state.league.seasons || []);
  renderLeagueMyTeam(state.league.myTeams || []);
  renderLeagueTeams(state.league.teams || []);
  renderLeagueStandings();
  renderLeaguePending(state.league.pendingTeams || [], Boolean(user.isAdmin));
  selectSeriesFormat(state.selectedLeagueFormat);
}
function renderLeagueNextStep(user, teams) {
  if (!leagueNextTitle) return;
  const hasFaceit = Boolean((user.faceitNickname || "").trim());
  const hasTeam = Boolean(teams.length);
  if (!hasFaceit) { leagueNextTitle.textContent = "Укажи FACEIT nickname"; leagueNextNote.textContent = "Матчи турнира проходят через FACEIT Hub."; leagueNextButton.textContent = "Указать"; leagueNextButton.dataset.target = "register"; return; }
  if (!hasTeam) { leagueNextTitle.textContent = "Вступи или создай команду"; leagueNextNote.textContent = "Есть код капитана? Введи его. Хочешь собрать состав — создай заявку."; leagueNextButton.textContent = "Открыть заявку"; leagueNextButton.dataset.target = "register"; return; }
  leagueNextTitle.textContent = "Команда готова"; leagueNextNote.textContent = "Проверь состав, пригласи игроков или смотри таблицу."; leagueNextButton.textContent = "Таблица"; leagueNextButton.dataset.target = "table";
}
function showLeagueSection(name) {
  const entering = name === "register" && document.querySelector("#league-register-section:not(.is-active)");
  state.leagueSection = name;
  leagueTabs.forEach(b => b.classList.toggle("is-current", b.dataset.leagueSection === name));
  leagueSections.forEach(s => s.classList.toggle("is-active", s.id === `league-${name}-section`));
  if (state.activeView === leagueView) renderSubnav(groupOf(leagueView), leagueView);
  if (entering) wizardStart();
}
function selectSeriesFormat(format) {
  state.selectedLeagueFormat = format === "2x2" ? "2x2" : "5x5";
  document.querySelectorAll(".wizard-format").forEach(b => b.classList.toggle("is-selected", b.dataset.format === state.selectedLeagueFormat));
}
function openSeriesRegistration(format) { selectSeriesFormat(format); showLeagueSection("register"); }
function leagueStatusLabel(s) {
  return { registration: "Набор", active: "Идёт", finished: "Завершён", pending: "На проверке", rejected: "Отклонена", played: "Сыгран" }[s] || s || "—";
}
function renderLeagueSeasons(seasons) {
  if (!leagueSeasonsNode) return;
  if (!seasons.length) { leagueSeasonsNode.innerHTML = "<span><strong>Скоро</strong></span>"; return; }
  leagueSeasonsNode.innerHTML = seasons.map(s => `<span><strong>${escapeHtml(s.formatTitle || s.gameTitle)}</strong><small>${escapeHtml(leagueStatusLabel(s.status))}</small></span>`).join("");
}
function renderLeagueMyTeam(teams) {
  if (!leagueMyTeamNode) return;
  if (!teams.length) { leagueMyTeamNode.innerHTML = "<p class=\"panel-note\">Нет команды.</p>"; return; }
  leagueMyTeamNode.innerHTML = teams.map(team => {
    const full = (team.members?.length || 0) >= Number(team.maxMembers || 99);
    return `<article class="league-row league-team-row"><div><strong>${escapeHtml(team.name)}</strong><span>${escapeHtml(team.formatTitle || team.gameTitle)} · ${escapeHtml(leagueStatusLabel(team.status))} · ${team.members?.length || 0}/${team.maxMembers || "?"}</span></div><button class="league-invite-button" type="button" data-team-id="${team.id}" ${full ? "disabled" : ""}>${full ? "Заполнено" : "Пригласить"}</button></article>`;
  }).join("");
}
function renderLeagueTeams(teams) {
  if (!leagueTeamsList) return;
  if (!teams.length) { leagueTeamsList.innerHTML = "<p class=\"panel-note\">Команд нет.</p>"; return; }
  leagueTeamsList.innerHTML = teams.map(t => `<article class="league-row"><div><strong>${escapeHtml(t.name)}</strong><span>${escapeHtml(t.formatTitle || t.gameTitle)} · ${escapeHtml(leagueStatusLabel(t.status))}</span></div><small>${t.members?.length || 0}</small></article>`).join("");
}
function renderLeagueStandings() {
  const tabs = state.league?.standingTabs || [];
  if (!tabs.length || !leagueStandingsTabs) return;
  if (!state.leagueStandingTab || !tabs.some(t => t.key === state.leagueStandingTab)) state.leagueStandingTab = state.league?.defaultStandingTab || tabs[0].key;
  leagueStandingsTabs.innerHTML = tabs.map(t => `<button type="button" data-standing-tab="${escapeHtml(t.key)}" class="${t.key === state.leagueStandingTab ? "is-current" : ""}">${escapeHtml(t.title)}</button>`).join("");
  const active = tabs.find(t => t.key === state.leagueStandingTab) || tabs[0];
  const season = active.season;
  if (!season) { if (leagueStandingsMeta) leagueStandingsMeta.innerHTML = ""; if (leagueStandingsList) leagueStandingsList.innerHTML = ""; return; }
  if (leagueStandingsMeta) leagueStandingsMeta.innerHTML = `<strong>${escapeHtml(season.name || active.title)}</strong><span>${escapeHtml(leagueStatusLabel(season.status))} · команд: ${season.teamsRegistered || 0}</span>`;
  const items = active.standings || [];
  if (!leagueStandingsList) return;
  if (!items.length || season.status === "registration") { leagueStandingsList.innerHTML = `<li>🎮 Зарегистрировано: ${season.teamsRegistered || 0}</li>`; return; }
  leagueStandingsList.innerHTML = items.map(item => {
    const trend = item.trend === "new" ? "NEW" : item.trend === "0" ? "—" : Number(item.trend || 0) > 0 ? `▲${item.trend}` : `▼${Math.abs(Number(item.trend))}`;
    return `<li class="${item.isCurrentUserTeam ? "is-current-team" : ""}"><strong>${item.place}. ${escapeHtml(item.name)}<small>${trend} · И ${item.played} В ${item.wins} П ${item.losses}</small></strong><span>${item.points}</span></li>`;
  }).join("");
}
function renderLeaguePending(items, isAdmin) {
  if (!leagueAdminPanel) return;
  leagueAdminPanel.hidden = !isAdmin; if (leagueAdminEmpty) leagueAdminEmpty.hidden = isAdmin;
  if (!isAdmin || !leaguePendingList) return;
  if (!items.length) { leaguePendingList.innerHTML = "<p class=\"panel-note\">Нет заявок.</p>"; return; }
  leaguePendingList.innerHTML = items.map(t => `<article class="league-row league-admin-row"><div><strong>${escapeHtml(t.name)}</strong><span>${escapeHtml(t.formatTitle || t.gameTitle)} · ${escapeHtml(t.captainName || "-")}</span></div><div class="league-admin-actions"><button type="button" data-team-id="${t.id}" data-status="active">Принять</button><button type="button" data-team-id="${t.id}" data-status="rejected">Отклонить</button></div></article>`).join("");
}
// ── REGISTRATION WIZARD: FACEIT → join or create → done, one screen at a time ──
const WIZARD_STEPS = { faceit: [1, "FACEIT аккаунт"], choice: [2, "Как будешь играть?"], join: [3, "Вступить по коду"], create: [3, "Новая команда"], done: [3, "Готово"] };
const wizard = { step: "faceit", history: [] };
const wizardBackButton = document.querySelector("#wizard-back");
function wizardGo(step, push = true) {
  if (push && wizard.step !== step) wizard.history.push(wizard.step);
  wizard.step = step;
  document.querySelectorAll("#league-register-section .wizard-step").forEach(el => { el.hidden = el.dataset.step !== step; });
  const [num, title] = WIZARD_STEPS[step];
  document.querySelector("#wizard-step-label").textContent = step === "done" ? "Регистрация" : `Шаг ${num} из 3`;
  document.querySelector("#wizard-title").textContent = title;
  document.querySelectorAll("#wizard-pips span").forEach((p, i) => p.classList.toggle("is-active", i < num));
  wizardBackButton.hidden = step === "done";
  if (step === "choice") document.querySelector("#wizard-faceit-name").textContent = state.league?.user?.faceitNickname || "—";
  if (step === "create") selectSeriesFormat(state.selectedLeagueFormat);
  window.scrollTo({ top: 0 });
  document.querySelector(`.wizard-step[data-step="${step}"] input`)?.focus({ preventScroll: true });
}
function wizardBack() {
  const prev = wizard.history.pop();
  if (prev) wizardGo(prev, false); else showLeagueSection("overview");
  tg?.HapticFeedback?.selectionChanged();
}
function wizardStart() {
  wizard.history = [];
  const hasFaceit = Boolean((state.league?.user?.faceitNickname || "").trim());
  if (leagueRegisterFaceit) leagueRegisterFaceit.value = state.league?.user?.faceitNickname || "";
  if (faceitVerifyStatus) faceitVerifyStatus.textContent = "";
  if (leagueJoinNote) leagueJoinNote.textContent = "";
  wizardGo(hasFaceit ? "choice" : "faceit", false);
}
function wizardDone(title, note, inviteCode) {
  document.querySelector("#wizard-done-title").textContent = title;
  document.querySelector("#wizard-done-note").textContent = note;
  document.querySelector("#wizard-done-invite").hidden = !inviteCode;
  document.querySelector("#wizard-done-code").textContent = inviteCode || "";
  document.querySelector("#wizard-done-start").hidden = false;
  wizard.history = [];
  wizardGo("done", false);
}
function setBusy(button, busy, idleText) {
  if (!button) return;
  button.disabled = busy;
  button.textContent = busy ? "Подождите..." : idleText;
}
async function leagueRegister() {
  const faceitNick = leagueRegisterFaceit?.value.trim() || "";
  if (!faceitNick) { faceitVerifyStatus.textContent = "Напиши ник, под которым играешь на FACEIT."; leagueRegisterFaceit.focus(); return; }
  setBusy(leagueRegisterButton, true, "Дальше →");
  faceitVerifyStatus.textContent = "Проверяем ник на FACEIT...";
  try {
    const r = await api(`/api/faceit/verify?nickname=${encodeURIComponent(faceitNick)}`);
    if (!r.ok) {
      faceitVerifyStatus.textContent = `Ник «${faceitNick}» не найден на FACEIT. Проверь написание.`;
      tg?.HapticFeedback?.notificationOccurred("error");
      setBusy(leagueRegisterButton, false, "Дальше →");
      return;
    }
    faceitVerifyStatus.textContent = `✓ ${r.player.nickname} · Level ${r.player.skillLevel} · ELO ${r.player.faceitElo}`;
  } catch { faceitVerifyStatus.textContent = ""; }
  try {
    const result = await postApi("/api/league/register", { game: "cs2", nick: faceitNick, faceitNick });
    renderLeague(result.league || {});
    tg?.HapticFeedback?.notificationOccurred("success");
    wizardGo("choice");
  } catch (err) {
    faceitVerifyStatus.textContent = errorMessage(err, "Не удалось сохранить. Попробуй ещё раз.");
  } finally { setBusy(leagueRegisterButton, false, "Дальше →"); }
}
async function leagueJoinTeam() {
  const code = leagueJoinCodeInput?.value.trim() || "";
  if (!code) { leagueJoinNote.textContent = "Введи код от капитана."; leagueJoinCodeInput.focus(); return; }
  setBusy(leagueJoinButton, true, "Вступить в команду");
  try {
    const result = await postApi("/api/league/team/join", { invite_code: code });
    leagueJoinCodeInput.value = ""; leagueJoinNote.textContent = "";
    renderLeague(result.league || {});
    tg?.HapticFeedback?.notificationOccurred("success");
    wizardDone(`Ты в команде «${result.team?.name || ""}»`, "Капитан увидит тебя в составе. Сетка турнира появится в понедельник в 04:00.");
  } catch (err) {
    tg?.HapticFeedback?.notificationOccurred("error");
    leagueJoinNote.textContent = errorMessage(err, "Код не подошёл. Проверь его у капитана.");
  } finally { setBusy(leagueJoinButton, false, "Вступить в команду"); }
}
async function leagueCreateTeam() {
  const name = leagueTeamName?.value.trim() || "";
  const note = document.querySelector("#league-create-note");
  if (!name) { note.textContent = "Придумай название команды."; leagueTeamName.focus(); return; }
  setBusy(leagueCreateTeamButton, true, "Подать заявку");
  try {
    const result = await postApi("/api/league/team", { game: "cs2", format: state.selectedLeagueFormat, name });
    leagueTeamName.value = "";
    renderLeague(result.league || {});
    const team = (result.league?.myTeams || []).filter(t => t.name === name).sort((a, z) => Number(z.id) - Number(a.id))[0];
    tg?.HapticFeedback?.notificationOccurred("success");
    wizardDone("Заявка отправлена", `Команда «${name}» (${state.selectedLeagueFormat === "2x2" ? "2×2" : "5×5"}) на проверке у админа. А пока позови игроков — отправь им этот код:`, team?.inviteToken);
  } catch (err) {
    tg?.HapticFeedback?.notificationOccurred("error");
    note.textContent = errorMessage(err, "Не удалось отправить заявку. Попробуй ещё раз.");
  } finally { setBusy(leagueCreateTeamButton, false, "Подать заявку"); }
}
async function leagueUpdateTeam(teamId, status) {
  try { const result = await postApi("/api/league/team/status", { teamId, status }); renderLeague(result.league || {}); setStatus(status === "active" ? "Принята." : "Отклонена."); }
  catch { setStatus("Не удалось."); }
}
function openLeagueInvite(teamId) {
  const team = (state.league?.myTeams || []).find(t => Number(t.id) === Number(teamId));
  if (!team || !leagueInviteSheet) return;
  if (leagueInviteCodeNode) leagueInviteCodeNode.textContent = team.inviteToken;
  if (leagueCopyCodeButton) leagueCopyCodeButton.textContent = "Скопировать";
  leagueInviteSheet.hidden = false;
}
function closeLeagueInvite() { if (leagueInviteSheet) leagueInviteSheet.hidden = true; }
async function copyLeagueInviteCode() {
  await navigator.clipboard.writeText(leagueInviteCodeNode?.textContent.trim() || "");
  if (leagueCopyCodeButton) { leagueCopyCodeButton.textContent = "Скопировано ✓"; setTimeout(() => { leagueCopyCodeButton.textContent = "Скопировать"; }, 2000); }
}
function shareLeagueInviteCode(codeOverride) {
  const code = (typeof codeOverride === "string" && codeOverride) || leagueInviteCodeNode?.textContent.trim() || "";
  const url = `https://t.me/share/url?url=&text=${encodeURIComponent(`Вступай в команду HardPoint Series!\nКод: ${code}`)}`;
  if (tg?.openTelegramLink) tg.openTelegramLink(url); else window.open(url, "_blank");
}

// ── LOAD ──
async function load() {
  tg?.ready(); tg?.expand();
  loadClub();
  try {
    const [me, league] = await Promise.all([api("/api/me"), api("/api/league")]);
    state.myTgId = me.user?.id;
    if (clubLoginInput) clubLoginInput.value = me.user.clubLogin || "";
    if (homeUsernameNode) homeUsernameNode.textContent = me.user.username ? `@${me.user.username}` : (me.user.name || "Игрок");
    renderLeague(league);
  } catch {
    if (homeUsernameNode) homeUsernameNode.textContent = "гость";
    renderLeague({});
    setStatus("Откройте из Telegram, чтобы участвовать в турнирах.");
  }
  showInitialView();
}

// ── EVENTS ──
saveLoginButton?.addEventListener("click", async () => { saveLoginButton.disabled = true; try { const r = await postApi("/api/club-login", { clubLogin: clubLoginInput.value.trim() }); clubLoginInput.value = r.clubLogin || ""; setStatus("Логин сохранён."); } catch { setStatus("Не удалось."); } finally { saveLoginButton.disabled = false; } });

document.querySelectorAll(".bottom-nav .nav-btn").forEach(b => b.addEventListener("click", () => { openGroup(b.dataset.group); tg?.HapticFeedback?.selectionChanged(); }));
homeClubCard?.addEventListener("click", () => showView(clubView));
homeSeriesCard?.addEventListener("click", () => showView(leagueView));
homeLiveCard?.addEventListener("click", () => showView(liveView));
liveTab5x5?.addEventListener("click", () => switchLiveFormat("5x5"));
liveTab2x2?.addEventListener("click", () => switchLiveFormat("2x2"));
liveContent?.addEventListener("click", e => {
  const link = e.target.closest("[data-open-url]"); if (link) { openExternal(link.dataset.openUrl); return; }
  const scoreBtn = e.target.closest("button.live-score-btn"); if (scoreBtn) { openScoreForm(scoreBtn); return; }
  const roomBtn = e.target.closest("button.live-faceit-btn"); if (roomBtn) openFaceitRoomForm(roomBtn);
});
leagueTabs.forEach(b => b.addEventListener("click", () => showLeagueSection(b.dataset.leagueSection)));
leagueNextButton?.addEventListener("click", () => showLeagueSection(leagueNextButton.dataset.target || "register"));
leagueActionJoin?.addEventListener("click", () => showLeagueSection("register"));
leagueActionCreate?.addEventListener("click", () => showLeagueSection("register"));
leagueActionTable?.addEventListener("click", () => showLeagueSection("table"));
seriesFormatButtons.forEach(b => b.addEventListener("click", () => openSeriesRegistration(b.dataset.seriesFormat)));
leagueRegisterButton?.addEventListener("click", leagueRegister);
wizardBackButton?.addEventListener("click", wizardBack);
document.querySelectorAll("[data-wizard-go]").forEach(b => b.addEventListener("click", () => { wizardGo(b.dataset.wizardGo); tg?.HapticFeedback?.selectionChanged(); }));
document.querySelector("#wizard-change-faceit")?.addEventListener("click", () => wizardGo("faceit"));
document.querySelectorAll(".wizard-format").forEach(b => b.addEventListener("click", () => { selectSeriesFormat(b.dataset.format); tg?.HapticFeedback?.selectionChanged(); }));
document.querySelector("#wizard-done-button")?.addEventListener("click", () => showLeagueSection("overview"));
document.querySelector("#wizard-share-button")?.addEventListener("click", () => shareLeagueInviteCode(document.querySelector("#wizard-done-code").textContent.trim()));
[[leagueRegisterFaceit, leagueRegister], [leagueJoinCodeInput, leagueJoinTeam], [leagueTeamName, leagueCreateTeam]].forEach(([input, action]) => input?.addEventListener("keydown", e => { if (e.key === "Enter") { e.preventDefault(); action(); } }));
leagueJoinCodeInput?.addEventListener("input", () => { leagueJoinCodeInput.value = leagueJoinCodeInput.value.toUpperCase(); });
leagueJoinButton?.addEventListener("click", leagueJoinTeam);
leagueCreateTeamButton?.addEventListener("click", leagueCreateTeam);
leagueStandingsTabs?.addEventListener("click", e => { const b = e.target.closest("button[data-standing-tab]"); if (!b) return; state.leagueStandingTab = b.dataset.standingTab; renderLeagueStandings(); });
leagueMyTeamNode?.addEventListener("click", e => { const b = e.target.closest("button[data-team-id]"); if (!b) return; openLeagueInvite(Number(b.dataset.teamId)); });
leagueInviteClose?.addEventListener("click", closeLeagueInvite);
leagueInviteSheet?.addEventListener("click", e => { if (e.target === leagueInviteSheet) closeLeagueInvite(); });
leagueCopyCodeButton?.addEventListener("click", copyLeagueInviteCode);
leagueShareCodeButton?.addEventListener("click", shareLeagueInviteCode);
leaguePendingList?.addEventListener("click", e => { const b = e.target.closest("button[data-team-id]"); if (!b) return; leagueUpdateTeam(Number(b.dataset.teamId), b.dataset.status); });

load();

// /start бот (кнопка для капитанов в форме создания команды)
document.querySelector('#open-bot-start')?.addEventListener('click', () => {
  const tg = window?.Telegram?.WebApp;
  if (tg?.openTelegramLink) tg.openTelegramLink('https://t.me/HardPoint_bot?start=captain');
  else window.open('https://t.me/HardPoint_bot?start=captain', '_blank');
});
