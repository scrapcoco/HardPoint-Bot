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
const homeEsportCard = document.querySelector("#home-esport-card");
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
const shopView = document.querySelector("#shop-view");
const missionsView = document.querySelector("#missions-view");
const clansView = document.querySelector("#clans-view");
const leagueView = document.querySelector("#league-view");
const esportView = document.querySelector("#esport-view");
const menuToggle = document.querySelector("#menu-toggle");
const menuPanel = document.querySelector("#menu-panel");
const backButton = document.querySelector("#back-button");
const homeMenuButton = document.querySelector("#home-menu-button");
const profileMenuButton = document.querySelector("#profile-menu-button");
const profileMissionsButton = document.querySelector("#profile-missions-button");
const profileClansButton = document.querySelector("#profile-clans-button");
const leagueMenuButton = document.querySelector("#league-menu-button");
const shopMenuButton = document.querySelector("#shop-menu-button");
const esportMenuButton = document.querySelector("#esport-menu-button");
const secretTrigger = document.querySelector("#secret-trigger");
const secretBox = document.querySelector("#secret-box");
const teamFinalsButton = document.querySelector("#team-finals-button");
const teamFinalsPanel = document.querySelector("#team-finals-panel");
const namaIconButton = document.querySelector("#nama-icon-button");
const namaProfilePanel = document.querySelector("#nama-profile-panel");
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
const leagueRegisterGame = document.querySelector("#league-register-game");
const leagueRegisterNick = document.querySelector("#league-register-nick");
const leagueRegisterButton = document.querySelector("#league-register-button");
const leagueJoinCard = document.querySelector("#league-join-card");
const leagueJoinForm = document.querySelector("#league-join-form");
const leagueJoinCodeInput = document.querySelector("#league-join-code");
const leagueJoinButton = document.querySelector("#league-join-button");
const leagueJoinNote = document.querySelector("#league-join-note");
const leagueTeamGame = document.querySelector("#league-team-game");
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
state.activeView = homeView;

function setStatus(message) {
  statusNode.textContent = message || "";
}

function authHeaders() {
  return {
    "X-Telegram-Init-Data": tg?.initData || "",
  };
}

