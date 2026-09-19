const state = { token: localStorage.getItem("mygpt_token"), conversations: [], activeConversation: null, authMode: "login" };
const $ = (selector) => document.querySelector(selector);
const isUnauthorized = (error) => error?.status === 401;

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body) headers["Content-Type"] = "application/json";
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(path, { ...options, headers });
  const payload = response.headers.get("content-type")?.includes("application/json") ? await response.json() : null;
  if (!response.ok) {
    const error = new Error(payload?.detail || "Something went wrong. Please try again.");
    error.status = response.status;
    throw error;
  }
  return payload;
}

async function streamChat(conversationId, query, onToken) {
  const response = await fetch(`/conversations/${conversationId}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${state.token}`,
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok || !response.body) {
    const payload = await response.json().catch(() => null);
    const error = new Error(payload?.detail || "Unable to start the response.");
    error.status = response.status;
    throw error;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let streamError = null;

  while (true) {
    const { done, value } = await reader.read();
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done });

    const events = buffer.split("\n\n");
    buffer = events.pop();
    for (const event of events) {
      const line = event.split("\n").find((entry) => entry.startsWith("data: "));
      if (!line) continue;
      const payload = JSON.parse(line.slice(6));
      if (payload.type === "token") onToken(payload.content);
      if (payload.type === "error") streamError = new Error(payload.message);
    }

    if (done) break;
  }

  if (streamError) throw streamError;
}

