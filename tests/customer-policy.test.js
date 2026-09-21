import test from "node:test";
import assert from "node:assert/strict";
import { customerContext, customerReply } from "../customer-policy.js";

test("el contexto público excluye códigos e importes de moneda desconocida", () => {
  const result = customerContext({ properties: [{ codigo: "CN-C03", precio: "2890000", nombre: "Gran Ceiba" }], faqs: [] });
  assert.deepEqual(result.properties, [{ nombre: "Gran Ceiba" }]);
});

test("bloquea las filtraciones reportadas y conserva recomendaciones comerciales", () => {
  for (const text of ["(Código: `CN-C03`)", "La base de datos no especifica la moneda", "Error Gemini API"]) {
    assert.doesNotMatch(customerReply(text, ["CN-C03"]), /CN-C03|base de datos|Gemini|API/);
  }
  const reply = "Te recomiendo Gran Ceiba por sus tres recámaras y jardín.";
  assert.equal(customerReply(reply, ["CN-C03"]), reply);
});
