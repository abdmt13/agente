import http from "node:http";

const fastApiPrefixes = [
  "/api/v1",
  "/personal",
  "/docs",
  "/redoc",
  "/openapi.json",
  "/metrics",
];

const server = http.createServer((request, response) => {
  const pathname = new URL(request.url ?? "/", "http://localhost").pathname;
  const useFastApi = fastApiPrefixes.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`),
  );
  const upstream = http.request(
    {
      hostname: "127.0.0.1",
      port: useFastApi ? 8000 : 3000,
      method: request.method,
      path: request.url,
      headers: request.headers,
    },
    (upstreamResponse) => {
      response.writeHead(upstreamResponse.statusCode ?? 502, upstreamResponse.headers);
      upstreamResponse.pipe(response);
    },
  );

  upstream.on("error", (error) => {
    if (!response.headersSent) {
      response.writeHead(502, { "content-type": "text/plain; charset=utf-8" });
    }
    response.end(`Upstream unavailable: ${error.message}`);
  });
  request.pipe(upstream);
});

server.listen(8080, "127.0.0.1", () => {
  console.log("Dual-service proxy listening on http://127.0.0.1:8080");
});