async function api(path) {
  const response = await fetch(path, { headers: authHeaders() });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

async function postApi(path, payload) {
  const response = await fetch(path, {
    method: "POST",
    headers: {
      ...authHeaders(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

function errorMessage(error, fallback) {
  try {
    const parsed = JSON.parse(error.message);
    return parsed.message || fallback;
  } catch (_) {
    return fallback;
  }
}

function initialsFor(value) {
  const clean = String(value || "HP").replace("@", "").trim();
  const parts = clean.split(/\s+/).filter(Boolean);
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  }
  return clean.slice(0, 2).toUpperCase() || "HP";
}

function renderTop(items) {
  if (!items.length) {
    topListNode.innerHTML = "<li>Пока нет приглашений</li>";
    return;
  }

  topListNode.innerHTML = items
    .map((item, index) => {
      const name = item.username ? `@${item.username}` : item.name;
      const prize = item.prize ? `<small>Приз: ${escapeHtml(item.prize)}</small>` : "";
      const clubLogin = item.clubLogin ? `<small>Логин: ${escapeHtml(item.clubLogin)}</small>` : "";
      const rank = item.rank ? `<small>${escapeHtml(item.rank.icon)} ${escapeHtml(item.rank.title)}</small>` : "";
      return `
        <li>
          <strong>${index + 1}. ${escapeHtml(name)}${rank}${clubLogin}${prize}</strong>
          <span>${item.total}</span>
        </li>
      `;
    })
    .join("");
}

function renderRank(user) {
  const rank = user.rank || {};
  const progress = user.progress || {};
  const score = Number(progress.score || rank.score || 0);
  const nextScore = Number(rank.nextScore || score);
  const minScore = Math.max(0, nextScore - Number(rank.remaining || 0));
  const range = Math.max(1, nextScore - minScore);
  const current = Math.max(0, score - minScore);
  const percent = rank.isMax ? 100 : Math.min(100, Math.round((current / range) * 100));

  rankTitleNode.textContent = `${rank.icon || "🥉"} ${rank.title || "Recruit"}`;
  rankScoreNode.textContent = String(score);
  rankMeterFillNode.style.width = `${percent}%`;
  rankNextNode.textContent = rank.isMax
    ? "Максимальный ранг открыт."
    : `До ${rank.nextIcon || ""} ${rank.nextTitle || "следующего ранга"}: ${rank.remaining || 0}`;
  rankInvitesNode.textContent = String(progress.invites || 0);
  rankCoinsNode.textContent = String(progress.coins || 0);
  rankVisitsNode.textContent = String(progress.visits || 0);
  headerCoinBalance.textContent = String(progress.coins || 0);
  coinNoteNode.textContent = `За каждого приглашённого друга: ${progress.inviteCoinReward || 20} монет.`;
  rankHintText.textContent = rank.isMax
    ? "Ты уже на максимальном ранге. Дальше держим лидерство."
    : `Пригласи ещё ${rank.remaining || 0} друга и стань ${rank.nextTitle || "сильнее"}.`;
}

function renderMissions(missions) {
  const daily = missions.dailyReward || {};
  const visit = missions.visitReward || {};
  const streak = missions.streak || {};
  const social = missions.social || {};
  const instagram = social.instagram || {};
  const discord = social.discord || {};

  dailyRewardButton.disabled = !daily.canClaim;
  dailyRewardButton.textContent = daily.canClaim ? "Забрать" : "Забрано";
  dailyRewardStatus.textContent = daily.canClaim
    ? "Доступно сегодня."
    : "Daily Reward уже получен. Возвращайся завтра.";

  visitRewardButton.disabled = !visit.canClaim;
  visitRewardButton.textContent = visit.canClaim ? "Забрать" : "Забрано";
  visitRewardStatus.textContent = visit.canClaim
    ? "Доступно сегодня."
    : "Награда за вход уже получена сегодня.";

  missionStreakNode.textContent = String(streak.days || 0);
  renderProfileStreak(streak);

  renderSocialMission(instagramRewardButton, instagramRewardStatus, instagram, "Instagram");
  renderSocialMission(discordRewardButton, discordRewardStatus, discord, "Discord");
}

function renderProfileStreak(streak) {
  const days = Math.max(0, Number(streak.days || 0));
  const percent = Math.min(100, (days / 30) * 100);
  profileStreakDaysNode.textContent = String(days);
  profileStreakFillNode.style.width = `${percent}%`;
  profileStreakMarkers.forEach((marker) => {
    const markerDay = Number(marker.dataset.day || 0);
    marker.classList.toggle("is-reached", days >= markerDay);
  });
}

function renderSocialMission(button, statusNode, mission, title) {
  const status = mission.status || "new";
  button.disabled = status === "pending" || status === "claimed";
  if (status === "claimed") {
    button.textContent = "Получено";
    statusNode.textContent = `Награда за ${title} уже получена.`;
  } else if (status === "pending") {
    button.textContent = "На проверке";
    statusNode.textContent = `Миссия на проверке. Осталось примерно ${mission.hoursLeft || 24} ч.`;
  } else if (status === "ready") {
    button.textContent = "Получить 500";
    statusNode.textContent = "Проверка завершена. Можно забрать награду.";
  } else {
    button.textContent = "Отправить";
    statusNode.textContent = "После подписки отправь миссию на проверку.";
  }
}

function formatXp(value) {
  return `${Number(value || 0)} XP`;
}

function renderClans(data) {
  state.clans = data || {};
  state.clanWeeklyTop = state.clans.weeklyTop || [];
  state.clanMonthlyTop = state.clans.monthlyTop || [];
  const access = state.clans.access || {};
  const clan = state.clans.currentClan;
  const canJoin = Boolean(access.canJoin);
  const canCreate = Boolean(access.canCreate);
  profileClanBadge.textContent = clan?.name || (canJoin ? "Доступно" : "С Rookie");

  clanGate.hidden = canJoin;
  clanCurrent.hidden = !clan;
  clanJoin.hidden = Boolean(clan);

  createClanButton.disabled = !canCreate;
  createClanNote.textContent = canCreate
    ? "Можно создать клан. После создания ты станешь лидером."
    : "Создание доступно с ранга Legend.";
  joinClanCodeButton.disabled = !canJoin;

  if (clan) {
    renderCurrentClan(clan);
  }
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

  const level = clan.level || {};
  const currentLevelXp = Number(level.xp || 0);
  const nextLevelXp = Number(level.nextXp || currentLevelXp);
  const levelRange = Math.max(1, nextLevelXp - currentLevelXp);
  const levelProgress = level.isMax ? 100 : Math.min(100, ((Number(clan.totalXp || 0) - currentLevelXp) / levelRange) * 100);
  clanLevelFillNode.style.width = `${levelProgress}%`;
  clanNextLevelNode.textContent = level.isMax
    ? "Максимальный уровень клана открыт."
    : `До ${level.nextLevel} уровня: ${level.remaining || 0} XP`;

  renderClanChest(clan);
  renderClanContribution(clan);
  renderClanMembers(clan.members || []);
  clanCodeNode.textContent = clan.code || "";
}

function renderClanChest(clan) {
  const chest = clan.chest || {};
  const reached = chest.reached;
  const next = chest.next;
  clanChestTitleNode.textContent = reached ? `Достигнут ${reached.title}` : "Сундук еще не достигнут";
  clanChestXpNode.textContent = formatXp(clan.weeklyXp);
  clanChestFillNode.style.width = `${Math.min(100, (Number(clan.weeklyXp || 0) / 3500) * 100)}%`;
  clanChestMarkers.forEach((marker) => {
    const markerChest = (chest.chests || []).find((item) => item.key === marker.dataset.chest);
    const isReached = markerChest
      && Number(clan.weeklyXp || 0) >= Number(markerChest.xp)
      && Number(clan.membersCount || 0) >= Number(markerChest.members);
    marker.classList.toggle("is-reached", Boolean(isReached));
  });

  if (reached && (!next || reached.key === "epic")) {
    clanChestNoteNode.textContent = `${reached.title}: по итогам недели активные участники получат ${reached.hours} ч.`;
  } else if (next) {
    const parts = [];
    if (chest.missingXp) parts.push(`${chest.missingXp} XP`);
    if (chest.missingMembers) parts.push(`${chest.missingMembers} участников`);
    clanChestNoteNode.textContent = parts.length
      ? `До ${next.title}: нужно еще ${parts.join(" и ")}.`
      : `Достигнут ${next.title}.`;
  } else {
    clanChestNoteNode.textContent = "Копите Weekly Clan XP, чтобы открыть сундук недели.";
  }
}

function renderClanContribution(clan) {
  const daily = clan.dailyGoal || {};
  const me = clan.me || {};
  clanDailyGoalNode.textContent = `${Math.min(Number(daily.checked || 0), Number(daily.target || 3))}/${daily.target || 3}`;
  clanCheckinButton.disabled = Boolean(clan.checkedToday);
  clanCheckinButton.textContent = clan.checkedToday ? "Сегодня готово" : "Отметиться за клан";
  clanCheckinStatus.textContent = clan.checkedToday
    ? "Ты уже принес клану XP сегодня."
    : `+10 Clan XP. Цель дня: ${daily.target || 3} участника = +${daily.reward || 50} XP.`;
  clanMyRoleNode.textContent = me.role === "leader" ? "Лидер" : "Участник";
  clanMyWeeklyNode.textContent = formatXp(me.weeklyXp);
  clanMyTotalNode.textContent = formatXp(me.totalXp);
  clanMyCheckinsNode.textContent = String(me.checkins || 0);
  clanMyActiveNode.textContent = me.isChestActive ? "Активен" : `+${me.needsForChest || 50} XP`;
}

function renderClanMembers(members) {
  if (!members.length) {
    clanMembersList.innerHTML = "<li>Пока нет участников</li>";
    return;
  }
  clanMembersList.innerHTML = members.map((member, index) => `
    <li>
      <strong>${index + 1}. ${escapeHtml(member.name)}</strong>
      <span>${formatXp(member.weeklyXp)} · ${member.checkins || 0} check-in</span>
    </li>
  `).join("");
}

function renderPublicClans(clans, canJoin) {
  if (!clans.length) {
    publicClansList.innerHTML = "<p class=\"panel-note\">Публичных кланов пока нет.</p>";
    return;
  }
  publicClansList.innerHTML = clans.map((clan) => {
    const full = Number(clan.membersCount || 0) >= Number(clan.level?.slots || 5);
    const disabled = !canJoin || full ? "disabled" : "";
    const buttonText = !canJoin ? "С Rookie" : full ? "Нет мест" : "Вступить";
    return `
      <article class="public-clan-card">
        <div>
          <strong>${escapeHtml(clan.name)}</strong>
          <span>LVL ${clan.level?.level || 1} · ${clan.membersCount || 0}/${clan.level?.slots || 5} · ${formatXp(clan.weeklyXp)}</span>
        </div>
        <button type="button" data-clan-id="${clan.id}" ${disabled}>${buttonText}</button>
      </article>
    `;
  }).join("");
}

function renderClanTop(items) {
  if (!items.length) {
    clanTopList.innerHTML = "<li>Пока нет кланов</li>";
    return;
  }
  clanTopList.innerHTML = items.map((clan, index) => `
    <li>
      <strong>${index + 1}. ${escapeHtml(clan.name)}<small>LVL ${clan.level?.level || 1} · ${clan.membersCount || 0} участников</small></strong>
      <span>${formatXp(clan.periodXp || clan.weeklyXp)}</span>
    </li>
  `).join("");
}

function renderLeague(data) {
  state.league = data || {};
  const user = state.league.user || {};
  const roleTitle = user.isAdmin ? "Админ" : user.role === "captain" ? "Капитан" : "Игрок";
  leagueRoleNode.textContent = roleTitle;
  leagueXpNode.textContent = `${Number(user.xp || 0)} XP`;
  leagueRegisterNick.value = user.gameNickCs2 || "";
  document.body.classList.toggle("has-league-admin", Boolean(user.isAdmin));
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
  const hasNick = Boolean((user.gameNickCs2 || "").trim());
  const hasTeam = Boolean(teams.length);
  if (!hasNick) {
    leagueNextTitle.textContent = "Сначала сохрани ник";
    leagueNextNote.textContent = "Ник нужен, чтобы вступить в команду или создать свою.";
    leagueNextButton.textContent = "Указать ник";
    leagueNextButton.dataset.target = "register";
    return;
  }
  if (!hasTeam) {
    leagueNextTitle.textContent = "Вступи или создай команду";
    leagueNextNote.textContent = "Есть код капитана? Введи его. Хочешь собрать состав — создай заявку.";
    leagueNextButton.textContent = "Открыть заявку";
    leagueNextButton.dataset.target = "register";
    return;
  }
  leagueNextTitle.textContent = "Команда готовится к Series";
  leagueNextNote.textContent = "Проверь состав, пригласи игроков или смотри таблицу сезона.";
  leagueNextButton.textContent = "Смотреть таблицу";
  leagueNextButton.dataset.target = "table";
}

function renderLeagueJoinAccess(user) {
  const hasNick = Boolean((user.gameNickCs2 || "").trim());
  leagueJoinForm.hidden = !hasNick;
  leagueJoinNote.textContent = hasNick
    ? "Введи код капитана. Можно без дефиса и любым регистром."
    : "Сначала укажи игровой ник, чтобы вступить в команду.";
}

function showLeagueSection(sectionName) {
  leagueTabs.forEach((button) => {
    button.classList.toggle("is-current", button.dataset.leagueSection === sectionName);
  });
  leagueSections.forEach((section) => {
    section.classList.toggle("is-active", section.id === `league-${sectionName}-section`);
  });
}

function selectSeriesFormat(format) {
  state.selectedLeagueFormat = format === "2x2" ? "2x2" : "5x5";
  leagueTeamFormat.value = state.selectedLeagueFormat;
  const isDuo = state.selectedLeagueFormat === "2x2";
  seriesSelectedTitle.textContent = isDuo ? "Duo Strike" : "Full Squad Challenge";
  seriesSelectedBadge.textContent = isDuo ? "⚡ 2×2 · Формат выбран" : "🛡️ 5×5 · Формат выбран";
  document.body.classList.toggle("series-duo", isDuo);
  syncLeagueTeamFormat();
}

function openSeriesRegistration(format) {
  selectSeriesFormat(format);
  showLeagueSection("register");
}

function leagueStatusLabel(status) {
  return {
    registration: "Идёт набор",
    active: "Сезон идёт",
    finished: "Завершено",
    pending: "На проверке",
    rejected: "Отклонена",
    scheduled: "Запланирован",
    played: "Сыгран",
    disputed: "Проверка результата",
  }[status] || status || "Без статуса";
}

function renderLeagueSeasons(seasons) {
  if (!seasons.length) {
    leagueSeasonsNode.innerHTML = "<span><strong>Скоро</strong><small>Сезоны готовятся</small></span>";
    return;
  }
  leagueSeasonsNode.innerHTML = seasons.map((season) => `
    <span><strong>${escapeHtml(season.formatTitle || season.gameTitle)}</strong><small>${escapeHtml(leagueStatusLabel(season.status))}</small></span>
  `).join("");
}

function renderLeagueMyTeam(teams) {
  if (!teams.length) {
    leagueMyTeamNode.innerHTML = "<p class=\"panel-note\">Пока нет команды. Открой “Заявка”: введи код капитана или создай свою команду.</p>";
    return;
  }
  leagueMyTeamNode.innerHTML = teams.map((team) => `
    <article class="league-row league-team-row">
      <div>
        <strong>${escapeHtml(team.name)}</strong>
        <span>${escapeHtml(team.formatTitle || team.gameTitle)} · ${escapeHtml(leagueStatusLabel(team.status))} · ${team.members?.length || 0}/${team.maxMembers || "?"}</span>
      </div>
      <button class="league-invite-button" type="button" data-team-id="${team.id}" ${(team.members?.length || 0) >= Number(team.maxMembers || 99) ? "disabled" : ""}>
        ${(team.members?.length || 0) >= Number(team.maxMembers || 99) ? "Состав заполнен" : "Пригласить"}
      </button>
    </article>
  `).join("");
}

function renderLeagueTeams(teams) {
  if (!teams.length) {
    leagueTeamsList.innerHTML = "<p class=\"panel-note\">Команд пока нет.</p>";
    return;
  }
  leagueTeamsList.innerHTML = teams.map((team) => `
    <article class="league-row">
      <div>
        <strong>${escapeHtml(team.name)}</strong>
        <span>${escapeHtml(team.formatTitle || team.gameTitle)} · ${escapeHtml(leagueStatusLabel(team.status))} · капитан ${escapeHtml(team.captainName || "-")}</span>
      </div>
      <small>${team.members?.length || 0}</small>
    </article>
  `).join("");
}

function renderLeagueStandings() {
  const tabs = state.league?.standingTabs || [];
  if (!tabs.length) {
    leagueStandingsTabs.innerHTML = "";
    leagueStandingsMeta.innerHTML = "<p class=\"panel-note\">Сезонов пока нет.</p>";
    leagueStandingsList.innerHTML = "";
    return;
  }
  if (!state.leagueStandingTab || !tabs.some((tab) => tab.key === state.leagueStandingTab)) {
    state.leagueStandingTab = state.league?.defaultStandingTab || tabs[0].key;
  }
  leagueStandingsTabs.innerHTML = tabs.map((tab) => `
    <button type="button" data-standing-tab="${escapeHtml(tab.key)}" class="${tab.key === state.leagueStandingTab ? "is-current" : ""}">
      ${escapeHtml(tab.title)}
    </button>
  `).join("");
  const activeTab = tabs.find((tab) => tab.key === state.leagueStandingTab) || tabs[0];
  const season = activeTab.season;
  if (!season) {
    leagueStandingsMeta.innerHTML = "<p class=\"panel-note\">Сезонов пока нет.</p>";
    leagueStandingsList.innerHTML = "";
    return;
  }
  leagueStandingsMeta.innerHTML = `
    <strong>${escapeHtml(season.name || activeTab.title)}</strong>
    <span>${escapeHtml(leagueStatusLabel(season.status))} · команд: ${season.teamsRegistered || 0}</span>
  `;
  const items = activeTab.standings || [];
  if (!items.length || season.status === "registration") {
    leagueStandingsList.innerHTML = `<li>🎮 Сезон ещё не начался. Команды регистрируются: ${season.teamsRegistered || 0}</li>`;
    return;
  }
  leagueStandingsList.innerHTML = items.map((item) => {
    const trend = item.trend === "new" ? "NEW" : item.trend === "0" ? "—" : Number(item.trend || 0) > 0 ? `▲${item.trend}` : `▼${Math.abs(Number(item.trend))}`;
    return `
      <li class="${item.isCurrentUserTeam ? "is-current-team" : ""}">
        <strong>${item.place}. ${escapeHtml(item.name)}<small>${trend} · И ${item.played} · В ${item.wins} · П ${item.losses}</small></strong>
        <span>${item.points}</span>
      </li>
    `;
  }).join("");
}

function renderLeaguePending(items, isAdmin) {
  leagueAdminPanel.hidden = !isAdmin;
  leagueAdminEmpty.hidden = isAdmin;
  if (!isAdmin) return;
  if (!items.length) {
    leaguePendingList.innerHTML = "<p class=\"panel-note\">Новых заявок нет.</p>";
    return;
  }
  leaguePendingList.innerHTML = items.map((team) => `
    <article class="league-row league-admin-row">
      <div>
        <strong>${escapeHtml(team.name)}</strong>
        <span>${escapeHtml(team.formatTitle || team.gameTitle)} · капитан ${escapeHtml(team.captainName || "-")}</span>
      </div>
      <div class="league-admin-actions">
        <button type="button" data-team-id="${team.id}" data-status="active">Принять</button>
        <button type="button" data-team-id="${team.id}" data-status="rejected">Отклонить</button>
      </div>
    </article>
  `).join("");
}

async function refreshLeague() {
  const league = await api("/api/league");
  renderLeague(league);
  return league;
}

async function leagueRegister() {
  leagueRegisterButton.disabled = true;
  try {
    const result = await postApi("/api/league/register", {
      game: leagueRegisterGame.value,
      nick: leagueRegisterNick.value.trim(),
    });
    renderLeague(result.league || {});
    setStatus("Ник для Series сохранён.");
  } catch (error) {
    setStatus("Не получилось сохранить ник. Проверь поле и дисциплину.");
  } finally {
    leagueRegisterButton.disabled = false;
  }
}

async function leagueCreateTeam() {
  leagueCreateTeamButton.disabled = true;
  try {
    const result = await postApi("/api/league/team", {
      game: leagueTeamGame.value,
      format: leagueTeamGame.value === "cs2" ? leagueTeamFormat.value : null,
      name: leagueTeamName.value.trim(),
    });
    leagueTeamName.value = "";
    renderLeague(result.league || {});
    setStatus("Заявка команды отправлена админу.");
  } catch (error) {
    setStatus("Не получилось создать команду. Сначала сохрани ник для этой игры.");
  } finally {
    syncLeagueTeamFormat();
  }
}

function syncLeagueTeamFormat() {
  leagueTeamFormatWrap.hidden = false;
  leagueCreateTeamButton.disabled = !leagueTeamFormat.value;
}

async function leagueUpdateTeam(teamId, status) {
  try {
    const result = await postApi("/api/league/team/status", { teamId, status });
    renderLeague(result.league || {});
    setStatus(status === "active" ? "Команда принята." : "Команда отклонена.");
  } catch (error) {
    setStatus("Не получилось изменить статус команды.");
  }
}

function openLeagueInvite(teamId) {
  const team = (state.league?.myTeams || []).find((item) => Number(item.id) === Number(teamId));
  if (!team) return;
  leagueInviteCodeNode.textContent = team.inviteToken;
  leagueCopyCodeButton.textContent = "Скопировать код";
  leagueInviteSheet.hidden = false;
}

function closeLeagueInvite() {
  leagueInviteSheet.hidden = true;
}

async function copyLeagueInviteCode() {
  const code = leagueInviteCodeNode.textContent.trim();
  if (!code) return;
  await navigator.clipboard.writeText(code);
  leagueCopyCodeButton.textContent = "Скопировано ✓";
  setTimeout(() => {
    leagueCopyCodeButton.textContent = "Скопировать код";
  }, 2000);
}

function shareLeagueInviteCode() {
  const code = leagueInviteCodeNode.textContent.trim();
  if (!code) return;
  const message = [
    "Вступай в мою команду в HardPoint Series!",
    "Открой бота → вкладка Series → Вступить в команду",
    `Код: ${code}`,
  ].join("\n");
  const shareUrl = `https://t.me/share/url?url=&text=${encodeURIComponent(message)}`;
  if (tg?.openTelegramLink) {
    tg.openTelegramLink(shareUrl);
  } else {
    window.open(shareUrl, "_blank");
  }
}

async function leagueJoinTeam() {
  leagueJoinButton.disabled = true;
  leagueJoinButton.textContent = "Проверяем...";
  try {
    const result = await postApi("/api/league/team/join", {
      invite_code: leagueJoinCodeInput.value.trim(),
    });
    leagueJoinCodeInput.value = "";
    renderLeague(result.league || {});
    setStatus(`Ты в команде ${result.team?.name || ""}!`);
    showLeagueSection("overview");
  } catch (error) {
    leagueJoinNote.textContent = errorMessage(error, "Не получилось вступить в команду.");
  } finally {
    leagueJoinButton.disabled = false;
    leagueJoinButton.textContent = "Вступить";
  }
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => (
    {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "\"": "&quot;",
      "'": "&#39;",
    }[char]
  ));
}

async function load() {
  try {
    tg?.ready();
    tg?.expand();

    const [me, weeklyTop, allTimeTop, clans, league] = await Promise.all([
      api("/api/me"),
      api("/api/weekly-top"),
      api("/api/all-time-top"),
      api("/api/clans"),
      api("/api/league"),
    ]);
    state.inviteLink = me.inviteLink;
    state.weeklyTop = weeklyTop.top;
    state.allTimeTop = allTimeTop.top;
    inviteLinkNode.textContent = me.inviteLink;
    weeklyCountNode.textContent = me.weeklyInvitedCount;
    allTimeCountNode.textContent = me.allTimeInvitedCount;
    clubLoginInput.value = me.user.clubLogin || "";
    const displayName = me.user.username ? `@${me.user.username}` : (me.user.name || "Игрок HardPoint");
    homeUsernameNode.textContent = displayName;
    homeAvatarButton.textContent = initialsFor(me.user.name || me.user.username || "HP");
    renderRank(me.user);
    renderMissions(me.missions || {});
    renderClans(clans);
    renderLeague(league);
    showWeeklyTop();
  } catch (error) {
    inviteLinkNode.textContent = "Откройте приложение из Telegram, чтобы получить ссылку.";
    weeklyCountNode.textContent = "0";
    allTimeCountNode.textContent = "0";
    homeUsernameNode.textContent = "@hardpoint";
    homeAvatarButton.textContent = "HP";
    renderRank({ progress: {}, rank: {} });
    renderMissions({});
    renderClans({});
    renderLeague({});
    renderTop([]);
    setStatus("Telegram не передал данные авторизации. В браузере это нормально.");
  }
}

async function refreshClans() {
  const clans = await api("/api/clans");
  renderClans(clans);
  return clans;
}

async function claimMission(mission) {
  const buttons = {
    daily: dailyRewardButton,
    visit: visitRewardButton,
    instagram: instagramRewardButton,
    discord: discordRewardButton,
  };
  const button = buttons[mission];
  button.disabled = true;
  try {
    const result = await postApi("/api/missions/claim", { mission });
    renderMissions(result.missions || {});
    renderRank(result.user || {});
    tg?.HapticFeedback?.notificationOccurred("success");
    setStatus(result.message || `Начислено: +${result.totalAwardedCoins || 0} HP Coins.`);
  } catch (error) {
    tg?.HapticFeedback?.notificationOccurred("error");
    setStatus("Миссия пока недоступна или уже на проверке.");
  } finally {
    if (!["Забрано", "Получено", "На проверке"].includes(button.textContent)) {
      button.disabled = false;
    }
  }
}

saveLoginButton.addEventListener("click", async () => {
  const clubLogin = clubLoginInput.value.trim();
  saveLoginButton.disabled = true;
  try {
    const result = await postApi("/api/club-login", { clubLogin });
    clubLoginInput.value = result.clubLogin || "";
    tg?.HapticFeedback?.notificationOccurred("success");
    setStatus(result.clubLogin ? "Логин клуба сохранён." : "Логин клуба очищен.");
  } catch (error) {
    tg?.HapticFeedback?.notificationOccurred("error");
    setStatus("Не получилось сохранить логин. Откройте приложение из Telegram.");
  } finally {
    saveLoginButton.disabled = false;
  }
});

function activateTab(activeButton) {
  [weeklyTab, allTimeTab].forEach((button) => {
    const isActive = button === activeButton;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-selected", String(isActive));
    button.style.color = isActive ? "#171714" : "var(--muted)";
    button.style.background = isActive ? "var(--yellow)" : "transparent";
    button.style.borderColor = isActive ? "rgba(255, 221, 61, 0.45)" : "transparent";
  });
}

function closeMenu() {
  menuPanel.classList.remove("is-open");
  menuPanel.setAttribute("aria-hidden", "true");
  menuToggle.setAttribute("aria-expanded", "false");
}

function closeProfileDropdown() {
  profileDropdown.classList.remove("is-open");
  profileDropdown.setAttribute("aria-hidden", "true");
  profileMenuButton.setAttribute("aria-expanded", "false");
}

function toggleProfileDropdown() {
  const shouldOpen = !profileDropdown.classList.contains("is-open");
  profileDropdown.classList.toggle("is-open", shouldOpen);
  profileDropdown.setAttribute("aria-hidden", String(!shouldOpen));
  profileMenuButton.setAttribute("aria-expanded", String(shouldOpen));
}

function showView(activeView, options = {}) {
  if (state.activeView && state.activeView !== activeView && !options.skipHistory) {
    state.previousView = state.activeView;
  }
  state.activeView = activeView;
  [homeView, profileView, missionsView, clansView, leagueView, shopView, esportView].forEach((view) => {
    view.classList.toggle("is-active", view === activeView);
  });
  [
    [homeMenuButton, homeView],
    [leagueMenuButton, leagueView],
    [esportMenuButton, esportView],
  ].forEach(([button, ...views]) => {
    button.classList.toggle("is-current", views.includes(activeView));
  });
  backButton.classList.toggle("is-visible", activeView !== homeView);
  closeMenu();
  closeProfileDropdown();
}

function goBack() {
  const targetView = state.previousView && state.previousView !== state.activeView
    ? state.previousView
    : homeView;
  state.previousView = homeView;
  showView(targetView, { skipHistory: true });
}

function toggleMenu() {
  const shouldOpen = !menuPanel.classList.contains("is-open");
  menuPanel.classList.toggle("is-open", shouldOpen);
  menuPanel.setAttribute("aria-hidden", String(!shouldOpen));
  menuToggle.setAttribute("aria-expanded", String(shouldOpen));
}

function showWeeklyTop() {
  activateTab(weeklyTab);
  topTitleNode.textContent = "Топ недели";
  renderTop(state.weeklyTop);
}

function showAllTimeTop() {
  activateTab(allTimeTab);
  topTitleNode.textContent = "Топ за всё время";
  renderTop(state.allTimeTop);
}

function showClanWeeklyTop() {
  activateClanTab(clanWeeklyTab);
  clanTopTitleNode.textContent = "Топ кланов недели";
  renderClanTop(state.clanWeeklyTop);
}

function showClanMonthlyTop() {
  activateClanTab(clanMonthlyTab);
  clanTopTitleNode.textContent = "Топ кланов месяца";
  renderClanTop(state.clanMonthlyTop);
}

function activateClanTab(activeButton) {
  [clanWeeklyTab, clanMonthlyTab].forEach((button) => {
    const isActive = button === activeButton;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-selected", String(isActive));
    button.style.color = isActive ? "#171714" : "var(--muted)";
    button.style.background = isActive ? "var(--yellow)" : "transparent";
    button.style.borderColor = isActive ? "rgba(255, 221, 61, 0.45)" : "transparent";
  });
}

async function createClan() {
  createClanButton.disabled = true;
  try {
    await postApi("/api/clans/create", {
      name: newClanNameInput.value.trim(),
      isPublic: newClanPublicInput.checked,
    });
    newClanNameInput.value = "";
    await refreshClans();
    setStatus("Клан создан.");
  } catch (error) {
    setStatus("Не получилось создать клан. Проверь ранг Legend и название.");
  } finally {
    createClanButton.disabled = !(state.clans?.access?.canCreate);
  }
}

async function joinClan(payload) {
  joinClanCodeButton.disabled = true;
  try {
    await postApi("/api/clans/join", payload);
    await refreshClans();
    setStatus("Ты вступил в клан.");
  } catch (error) {
    setStatus("Не получилось вступить в клан. Проверь Rookie, код или места.");
  } finally {
    joinClanCodeButton.disabled = !(state.clans?.access?.canJoin);
  }
}

async function clanCheckIn() {
  clanCheckinButton.disabled = true;
  try {
    const result = await postApi("/api/clans/check-in", {});
    await refreshClans();
    setStatus(result.message || "Отметка принята.");
  } catch (error) {
    setStatus("Сегодня ты уже отметился или еще не состоишь в клане.");
  }
}

copyButton.addEventListener("click", async () => {
  if (!state.inviteLink) return;
  await navigator.clipboard.writeText(state.inviteLink);
  tg?.HapticFeedback?.notificationOccurred("success");
  setStatus("Ссылка скопирована.");
});

shareButton.addEventListener("click", () => {
  if (!state.inviteLink) return;
  const text = encodeURIComponent(`Заходи в HardPoint: ${state.inviteLink}`);
  tg?.openTelegramLink(`https://t.me/share/url?url=${encodeURIComponent(state.inviteLink)}&text=${text}`);
});

weeklyTab.addEventListener("click", showWeeklyTop);
allTimeTab.addEventListener("click", showAllTimeTop);
clanWeeklyTab.addEventListener("click", showClanWeeklyTop);
clanMonthlyTab.addEventListener("click", showClanMonthlyTop);
menuToggle.addEventListener("click", toggleMenu);
backButton.addEventListener("click", goBack);
homeMenuButton.addEventListener("click", () => showView(homeView));
profileMenuButton.addEventListener("click", toggleProfileDropdown);
homeAvatarButton.addEventListener("click", () => showView(profileView));
dropdownProfileButton.addEventListener("click", () => showView(profileView));
dropdownSettingsButton.addEventListener("click", () => showView(profileView));
profileMissionsButton.addEventListener("click", () => showView(missionsView));
profileClansButton.addEventListener("click", () => showView(clansView));
homeMissionsCard.addEventListener("click", () => showView(missionsView));
homeSeriesCard.addEventListener("click", () => showView(leagueView));
homeClansCard.addEventListener("click", () => showView(clansView));
homeEsportCard.addEventListener("click", () => showView(esportView));
leagueMenuButton.addEventListener("click", () => showView(leagueView));
leagueTabs.forEach((button) => {
  button.addEventListener("click", () => showLeagueSection(button.dataset.leagueSection));
});
leagueNextButton.addEventListener("click", () => showLeagueSection(leagueNextButton.dataset.target || "register"));
leagueActionJoin.addEventListener("click", () => showLeagueSection("register"));
leagueActionCreate.addEventListener("click", () => showLeagueSection("register"));
leagueActionTable.addEventListener("click", () => showLeagueSection("table"));
shopMenuButton.addEventListener("click", () => showView(shopView));
esportMenuButton.addEventListener("click", () => showView(esportView));
seriesFormatButtons.forEach((button) => {
  button.addEventListener("click", () => openSeriesRegistration(button.dataset.seriesFormat));
});
seriesBackToFormats.addEventListener("click", () => showLeagueSection("overview"));
leagueRegisterGame.addEventListener("change", () => {
  const user = state.league?.user || {};
  leagueRegisterNick.value = user.gameNickCs2 || "";
});
leagueRegisterButton.addEventListener("click", leagueRegister);
leagueJoinCodeInput.addEventListener("input", () => {
  leagueJoinCodeInput.value = leagueJoinCodeInput.value.toUpperCase();
});
leagueJoinButton.addEventListener("click", leagueJoinTeam);
leagueTeamGame.addEventListener("change", syncLeagueTeamFormat);
leagueTeamFormat.addEventListener("change", syncLeagueTeamFormat);
leagueCreateTeamButton.addEventListener("click", leagueCreateTeam);
leagueStandingsTabs.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-standing-tab]");
  if (!button) return;
  state.leagueStandingTab = button.dataset.standingTab;
  renderLeagueStandings();
});
leagueMyTeamNode.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-team-id]");
  if (!button) return;
  openLeagueInvite(Number(button.dataset.teamId));
});
leagueInviteClose.addEventListener("click", closeLeagueInvite);
leagueInviteSheet.addEventListener("click", (event) => {
  if (event.target === leagueInviteSheet) closeLeagueInvite();
});
leagueCopyCodeButton.addEventListener("click", copyLeagueInviteCode);
leagueShareCodeButton.addEventListener("click", shareLeagueInviteCode);
leaguePendingList.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-team-id]");
  if (!button) return;
  leagueUpdateTeam(Number(button.dataset.teamId), button.dataset.status);
});
createClanButton.addEventListener("click", createClan);
joinClanCodeButton.addEventListener("click", () => joinClan({ code: joinClanCodeInput.value.trim() }));
clanCheckinButton.addEventListener("click", clanCheckIn);
copyClanCodeButton.addEventListener("click", async () => {
  const code = clanCodeNode.textContent.trim();
  if (!code) return;
  await navigator.clipboard.writeText(code);
  setStatus("Код клана скопирован.");
});
publicClansList.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-clan-id]");
  if (!button) return;
  joinClan({ clanId: Number(button.dataset.clanId) });
});
dailyRewardButton.addEventListener("click", () => claimMission("daily"));
visitRewardButton.addEventListener("click", () => claimMission("visit"));
instagramRewardButton.addEventListener("click", () => claimMission("instagram"));
discordRewardButton.addEventListener("click", () => claimMission("discord"));
secretTrigger.addEventListener("click", () => {
  const isOpen = !secretBox.classList.contains("is-open");
  secretBox.classList.toggle("is-open", isOpen);
  secretBox.setAttribute("aria-hidden", String(!isOpen));
  if (isOpen) {
    tg?.HapticFeedback?.notificationOccurred("success");
  }
});
document.addEventListener("click", (event) => {
  if (!profileDropdown.contains(event.target) && !profileMenuButton.contains(event.target)) {
    closeProfileDropdown();
  }
});
teamFinalsButton.addEventListener("click", () => {
  const isOpen = !teamFinalsPanel.classList.contains("is-open");
  teamFinalsPanel.classList.toggle("is-open", isOpen);
  teamFinalsPanel.setAttribute("aria-hidden", String(!isOpen));
  teamFinalsButton.classList.toggle("is-active", isOpen);
  teamFinalsButton.setAttribute("aria-expanded", String(isOpen));
});
namaIconButton.addEventListener("click", () => {
  const isOpen = !namaProfilePanel.classList.contains("is-open");
  namaProfilePanel.classList.toggle("is-open", isOpen);
  namaProfilePanel.setAttribute("aria-hidden", String(!isOpen));
  namaIconButton.classList.toggle("is-active", isOpen);
  namaIconButton.setAttribute("aria-expanded", String(isOpen));
});

