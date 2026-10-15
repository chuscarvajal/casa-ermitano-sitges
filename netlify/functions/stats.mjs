import { getStore } from '@netlify/blobs';

// Panel privado de clics de CTA. Protegido por ?key=
// Uso:   /.netlify/functions/stats?key=CLAVE
//        ...&format=json  |  ...&format=csv  |  ...&days=7
//        ...&action=reset&confirm=si   (borra todos los registros: útil para limpiar pruebas)
//
// Config por variables de entorno de Netlify (recomendado):
//   CTA_STATS_KEY  -> clave de acceso al panel (pon una única por proyecto)
//   CTA_SITE_NAME  -> nombre que sale en la cabecera del panel
const env = (k) => (globalThis.Netlify?.env?.get?.(k)) || process.env[k];
const SECRET = () => env('CTA_STATS_KEY') || 'ermitano-cta-7b82ccde2db1';
const SITE = () => env('CTA_SITE_NAME') || 'Casa del Ermitaño';

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function tally(events, field) {
  const m = new Map();
  for (const e of events) m.set(e[field] || '—', (m.get(e[field] || '—') || 0) + 1);
  return [...m.entries()].sort((a, b) => b[1] - a[1]);
}
function table(title, rows, c1) {
  const max = rows.reduce((a, r) => Math.max(a, r[1]), 0) || 1;
  const body = rows.map(([k, v]) =>
    `<tr><td>${esc(k)}</td><td class="n">${v}</td><td class="barcell"><span class="bar" style="width:${(v / max * 100).toFixed(1)}%"></span></td></tr>`).join('');
  return `<section><h2>${esc(title)}</h2><div class="tw"><table><thead><tr><th scope="col">${esc(c1)}</th><th scope="col" class="n">Clics</th><th aria-hidden="true"></th></tr></thead><tbody>${body || '<tr><td colspan="3">Sin datos todavía.</td></tr>'}</tbody></table></div></section>`;
}

