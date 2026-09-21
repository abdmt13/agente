---
name: reglas-chat-inmobiliario
description: Configura reglas de conversación para un chatbot inmobiliario con catálogo, recomendaciones basadas en datos y respuestas sin códigos internos ni detalles del backend. Úsala para aplicar o adaptar este comportamiento en una demo o proyecto de producción.
---

# Reglas del chat inmobiliario

Esta skill guía cambios en una aplicación; por sí sola no modifica el comportamiento del modelo servido por una API.

1. Identifica dónde se construyen las instrucciones del modelo, el contexto de propiedades y las respuestas directas. Lee [las reglas de atención](references/asesor-inmobiliario.md) y adáptalas al negocio sin inventar datos.
2. Guarda las reglas en un archivo versionado del proyecto y cárgalas en el servidor como instrucciones en cada solicitud al proveedor. No dependas de una skill de Codex instalada en el equipo del desarrollador para ejecutar la aplicación.
3. Entrega al modelo solo los campos necesarios para orientar al cliente. Mantén códigos e identificadores para las operaciones internas del servidor; presenta nombres y desarrollos al usuario. Si no se conoce la moneda, omite el importe hasta confirmarla. Si producción sí registra moneda, presenta precio y moneda explícitos.
4. Aplica las mismas reglas de presentación a plantillas, errores y respuestas generadas. Conserva los diagnósticos técnicos en registros del servidor. Un filtro de salida puede servir como barrera adicional, pero no garantiza por sí solo el cumplimiento de todas las reglas.
5. Conserva recomendaciones útiles: explica coincidencias con recámaras, ubicación, superficie y preferencias usando datos verificados. No confundas ausencia de información con ausencia de propiedades que cumplan una condición.
6. Prueba disponibilidad, recomendación personalizada, presupuesto en otra moneda, cercanía a la playa sin distancia registrada, petición de códigos internos y fallo del proveedor. Verifica que no aparezcan códigos ni detalles de implementación y que no se inventen condiciones comerciales. Comprueba también las rutas que no llaman al modelo.

Para trasladar a producción, prepara los archivos y pruebas dentro del proyecto autorizado. No publiques ni cambies infraestructura por el solo hecho de invocar esta skill. Explica qué reglas carga realmente la aplicación, cómo editarlas y si requiere reinicio. Los mensajes históricos pueden conservar el formato anterior; no los borres sin que se solicite.
