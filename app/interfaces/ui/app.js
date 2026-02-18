const LS_KEYS = {
  theme: "as_admin_theme",
  collapsed: "as_admin_sidebar_collapsed",
  settings: "as_admin_settings",
  playgroundAni: "as_playground_ani",
};

const DEFAULT_SETTINGS = { sessionId: "", apiBase: "", pageSize: 10 };

const RESOURCE_DEFS = {
  customers: {
    title: "Customer",
    endpoint: "/api/v1/admin/customers",
    key: "cust_id",
    defaultSortBy: "cust_id",
    defaultSortDir: "asc",
    columns: [
      { key: "cust_id", label: "ID", sortable: true },
      { key: "ani", label: "ANI", sortable: true },
      { key: "name", label: "Name", sortable: true },
      { key: "email", label: "Email", sortable: true },
      { key: "dob", label: "DOB", sortable: true, type: "date" },
      { key: "address", label: "Address", truncate: 36 },
    ],
    fields: [
      { name: "cust_id", label: "Customer ID", type: "number", required: true, integer: true, readOnlyOnEdit: true },
      { name: "ani", label: "ANI", type: "text" },
      { name: "name", label: "Name", type: "text", required: true },
      { name: "email", label: "Email", type: "email" },
      { name: "dob", label: "Date of Birth", type: "date" },
      { name: "address", label: "Address", type: "textarea", full: true },
    ],
  },
  policies: {
    title: "Policy",
    endpoint: "/api/v1/admin/policies",
    key: "policy_no",
    defaultSortBy: "policy_no",
    defaultSortDir: "asc",
    columns: [
      { key: "policy_no", label: "Policy No", sortable: true },
      { key: "cust_id", label: "Cust ID", sortable: true },
      { key: "vehicle_no", label: "Vehicle No", sortable: true },
      { key: "policy_type", label: "Type", sortable: true },
      { key: "total_coverage", label: "Total Coverage", sortable: true, type: "number" },
      { key: "used_coverage", label: "Used Coverage", sortable: true, type: "number" },
      { key: "rsa_eligibility", label: "RSA", sortable: true, type: "boolean" },
      { key: "date_of_expiry", label: "Expiry", sortable: true, type: "date" },
      { key: "status", label: "Status", sortable: true },
    ],
    fields: [
      { name: "policy_no", label: "Policy No", type: "text", required: true, readOnlyOnEdit: true },
      { name: "cust_id", label: "Customer ID", type: "number", required: true, integer: true },
      { name: "vehicle_no", label: "Vehicle No", type: "text", required: true },
      { name: "policy_type", label: "Policy Type", type: "text", required: true },
      { name: "benefits", label: "Benefits", type: "textarea", full: true },
      { name: "total_coverage", label: "Total Coverage", type: "number", required: true },
      { name: "used_coverage", label: "Used Coverage", type: "number" },
      { name: "rsa_eligibility", label: "RSA Eligibility", type: "checkbox" },
      { name: "date_of_purchase", label: "Date of Purchase", type: "date", required: true },
      { name: "date_of_expiry", label: "Date of Expiry", type: "date", required: true },
      { name: "status", label: "Status", type: "select", required: true, options: ["Active", "Expired"] },
    ],
  },
  claims: {
    title: "Claim",
    endpoint: "/api/v1/admin/claims",
    key: "claim_id",
    defaultSortBy: "claim_id",
    defaultSortDir: "desc",
    columns: [
      { key: "claim_id", label: "Claim ID", sortable: true },
      { key: "cust_id", label: "Cust ID", sortable: true },
      { key: "vehicle_no", label: "Vehicle No", sortable: true },
      { key: "incident_date", label: "Incident Date", sortable: true, type: "date" },
      { key: "incident_time", label: "Time", sortable: true },
      { key: "incident_place", label: "Place", sortable: true, truncate: 20 },
      { key: "damage_type", label: "Damage Type", sortable: true },
      { key: "fir_filed", label: "FIR Filed", sortable: true, type: "boolean" },
    ],
    fields: [
      { name: "cust_id", label: "Customer ID", type: "number", required: true, integer: true },
      { name: "vehicle_no", label: "Vehicle No", type: "text", required: true },
      { name: "incident_date", label: "Incident Date", type: "date", required: true },
      { name: "incident_time", label: "Incident Time", type: "time" },
      { name: "incident_place", label: "Incident Place", type: "text" },
      { name: "damage_type", label: "Damage Type", type: "text" },
      { name: "damage_description", label: "Damage Description", type: "textarea", full: true },
      { name: "fir_filed", label: "FIR Filed", type: "checkbox" },
      { name: "fir_no", label: "FIR No", type: "text" },
    ],
  },
  callbacks: {
    title: "Callback",
    endpoint: "/api/v1/admin/callbacks",
    key: "callback_id",
    defaultSortBy: "callback_id",
    defaultSortDir: "asc",
    columns: [
      { key: "callback_id", label: "Callback ID" },
      { key: "cust_id", label: "Cust ID" },
      { key: "ani", label: "ANI" },
      { key: "phone", label: "Phone" },
      { key: "status", label: "Status" },
      { key: "priority", label: "Priority" },
      { key: "scheduled_at", label: "Scheduled At", type: "datetime", truncate: 24 },
      { key: "assigned_to", label: "Assigned To", truncate: 18 },
      { key: "attempt_count", label: "Attempts" },
      { key: "reason", label: "Reason", truncate: 22 },
    ],
    fields: [
      { name: "cust_id", label: "Customer ID", type: "number", integer: true },
      { name: "ani", label: "ANI", type: "text" },
      { name: "phone", label: "Phone", type: "text" },
      { name: "reason", label: "Reason", type: "textarea", full: true },
      { name: "preferred_from", label: "Preferred From", type: "datetime" },
      { name: "preferred_to", label: "Preferred To", type: "datetime" },
      { name: "scheduled_at", label: "Scheduled At", type: "datetime" },
      {
        name: "status",
        label: "Status",
        type: "select",
        options: ["Requested", "Scheduled", "InProgress", "Completed", "Cancelled", "Failed", "NoAnswer"],
      },
      { name: "priority", label: "Priority (1-5)", type: "number", integer: true, required: true },
      { name: "assigned_to", label: "Assigned To", type: "text" },
      { name: "attempt_count", label: "Attempt Count", type: "number", integer: true },
      { name: "last_attempt_at", label: "Last Attempt At", type: "datetime" },
      { name: "outcome", label: "Outcome", type: "textarea", full: true },
    ],
  },
  "chat-summaries": {
    title: "Chat Summary",
    endpoint: "/api/v1/admin/chat-summaries",
    key: "cust_id",
    defaultSortBy: "updated_at",
    defaultSortDir: "desc",
    columns: [
      { key: "cust_id", label: "Cust ID", sortable: true },
      { key: "chat_summary", label: "Chat Summary", type: "json", truncate: 70 },
      { key: "updated_at", label: "Updated At", sortable: true, type: "datetime" },
    ],
    fields: [
      { name: "cust_id", label: "Customer ID", type: "number", required: true, integer: true, readOnlyOnEdit: true },
      { name: "chat_summary", label: "Chat Summary (JSON)", type: "json", required: true, full: true },
    ],
  },
};

