const state = { token: localStorage.getItem("diva_token"), characters: [], conversations: [], activeConversation: null, authMode: "login", selectedAvatarFile: null };
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

async function uploadAvatar(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch("/uploads/avatar", {
    method: "POST",
    headers: { Authorization: `Bearer ${state.token}` },
    body: formData,
  });
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const error = new Error(payload?.detail || "Could not upload the image.");
    error.status = response.status;
    throw error;
  }
  return payload.avatar_url;
}

function hideAllScreens() {
  $("#auth-screen").classList.add("hidden");
  $("#characters-screen").classList.add("hidden");
  $("#app-screen").classList.add("hidden");
  document.documentElement.classList.remove("app-active");
  document.body.classList.remove("app-active");
}
function showAuth() {
  hideAllScreens();
  $("#auth-screen").classList.remove("hidden");
}
function showCharacters() {
  hideAllScreens();
  $("#characters-screen").classList.remove("hidden");
  loadCharacters();
  loadConversations();
}
function showApp() {
  hideAllScreens();
  document.documentElement.classList.add("app-active");
  document.body.classList.add("app-active");
  $("#app-screen").classList.remove("hidden");
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

function getCharacterBlurb(character) {
  const profile = character.summary?.characters?.[0];
  if (!profile) return "";
  const text = profile.description || profile.personality || profile.backstory || profile.bio || profile.summary || "";
  if (text.length <= 140) return text;
  return `${text.slice(0, 140).trim()}…`;
}

function characterInitial(name) {
  return (name || "?").trim().charAt(0).toUpperCase();
}

async function loadCharacters() {
  const grid = $("#character-grid");
  grid.innerHTML = '<div class="characters-loading">Loading characters…</div>';
  try {
    state.characters = await api("/characters/");
    renderCharacterGrid();
  } catch (error) {
    if (isUnauthorized(error)) { endExpiredSession(); return; }
    grid.innerHTML = `<div class="characters-loading">${escapeHtml(error.message)}</div>`;
  }
}

function renderCharacterGrid() {
  const grid = $("#character-grid");
  grid.innerHTML = "";
  if (!state.characters.length) {
    grid.innerHTML = '<div class="characters-loading">No characters yet — create the first one.</div>';
    return;
  }
  state.characters.forEach((character) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "character-card";
    const blurb = getCharacterBlurb(character);
    card.innerHTML = `
      <div class="character-avatar">${character.avatar_url ? `
        <img class="character-avatar-blur" src="${escapeHtml(character.avatar_url)}" alt="" aria-hidden="true" />
        <img class="character-avatar-photo" src="${escapeHtml(character.avatar_url)}" alt="${escapeHtml(character.name)}" />
      ` : characterInitial(character.name)}</div>
      <h3>${escapeHtml(character.name)}</h3>
      ${blurb ? `<p>${escapeHtml(blurb)}</p>` : ""}
    `;
    card.onclick = () => openCharacter(character);
    grid.append(card);
  });
}

async function openCharacter(character) {
  try {
    if (!state.conversations.length) {
      state.conversations = await api("/conversations/");
    }
    let chat = state.conversations.find((item) => item.character_id === character.character_id);
    if (!chat) {
      const conversation = await api("/conversations/", { method: "POST", body: JSON.stringify({ character_id: character.character_id }) });
      chat = { ...conversation, character_name: character.name, character_avatar_url: character.avatar_url };
      state.conversations.unshift(chat);
    }
    showApp();
    renderConversationList();
    await openConversation(chat);
  } catch (error) {
    if (isUnauthorized(error)) { endExpiredSession(); return; }
    alert(error.message);
  }
}

async function loadConversations() {
  try {
    state.conversations = await api("/conversations/");
    renderConversationList();
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
          $("#messages").innerHTML = '<div class="empty-state"><span class="empty-icon">✦</span><h2>Start somewhere new.</h2><p>Head back to the character list to pick up a story or meet someone new.</p><button id="empty-new-chat" class="primary">Browse characters</button></div>';
          $("#empty-new-chat").onclick = showCharacters;
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
  } catch (error) {
    if (isUnauthorized(error)) { endExpiredSession(); return; }
    $("#messages").innerHTML = `<div class="empty-state"><p>${escapeHtml(error.message)}</p></div>`;
  }
}

function getActiveCharacter() {
  if (!state.activeConversation) return null;
  return state.characters.find((character) => character.character_id === state.activeConversation.character_id) || null;
}

function createAssistantAvatar() {
  const character = getActiveCharacter();
  const avatarUrl = state.activeConversation?.character_avatar_url || character?.avatar_url;
  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  if (avatarUrl) {
    const image = document.createElement("img");
    image.src = avatarUrl;
    image.alt = "";
    avatar.append(image);
  } else {
    avatar.textContent = characterInitial(state.activeConversation?.character_name || character?.name);
  }
  return avatar;
}

