import { getStore } from '@netlify/blobs';

// Registra un clic de CTA (llamar / whatsapp / email / mapa / formulario)
// con fecha + página + sección. Almacena en Netlify Blobs (store "cta-events").
// Endpoint: POST /.netlify/functions/track   body JSON {cta, section, page, ts}
export default async (req) => {
  if (req.method !== 'POST') return new Response('', { status: 405 });

  let d;
  try { d = await req.json(); } catch { return new Response('', { status: 400 }); }

  const clean = (s, n) => String(s == null ? '' : s).replace(/[\r\n\t]+/g, ' ').slice(0, n);
  const ts = /^\d{4}-\d{2}-\d{2}T/.test(d.ts) ? d.ts : new Date().toISOString();
  const rec = {
    cta: clean(d.cta, 24),
    section: clean(d.section, 40),
    page: clean(d.page, 160) || '/',
    ref: clean(req.headers.get('referer'), 160),
    ua: /Mobi|Android|iPhone/i.test(req.headers.get('user-agent') || '') ? 'movil' : 'escritorio',
    ts,
  };
  if (!rec.cta) return new Response('', { status: 400 });

  try {
    const store = getStore('cta-events');
    const day = ts.slice(0, 10);
    const key = `${day}/${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    await store.setJSON(key, rec);
  } catch (e) {
    return new Response('store error', { status: 500 });
  }
  return new Response('ok', { status: 200, headers: { 'cache-control': 'no-store' } });
};