const VIEW_TO_RESOURCE = {
  "view-customers": "customers",
  "view-policies": "policies",
  "view-claims": "claims",
  "view-callbacks": "callbacks",
  "view-chat-summaries": "chat-summaries",
};

const state = {
  activeView: "view-playground",
  settings: { ...DEFAULT_SETTINGS },
  resources: {},
  playground: { busy: false },
  modal: { open: false, mode: "view", resource: "", record: null },
  pendingDelete: null,
};

Object.keys(RESOURCE_DEFS).forEach((resource) => {
  const def = RESOURCE_DEFS[resource];
  state.resources[resource] = {
    search: "",
    page: 1,
    total: 0,
    pageSize: DEFAULT_SETTINGS.pageSize,
    sortBy: def.defaultSortBy,
    sortDir: def.defaultSortDir,
    items: [],
  };
});

const el = {
  appShell: document.getElementById("app-shell"),
  sidebarToggle: document.getElementById("sidebar-toggle"),
  mobileMenuToggle: document.getElementById("mobile-menu-toggle"),
  sidebarOverlay: document.getElementById("sidebar-overlay"),
  navItems: document.querySelectorAll(".nav-item"),
  views: document.querySelectorAll(".view"),
  quickNav: document.querySelectorAll(".quick-nav"),
  themeToggle: document.getElementById("theme-toggle"),
  settingsToggle: document.getElementById("settings-toggle"),
  settingsDropdown: document.getElementById("settings-dropdown"),
  sessionPill: document.getElementById("session-pill"),
  settingSessionId: document.getElementById("setting-session-id"),
  regenSessionId: document.getElementById("regen-session-id"),
  settingApiBase: document.getElementById("setting-api-base"),
  settingPageSize: document.getElementById("setting-page-size"),
  saveSettings: document.getElementById("save-settings"),
  resetSettings: document.getElementById("reset-settings"),
  pgAni: document.getElementById("pg-ani"),
  pgTransport: document.getElementById("pg-transport"),
  pgChannel: document.getElementById("pg-channel"),
  pgLog: document.getElementById("pg-log"),
  pgInput: document.getElementById("pg-input"),
  pgSend: document.getElementById("pg-send"),
  pgClear: document.getElementById("pg-clear"),
  pgSessionLabel: document.getElementById("pg-session-label"),
  callbackStatus: document.getElementById("filter-callback-status"),
  callbackAssignedTo: document.getElementById("filter-callback-assigned-to"),
  callbackDueBefore: document.getElementById("filter-callback-due-before"),
  callbackApplyFilters: document.getElementById("callback-apply-filters"),
  statCustomers: document.getElementById("stat-customers"),
  statPolicies: document.getElementById("stat-policies"),
  statClaims: document.getElementById("stat-claims"),
  statChatSummaries: document.getElementById("stat-chat-summaries"),
  addButtons: document.querySelectorAll(".add-record-btn"),
  footerYear: document.getElementById("footer-year"),
  crudModalBackdrop: document.getElementById("crud-modal-backdrop"),
  crudModalTitle: document.getElementById("crud-modal-title"),
  crudModalBody: document.getElementById("crud-modal-body"),
  crudModalClose: document.getElementById("crud-modal-close"),
  crudSaveBtn: document.getElementById("crud-save-btn"),
  crudCancelBtn: document.getElementById("crud-cancel-btn"),
  confirmBackdrop: document.getElementById("confirm-modal-backdrop"),
  confirmMessage: document.getElementById("confirm-message"),
  confirmClose: document.getElementById("confirm-close"),
  confirmYes: document.getElementById("confirm-yes"),
  confirmNo: document.getElementById("confirm-no"),
  toastRoot: document.getElementById("toast-root"),
};

