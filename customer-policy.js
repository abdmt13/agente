import { readFile } from "node:fs/promises";

export const customerRules = await readFile(new URL("./prompts/asesor-inmobiliario.md", import.meta.url), "utf8");

export function customerContext(context) {
  return {
    ...context,
    properties: context.properties.map(({ codigo, precio, ...property }) => property)
  };
}

// Barrera adicional: no publicar una respuesta técnica ni códigos conocidos.
// No sustituye las reglas ni constituye un filtro completo de información sensible.
export function customerReply(reply, codes = []) {
  const technical = /base\s+de\s+datos|\b(?:backend|mysql|sql|json|gemini|openai|api|prompt|prompts|GEMINI_API_KEY|OPENAI_API_KEY)\b/i;
  if (technical.test(reply) || codes.some(code => code && reply.toLowerCase().includes(code.toLowerCase()))) {
    return "Necesito confirmar algunos detalles para orientarte mejor. ¿Qué característica es la más importante para ti en tu próxima propiedad?";
  }
  return reply;
}
