// Respuestas acotadas a consultas generales; los demás filtros los interpreta la IA.
export function catalogReply(message, { properties, truncated }) {
  const text = message.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase();
  const coastal = /\b(costa|playa|mar)\b/.test(text) && /\b(propiedad|casa|departamento|terreno|inmueble)\b/.test(text);
  const general = /(?:(?:cuales|que)\s+(?:son\s+)?(?:las\s+)?(?:propiedades\s+|opciones\s+|casas\s+)?(?:disponibles|tienen)|que\s+(?:propiedades|opciones|casas)\s+(?:hay|tienen))[?¿.!\s]*$/.test(text)
    && !/\b(presupuesto|menos|hasta|recamaras|zona|costa|playa|departamento|terreno)\b|\d/.test(text);
  if (!coastal && !general) return null;
  if (coastal) {
    return "Necesitamos confirmar qué opciones están cerca de la playa y sus precios antes de compararlas con tu presupuesto. ¿Qué ciudad o playa te interesa?";
  }
  if (!properties.length) return "Por ahora no tenemos propiedades disponibles para mostrarte.";
  const options = properties.slice(0, 5).map(p => `${p.nombre}${p.desarrollo ? `, en ${p.desarrollo}` : ""}: ${p.tipo}, ${[p.ciudad, p.zona].filter(Boolean).join(", ") || "ubicación por confirmar"}.`);
  return `${truncated || properties.length > 5 ? "Estas son algunas opciones" : "Estas son las opciones"} disponibles:\n\n${options.join("\n\n")}\n\nLos precios están pendientes de confirmación con un asesor. ¿Qué opción te interesa?`;
}
