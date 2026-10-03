"""Genera el informe de Search Console (oct 2026) para Eduardo: HTML A4 + PDF."""
import datetime as dt, io, collections, asyncio, pathlib
import openpyxl

BASE = pathlib.Path(__file__).parent
XLSX = BASE / "https___criaderocasadelermitano.es_-Performance-on-Search-2026-10-03.xlsx"
ASSETS = (BASE.parent / "public" / "assets").as_uri()

wb = openpyxl.load_workbook(XLSX, read_only=True)
rows = list(wb["Gráfico"].iter_rows(values_only=True))[1:]
daily = {r[0].date(): (r[1] or 0, r[2] or 0) for r in rows}

def period(a, b):
    c = i = n = 0
    x = a
    while x <= b:
        if x in daily:
            c += daily[x][0]; i += daily[x][1]; n += 1
        x += dt.timedelta(days=1)
    return c, i, n

P = [("13-29 ago", period(dt.date(2026, 8, 13), dt.date(2026, 8, 29))),
     ("30 ago-15 sep", period(dt.date(2026, 8, 30), dt.date(2026, 9, 15))),
     ("16 sep-2 oct", period(dt.date(2026, 9, 16), dt.date(2026, 10, 2)))]

weeks = collections.OrderedDict()
for d in sorted(daily):
    wk = d - dt.timedelta(days=d.weekday())
    c, i, n = weeks.get(wk, (0, 0, 0))
    weeks[wk] = (c + daily[d][0], i + daily[d][1], n + 1)

total_clicks = sum(v[0] for v in daily.values())
total_impr = sum(v[1] for v in daily.values())

GOLD, BROWN, INK, MUTED, GRID = "#b77a1c", "#5a3a10", "#2a1a08", "#7a6448", "#e7dccb"
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

def fmt(x, dec=1):
    return f"{x:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ---------- grafico 1: clics/dia semanales (linea) ----------
