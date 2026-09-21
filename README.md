# Chatbot IA

MVP de un asistente conversacional: el cliente escribe libremente y recibe una respuesta contextual, sin formularios ni menús rígidos.

## Configurar Gemini

En `.env`, usa `AI_PROVIDER=gemini`, `GEMINI_API_KEY=tu_clave` y `GEMINI_MODEL=gemini-3.5-flash-lite`. Reinicia con `npm start` después de cambiar la configuración. La clave se envía únicamente desde el servidor a Google. No uses `OPENAI_API_KEY` para una clave de Gemini.

Gemini recibe los últimos 20 mensajes de la sesión guardados en MySQL y las instrucciones de `BOT_INSTRUCTIONS`. Para volver a OpenAI, usa `AI_PROVIDER=openai` y una clave propia de OpenAI. Sin clave del proveedor seleccionado, se activa el modo demostración.

Para atención al cliente se usa `GEMINI_THINKING_LEVEL=minimal` y un máximo de 768 tokens de salida. Puedes cambiar el esfuerzo de razonamiento en `.env` según el modelo. `GEMINI_TIMEOUT_MS` permite configurar la espera entre 1000 y 120000 milisegundos (15000 por defecto, compartidos entre los dos intentos). La consola muestra el tiempo y estado de cada solicitud sin registrar claves ni mensajes. El navegador avisa después de 10 segundos y recupera el texto enviado si ocurre un error. La respuesta se muestra completa al terminar la generación.

## Requisitos de ejecución

- Node.js 20 o superior.
- MySQL en ejecución y una base de datos existente (`agentevirtualmvp`).
- Una API key del proveedor seleccionado para activar la IA. Sin ella, la aplicación funciona en modo demostración.

## Ejecutar

1. Abre una terminal dentro de esta carpeta.
2. Si todavía no existe `.env`, copia `.env.example` como `.env`.
3. Coloca tu API key en `GEMINI_API_KEY` y usa `AI_PROVIDER=gemini`.
4. Personaliza `BOT_INSTRUCTIONS` con el nombre, políticas y tono de tu negocio.
5. Configura `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` y `DB_NAME` en `.env`.
6. Ejecuta:

```powershell
npm install
npm start
```

7. Abre <http://localhost:3000>.

El proyecto utiliza `mysql2` para conectarse a MySQL desde el servidor. Las credenciales permanecen en `.env`, que está excluido de Git.

## Base de datos de la demo

La configuración local usa el servidor `127.0.0.2`, puerto `3306`, usuario `root` y base `agentevirtualmvp`. `127.0.0.2` es una dirección IP, no un puerto. Coloca la contraseña en `DB_PASSWORD`; no la agregues al código ni a `.env.example`.

Al iniciar, el servidor crea las tablas `chatbot_conversations` y `chatbot_messages` si no existen. El usuario de MySQL necesita permisos para crear tablas, consultar, insertar, actualizar y eliminar registros en esa base. No se crean ni modifican tablas del negocio.

Cada intercambio guarda ambos mensajes en una transacción, incluso sin clave de OpenAI. El identificador de contexto de OpenAI también se guarda para continuar la sesión tras reiniciar el servidor. Al recargar la pestaña se consulta el historial de MySQL; «Nueva conversación» elimina la conversación anterior y sus mensajes. La sesión del navegador se conserva en `sessionStorage` durante la vida de la pestaña.

Si MySQL no está disponible, el servidor no inicia y muestra el código del error. Revisa que el servicio esté activo, el puerto y las credenciales sean correctos y la base exista.

La conexión guarda conversaciones y consulta propiedades disponibles de desarrollos activos y preguntas frecuentes antes de responder. Se envían al proveedor hasta 50 propiedades y 30 preguntas frecuentes; nunca datos de clientes o citas. Las tablas `propiedades`, `desarrollos` y `preguntas_frecuentes` deben existir con el esquema de la base de prueba. El catálogo no registra moneda; el asistente debe aclararla y no comparar precios con presupuestos en USD sin confirmación.

La dirección `127.0.0.2` apunta a esta computadora. Para una demo remota, el servidor debe poder acceder a MySQL y el cliente debe abrir la dirección donde se aloje la aplicación.

## Estructura

```text
chatbot-ia/
├── public/
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── .env.example
├── .gitignore
├── package.json
├── database.js
└── server.js
```

## Qué incluye

- Interfaz adaptable a móvil y escritorio.
- Mensajes escritos en lenguaje natural.
- Memoria por sesión mediante `previous_response_id` persistido en MySQL.
- Historial de mensajes en MySQL y recuperación al recargar la pestaña.
- Clave de OpenAI protegida en el backend.
- Instrucciones configurables.
- Indicador de escritura, manejo de errores y nueva conversación.
- Modo demostración sin API key.

## Antes de producción

- Usar un usuario MySQL dedicado con permisos limitados en lugar de `root`.
- Autenticar usuarios y limitar solicitudes.
- Agregar moderación, métricas y transferencia a una persona.
- Conectar funciones controladas para pedidos, citas o inventario.
- Incorporar una base de conocimiento con información verificada del negocio.

La implementación usa la Responses API siguiendo la documentación oficial:
<https://developers.openai.com/api/reference/typescript/resources/beta/subresources/responses/methods/create>

## Reglas de conversación

Edita `prompts/asesor-inmobiliario.md` y reinicia con `npm start` para probar cambios. El servidor carga esas reglas para Gemini y OpenAI. Las respuestas directas se definen en `catalog.js` y deben mantener el mismo estilo. `customer-policy.js` excluye códigos e importes sin moneda del contexto de propiedades y añade una barrera de salida para referencias técnicas conocidas. No es una garantía general contra toda filtración.

La skill reutilizable está en `skills/reglas-chat-inmobiliario/SKILL.md`; sirve para adaptar estas reglas en otros proyectos de Codex. El chatbot ejecutado consume el archivo de instrucciones, no la skill. Los mensajes ya guardados conservan su texto anterior; inicia una conversación nueva para evaluar las nuevas reglas.

Los precios se omiten mientras no se conozca su moneda. Al incorporar moneda al esquema de producción, actualiza la proyección y las plantillas para mostrar precios con su moneda y validar presupuestos.

Las preguntas generales de disponibilidad y las consultas de propiedades cerca de la costa tienen respuestas directas desde el catálogo, sin esperar a Gemini. No se afirman distancias ni se comparan monedas sin información registrada. Las demás consultas usan IA con contexto del catálogo; la latencia del proveedor puede variar.

## Verificación para el despliegue de pruebas

Ejecuta `npm test` y `npm run test:integration`. La integración crea una sesión temporal, verifica persistencia tras reiniciar y elimina solo esa sesión.

El modelo predeterminado es `gemini-3.5-flash-lite`. Ante HTTP 500, 502, 503 o 504 se realiza un único reintento tras 250 ms; `GEMINI_FALLBACK_MODEL` permite elegir otro modelo (por defecto el mismo). No se reintentan errores de cuota ni credenciales. Ambos intentos comparten el límite `GEMINI_TIMEOUT_MS=15000`. Reinicia el proceso tras actualizar `.env`.

Para un servidor remoto configura las variables del proveedor y MySQL en el alojamiento. La dirección local 127.0.0.2 no permite acceder desde otro equipo a esta base: necesitas una instancia accesible desde el servidor y trasladar allí el esquema y los datos de prueba. No se ha realizado un despliegue ni una migración remota.
