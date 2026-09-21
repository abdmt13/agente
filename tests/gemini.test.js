import test from "node:test";
import assert from "node:assert/strict";
import { generateGeminiReply } from "../gemini.js";

test("Gemini: petición breve, historial, errores y tiempo de lectura", async (t) => {
  const args = { apiKey: "test", model: "gemini-3.6-flash", instructions: "Ayuda", message: "hola",
    history: [{ role: "user", content: "antes" }, { role: "assistant", content: "respuesta" }] };
  const mock = t.mock.method(globalThis, "fetch", async (url, options) => {
    const body = JSON.parse(options.body);
    assert.equal(body.generationConfig.thinkingConfig.thinkingLevel, "minimal");
    assert.equal(body.generationConfig.maxOutputTokens, 768);
    assert.equal(body.contents[1].role, "model");
    assert.equal(body.contents.at(-1).parts[0].text, "hola");
    return { ok: true, status: 200, json: async () => ({ candidates: [{ content: { parts: [{ text: "Hola" }] } }] }) };
  });
  assert.equal(await generateGeminiReply(args), "Hola");
  mock.mock.mockImplementation(async () => ({ok:false,status:429,json:async()=>({error:{status:"RESOURCE_EXHAUSTED"}})}));
  await assert.rejects(generateGeminiReply(args), /cuota/);
  mock.mock.mockImplementation(async () => { throw new TypeError("fetch failed"); });
  await assert.rejects(generateGeminiReply(args), /conexión/);
  mock.mock.mockImplementation(async () => ({ok:true,status:200,json:async()=>{throw new DOMException("timeout", "TimeoutError");}}));
  await assert.rejects(generateGeminiReply(args), /no respondió/);
});

test("Gemini recupera un 503 con un único reintento y comparte el límite de tiempo", async (t) => {
  const signals = [];
  const mock = t.mock.method(globalThis, "fetch", async (url, options) => {
    signals.push(options.signal);
    if (signals.length === 1) return { ok: false, status: 503, json: async () => ({ error: { status: "UNAVAILABLE" } }) };
    return { ok: true, status: 200, json: async () => ({ candidates: [{ content: { parts: [{ thought: true, text: "oculto" }, { text: "Disponible" }] } }] }) };
  });
  assert.equal(await generateGeminiReply({ apiKey: "test", model: "gemini-3.5-flash-lite", instructions: "Ayuda", message: "propiedades" }), "Disponible");
  assert.equal(mock.mock.callCount(), 2);
  assert.equal(signals[0], signals[1]);
  mock.mock.mockImplementation(async () => ({ ok: false, status: 503, json: async () => ({}) }));
  await assert.rejects(generateGeminiReply({ apiKey: "test", model: "gemini-3.5-flash-lite", instructions: "Ayuda", message: "hola" }), /temporalmente/);
  assert.equal(mock.mock.callCount(), 4);
});