const isMobile = () => window.matchMedia("(max-width: 940px)").matches;
const uuid = () => (window.crypto?.randomUUID ? window.crypto.randomUUID() : `session-${Date.now()}`);
const normalizeApiBase = (base) => String(base || "").trim().replace(/\/+$/, "");
const esc = (s) =>
  String(s ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
const trunc = (s, n) => (String(s ?? "").length <= n ? String(s ?? "") : `${String(s ?? "").slice(0, n - 1)}…`);
const toDateTimeLocal = (value) => {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const pad = (n) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
};

function jsonStr(v, pretty = false) {
  try {
    return JSON.stringify(v, null, pretty ? 2 : 0);
  } catch {
    return String(v);
  }
}

function toast(message, type = "info") {
  const div = document.createElement("div");
  div.className = `toast ${type}`;
  div.textContent = message;
  el.toastRoot.appendChild(div);
  setTimeout(() => div.remove(), 3200);
}

function setTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem(LS_KEYS.theme, theme);
}

function toggleTheme() {
  setTheme((document.documentElement.getAttribute("data-theme") || "light") === "dark" ? "light" : "dark");
}

function initTheme() {
  setTheme(localStorage.getItem(LS_KEYS.theme) || "light");
}

function setSidebarCollapsed(collapsed) {
  if (isMobile()) return;
  el.appShell.classList.toggle("collapsed", collapsed);
  localStorage.setItem(LS_KEYS.collapsed, collapsed ? "1" : "0");
}

function initSidebar() {
  if (!isMobile()) {
    el.appShell.classList.toggle("collapsed", localStorage.getItem(LS_KEYS.collapsed) === "1");
  } else {
    el.appShell.classList.remove("collapsed");
  }
}

function toggleSidebar() {
  if (isMobile()) {
    el.appShell.classList.toggle("sidebar-open");
    return;
  }
  setSidebarCollapsed(!el.appShell.classList.contains("collapsed"));
}

function closeSidebarMobile() {
  if (isMobile()) el.appShell.classList.remove("sidebar-open");
}

function closeSettings() {
  el.settingsDropdown.classList.remove("open");
}

function toggleSettings() {
  el.settingsDropdown.classList.toggle("open");
}

function updateSessionPill() {
  el.sessionPill.textContent = `session: ${state.settings.sessionId || "--"}`;
}

function updatePlaygroundSessionLabel() {
  if (!el.pgSessionLabel) return;
  el.pgSessionLabel.textContent = `session: ${state.settings.sessionId || "--"}`;
}

function loadSettings() {
  try {
    const raw = localStorage.getItem(LS_KEYS.settings);
    if (raw) state.settings = { ...DEFAULT_SETTINGS, ...JSON.parse(raw) };
  } catch {}
  if (!state.settings.sessionId) state.settings.sessionId = uuid();
  if (![10, 20, 50].includes(Number(state.settings.pageSize))) state.settings.pageSize = 10;
  state.settings.apiBase = normalizeApiBase(state.settings.apiBase || "");
  el.settingSessionId.value = state.settings.sessionId;
  el.settingApiBase.value = state.settings.apiBase;
  el.settingPageSize.value = String(state.settings.pageSize);
  if (el.pgAni) {
    const savedAni = localStorage.getItem(LS_KEYS.playgroundAni);
    if (savedAni) el.pgAni.value = savedAni;
  }
  updateSessionPill();
  updatePlaygroundSessionLabel();
}

function saveSettings() {
  state.settings.sessionId = String(el.settingSessionId.value || "").trim() || uuid();
  state.settings.apiBase = normalizeApiBase(el.settingApiBase.value || "");
  state.settings.pageSize = Number(el.settingPageSize.value || 10);
  localStorage.setItem(LS_KEYS.settings, JSON.stringify(state.settings));
  Object.keys(state.resources).forEach((r) => {
    state.resources[r].page = 1;
    state.resources[r].pageSize = state.settings.pageSize;
  });
  updateSessionPill();
  updatePlaygroundSessionLabel();
  closeSettings();
  toast("Settings saved.", "success");
  loadDashboard();
  const resource = VIEW_TO_RESOURCE[state.activeView];
  if (resource) loadResource(resource);
}

function resetSettings() {
  state.settings = { ...DEFAULT_SETTINGS, sessionId: uuid() };
  el.settingSessionId.value = state.settings.sessionId;
  el.settingApiBase.value = "";
  el.settingPageSize.value = "10";
  saveSettings();
}

function buildWsUrl(path) {
  const base = state.settings.apiBase || window.location.origin;
  const url = new URL(base);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  url.pathname = path;
  url.search = "";
  url.hash = "";
  return url.toString();
}

function buildUrl(path, params = null) {
  const base = state.settings.apiBase || window.location.origin;
  const url = new URL(base + path);
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v === undefined || v === null || v === "") return;
      url.searchParams.set(k, String(v));
    });
  }
  return url.toString();
}