function appendMessage(role, content) {
  const item = document.createElement("div");
  item.className = `message ${role === "user" ? "user" : "assistant"}`;
  const bubble = document.createElement("div"); bubble.className = "bubble"; bubble.textContent = content;
  if (role !== "user") item.append(createAssistantAvatar());
  item.append(bubble); $("#messages").append(item); $("#messages").scrollTop = $("#messages").scrollHeight;
}
function escapeHtml(value) { const element = document.createElement("div"); element.textContent = value || ""; return element.innerHTML; }
function clearAvatarSelection() {
  state.selectedAvatarFile = null;
  $("#character-avatar-input").value = "";
  $("#avatar-preview-img").src = "";
  $("#avatar-preview").classList.add("hidden");
}
function openModal() { $("#character-modal").classList.remove("hidden"); $("#character-name").focus(); }
function closeModal() { $("#character-modal").classList.add("hidden"); $("#character-form").reset(); $("#character-error").textContent = ""; clearAvatarSelection(); }
function logout() { localStorage.removeItem("diva_token"); state.token = null; state.activeConversation = null; state.conversations = []; state.characters = []; showAuth(); }

$("#auth-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const email = $("#email").value.trim(); const password = $("#password").value;
  const error = $("#auth-error"); error.textContent = "";
  try {
    if (state.authMode === "signup") await api("/users/", { method: "POST", body: JSON.stringify({ email, password }) });
    const login = await api("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
    state.token = login.access_token; localStorage.setItem("diva_token", state.token); showCharacters();
  } catch (err) { error.textContent = err.message; }
});
document.querySelectorAll(".tab").forEach((tab) => tab.addEventListener("click", () => setAuthMode(tab.dataset.mode)));
$("#characters-new").onclick = openModal;
$("#close-modal").onclick = closeModal;
$("#avatar-remove").onclick = clearAvatarSelection;
$("#character-avatar-input").addEventListener("change", (event) => {
  const file = event.target.files[0];
  if (!file) { clearAvatarSelection(); return; }
  if (file.size > 5 * 1024 * 1024) {
    $("#character-error").textContent = "Image must be smaller than 5MB.";
    event.target.value = "";
    return;
  }
  $("#character-error").textContent = "";
  state.selectedAvatarFile = file;
  const reader = new FileReader();
  reader.onload = () => {
    $("#avatar-preview-img").src = reader.result;
    $("#avatar-preview").classList.remove("hidden");
  };
  reader.readAsDataURL(file);
});
$("#logout").onclick = logout;
$("#characters-logout").onclick = logout;
$("#back-to-characters").onclick = () => { setSidebarOpen(false); showCharacters(); };
$("#empty-new-chat").onclick = showCharacters;
$("#menu-toggle").onclick = () => setSidebarOpen(!$("#app-screen").classList.contains("sidebar-open"));
$("#sidebar-backdrop").onclick = () => setSidebarOpen(false);

$("#character-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const name = $("#character-name").value.trim(); const summary = $("#character-summary").value.trim(); const error = $("#character-error"); const button = $("#create-chat-submit");
  error.textContent = ""; button.disabled = true; button.textContent = "Creating…";
  try {
    let avatar_url = null;
    if (state.selectedAvatarFile) {
      button.textContent = "Uploading photo…";
      avatar_url = await uploadAvatar(state.selectedAvatarFile);
      button.textContent = "Creating…";
    }
    const character = await api("/characters/from-summary", { method: "POST", body: JSON.stringify({ name, summary, avatar_url }) });
    const conversation = await api("/conversations/", { method: "POST", body: JSON.stringify({ character_id: character.character_id }) });
    const chat = { ...conversation, character_name: name, character_avatar_url: character.avatar_url };
    state.conversations.unshift(chat);
    closeModal();
    showApp();
    renderConversationList();
    await openConversation(chat);
  } catch (err) {
    if (isUnauthorized(err)) { endExpiredSession(); return; }
    error.textContent = err.message;
  } finally { button.disabled = false; button.textContent = "Create character"; }
});

$("#composer").addEventListener("submit", async (event) => {
  event.preventDefault(); const input = $("#message-input"); const query = input.value.trim(); if (!query || !state.activeConversation) return;
  input.value = ""; input.disabled = true; appendMessage("user", query);
  const typing = document.createElement("div");
  typing.className = "message assistant typing";
  typing.append(createAssistantAvatar());
  const typingBubble = document.createElement("div");
  typingBubble.className = "bubble";
  typingBubble.textContent = "Thinking…";
  typing.append(typingBubble);
  $("#messages").append(typing);
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

if (state.token) showCharacters(); else showAuth();
