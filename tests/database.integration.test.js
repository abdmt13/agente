import test from "node:test";
import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { connectDatabase } from "../database.js";

test("MySQL: guardar, reconectar, consultar y borrar una sesión", async () => {
  const sessionId = randomUUID();
  let db = await connectDatabase();
  try {
    const catalog = await db.getBusinessContext();
    assert.ok(Array.isArray(catalog.properties));
    assert.ok(Array.isArray(catalog.faqs));
    await db.saveTurn(sessionId, "Información: café ☕ ' ?", "Respuesta de prueba", "response-test");
    await db.close();
    db = await connectDatabase();
    assert.equal(await db.getPreviousResponseId(sessionId), "response-test");
    assert.deepEqual(await db.getMessages(sessionId, true), await db.getMessages(sessionId));
    assert.deepEqual(await db.getMessages(sessionId), [
      { role: "user", content: "Información: café ☕ ' ?" },
      { role: "assistant", content: "Respuesta de prueba" }
    ]);
    await db.deleteConversation(sessionId);
    assert.deepEqual(await db.getMessages(sessionId), []);
    assert.equal(await db.getPreviousResponseId(sessionId), undefined);
  } finally {
    await db.deleteConversation(sessionId);
    await db.close();
  }
});

test("HTTP: modo demo e historial después de reiniciar el servidor", async () => {
  const sessionId = randomUUID();
  let child;
  let base;
  async function start() {
    child = spawn(process.execPath, ["server.js"], {
      env: { ...process.env, AI_PROVIDER: "gemini", GEMINI_API_KEY: "", OPENAI_API_KEY: "", PORT: "0" },
      stdio: ["ignore", "pipe", "pipe"]
    });
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error("El servidor no inició")), 10000);
      child.once("exit", () => { clearTimeout(timer); reject(new Error("El servidor terminó")); });
      child.once("error", (error) => { clearTimeout(timer); reject(error); });
      child.stdout.on("data", (data) => {
        const match = data.toString().match(/http:\/\/localhost:(\d+)/);
        if (match) { base = match[0]; clearTimeout(timer); resolve(); }
      });
    });
  }
  async function stop() {
    if (child && child.exitCode === null) {
      const exited = once(child, "exit");
      child.kill();
      await exited;
    }
  }
  try {
    await start();
    const response = await fetch(`${base}/api/chat`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sessionId, message: "hola" })
    });
    assert.equal(response.status, 200);
    assert.equal((await response.json()).demo, true);
    await stop();
    await start();
    const history = await (await fetch(`${base}/api/chat/${sessionId}`)).json();
    assert.equal(history.messages.length, 2);
    assert.equal(history.messages[0].content, "hola");
    assert.equal((await fetch(`${base}/api/chat/${sessionId}`, { method: "DELETE" })).status, 200);
    const empty = await (await fetch(`${base}/api/chat/${sessionId}`)).json();
    assert.deepEqual(empty.messages, []);
  } finally {
    await stop();
    const db = await connectDatabase();
    try { await db.deleteConversation(sessionId); } finally { await db.close(); }
  }
});