const canvas = document.querySelector("#arena");
const context = canvas.getContext("2d");
let width = 0;
let height = 0;
let points = [];

function resize() {
  const ratio = window.devicePixelRatio || 1;
  width = window.innerWidth;
  height = window.innerHeight;
  canvas.width = Math.floor(width * ratio);
  canvas.height = Math.floor(height * ratio);
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  points = Array.from({ length: 34 }, () => ({
    x: Math.random() * width,
    y: Math.random() * height,
    vx: (Math.random() - 0.5) * 0.28,
    vy: (Math.random() - 0.5) * 0.28,
  }));
}

function draw() {
  context.clearRect(0, 0, width, height);
  context.strokeStyle = "rgba(255, 221, 61, 0.12)";
  context.lineWidth = 1;
  points.forEach((point, index) => {
    point.x += point.vx;
    point.y += point.vy;
    if (point.x < 0 || point.x > width) point.vx *= -1;
    if (point.y < 0 || point.y > height) point.vy *= -1;

    for (let next = index + 1; next < points.length; next += 1) {
      const other = points[next];
      const distance = Math.hypot(point.x - other.x, point.y - other.y);
      if (distance < 115) {
        context.globalAlpha = 1 - distance / 115;
        context.beginPath();
        context.moveTo(point.x, point.y);
        context.lineTo(other.x, other.y);
        context.stroke();
      }
    }
  });
  context.globalAlpha = 1;
  requestAnimationFrame(draw);
}

window.addEventListener("resize", resize);
resize();
draw();
load();