async function requestJson(path, options = {}, params = null) {
  const response = await fetch(buildUrl(path, params), options);
  const text = await response.text();
  let payload = null;
  try {
    payload = text ? JSON.parse(text) : null;
  } catch {}
  if (!response.ok) {
    throw new Error(payload?.detail || text || "Request failed");
  }
  return payload;
}

function setPlaygroundBusy(busy) {
  state.playground.busy = busy;
  if (el.pgSend) el.pgSend.disabled = busy;
  if (el.pgInput) el.pgInput.disabled = busy;
  if (el.pgTransport) el.pgTransport.disabled = busy;
  if (el.pgChannel) el.pgChannel.disabled = busy;
}

function clearPlaygroundLog() {
  if (!el.pgLog) return;
  el.pgLog.innerHTML = '<div class="chat-empty">Send a message to begin playground testing.</div>';
}

function appendPlaygroundMessage(role, message, metadata = null) {
  if (!el.pgLog) return null;
  const empty = el.pgLog.querySelector(".chat-empty");
  if (empty) empty.remove();

  const row = document.createElement("div");
  row.className = `chat-row ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "chat-bubble";
  bubble.textContent = String(message || "");
  row.appendChild(bubble);

  if (metadata) {
    const meta = document.createElement("div");
    meta.className = "chat-meta";

    const addBadge = (value) => {
      if (!value) return;
      const badge = document.createElement("span");
      badge.className = "chat-badge";
      badge.textContent = String(value);
      meta.appendChild(badge);
    };

    addBadge(metadata.transport);
    addBadge(metadata.channel);
    addBadge(metadata.intent ? `intent:${metadata.intent}` : null);
    addBadge(metadata.language ? `lang:${metadata.language}` : null);
    if (metadata.followUp) {
      const hint = document.createElement("div");
      hint.textContent = `Follow-up: ${metadata.followUp}`;
      meta.appendChild(hint);
    }
    row.appendChild(meta);
  }

  el.pgLog.appendChild(row);
  el.pgLog.scrollTop = el.pgLog.scrollHeight;
  return row;
}

function appendPlaygroundTyping() {
  if (!el.pgLog) return null;
  const empty = el.pgLog.querySelector(".chat-empty");
  if (empty) empty.remove();

  const row = document.createElement("div");
  row.className = "chat-row assistant";

  const bubble = document.createElement("div");
  bubble.className = "chat-bubble";
  bubble.innerHTML = `
    <span class="typing-dots" aria-label="Assistant is typing">
      <span></span><span></span><span></span>
    </span>
  `;
  row.appendChild(bubble);

  el.pgLog.appendChild(row);
  el.pgLog.scrollTop = el.pgLog.scrollHeight;
  return row;
}

async function sendChatRest(payload) {
  return requestJson("/api/v1/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

async function sendChatWs(payload) {
  return new Promise((resolve, reject) => {
    let settled = false;
    const ws = new WebSocket(buildWsUrl("/ws/chat"));
    const timer = setTimeout(() => {
      if (settled) return;
      settled = true;
      try {
        ws.close();
      } catch {}
      reject(new Error("WebSocket timeout"));
    }, 15000);

    ws.onopen = () => {
      ws.send(JSON.stringify(payload));
    };

    ws.onmessage = (event) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      try {
        const raw = typeof event.data === "string" ? event.data : "";
        const parsed = raw ? JSON.parse(raw) : {};
        resolve(parsed);
      } catch {
        reject(new Error("Invalid WebSocket response"));
      } finally {
        try {
          ws.close();
        } catch {}
      }
    };

    ws.onerror = () => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      reject(new Error("WebSocket connection failed"));
      try {
        ws.close();
      } catch {}
    };

    ws.onclose = () => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      reject(new Error("WebSocket closed before response"));
    };
  });
}

async function sendPlaygroundMessage() {
  if (state.playground.busy) return;

  const ani = String(el.pgAni?.value || "").trim();
  const message = String(el.pgInput?.value || "").trim();
  const requestedTransport = String(el.pgTransport?.value || "rest").toLowerCase();
  const channel = String(el.pgChannel?.value || "web").toLowerCase();

  if (!ani) {
    toast("ANI is required for playground requests.", "error");
    return;
  }
  if (!message) return;

  localStorage.setItem(LS_KEYS.playgroundAni, ani);
  appendPlaygroundMessage("user", message, {
    transport: requestedTransport,
    channel,
  });
  if (el.pgInput) el.pgInput.value = "";

  const payload = {
    ani,
    session_uuid: state.settings.sessionId || uuid(),
    input_message: message,
    channel,
  };

  setPlaygroundBusy(true);
  const typingRow = appendPlaygroundTyping();
  let usedTransport = requestedTransport;

  try {
    let result = null;
    if (requestedTransport === "ws") {
      try {
        result = await sendChatWs(payload);
      } catch (wsErr) {
        usedTransport = "rest-fallback";
        toast(`WS failed (${wsErr.message}). Falling back to REST.`, "error");
        result = await sendChatRest(payload);
      }
    } else {
      result = await sendChatRest(payload);
    }

    typingRow?.remove();
    appendPlaygroundMessage("assistant", String(result?.response || "No response"), {
      transport: usedTransport,
      intent: result?.intent,
      language: result?.language,
      followUp: result?.follow_up_needed ? result?.follow_up_query || "Follow-up required." : null,
    });
  } catch (err) {
    typingRow?.remove();
    appendPlaygroundMessage("assistant", `Request failed: ${err.message}`, {
      transport: usedTransport,
    });
    toast(err.message, "error");
  } finally {
    setPlaygroundBusy(false);
    updatePlaygroundSessionLabel();
  }
}

function setActiveView(viewId) {
  state.activeView = viewId;
  el.views.forEach((v) => v.classList.toggle("active", v.id === viewId));
  el.navItems.forEach((item) => item.classList.toggle("active", item.dataset.view === viewId));
  closeSidebarMobile();
  if (viewId === "view-playground") {
    return;
  }
  if (viewId === "view-dashboard") {
    loadDashboard();
    return;
  }
  const resource = VIEW_TO_RESOURCE[viewId];
  if (resource) loadResource(resource);
}

function resourceEls(resource) {
  return {
    search: document.getElementById(`search-${resource}`),
    table: document.getElementById(`table-${resource}`),
    pager: document.getElementById(`pager-${resource}`),
  };
}

function cellText(col, value) {
  if (value === null || value === undefined || value === "") return '<span class="mono">--</span>';
  if (col.type === "boolean") return value ? "Yes" : "No";
  if (col.type === "json") return esc(trunc(jsonStr(value), col.truncate || 70));
  if (col.truncate) return esc(trunc(String(value), col.truncate));
  return esc(String(value));
}

function renderTable(resource) {
  const def = RESOURCE_DEFS[resource];
  const st = state.resources[resource];
  const { table } = resourceEls(resource);
  if (!table) return;

  const sortIcon = (key) => {
    if (st.sortBy !== key) return "";
    return st.sortDir === "asc"
      ? " <i class='fa-solid fa-arrow-up-short-wide'></i>"
      : " <i class='fa-solid fa-arrow-down-wide-short'></i>";
  };

  table.innerHTML = `
    <thead>
      <tr>
        ${def.columns
          .map((col) => {
            const sortAttr = col.sortable ? `data-sort="${col.key}" class="th-sort" title="Sort"` : "";
            return `<th ${sortAttr}>${esc(col.label)}${sortIcon(col.key)}</th>`;
          })
          .join("")}
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      ${
        st.items.length
          ? st.items
              .map(
                (row) => `
            <tr>
              ${def.columns.map((col) => `<td>${cellText(col, row[col.key])}</td>`).join("")}
              <td>
                <div class="actions">
                  ${
                    resource === "callbacks"
                      ? `<button class="action-btn" data-action="attempt" data-resource="${resource}" data-id="${esc(String(row[def.key]))}" title="Mark attempt"><i class="fa-solid fa-phone-volume"></i></button>`
                      : ""
                  }
                  <button class="action-btn" data-action="view" data-resource="${resource}" data-id="${esc(String(row[def.key]))}" title="View record"><i class="fa-regular fa-eye"></i></button>
                  <button class="action-btn" data-action="edit" data-resource="${resource}" data-id="${esc(String(row[def.key]))}" title="Edit record"><i class="fa-regular fa-pen-to-square"></i></button>
                  <button class="action-btn" data-action="delete" data-resource="${resource}" data-id="${esc(String(row[def.key]))}" title="Delete record"><i class="fa-regular fa-trash-can"></i></button>
                </div>
              </td>
            </tr>`
              )
              .join("")
          : `<tr><td colspan="${def.columns.length + 1}" class="empty-state">No records found.</td></tr>`
      }
    </tbody>
  `;

  if (!table.dataset.bound) {
    table.addEventListener("click", onTableClick);
    table.dataset.bound = "1";
  }
}

function renderPager(resource) {
  const st = state.resources[resource];
  const { pager } = resourceEls(resource);
  const totalPages = Math.max(1, Math.ceil(st.total / st.pageSize));

  pager.innerHTML = `
    <div class="mono">Total: ${st.total} | Page ${st.page} of ${totalPages}</div>
    <div class="controls">
      <button class="ghost-btn" data-page-action="prev" data-resource="${resource}" ${st.page <= 1 ? "disabled" : ""}>Prev</button>
      <button class="ghost-btn" data-page-action="next" data-resource="${resource}" ${st.page >= totalPages ? "disabled" : ""}>Next</button>
    </div>
  `;
  pager.querySelectorAll("[data-page-action]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const action = btn.dataset.pageAction;
      st.page = action === "prev" ? Math.max(1, st.page - 1) : st.page + 1;
      loadResource(resource);
    });
  });
}

function callbackFilterParams() {
  const params = {};
  if (el.callbackStatus?.value) params.status = el.callbackStatus.value;
  if (el.callbackAssignedTo?.value) params.assigned_to = el.callbackAssignedTo.value.trim();
  if (el.callbackDueBefore?.value) {
    const date = new Date(el.callbackDueBefore.value);
    if (!Number.isNaN(date.getTime())) params.due_before = date.toISOString();
  }
  return params;
}

function applyCallbackFilters() {
  const st = state.resources.callbacks;
  if (!st) return;
  st.page = 1;
  loadResource("callbacks");
}

async function loadResource(resource) {
  const def = RESOURCE_DEFS[resource];
  const st = state.resources[resource];
  st.pageSize = state.settings.pageSize;
  const extraParams = resource === "callbacks" ? callbackFilterParams() : {};
  try {
    const data = await requestJson(def.endpoint, {}, {
      search: st.search || undefined,
      page: st.page,
      page_size: st.pageSize,
      sort_by: st.sortBy,
      sort_dir: st.sortDir,
      ...extraParams,
    });
    st.items = Array.isArray(data.items) ? data.items : [];
    st.total = Number(data.total || 0);
    st.page = Number(data.page || st.page);
    st.pageSize = Number(data.page_size || st.pageSize);
    renderTable(resource);
    renderPager(resource);
  } catch (err) {
    toast(err.message, "error");
  }
}

async function loadDashboard() {
  try {
    const data = await requestJson("/api/v1/admin/dashboard");
    el.statCustomers.textContent = String(data.customer_count ?? 0);
    el.statPolicies.textContent = String(data.policy_count ?? 0);
    el.statClaims.textContent = String(data.claim_count ?? 0);
    el.statChatSummaries.textContent = String(data.chat_summary_count ?? 0);
  } catch (err) {
    toast(err.message, "error");
  }
}

async function fetchRecord(resource, idValue) {
  const def = RESOURCE_DEFS[resource];
  const res = await requestJson(`${def.endpoint}/${encodeURIComponent(idValue)}`);
  return res.record;
}

function fieldInput(field, value, mode) {
  const wrapper = document.createElement("div");
  wrapper.className = `field ${field.full ? "full" : ""}`.trim();
  const label = document.createElement("label");
  label.textContent = field.label + (field.required && mode === "create" ? " *" : "");
  wrapper.appendChild(label);

  const readOnly = (mode === "edit" && field.readOnlyOnEdit) || (mode === "create" && field.readOnlyOnCreate);
  if (readOnly) {
    const ro = document.createElement("div");
    ro.className = "readonly-box";
    ro.textContent = value ?? "--";
    wrapper.appendChild(ro);
    return wrapper;
  }

  if (field.type === "checkbox") {
    const row = document.createElement("div");
    row.className = "checkbox-field";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.dataset.field = field.name;
    checkbox.checked = Boolean(value);
    row.appendChild(checkbox);
    const hint = document.createElement("span");
    hint.textContent = "Enabled";
    row.appendChild(hint);
    wrapper.appendChild(row);
    return wrapper;
  }

  if (field.type === "select") {
    const select = document.createElement("select");
    select.dataset.field = field.name;
    (field.options || []).forEach((opt) => {
      const option = document.createElement("option");
      option.value = opt;
      option.textContent = opt;
      select.appendChild(option);
    });
    if (value !== undefined && value !== null && value !== "") select.value = String(value);
    wrapper.appendChild(select);
    return wrapper;
  }

  const input = field.type === "textarea" || field.type === "json" ? document.createElement("textarea") : document.createElement("input");
  if (input.tagName === "INPUT") {
    input.type =
      field.type === "number"
        ? "number"
        : field.type === "email"
        ? "email"
        : field.type === "date"
        ? "date"
        : field.type === "datetime"
        ? "datetime-local"
        : field.type === "time"
        ? "time"
        : "text";
  } else {
    input.rows = field.type === "json" ? 8 : 4;
  }
  input.dataset.field = field.name;
  input.value =
    field.type === "json"
      ? value
        ? jsonStr(value, true)
        : ""
      : field.type === "datetime"
      ? toDateTimeLocal(value)
      : value ?? "";
  wrapper.appendChild(input);
  return wrapper;
}

function viewRecord(resource, record) {
  const def = RESOURCE_DEFS[resource];
  const grid = document.createElement("div");
  grid.className = "form-grid";
  def.fields.forEach((field) => {
    const row = document.createElement("div");
    row.className = `field ${field.full ? "full" : ""}`.trim();
    const label = document.createElement("label");
    label.textContent = field.label;
    const box = document.createElement("div");
    box.className = "readonly-box";
    const value = record[field.name];
    box.textContent =
      field.type === "json" ? jsonStr(value, true) : value === null || value === undefined || value === "" ? "--" : String(value);
    row.appendChild(label);
    row.appendChild(box);
    grid.appendChild(row);
  });
  return grid;
}

function openCrudModal(mode, resource, record = null) {
  state.modal = { open: true, mode, resource, record };
  const def = RESOURCE_DEFS[resource];
  el.crudModalTitle.textContent =
    mode === "create" ? `Create ${def.title}` : mode === "edit" ? `Edit ${def.title}` : `View ${def.title}`;
  el.crudModalBody.innerHTML = "";
  el.crudSaveBtn.style.display = mode === "view" ? "none" : "inline-flex";

  if (mode === "view") {
    el.crudModalBody.appendChild(viewRecord(resource, record || {}));
  } else {
    const form = document.createElement("div");
    form.className = "form-grid";
    def.fields.forEach((field) => form.appendChild(fieldInput(field, record ? record[field.name] : null, mode)));
    el.crudModalBody.appendChild(form);
  }
  el.crudModalBackdrop.classList.add("open");
  el.crudModalBackdrop.setAttribute("aria-hidden", "false");
}

function openAttemptModal(resource, idValue) {
  const def = RESOURCE_DEFS[resource];
  const record = { [def.key]: idValue };
  state.modal = { open: true, mode: "attempt", resource, record };
  el.crudModalTitle.textContent = `Mark Attempt - ${def.title} ${idValue}`;
  el.crudModalBody.innerHTML = `
    <div class="form-grid">
      <div class="field">
        <label>Status</label>
        <select data-attempt-field="status">
          <option value="">(Keep existing)</option>
          <option value="InProgress">InProgress</option>
          <option value="NoAnswer">NoAnswer</option>
          <option value="Failed">Failed</option>
          <option value="Completed">Completed</option>
          <option value="Cancelled">Cancelled</option>
        </select>
      </div>
      <div class="field">
        <label>Attempt At</label>
        <input data-attempt-field="attempt_at" type="datetime-local" />
      </div>
      <div class="field full">
        <label>Outcome</label>
        <textarea data-attempt-field="outcome" rows="4" placeholder="Rang 30s, no pickup"></textarea>
      </div>
    </div>
  `;
  el.crudSaveBtn.style.display = "inline-flex";
  el.crudModalBackdrop.classList.add("open");
  el.crudModalBackdrop.setAttribute("aria-hidden", "false");
}

function closeCrudModal() {
  state.modal.open = false;
  el.crudModalBackdrop.classList.remove("open");
  el.crudModalBackdrop.setAttribute("aria-hidden", "true");
}

function modalPayload(resource, mode) {
  const def = RESOURCE_DEFS[resource];
  const payload = {};
  const nodes = el.crudModalBody.querySelectorAll("[data-field]");
  for (const node of nodes) {
    const fieldName = node.dataset.field;
    const field = def.fields.find((f) => f.name === fieldName);
    if (!field) continue;

    let value = null;
    if (field.type === "checkbox") {
      value = node.checked;
    } else {
      const raw = String(node.value ?? "").trim();
      if (raw === "") {
        value = null;
      } else if (field.type === "number") {
        value = field.integer ? parseInt(raw, 10) : parseFloat(raw);
        if (Number.isNaN(value)) throw new Error(`${field.label} must be a valid number.`);
      } else if (field.type === "datetime") {
        const dt = new Date(raw);
        if (Number.isNaN(dt.getTime())) throw new Error(`${field.label} must be a valid date/time.`);
        value = dt.toISOString();
      } else if (field.type === "json") {
        try {
          value = JSON.parse(raw);
        } catch {
          throw new Error(`${field.label} must be valid JSON.`);
        }
      } else {
        value = raw;
      }
    }

    if (mode === "create" && field.required && (value === null || value === "")) {
      throw new Error(`${field.label} is required.`);
    }
    if (field.type === "email" && value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value))) {
      throw new Error("Please provide a valid email.");
    }
    payload[fieldName] = value;
  }
  return payload;
}

function attemptPayloadFromModal() {
  const statusNode = el.crudModalBody.querySelector("[data-attempt-field='status']");
  const attemptNode = el.crudModalBody.querySelector("[data-attempt-field='attempt_at']");
  const outcomeNode = el.crudModalBody.querySelector("[data-attempt-field='outcome']");
  if (!statusNode || !attemptNode || !outcomeNode) {
    throw new Error("Attempt form is incomplete.");
  }

  const status = String(statusNode.value || "").trim() || null;
  const outcome = String(outcomeNode.value || "").trim() || null;
  const attemptRaw = String(attemptNode.value || "").trim();
  const attemptAt = attemptRaw ? new Date(attemptRaw).toISOString() : null;

  return {
    status,
    outcome,
    attempt_at: attemptAt,
  };
}

async function submitCrudModal() {
  if (!state.modal.open) return;
  const { mode, resource, record } = state.modal;
  if (mode === "view") return;
  const def = RESOURCE_DEFS[resource];
  try {
    const payload = mode === "attempt" ? attemptPayloadFromModal() : modalPayload(resource, mode);
    const method = mode === "create" || mode === "attempt" ? "POST" : "PATCH";
    const path =
      mode === "create"
        ? def.endpoint
        : mode === "attempt"
        ? `${def.endpoint}/${encodeURIComponent(record[def.key])}/attempt`
        : `${def.endpoint}/${encodeURIComponent(record[def.key])}`;
    await requestJson(path, { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    closeCrudModal();
    toast(
      `${def.title} ${
        mode === "create" ? "created" : mode === "attempt" ? "attempt updated" : "updated"
      } successfully.`,
      "success"
    );
    await loadResource(resource);
    await loadDashboard();
  } catch (err) {
    toast(err.message, "error");
  }
}

function openDeleteConfirm(resource, idValue) {
  state.pendingDelete = { resource, idValue };
  el.confirmMessage.textContent = `Delete ${RESOURCE_DEFS[resource].title} (${idValue})? This action cannot be undone.`;
  el.confirmBackdrop.classList.add("open");
  el.confirmBackdrop.setAttribute("aria-hidden", "false");
}

function closeDeleteConfirm() {
  state.pendingDelete = null;
  el.confirmBackdrop.classList.remove("open");
  el.confirmBackdrop.setAttribute("aria-hidden", "true");
}

async function confirmDelete() {
  if (!state.pendingDelete) return;
  const { resource, idValue } = state.pendingDelete;
  try {
    await requestJson(`${RESOURCE_DEFS[resource].endpoint}/${encodeURIComponent(idValue)}`, { method: "DELETE" });
    closeDeleteConfirm();
    toast(`${RESOURCE_DEFS[resource].title} deleted.`, "success");
    await loadResource(resource);
    await loadDashboard();
  } catch (err) {
    toast(err.message, "error");
  }
}

async function onTableClick(event) {
  const target = event.target;
  if (!(target instanceof HTMLElement)) return;

  const header = target.closest("th[data-sort]");
  if (header) {
    const table = header.closest("table");
    const resource = table?.id?.replace("table-", "");
    if (!resource || !RESOURCE_DEFS[resource]) return;
    const st = state.resources[resource];
    const sortBy = header.dataset.sort;
    if (st.sortBy === sortBy) st.sortDir = st.sortDir === "asc" ? "desc" : "asc";
    else {
      st.sortBy = sortBy;
      st.sortDir = "asc";
    }
    st.page = 1;
    await loadResource(resource);
    return;
  }

  const actionBtn = target.closest("button[data-action]");
  if (!actionBtn) return;
  const action = actionBtn.dataset.action;
  const resource = actionBtn.dataset.resource;
  const idValue = actionBtn.dataset.id;
  if (!action || !resource || !idValue || !RESOURCE_DEFS[resource]) return;

  if (action === "attempt" && resource === "callbacks") {
    openAttemptModal(resource, idValue);
    return;
  }

  if (action === "delete") {
    openDeleteConfirm(resource, idValue);
    return;
  }

  try {
    const record = await fetchRecord(resource, idValue);
    if (action === "view") openCrudModal("view", resource, record);
    if (action === "edit") openCrudModal("edit", resource, record);
  } catch (err) {
    toast(err.message, "error");
  }
}

function bindSearch(resource) {
  const { search } = resourceEls(resource);
  if (!search) return;
  let timer = null;
  search.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      const st = state.resources[resource];
      st.search = search.value.trim();
      st.page = 1;
      loadResource(resource);
    }, 260);
  });
}

function bindEvents() {
  el.sidebarToggle?.addEventListener("click", toggleSidebar);
  el.mobileMenuToggle?.addEventListener("click", toggleSidebar);
  el.sidebarOverlay?.addEventListener("click", closeSidebarMobile);
  el.themeToggle?.addEventListener("click", toggleTheme);

  el.settingsToggle?.addEventListener("click", (event) => {
    event.stopPropagation();
    toggleSettings();
  });
  document.addEventListener("click", (event) => {
    if (!el.settingsDropdown.classList.contains("open")) return;
    const target = event.target;
    if (!(target instanceof Node)) return;
    if (el.settingsDropdown.contains(target) || el.settingsToggle.contains(target)) return;
    closeSettings();
  });

  el.regenSessionId?.addEventListener("click", () => {
    el.settingSessionId.value = uuid();
  });
  el.saveSettings?.addEventListener("click", saveSettings);
  el.resetSettings?.addEventListener("click", resetSettings);

  el.navItems.forEach((item) => item.addEventListener("click", () => setActiveView(item.dataset.view)));
  el.quickNav.forEach((btn) => btn.addEventListener("click", () => setActiveView(btn.dataset.view)));
  el.pgSend?.addEventListener("click", sendPlaygroundMessage);
  el.pgClear?.addEventListener("click", clearPlaygroundLog);
  el.pgInput?.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendPlaygroundMessage();
    }
  });
  el.callbackApplyFilters?.addEventListener("click", applyCallbackFilters);
  el.callbackStatus?.addEventListener("change", applyCallbackFilters);
  el.callbackDueBefore?.addEventListener("change", applyCallbackFilters);
  el.callbackAssignedTo?.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      applyCallbackFilters();
    }
  });
  el.addButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const resource = btn.dataset.resource;
      if (!resource || !RESOURCE_DEFS[resource]) return;
      openCrudModal("create", resource);
    });
  });

  el.crudModalClose?.addEventListener("click", closeCrudModal);
  el.crudCancelBtn?.addEventListener("click", closeCrudModal);
  el.crudSaveBtn?.addEventListener("click", submitCrudModal);
  el.crudModalBackdrop?.addEventListener("click", (event) => {
    if (event.target === el.crudModalBackdrop) closeCrudModal();
  });

  el.confirmClose?.addEventListener("click", closeDeleteConfirm);
  el.confirmNo?.addEventListener("click", closeDeleteConfirm);
  el.confirmYes?.addEventListener("click", confirmDelete);
  el.confirmBackdrop?.addEventListener("click", (event) => {
    if (event.target === el.confirmBackdrop) closeDeleteConfirm();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeSettings();
      closeCrudModal();
      closeDeleteConfirm();
      closeSidebarMobile();
    }
  });

  window.addEventListener("resize", () => {
    if (!isMobile()) {
      el.appShell.classList.remove("sidebar-open");
      initSidebar();
    }
  });

  Object.keys(RESOURCE_DEFS).forEach(bindSearch);
}

function init() {
  initTheme();
  initSidebar();
  loadSettings();
  clearPlaygroundLog();
  bindEvents();
  el.footerYear.textContent = String(new Date().getFullYear());
  loadDashboard();
  setActiveView(state.activeView);
}

init();