export default async (req) => {
  const url = new URL(req.url);
  if (url.searchParams.get('key') !== SECRET()) {
    return new Response('No autorizado. Añade ?key=TU_CLAVE a la URL.', { status: 401 });
  }

  const store = getStore('cta-events');

  // Borrado de datos (para limpiar pruebas): ?action=reset&confirm=si
  if (url.searchParams.get('action') === 'reset' && url.searchParams.get('confirm') === 'si') {
    const { blobs } = await store.list();
    await Promise.all(blobs.map((b) => store.delete(b.key).catch(() => {})));
    return new Response(`Borrados ${blobs.length} registros.`, { status: 200, headers: { 'cache-control': 'no-store' } });
  }

  let events = [];
  try {
    const { blobs } = await store.list();
    events = (await Promise.all(blobs.map((b) => store.get(b.key, { type: 'json' }).catch(() => null)))).filter(Boolean);
  } catch (e) {
    return new Response('store error: ' + e.message, { status: 500 });
  }

  const days = parseInt(url.searchParams.get('days') || '0', 10);
  if (days > 0) {
    const cut = new Date(Date.now() - days * 86400000).toISOString();
    events = events.filter((e) => (e.ts || '') >= cut);
  }
  events.sort((a, b) => (b.ts || '').localeCompare(a.ts || ''));

  if (url.searchParams.get('format') === 'json') {
    return Response.json({ total: events.length, events });
  }
  if (url.searchParams.get('format') === 'csv') {
    const head = 'fecha,hora,cta,seccion,pagina,dispositivo\n';
    const rows = events.map((e) => {
      const [f, h] = (e.ts || '').split('T');
      return [f, (h || '').slice(0, 8), e.cta, e.section, e.page, e.ua].map((x) => `"${String(x || '').replace(/"/g, '""')}"`).join(',');
    }).join('\n');
    return new Response(head + rows, { headers: { 'content-type': 'text/csv; charset=utf-8', 'content-disposition': 'attachment; filename="cta-clics.csv"' } });
  }

  const dateAgg = [...events.reduce((m, e) => m.set((e.ts || '').slice(0, 10), (m.get((e.ts || '').slice(0, 10)) || 0) + 1), new Map())].sort((a, b) => b[0].localeCompare(a[0]));
  const recent = events.slice(0, 60).map((e) => {
    const [f, h] = (e.ts || '').split('T');
    return `<tr><td>${esc(f)} ${esc((h || '').slice(0, 5))}</td><td><span class="pill p-${esc(e.cta)}">${esc(e.cta)}</span></td><td>${esc(e.section)}</td><td class="pg">${esc(e.page)}</td><td>${esc(e.ua)}</td></tr>`;
  }).join('');
  const k = esc(url.searchParams.get('key'));

  const html = `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><meta name="theme-color" content="#0e0e0e"><title>Clics de CTA · ${esc(SITE())}</title><style>
  :root{--ink:#0e0e0e;--y:#f5c400;--line:#e7e7e2;--muted:#6c6c6c;--bg:#faf9f6}
  *{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:#1a1a1a;line-height:1.5}
  header{background:var(--ink);color:#fff;padding:22px 24px}
  header h1{margin:0;font-size:20px}header p{margin:4px 0 0;color:#bdbdbd;font-size:13px}
  .wrap{max-width:1080px;margin:0 auto;padding:24px}
  .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:14px;margin-bottom:26px}
  .kpi{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 18px}
  .kpi .v{font-size:30px;font-weight:800;color:var(--ink)}.kpi .k{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
  section{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-bottom:20px}
  h2{font-size:15px;margin:0 0 12px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
  table{width:100%;border-collapse:collapse;font-size:14px}
  th,td{text-align:left;padding:7px 8px;border-bottom:1px solid #f0efe9}
  th{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
  td.n,th.n{text-align:right;font-variant-numeric:tabular-nums;font-weight:700;width:70px}
  td.pg{color:var(--muted);font-size:12px;max-width:360px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .barcell{width:40%}.bar{display:block;height:9px;border-radius:5px;background:var(--y)}
  .pill{display:inline-block;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700}
  .p-llamar{background:#fde68a}.p-whatsapp{background:#bbf7d0}.p-email{background:#e0e7ff}.p-formulario{background:#fbcfe8}.p-mapa{background:#e2e8f0}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px}@media(max-width:720px){.grid2{grid-template-columns:1fr}}
  .tools a{display:inline-block;margin-right:12px;color:#1a56db;font-size:13px}
  .tw{overflow-x:auto;-webkit-overflow-scrolling:touch}
  header h1,h2{text-wrap:balance}
  html{color-scheme:light}
  .tools a:hover{text-decoration:underline}
  </style></head><body>
  <header><h1>Clics de CTA · ${esc(SITE())}</h1><p>Cuánta gente pulsa Llamar / WhatsApp / formulario, por fecha · página · sección${days ? ` · últimos ${days} días` : ' · todo el histórico'}</p></header>
  <main class="wrap">
    <div class="kpis">
      <div class="kpi"><div class="v">${events.length}</div><div class="k">Clics totales</div></div>
      <div class="kpi"><div class="v">${(tally(events, 'cta').find((r) => r[0] === 'llamar') || [0, 0])[1]}</div><div class="k">📞 Llamar</div></div>
      <div class="kpi"><div class="v">${(tally(events, 'cta').find((r) => r[0] === 'whatsapp') || [0, 0])[1]}</div><div class="k">💬 WhatsApp</div></div>
      <div class="kpi"><div class="v">${(tally(events, 'cta').find((r) => r[0] === 'formulario') || [0, 0])[1]}</div><div class="k">📝 Formulario</div></div>
    </div>
    <p class="tools">Exportar: <a href="?key=${k}&format=csv">CSV</a><a href="?key=${k}&format=json">JSON</a> · Filtrar: <a href="?key=${k}&days=7">7 días</a><a href="?key=${k}&days=30">30 días</a><a href="?key=${k}">Todo</a></p>
    ${table('Por fecha', dateAgg, 'Día')}
    <div class="grid2">${table('Por tipo de CTA', tally(events, 'cta'), 'CTA')}${table('Por dispositivo', tally(events, 'ua'), 'Dispositivo')}</div>
    <div class="grid2">${table('Por sección', tally(events, 'section'), 'Sección')}${table('Por página', tally(events, 'page'), 'Página')}</div>
    <section><h2>Últimos clics (60)</h2><div class="tw"><table><thead><tr><th scope="col">Fecha</th><th scope="col">CTA</th><th scope="col">Sección</th><th scope="col">Página</th><th scope="col">Disp.</th></tr></thead><tbody>${recent || '<tr><td colspan="5">Sin clics todavía. Prueba a pulsar un botón de la web.</td></tr>'}</tbody></table></div></section>
  </main></body></html>`;

  return new Response(html, { headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store' } });
};
