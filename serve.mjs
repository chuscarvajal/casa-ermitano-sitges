import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, 'public');
const PORT = Number(process.env.PORT || 3000);

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
  '.woff': 'font/woff',
};

function send(res, code, body, type = 'text/plain; charset=utf-8') {
  res.writeHead(code, { 'Content-Type': type, 'Cache-Control': 'no-store' });
  res.end(body);
}

const server = http.createServer((req, res) => {
  const urlPath = decodeURIComponent(req.url.split('?')[0]);
  let filePath = path.join(ROOT, urlPath === '/' ? '/index.html' : urlPath);
  if (!filePath.startsWith(ROOT)) return send(res, 403, 'forbidden');
  fs.stat(filePath, (err, st) => {
    if (err || !st) return send(res, 404, 'not found');
    if (st.isDirectory()) filePath = path.join(filePath, 'index.html');
    const ext = path.extname(filePath).toLowerCase();
    fs.readFile(filePath, (e, buf) => {
      if (e) return send(res, 404, 'not found');
      send(res, 200, buf, MIME[ext] || 'application/octet-stream');
    });
  });
});

function listen(p) {
  server.once('error', (err) => {
    if (err.code === 'EADDRINUSE' && p < PORT + 10) {
      console.log(`port ${p} busy, trying ${p + 1}`);
      listen(p + 1);
    } else {
      console.error(err);
      process.exit(1);
    }
  });
  server.listen(p, () => console.log(`serving ${ROOT} at http://localhost:${p}`));
}
listen(PORT);
