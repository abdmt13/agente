import test from "node:test";
import assert from "node:assert/strict";
import { catalogReply } from "../catalog.js";

test("disponibilidad responde con catálogo y costa no inventa distancias ni moneda", () => {
  const context = { properties: [{ codigo: "P1", nombre: "Casa prueba", tipo: "Casa", precio: "1000000", ciudad: "Merida", zona: "Norte" }], truncated: false };
  const reply = catalogReply("quiero adquirir una propiedad de ustedes, cuales son las disponibles", context);
  assert.match(reply, /Casa prueba/);
  assert.doesNotMatch(reply, /P1|1,000,000|moneda|base de datos/);
  assert.match(reply, /confirmación con un asesor/);
  assert.match(catalogReply("quiero una propiedad cerca de la costa, mi presupuesto es de un millon de dolares", context), /Necesitamos confirmar/);
  assert.equal(catalogReply("quiero un departamento hasta 1000000", context), null);
  assert.equal(catalogReply("cuáles son las disponibles con 3 recámaras", context), null);
});
