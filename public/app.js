const form = document.querySelector("#chat-form");
const input = document.querySelector("#message");
const sendButton = document.querySelector("#send");
const messages = document.querySelector("#messages");
const notice = document.querySelector("#notice");
const newChatButton = document.querySelector("#new-chat");

let sessionId = sessionStorage.getItem("chatbot-session") || crypto.randomUUID();
sessionStorage.setItem("chatbot-session", sessionId);
let waiting = false;

async function restoreConversation() {
  setWaiting(true);
  try {
    const response = await fetch(`/api/chat/${encodeURIComponent(sessionId)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "No se pudo recuperar la conversación.");
    if (data.messages.length) {
      messages.replaceChildren();
      for (const message of data.messages) addMessage(message.content, message.role);
    }
  } catch (error) {
    notice.hidden = false;
    notice.textContent = error.message;
  } finally {
    setWaiting(false);
  }
}
restoreConversation();

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message || waiting) return;

  addMessage(message, "user");
  input.value = "";
  resizeInput();
  setWaiting(true);
  const typing = addTyping();
  const slowNotice = setTimeout(() => {
    notice.hidden = false;
    notice.textContent = "La respuesta está tardando más de lo habitual. Seguimos esperando…";
  }, 10000);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sessionId, message })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "No se pudo enviar el mensaje.");
    typing.remove();
    addMessage(data.reply, "assistant");
    notice.hidden = !data.demo;
    notice.textContent = data.demo
      ? "Modo demostración: configura la clave del proveedor de IA en .env para activar respuestas inteligentes."
      : "";
  } catch (error) {
    typing.remove();
    addMessage(error.message, "assistant");
    input.value = message;
    resizeInput();
    notice.hidden = true;
  } finally {
    clearTimeout(slowNotice);
    setWaiting(false);
    input.focus();
  }
});

input.addEventListener("input", resizeInput);
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

newChatButton.addEventListener("click", async () => {
  if (waiting) return;
  const oldSessionId = sessionId;
  setWaiting(true);
  try {
    const response = await fetch(`/api/chat/${encodeURIComponent(oldSessionId)}`, { method: "DELETE" });
    if (!response.ok) throw new Error("No se pudo reiniciar la conversación.");
  } catch (error) {
    notice.hidden = false;
    notice.textContent = error.message;
    return;
  } finally {
    setWaiting(false);
  }
  sessionId = crypto.randomUUID();
  sessionStorage.setItem("chatbot-session", sessionId);
  messages.replaceChildren();
  addMessage("¡Hola! Empecemos de nuevo. ¿En qué puedo ayudarte?", "assistant");
  notice.hidden = true;
  input.focus();
});

function addMessage(text, role) {
  const article = document.createElement("article");
  article.className = `message ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  article.append(bubble);
  messages.append(article);
  scrollToBottom();
  return article;
}

function addTyping() {
  const article = document.createElement("article");
  article.className = "message assistant typing";
  article.setAttribute("aria-label", "El asistente está escribiendo");
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = "<span></span><span></span><span></span>";
  article.append(bubble);
  messages.append(article);
  scrollToBottom();
  return article;
}

function setWaiting(value) {
  waiting = value;
  sendButton.disabled = value;
  input.disabled = value;
  newChatButton.disabled = value;
}

function resizeInput() {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 150)}px`;
}

function scrollToBottom() {
  messages.scrollTop = messages.scrollHeight;
}
