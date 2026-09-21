import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";
import { connectDatabase } from "./database.js";
import { generateGeminiReply } from "./gemini.js";
import { catalogReply } from "./catalog.js";
import { customerRules, customerContext, customerReply } from "./customer-policy.js";

const root = fileURLToPath(new URL("./public", import.meta.url));

await loadEnv();
const provider = process.env.AI_PROVIDER || "openai";
if (!["openai", "gemini"].includes(provider)) throw new Error("AI_PROVIDER debe ser openai o gemini");
const apiKey = provider === "gemini" ? process.env.GEMINI_API_KEY : process.env.OPENAI_API_KEY;
let database;
try {
  database = await connectDatabase();
  console.log("Base de datos conectada.");
} catch (error) {
  console.error(`No se pudo conectar a MySQL (${error.code || "error"}). Revisa DB_HOST, DB_PORT, DB_USER, DB_PASSWORD y DB_NAME en .env.`);
  process.exit(1);
}

const port = Number(process.env.PORT || 3000);
const model = process.env.OPENAI_MODEL || "gpt-5.4-mini";
const instructions = process.env.BOT_INSTRUCTIONS ||
  "Eres un asistente de atención al cliente. Responde en español, con claridad y honestidad. No inventes información.";

const mimeTypes = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".svg": "image/svg+xml"
};

const server = createServer(async (request, response) => {
  try {
    if (request.method === "POST" && request.url === "/api/chat") {
      return await handleChat(request, response);
    }

    if (request.method === "DELETE" && request.url?.startsWith("/api/chat/")) {
      const sessionId = decodeURIComponent(request.url.slice("/api/chat/".length));
      if (!validSessionId(sessionId)) return sendJson(response, 400, { error: "Sesión inválida." });
      await database.deleteConversation(sessionId);
      return sendJson(response, 200, { ok: true });
    }

    if (request.method === "GET" && request.url?.startsWith("/api/chat/")) {
      const sessionId = decodeURIComponent(request.url.slice("/api/chat/".length));
      if (!validSessionId(sessionId)) return sendJson(response, 400, { error: "Sesión inválida." });
      return sendJson(response, 200, { messages: await database.getMessages(sessionId) });
    }

    if (request.method === "GET") {
      return await serveStatic(request.url || "/", response);
    }

    sendJson(response, 404, { error: "Ruta no encontrada" });
  } catch (error) {
    console.error(error);
    sendJson(response, 500, { error: "Ocurrió un error inesperado." });
  }
});

server.listen(port, () => {
  console.log(`Chatbot disponible en http://localhost:${server.address().port}`);
  console.log(`Proveedor: ${provider}; modelo: ${provider === "gemini" ? (process.env.GEMINI_MODEL || "gemini-3.5-flash-lite") : model}`);
  if (!apiKey) {
    console.log("Modo demostración activo: configura la clave del proveedor en .env para usar IA.");
  }
});