def line_chart():
    W, H, L, R, T, B = 720, 260, 44, 20, 20, 40
    pts = [(k, v[0] / v[2]) for k, v in weeks.items()]
    ymax = 5
    xs = lambda i: L + i * (W - L - R) / (len(pts) - 1)
    ys = lambda v: T + (H - T - B) * (1 - v / ymax)
    g = []
    for t in range(0, ymax + 1):
        y = ys(t)
        g.append(f'<line x1="{L}" x2="{W-R}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        g.append(f'<text x="{L-8}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="{MUTED}">{t}</text>')
    path = " ".join(f'{"M" if i==0 else "L"}{xs(i):.1f},{ys(v):.1f}' for i, (_, v) in enumerate(pts))
    area = path + f" L{xs(len(pts)-1):.1f},{ys(0):.1f} L{xs(0):.1f},{ys(0):.1f} Z"
    g.append(f'<path d="{area}" fill="{GOLD}" opacity="0.12"/>')
    g.append(f'<path d="{path}" fill="none" stroke="{GOLD}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>')
    for i, (k, v) in enumerate(pts):
        if i % 2 == 0 or i == len(pts) - 1:
            g.append(f'<text x="{xs(i):.1f}" y="{H-B+18}" text-anchor="middle" font-size="11" fill="{MUTED}">{k.day} {MESES[k.month-1]}</text>')
    # marca del inicio de las mejoras y ultimo valor
    imp = list(weeks).index(dt.date(2026, 9, 14))
    x = xs(imp)
    g.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{T}" y2="{H-B}" stroke="{BROWN}" stroke-dasharray="4 4" stroke-width="1.2"/>')
    g.append(f'<text x="{x-6:.1f}" y="{T+12}" text-anchor="end" font-size="11" fill="{BROWN}" font-weight="600">Mejoras en la web (16 sep)</text>')
    lx, lv = xs(len(pts) - 1), pts[-1][1]
    g.append(f'<circle cx="{lx:.1f}" cy="{ys(lv):.1f}" r="5" fill="{GOLD}" stroke="#fff" stroke-width="2"/>')
    peak_i = max(range(len(pts)), key=lambda i: pts[i][1])
    g.append(f'<text x="{xs(peak_i):.1f}" y="{ys(pts[peak_i][1])-10:.1f}" text-anchor="middle" font-size="12" font-weight="700" fill="{INK}">{fmt(pts[peak_i][1])}</text>')
    g.append(f'<text x="{lx:.1f}" y="{ys(lv)+22:.1f}" text-anchor="end" font-size="12" font-weight="700" fill="{INK}">{fmt(lv)} al día</text>')
    return f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Clics al día, media semanal">{"".join(g)}</svg>'

# ---------- grafico 2: barras por periodo ----------
def bars(metric, label_fmt, ymax):
    W, H, L, R, T, B = 330, 210, 10, 10, 26, 40
    n = len(P)
    bw = 62
    gap = (W - L - R - n * bw) / (n + 1)
    g = [f'<line x1="{L}" x2="{W-R}" y1="{H-B}" y2="{H-B}" stroke="{GRID}"/>']
    for i, (name, (c, im, d)) in enumerate(P):
        v = metric(c, im, d)
        h = (H - T - B) * v / ymax
        x = L + gap + i * (bw + gap)
        col = GOLD if i == n - 1 else "#d9c3a0"
        g.append(f'<path d="M{x},{H-B} V{H-B-h+4:.1f} Q{x},{H-B-h:.1f} {x+4},{H-B-h:.1f} H{x+bw-4} Q{x+bw},{H-B-h:.1f} {x+bw},{H-B-h+4:.1f} V{H-B} Z" fill="{col}"/>')
        g.append(f'<text x="{x+bw/2}" y="{H-B-h-8:.1f}" text-anchor="middle" font-size="14" font-weight="700" fill="{INK}">{label_fmt(v)}</text>')
        g.append(f'<text x="{x+bw/2}" y="{H-B+18}" text-anchor="middle" font-size="11" fill="{MUTED}">{name}</text>')
    return f'<svg viewBox="0 0 {W} {H}" width="100%">{"".join(g)}</svg>'

chart_clicks = bars(lambda c, i, d: c / d, lambda v: fmt(v), 4.5)
chart_ctr = bars(lambda c, i, d: 100 * c / i, lambda v: fmt(v) + " %", 9.5)

(c0, i0, d0), (c1, i1, d1), (c2, i2, d2) = [p[1] for p in P]
mult = (c2 / d2) / (c0 / d0)

HTML = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>Informe Google · Casa del Ermitaño · octubre 2026</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
@page {{ size: A4; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Plus Jakarta Sans', sans-serif; color: {INK}; background: #f9f4ec; line-height: 1.55; font-size: 13px; }}
.page {{ width: 210mm; height: 297mm; padding: 16mm 16mm 14mm; position: relative; overflow: hidden; page-break-after: always; background: #f9f4ec; }}
.page:last-child {{ page-break-after: auto; }}
h1, h2, h3 {{ font-family: 'Fraunces', serif; letter-spacing: -0.02em; line-height: 1.15; }}
h2 {{ font-size: 25px; margin-bottom: 6px; color: {BROWN}; }}
h3 {{ font-size: 16px; margin-bottom: 6px; }}
.kicker {{ font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: {GOLD}; font-weight: 700; margin-bottom: 6px; }}
.lead {{ font-size: 14px; color: #5a4228; margin-bottom: 14px; }}
.card {{ background: #fff; border: 1px solid #eadfcd; border-radius: 16px; padding: 16px 18px; box-shadow: 0 6px 18px -8px rgba(90,58,16,.18); }}
.grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
.foot {{ position: absolute; bottom: 9mm; left: 16mm; right: 16mm; display: flex; justify-content: space-between; font-size: 10px; color: {MUTED}; border-top: 1px solid #e3d6c1; padding-top: 6px; }}
/* portada */
.cover {{ padding: 0; background: {BROWN}; color: #fff; }}
.cover-photo {{ height: 190mm; background: url('{ASSETS}/eduardo-mangas-adiestrador-canino-playa-sitges.webp') 62% 0%/cover; position: relative; }}
.cover-photo::after {{ content: ''; position: absolute; inset: 0; background: linear-gradient(to top, {BROWN} 0%, rgba(90,58,16,.25) 38%, rgba(0,0,0,0) 60%); }}
.bubble {{ position: absolute; top: 30mm; left: 10mm; width: 66mm; background: #fff; color: {INK}; border-radius: 18px; padding: 14px 16px; font-size: 14px; font-weight: 600; box-shadow: 0 10px 30px rgba(0,0,0,.25); z-index: 2; }}
.bubble::after {{ content: ''; position: absolute; right: -14px; top: 22px; border: 9px solid transparent; border-left: 16px solid #fff; }}
.bubble b {{ color: {GOLD}; }}
.cover-body {{ padding: 0 16mm; margin-top: -30mm; position: relative; z-index: 2; }}
.cover h1 {{ font-size: 38px; margin: 6px 0 8px; }}
.cover .sub {{ color: #f1e3cb; font-size: 14px; max-width: 150mm; }}
.heroes {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 16px; }}
.hero {{ background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.18); border-radius: 14px; padding: 12px 14px; }}
.hero .n {{ font-family: 'Fraunces', serif; font-size: 34px; color: #f2c46d; line-height: 1; }}
.hero .t {{ font-size: 11.5px; color: #f1e3cb; margin-top: 6px; }}
.cover .kicker {{ color: #f2c46d; }}
.cover .foot {{ color: #d9c3a0; border-color: rgba(255,255,255,.2); }}
/* otros */
.big {{ font-family: 'Fraunces', serif; font-size: 30px; color: {GOLD}; line-height: 1; }}
.note {{ font-size: 11.5px; color: {MUTED}; margin-top: 6px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; }}
th {{ text-align: left; font-size: 10.5px; text-transform: uppercase; letter-spacing: .08em; color: {MUTED}; padding: 6px 8px; border-bottom: 1px solid #e3d6c1; }}
td {{ padding: 7px 8px; border-bottom: 1px solid #f0e7d8; }}
td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
.up {{ color: #2f7a3e; font-weight: 700; }}
.tags {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }}
.tag {{ background: #f6ead6; color: {BROWN}; border-radius: 999px; padding: 4px 10px; font-size: 11.5px; font-weight: 600; }}
.photo {{ border-radius: 14px; width: 100%; height: 100%; object-fit: cover; display: block; min-height: 0; }}
.photos {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; overflow: hidden; }}
.photos > * {{ min-height: 0; overflow: hidden; }}
.steps li {{ margin: 0 0 10px 18px; }}
.steps b {{ color: {BROWN}; }}
.quote {{ border-left: 4px solid {GOLD}; padding: 6px 0 6px 14px; font-size: 14px; font-style: italic; color: #5a4228; }}
</style></head><body>

<!-- 1. PORTADA -->
<section class="page cover">
  <div class="cover-photo">
    <div class="bubble">“Desde que cambiamos la web, Google nos manda <b>casi el triple de visitas</b> que a mediados de agosto.”</div>
  </div>
  <div class="cover-body">
    <div class="kicker">Informe de Google · octubre 2026</div>
    <h1>Casa del Ermitaño crece en Google</h1>
    <p class="sub">Resultados de la web criaderocasadelermitano.es en el buscador de Google, del 7 de julio al 2 de octubre de 2026, y qué ha cambiado desde las mejoras del 16 de septiembre.</p>
    <div class="heroes">
      <div class="hero"><div class="n">{int(total_clicks)}</div><div class="t">personas han entrado en la web desde Google</div></div>
      <div class="hero"><div class="n">x{fmt(mult)}</div><div class="t">visitas al día ahora frente a mediados de agosto</div></div>
      <div class="hero"><div class="n">{fmt(100*c2/i2)} %</div><div class="t">de quien nos ve en Google hace clic: el mejor dato hasta hoy</div></div>
    </div>
  </div>
  <div class="foot"><span>Preparado por Chus Carvajal para Eduardo Mangas</span><span>Datos: Google Search Console</span></div>
</section>

<!-- 2. EVOLUCION -->
<section class="page">
  <div class="kicker">La evolución</div>
  <h2>Cada semana entra más gente</h2>
  <p class="lead">Visitas que llegan desde Google, en media diaria de cada semana. En julio era prácticamente cero; hoy entran casi 4 personas al día, unas <b>120 al mes</b>, buscando un adiestrador o un criadero de Chihuahua.</p>
  <div class="card">{line_chart()}
    <p class="note">La última semana tiene 5 días (28 sep - 2 oct). Google publica los datos con 1-2 días de retraso.</p>
  </div>
  <div class="grid2" style="margin-top:14px">
    <div class="card">
      <h3>Visitas al día</h3>
      <p class="note" style="margin:0 0 6px">Tres periodos iguales de 17 días</p>
      {chart_clicks}
    </div>
    <div class="card">
      <h3>De cada 100 que nos ven, cuántos entran</h3>
      <p class="note" style="margin:0 0 6px">Porcentaje de clics (CTR)</p>
      {chart_ctr}
    </div>
  </div>
  <div class="card" style="margin-top:14px">
    <p class="quote">Las visitas suben y, sobre todo, <b>sube la proporción de gente que elige nuestra web</b> cuando nos ve en Google: del 4,6 % al 8,3 %. Eso es efecto directo de los títulos, las fotos reales y la ficha de Google enlazada.</p>
  </div>
  <div class="foot"><span>Casa del Ermitaño · Informe de Google</span><span>2</span></div>
</section>

<!-- 3. QUE FUNCIONA -->
<section class="page">
  <div class="kicker">Qué está funcionando</div>
  <h2>El criadero ya es la segunda puerta de entrada</h2>
  <p class="lead">Visitas desde Google por página, desde el 7 de julio. Entre paréntesis, lo ganado solo en las dos últimas semanas.</p>
  <div class="card">
    <table>
      <tr><th>Página</th><th style="text-align:right">Visitas</th><th style="text-align:right">Veces vista en Google</th></tr>
      <tr><td><b>Inicio</b> (adiestramiento y psicología)</td><td class="num">118 <span class="up">(+39)</span></td><td class="num">1.285</td></tr>
      <tr><td><b>Criadero de Chihuahua en Barcelona</b></td><td class="num">59 <span class="up">(+25)</span></td><td class="num">1.173</td></tr>
      <tr><td>Perros PPP: licencia y manejo</td><td class="num">4</td><td class="num">289</td></tr>
      <tr><td>Adiestramiento y obediencia</td><td class="num">4</td><td class="num">161</td></tr>
      <tr><td>Educación de cachorros</td><td class="num">3 <span class="up">(+1)</span></td><td class="num">128</td></tr>
      <tr><td>Perros agresivos y reactivos</td><td class="num">2 <span class="up">(+1)</span></td><td class="num">133</td></tr>
      <tr><td>Ansiedad por separación</td><td class="num">1 <span class="up">(+1)</span></td><td class="num">39</td></tr>
    </table>
    <p class="note">El criadero casi ha duplicado sus visitas en dos semanas (de 34 a 59), justo cuando publicamos las camadas, a Billy y los vídeos.</p>
  </div>
  <div class="photos" style="margin-top:14px; height: 66mm">
    <img class="photo" src="{ASSETS}/criadero/camada-waka-waka-recien-nacidos.webp" alt="Camada de Waka Waka">
    <img class="photo" src="{ASSETS}/criadero/padre-camadas-razzle-dazzle-ring.webp" alt="Razzle-Dazzle" style="object-position:center 40%">
  </div>
  <div class="card" style="margin-top:14px">
    <h3>Google ya nos enseña para búsquedas nuevas</h3>
    <p style="font-size:12.5px">En dos semanas han aparecido 31 búsquedas por las que antes no salíamos:</p>
    <div class="tags">
      <span class="tag">criaderos de chihuahua</span><span class="tag">criador chihuahua</span><span class="tag">criadores de chihuahuas</span>
      <span class="tag">comprar chihuahua en barcelona</span><span class="tag">psicólogo para perros</span><span class="tag">terapia canina</span>
      <span class="tag">conducta canina</span><span class="tag">permisos posesión de perros peligrosos</span><span class="tag">real decreto 287/2002</span>
    </div>
    <p class="note">Antes solo nos encontraban para “Barcelona”; ahora también en búsquedas de toda España.</p>
  </div>
  <div class="foot"><span>Casa del Ermitaño · Informe de Google</span><span>3</span></div>
</section>

<!-- 4. SIGUIENTES PASOS -->
<section class="page">
  <div class="kicker">Lo siguiente</div>
  <h2>Dónde está el próximo salto</h2>
  <p class="lead">Ya aparecemos mucho; el trabajo ahora es convertir esas apariciones en llamadas y WhatsApps.</p>
  <div class="grid2">
    <div class="card"><div class="big">55</div><h3 style="margin-top:6px">“¿El pastor del Cáucaso es PPP?”</h3><p style="font-size:12.5px">Google nos enseña en el puesto 8 y nadie entra todavía. Vamos a cambiar el título de la página PPP para que esa gente haga clic.</p></div>
    <div class="card"><div class="big">+100</div><h3 style="margin-top:6px">“Criadero chihuahua Barcelona”</h3><p style="font-size:12.5px">Más de 100 apariciones, aún en segunda página. Subir a la primera es cuestión de tiempo, de contenido nuevo cada semana y de reseñas.</p></div>
  </div>
  <div class="card" style="margin-top:14px">
    <h3>Plan para las próximas semanas</h3>
    <ol class="steps" style="margin-top:8px">
      <li><b>Camadas:</b> diario de las camadas en la web y una publicación semanal en la ficha de Google con tus vídeos de TikTok. Google premia lo que se actualiza, y es lo que más gente trae ahora.</li>
      <li><b>Página PPP:</b> nuevo título y descripción para la pregunta del pastor del Cáucaso.</li>
      <li><b>Reseñas en Google:</b> pedir una a cada familia y a cada cliente de adiestramiento. Es lo que más pesa para salir en el mapa.</li>
      <li><b>Próxima medición:</b> a mediados de noviembre, con los cachorros ya crecidos.</li>
      <li><b>Más adelante:</b> alta del criadero en la lista de criadores de la RSCE y en MundoAnimalia (gratis), cuando tengamos el número de registro. Son enlaces que ayudan a “criadero chihuahua Barcelona”.</li>
    </ol>
  </div>
  <div class="photos" style="margin-top:14px; height: 64mm">
    <img class="photo" src="{ASSETS}/eduardo-mangas-educador-canino-obediencia-sitges.webp" alt="Eduardo Mangas" style="object-position:center 30%">
    <div class="card" style="display:flex;flex-direction:column;justify-content:center">
      <p class="quote">De casi cero visitas en julio a unas 120 al mes en octubre, con la misma ficha y sin pagar publicidad. Cada visita es alguien que busca exactamente lo que haces.</p>
    </div>
  </div>
  <div class="foot"><span>Datos de Google Search Console, búsqueda web, 7 jul - 2 oct 2026. Visitas = clics desde Google.</span><span>4</span></div>
</section>
</body></html>"""

out_html = BASE / "informe-gsc-casa-ermitano-2026-10-03.html"
out_html.write_text(HTML, encoding="utf-8")

async def pdf():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        await pg.goto(out_html.as_uri(), wait_until="networkidle")
        await pg.evaluate("document.fonts.ready")
        await pg.pdf(path=str(BASE / "Informe-Google-Casa-del-Ermitano-octubre-2026.pdf"), format="A4", print_background=True, prefer_css_page_size=True)
        for n in range(1, 5):
            await pg.set_viewport_size({"width": 794, "height": 1123})
        await pg.screenshot(path=str(BASE.parent / ".tmp_informe_full.png"), full_page=True)
        await b.close()
asyncio.run(pdf())
print("total clics", total_clicks, "impr", total_impr, "mult", round(mult, 2))
print([(k, v) for k, v in weeks.items()][-3:])