function showApp() {
  document.documentElement.classList.add("app-active");
  document.body.classList.add("app-active");
  $("#auth-screen").classList.add("hidden");
  $("#app-screen").classList.remove("hidden");
  loadConversations();
}
function showAuth() {
  document.documentElement.classList.remove("app-active");
  document.body.classList.remove("app-active");
  $("#app-screen").classList.add("hidden");
  $("#auth-screen").classList.remove("hidden");
}
function setSidebarOpen(isOpen) {
  $("#app-screen").classList.toggle("sidebar-open", isOpen);
  $("#menu-toggle").setAttribute("aria-expanded", String(isOpen));
  $("#menu-toggle").setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
}
function endExpiredSession() {
  logout();
  $("#auth-error").textContent = "Your session expired. Please sign in again.";
}
function setAuthMode(mode) {
  state.authMode = mode;
  document.querySelectorAll(".tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.mode === mode));
  $("#auth-title").textContent = mode === "login" ? "Welcome back" : "Create your account";
  $("#auth-subtitle").textContent = mode === "login" ? "Sign in to continue your conversations." : "Start your first remembered conversation.";
  $("#auth-submit").textContent = mode === "login" ? "Sign in" : "Create account";
  $("#password").autocomplete = mode === "login" ? "current-password" : "new-password";
  $("#auth-error").textContent = "";
}

async function loadConversations() {
  try {
    state.conversations = await api("/conversations/");
    renderConversationList();
    if (!state.activeConversation && state.conversations.length) openConversation(state.conversations[0]);
  } catch (error) { if (isUnauthorized(error)) endExpiredSession(); }
}

function renderConversationList() {
  const list = $("#chat-list");
  list.innerHTML = "";
  state.conversations.forEach((chat) => {
    const item = document.createElement("div");
    item.className = `chat-item ${state.activeConversation?.conversation_id === chat.conversation_id ? "active" : ""}`;
    const button = document.createElement("button");
    button.className = "chat-open";
    const name = chat.title || chat.character_name || "Untitled chat";
    const date = chat.updated_at ? new Date(chat.updated_at).toLocaleDateString(undefined, { month: "short", day: "numeric" }) : "New";
    button.innerHTML = `<strong>${escapeHtml(name)}</strong><small>${date}</small>`;
    button.onclick = () => openConversation(chat);
    const remove = document.createElement("button");
    remove.className = "chat-delete";
    remove.type = "button";
    remove.title = "Delete chat";
    remove.setAttribute("aria-label", `Delete ${name}`);
    remove.textContent = "×";
    remove.onclick = async (event) => {
      event.stopPropagation();
      if (!confirm(`Delete “${name}”? This cannot be undone.`)) return;
      try {
        await api(`/conversations/${chat.conversation_id}`, { method: "DELETE" });
        const wasActive = state.activeConversation?.conversation_id === chat.conversation_id;
        state.conversations = state.conversations.filter((item) => item.conversation_id !== chat.conversation_id);
        if (wasActive) {
          state.activeConversation = null;
          $("#chat-title").textContent = "Choose a conversation";
          $("#composer").classList.add("hidden");
          $("#messages").innerHTML = '<div class="empty-state"><span class="empty-icon">✦</span><h2>Start somewhere new.</h2><p>Create a chat and continue a story whenever you want.</p><button id="empty-new-chat" class="primary">Create a chat</button></div>';
          $("#empty-new-chat").onclick = openModal;
        }
        renderConversationList();
      } catch (error) {
        alert(error.message);
      }
    };
    item.append(button, remove);
    list.append(item);
  });
}

async function openConversation(chat) {
  state.activeConversation = chat;
  $("#chat-title").textContent = chat.title || chat.character_name || "Conversation";
  $("#composer").classList.remove("hidden");
  renderConversationList();
  $("#messages").innerHTML = '<div class="typing"><div class="bubble">Loading conversation…</div></div>';
  try {
    const messages = await api(`/conversations/${chat.conversation_id}/messages/`);
    $("#messages").innerHTML = "";
    messages.forEach((message) => appendMessage(message.role, message.content));
    if (!messages.length) appendMessage("assistant", `Hi, I’m ${chat.character_name || "here"}. What’s on your mind?`);
  } catch (error) {
    if (isUnauthorized(error)) { endExpiredSession(); return; }
    $("#messages").innerHTML = `<div class="empty-state"><p>${escapeHtml(error.message)}</p></div>`;
  }
}

function appendMessage(role, content) {
  const item = document.createElement("div");
  item.className = `message ${role === "user" ? "user" : "assistant"}`;
  const bubble = document.createElement("div"); bubble.className = "bubble"; bubble.textContent = content;
  item.append(bubble); $("#messages").append(item); $("#messages").scrollTop = $("#messages").scrollHeight;
}
function escapeHtml(value) { const element = document.createElement("div"); element.textContent = value || ""; return element.innerHTML; }
function openModal() { $("#character-modal").classList.remove("hidden"); $("#character-name").focus(); }
function closeModal() { $("#character-modal").classList.add("hidden"); $("#character-form").reset(); $("#character-error").textContent = ""; }
function logout() { localStorage.removeItem("mygpt_token"); state.token = null; state.activeConversation = null; state.conversations = []; showAuth(); }

$("#auth-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const email = $("#email").value.trim(); const password = $("#password").value;
  const error = $("#auth-error"); error.textContent = "";
  try {
    if (state.authMode === "signup") await api("/users/", { method: "POST", body: JSON.stringify({ email, password }) });
    const login = await api("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
    state.token = login.access_token; localStorage.setItem("mygpt_token", state.token); showApp();
  } catch (err) { error.textContent = err.message; }
});
document.querySelectorAll(".tab").forEach((tab) => tab.addEventListener("click", () => setAuthMode(tab.dataset.mode)));
$("#new-chat").onclick = () => { setSidebarOpen(false); openModal(); };
$("#empty-new-chat").onclick = openModal;
$("#close-modal").onclick = closeModal;
$("#logout").onclick = logout;
$("#menu-toggle").onclick = () => setSidebarOpen(!$("#app-screen").classList.contains("sidebar-open"));
$("#sidebar-backdrop").onclick = () => setSidebarOpen(false);

$("#character-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const name = $("#character-name").value.trim(); const summary = $("#character-summary").value.trim(); const error = $("#character-error"); const button = $("#create-chat-submit");
  error.textContent = ""; button.disabled = true; button.textContent = "Creating…";
  try {
    const character = await api("/characters/from-summary", { method: "POST", body: JSON.stringify({ name, summary }) });
    const conversation = await api("/conversations/", { method: "POST", body: JSON.stringify({ character_id: character.character_id }) });
    const chat = { ...conversation, character_name: name };
    state.conversations.unshift(chat); closeModal(); await openConversation(chat);
  } catch (err) { error.textContent = err.message; } finally { button.disabled = false; button.textContent = "Create chat"; }
});

$("#composer").addEventListener("submit", async (event) => {
  event.preventDefault(); const input = $("#message-input"); const query = input.value.trim(); if (!query || !state.activeConversation) return;
  input.value = ""; input.disabled = true; appendMessage("user", query);
  const typing = document.createElement("div"); typing.className = "message assistant typing"; typing.innerHTML = '<div class="bubble">Thinking…</div>'; $("#messages").append(typing);
  const bubble = typing.querySelector(".bubble"); let started = false;
  try {
    await streamChat(state.activeConversation.conversation_id, query, (token) => {
      if (!started) { bubble.textContent = ""; typing.classList.remove("typing"); started = true; }
      bubble.textContent += token;
      $("#messages").scrollTop = $("#messages").scrollHeight;
    });
    if (!started) bubble.textContent = "No response was returned.";
  }
  catch (err) {
    if (isUnauthorized(err)) { endExpiredSession(); return; }
    bubble.textContent = err.message;
  }
  finally { input.disabled = false; input.focus(); }
});

$("#message-input").addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    $("#composer").requestSubmit();
  }
});

if (state.token) showApp(); else showAuth();