async function handleChat(request, response) {
  const body = await readJson(request);
  const message = String(body.message || "").trim();
  const sessionId = String(body.sessionId || "").trim();

  if (!message || !validSessionId(sessionId)) {
    return sendJson(response, 400, { error: "Faltan el mensaje o el identificador de sesión." });
  }

  if (message.length > 4000) {
    return sendJson(response, 400, { error: "El mensaje es demasiado largo." });
  }

  let businessInstructions = instructions;
  let internalCodes = [];
  if (apiKey) {
    const context = await database.getBusinessContext();
    internalCodes = context.properties.map(p => p.codigo);
    const directReply = catalogReply(message, context);
    if (directReply) {
      await database.saveTurn(sessionId, message, directReply);
      return sendJson(response, 200, { reply: directReply, demo: false });
    }
    businessInstructions += `\n${customerRules}\nSi truncated es true, las opciones son parciales y no puedes descartar otras.
CATALOGO_JSON: ${JSON.stringify(customerContext(context))}`;
  }

  if (apiKey && provider === "gemini") {
    const history = await database.getMessages(sessionId, true);
    let reply;
    try {
      reply = await generateGeminiReply({ apiKey, model: process.env.GEMINI_MODEL || "gemini-3.5-flash-lite", instructions: businessInstructions, history, message });
    } catch (error) {
      console.error("No se pudo generar la respuesta:", error.message);
      return sendJson(response, 502, { error: "No pude responder en este momento. Por favor, intenta de nuevo en unos momentos." });
    }
    reply = customerReply(reply, internalCodes);
    await database.saveTurn(sessionId, message, reply);
    return sendJson(response, 200, { reply, demo: false });
  }
  if (!apiKey) {
    const reply = demoReply(message);
    await database.saveTurn(sessionId, message, reply);
    return sendJson(response, 200, {
      reply,
      demo: true
    });
  }

  const previousResponseId = await database.getPreviousResponseId(sessionId);
  const payload = {
    model,
    instructions: businessInstructions,
    input: message,
    max_output_tokens: 500
  };

  if (previousResponseId) payload.previous_response_id = previousResponseId;

  const apiResponse = await fetch("https://api.openai.com/v1/responses", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  const data = await apiResponse.json();
  if (!apiResponse.ok) {
    const code = data.error?.code;
    console.error("OpenAI API:", { status: apiResponse.status, code, type: data.error?.type });
    let error = "No pude generar la respuesta. Revisa la configuración de OpenAI en el servidor.";
    if (code === "credit_balance_exhausted") {
      error = "El saldo de créditos de la API de OpenAI está agotado. Recarga el saldo en la sección Billing de OpenAI Platform para continuar.";
    } else if (data.error?.type === "insufficient_quota") {
      error = "La API de OpenAI no tiene cuota disponible. Revisa el saldo y los límites de uso en OpenAI Platform.";
    } else if (apiResponse.status === 401) {
      error = "OpenAI rechazó la clave API. Revisa OPENAI_API_KEY en .env y reinicia el servidor.";
    } else if (code === "model_not_found") {
      error = "El modelo configurado no existe o tu proyecto no tiene acceso. Revisa OPENAI_MODEL en .env.";
    } else if (apiResponse.status === 429) {
      error = "Se alcanzó el límite temporal de solicitudes de OpenAI. Espera un momento e intenta de nuevo.";
    }
    return sendJson(response, 502, {
      error: "No pude responder en este momento. Por favor, intenta de nuevo en unos momentos."
    });
  }

  const reply = customerReply(extractOutputText(data), internalCodes);
  await database.saveTurn(sessionId, message, reply, data.id);
  sendJson(response, 200, { reply, demo: false });
}

function validSessionId(value) {
  return /^[a-zA-Z0-9_-]{1,100}$/.test(value);
}

async function serveStatic(url, response) {
  const pathname = new URL(url, "http://localhost").pathname;
  const requested = pathname === "/" ? "index.html" : pathname.slice(1);
  const safePath = normalize(requested).replace(/^(\.\.(\\|\/|$))+/, "");
  const filePath = join(root, safePath);

  if (!filePath.startsWith(root)) {
    return sendJson(response, 403, { error: "Acceso denegado" });
  }

  try {
    const contents = await readFile(filePath);
    response.writeHead(200, {
      "Content-Type": mimeTypes[extname(filePath)] || "application/octet-stream",
      "Cache-Control": "no-store"
    });
    response.end(contents);
  } catch (error) {
    if (error.code === "ENOENT") return sendJson(response, 404, { error: "Archivo no encontrado" });
    throw error;
  }
}

function extractOutputText(data) {
  if (data.output_text) return data.output_text;
  return (data.output || [])
    .flatMap((item) => item.content || [])
    .filter((item) => item.type === "output_text")
    .map((item) => item.text)
    .join("\n") || "No pude elaborar una respuesta.";
}

function demoReply(message) {
  const text = message.toLowerCase();
  if (/hola|buen(os|as)|qué tal|que tal/.test(text)) {
    return "¡Hola! Soy el asistente virtual. ¿En qué puedo ayudarte hoy?";
  }
  if (/precio|costo|cuánto|cuanto/.test(text)) {
    return "Puedo ayudarte con precios, pero primero necesito saber qué producto o servicio te interesa.";
  }
  if (/pedido|envío|envio|entrega/.test(text)) {
    return "Con gusto revisamos tu pedido. En una versión conectada podría solicitar el número de pedido y consultar su estado.";
  }
  return "Entendí tu mensaje. Ahora estoy en modo demostración; configura la clave del proveedor de IA en .env para generar respuestas inteligentes y contextuales.";
}

function sendJson(response, status, body) {
  response.writeHead(status, { "Content-Type": "application/json; charset=utf-8" });
  response.end(JSON.stringify(body));
}

async function readJson(request) {
  let raw = "";
  for await (const chunk of request) {
    raw += chunk;
    if (raw.length > 20_000) throw new Error("Solicitud demasiado grande");
  }
  try {
    return JSON.parse(raw || "{}");
  } catch {
    return {};
  }
}

async function loadEnv() {
  try {
    const file = await readFile(fileURLToPath(new URL("./.env", import.meta.url)), "utf8");
    for (const line of file.split(/\r?\n/)) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;
      const separator = trimmed.indexOf("=");
      if (separator < 1) continue;
      const key = trimmed.slice(0, separator).trim();
      const value = trimmed.slice(separator + 1).trim().replace(/^['"]|['"]$/g, "");
      if (process.env[key] === undefined) process.env[key] = value;
    }
  } catch (error) {
    if (error.code !== "ENOENT") throw error;
  }
}
