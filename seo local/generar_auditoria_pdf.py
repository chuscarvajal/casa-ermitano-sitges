"""
Generador de PDF — Auditoría GBP Casa del Ermitaño
Chus Carvajal | Carvajal Photos SEO | Junio 2026
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import Flowable
import os

# ─── COLORES ────────────────────────────────────────────────────────────────
NAVY        = colors.HexColor('#0D1B2A')
NAVY_MID    = colors.HexColor('#1B2B3B')
ACCENT      = colors.HexColor('#C8A96E')   # dorado
RED         = colors.HexColor('#C0392B')
RED_LIGHT   = colors.HexColor('#FDECEA')
ORANGE      = colors.HexColor('#E67E22')
ORANGE_LIGHT= colors.HexColor('#FEF3E2')
GREEN       = colors.HexColor('#27AE60')
GREEN_LIGHT = colors.HexColor('#E8F8F0')
GREY_DARK   = colors.HexColor('#2C3E50')
GREY_MID    = colors.HexColor('#7F8C8D')
GREY_LIGHT  = colors.HexColor('#F4F6F8')
GREY_LINE   = colors.HexColor('#DDE2E8')
WHITE       = colors.white
TEXT_BODY   = colors.HexColor('#2D3748')

PAGE_W, PAGE_H = A4

# ─── ESTILOS ────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def make_style(name, **kw):
    return ParagraphStyle(name, **kw)

S = {
    'cover_title': make_style('ct',
        fontName='Helvetica-Bold', fontSize=28, textColor=WHITE,
        leading=34, alignment=TA_LEFT, spaceAfter=6),
    'cover_sub': make_style('cs',
        fontName='Helvetica', fontSize=14, textColor=ACCENT,
        leading=20, alignment=TA_LEFT, spaceAfter=4),
    'cover_meta': make_style('cm',
        fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#A0AEC0'),
        leading=16, alignment=TA_LEFT),
    'h1': make_style('h1',
        fontName='Helvetica-Bold', fontSize=15, textColor=NAVY,
        leading=20, spaceBefore=18, spaceAfter=8,
        borderPad=0),
    'h2': make_style('h2',
        fontName='Helvetica-Bold', fontSize=12, textColor=GREY_DARK,
        leading=16, spaceBefore=14, spaceAfter=5),
    'h3': make_style('h3',
        fontName='Helvetica-Bold', fontSize=10.5, textColor=GREY_DARK,
        leading=14, spaceBefore=10, spaceAfter=4),
    'body': make_style('bd',
        fontName='Helvetica', fontSize=9.5, textColor=TEXT_BODY,
        leading=15, spaceAfter=4, alignment=TA_JUSTIFY),
    'body_small': make_style('bs',
        fontName='Helvetica', fontSize=8.5, textColor=GREY_DARK,
        leading=13, spaceAfter=2),
    'bold': make_style('bl',
        fontName='Helvetica-Bold', fontSize=9.5, textColor=TEXT_BODY,
        leading=15, spaceAfter=4),
    'bullet': make_style('bu',
        fontName='Helvetica', fontSize=9.5, textColor=TEXT_BODY,
        leading=15, spaceAfter=3, leftIndent=12, bulletIndent=0),
    'quote': make_style('qu',
        fontName='Helvetica-Oblique', fontSize=9, textColor=GREY_DARK,
        leading=14, spaceAfter=6, leftIndent=16, rightIndent=8,
        borderPad=6),
    'caption': make_style('ca',
        fontName='Helvetica', fontSize=8, textColor=GREY_MID,
        leading=12, spaceAfter=2, alignment=TA_CENTER),
    'kw_item': make_style('ki',
        fontName='Helvetica', fontSize=9, textColor=GREY_DARK,
        leading=13, spaceAfter=2, leftIndent=10),
    'section_num': make_style('sn',
        fontName='Helvetica-Bold', fontSize=9, textColor=ACCENT,
        leading=12, spaceAfter=2),
    'toc_item': make_style('ti',
        fontName='Helvetica', fontSize=9.5, textColor=GREY_DARK,
        leading=16, leftIndent=8),
    'signature_name': make_style('sig',
        fontName='Helvetica-Bold', fontSize=11, textColor=NAVY,
        leading=14, alignment=TA_CENTER),
    'signature_title': make_style('sit',
        fontName='Helvetica', fontSize=9, textColor=GREY_MID,
        leading=13, alignment=TA_CENTER),
    'footer': make_style('ft',
        fontName='Helvetica', fontSize=7.5, textColor=GREY_MID,
        leading=10, alignment=TA_CENTER),
}

# ─── FLOWABLE: BADGE LABEL ───────────────────────────────────────────────────
class Badge(Flowable):
    def __init__(self, text, bg, fg=WHITE, w=None, h=18, radius=4):
        super().__init__()
        self.text = text
        self.bg = bg
        self.fg = fg
        self._w = w
        self._h = h
        self.radius = radius

    def wrap(self, *args):
        self.width = self._w or 120
        self.height = self._h + 6
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        c.roundRect(0, 3, self.width, self._h, self.radius, fill=1, stroke=0)
        c.setFillColor(self.fg)
        c.setFont('Helvetica-Bold', 8)
        c.drawCentredString(self.width / 2, 3 + self._h / 2 - 3, self.text)


class ColorBar(Flowable):
    """Barra horizontal decorativa."""
    def __init__(self, width, height=3, color=ACCENT):
        super().__init__()
        self.bar_w = width
        self.bar_h = height
        self.color = color

    def wrap(self, *args):
        return self.bar_w, self.bar_h + 4

    def draw(self):
        c = self.canv
        c.setFillColor(self.color)
        c.rect(0, 2, self.bar_w, self.bar_h, fill=1, stroke=0)


class SectionHeader(Flowable):
    """Cabecera de sección con fondo de color."""
    def __init__(self, number, title, color=NAVY, width=None):
        super().__init__()
        self.number = number
        self.title = title
        self.color = color
        self._width = width or (PAGE_W - 2 * 2 * cm)

    def wrap(self, *args):
        return self._width, 32

    def draw(self):
        c = self.canv
        c.setFillColor(self.color)
        c.roundRect(0, 0, self._width, 30, 5, fill=1, stroke=0)
        c.setFillColor(ACCENT)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(10, 10, self.number)
        c.setFillColor(WHITE)
        c.setFont('Helvetica-Bold', 11)
        c.drawString(42, 10, self.title)


class AlertBox(Flowable):
    """Cabecera de alerta: badge de nivel + título. El texto va en Paragraphs separados."""
    def __init__(self, level, title, width=None):
        super().__init__()
        self.level = level  # 'critical', 'medium', 'good'
        self.title = title
        self._width = width or (PAGE_W - 4 * cm)
        self._colors = {
            'critical': (RED,    RED_LIGHT,    '! CRITICO'),
            'medium':   (ORANGE, ORANGE_LIGHT, '~ MEDIO'),
            'good':     (GREEN,  GREEN_LIGHT,  '+ RAPIDO'),
        }

    def wrap(self, *args):
        self.height = 34
        return self._width, self.height + 4

    def draw(self):
        c = self.canv
        border_c, bg_c, badge_text = self._colors.get(self.level, (GREY_MID, GREY_LIGHT, ''))
        h = self.height

        # Background
        c.setFillColor(bg_c)
        c.roundRect(0, 2, self._width, h, 5, fill=1, stroke=0)
        # Left border stripe
        c.setFillColor(border_c)
        c.rect(0, 2, 4, h, fill=1, stroke=0)

        # Badge pill
        c.setFillColor(border_c)
        c.roundRect(10, h - 18, 72, 15, 3, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont('Helvetica-Bold', 7.5)
        c.drawString(14, h - 11, badge_text)

        # Title text
        c.setFillColor(GREY_DARK)
        c.setFont('Helvetica-Bold', 10.5)
        # Truncate if too long
        max_w = self._width - 100
        title = self.title
        c.drawString(90, h - 12, title[:80])


# ─── PAGE TEMPLATE ───────────────────────────────────────────────────────────
def make_page_template(canvas_obj, doc, is_cover=False):
    canvas_obj.saveState()
    w, h = A4

    if is_cover:
        # Fondo degradado oscuro
        canvas_obj.setFillColor(NAVY)
        canvas_obj.rect(0, 0, w, h, fill=1, stroke=0)
        # Franja lateral izquierda
        canvas_obj.setFillColor(ACCENT)
        canvas_obj.rect(0, 0, 6, h, fill=1, stroke=0)
        # Franja superior
        canvas_obj.setFillColor(NAVY_MID)
        canvas_obj.rect(0, h * 0.55, w, h * 0.45, fill=1, stroke=0)
        # Línea divisoria
        canvas_obj.setFillColor(ACCENT)
        canvas_obj.rect(6, h * 0.55, w, 3, fill=1, stroke=0)
    else:
        # Header línea
        canvas_obj.setFillColor(NAVY)
        canvas_obj.rect(0, h - 14*mm, w, 14*mm, fill=1, stroke=0)
        canvas_obj.setFillColor(ACCENT)
        canvas_obj.rect(0, h - 14*mm, 4, 14*mm, fill=1, stroke=0)
        # Header text
        canvas_obj.setFillColor(WHITE)
        canvas_obj.setFont('Helvetica-Bold', 8)
        canvas_obj.drawString(15*mm, h - 9*mm, 'AUDITORIA SEO LOCAL — GOOGLE BUSINESS PROFILE')
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(ACCENT)
        canvas_obj.drawRightString(w - 15*mm, h - 9*mm, 'Criadero Casa del Ermitano')

        # Footer
        canvas_obj.setFillColor(GREY_LIGHT)
        canvas_obj.rect(0, 0, w, 12*mm, fill=1, stroke=0)
        canvas_obj.setFillColor(ACCENT)
        canvas_obj.rect(0, 12*mm, w, 1, fill=1, stroke=0)
        canvas_obj.setFillColor(GREY_MID)
        canvas_obj.setFont('Helvetica', 7.5)
        canvas_obj.drawString(15*mm, 4.5*mm, 'Chus Carvajal · Carvajal Photos SEO · carvajalphotos@gmail.com')
        canvas_obj.drawRightString(w - 15*mm, 4.5*mm, f'Pagina {doc.page}')

    canvas_obj.restoreState()


class CoverPageTemplate:
    pass


def first_page(c, doc):
    make_page_template(c, doc, is_cover=True)

def later_pages(c, doc):
    make_page_template(c, doc, is_cover=False)


# ─── HELPER: tabla estilizada ────────────────────────────────────────────────
def make_table(data, col_widths, header_bg=NAVY, row_bg_alt=GREY_LIGHT, font_size=8.5):
    table = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), header_bg),
        ('TEXTCOLOR',  (0, 0), (-1, 0), WHITE),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, 0), font_size),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
        ('TOPPADDING',    (0, 0), (-1, 0), 7),
        # Body
        ('FONTNAME',   (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',   (0, 1), (-1, -1), font_size - 0.5),
        ('TEXTCOLOR',  (0, 1), (-1, -1), TEXT_BODY),
        ('TOPPADDING',    (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        # Borders
        ('GRID',       (0, 0), (-1, -1), 0.4, GREY_LINE),
        ('LINEBELOW',  (0, 0), (-1, 0), 1.5, ACCENT),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, row_bg_alt]),
        ('LEFTPADDING',  (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]
    table.setStyle(TableStyle(style))
    return table


def bullet(text, color=TEXT_BODY):
    return Paragraph(f'<font color="#C8A96E">■</font>  {text}', S['bullet'])

def check(text, done=False):
    icon = '✓' if done else '○'
    col = GREEN if done else GREY_MID
    return Paragraph(f'<font color="{col.hexval() if hasattr(col,"hexval") else "#7F8C8D"}">{icon}</font>  {text}', S['bullet'])


# ─── BUILD PDF ───────────────────────────────────────────────────────────────
OUTPUT_PATH = r'C:\Users\Usuario\Documents\CLAUDE\ADIESTRADOR CANINO\CASAERMITANO\seo local\Auditoria_GBP_CasaDelErmitano_ChusCarvajalSEO.pdf'

MARGIN_T = 2.2*cm
MARGIN_B = 2.0*cm
MARGIN_L = 2.0*cm
MARGIN_R = 2.0*cm

CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R

doc = SimpleDocTemplate(
    OUTPUT_PATH,
    pagesize=A4,
    topMargin=MARGIN_T + 10*mm,
    bottomMargin=MARGIN_B + 6*mm,
    leftMargin=MARGIN_L,
    rightMargin=MARGIN_R,
    title='Auditoria SEO Local GBP — Casa del Ermitano',
    author='Chus Carvajal · Carvajal Photos SEO',
    subject='Auditoria Google Business Profile',
)

story = []

# ════════════════════════════════════════════════════════════════════════════
# PORTADA
# ════════════════════════════════════════════════════════════════════════════
story.append(Spacer(1, 6.5*cm))
story.append(Paragraph('AUDITORÍA SEO LOCAL', S['cover_title']))
story.append(Paragraph('Google Business Profile', S['cover_sub']))
story.append(Spacer(1, 0.3*cm))
story.append(ColorBar(CONTENT_W, 2, ACCENT))
story.append(Spacer(1, 0.5*cm))
story.append(Paragraph(
    'Criadero Casa del Ermitaño<br/>Adiestramiento &amp; Psicología Canina',
    ParagraphStyle('ct2', fontName='Helvetica', fontSize=13,
                   textColor=colors.HexColor('#CBD5E0'), leading=20)
))
story.append(Spacer(1, 5.5*cm))
story.append(Paragraph('Preparado por', S['cover_meta']))
story.append(Paragraph('Chus Carvajal', ParagraphStyle('cn',
    fontName='Helvetica-Bold', fontSize=16, textColor=WHITE, leading=20)))
story.append(Paragraph('Carvajal Photos SEO', S['cover_meta']))
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph('carvajalphotos@gmail.com', S['cover_meta']))
story.append(Spacer(1, 0.6*cm))
story.append(Paragraph('Junio 2026 — Documento Confidencial', S['cover_meta']))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# ÍNDICE
# ════════════════════════════════════════════════════════════════════════════
story.append(SectionHeader('', 'ÍNDICE DE CONTENIDOS', NAVY, CONTENT_W))
story.append(Spacer(1, 0.4*cm))

toc_items = [
    ('1', 'Estado Actual de la Ficha GBP'),
    ('2', 'Problemas Críticos (Acción Inmediata)'),
    ('3', 'Problemas de Nivel Medio'),
    ('4', 'Oportunidades Rápidas — Quick Wins'),
    ('5', 'Análisis de Competencia Local'),
    ('6', 'Keywords Objetivo para GBP'),
    ('7', 'Hoja de Ruta — Plan de Acción'),
    ('8', 'KPIs a Monitorizar'),
    ('9', 'Resumen Ejecutivo y Firma'),
]
for num, title in toc_items:
    row_data = [[
        Paragraph(f'<b>{num}.</b>', ParagraphStyle('tn', fontName='Helvetica-Bold',
            fontSize=9.5, textColor=ACCENT, leading=14)),
        Paragraph(title, S['toc_item']),
    ]]
    t = Table(row_data, colWidths=[1.2*cm, CONTENT_W - 1.2*cm])
    t.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, GREY_LINE),
        ('TOPPADDING', (0, 0), (-1, 0), 5),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
    ]))
    story.append(t)

story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — ESTADO ACTUAL
# ════════════════════════════════════════════════════════════════════════════
story.append(SectionHeader('01', 'ESTADO ACTUAL DE LA FICHA', NAVY, CONTENT_W))
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph(
    'Diagnóstico inicial del perfil de Google Business Profile basado en rastreo de directorios, '
    'plataformas de reseñas y datos públicos de la ficha. Fecha de auditoría: 2 de junio de 2026.',
    S['body']
))
story.append(Spacer(1, 0.4*cm))

# Tabla de estado — con iconos de semáforo
estado_data = [
    ['Campo', 'Estado actual', 'Valoración'],
    ['Nombre del negocio', 'Criadero Casa del Ermitaño,\nAdiestramiento & Psicología Canina', '✓ OK'],
    ['Titular', 'Eduardo Mangas (desde 1998)', '✓ OK'],
    ['Teléfono', '+34 674 091 010', '✓ OK'],
    ['Dirección en GBP', 'Carrer Miramar, 18, Urb. Vallpineda, Garraf', '⚠ Inconsistente'],
    ['Dirección en directorios', 'Garraf / Sitges / Sant Pere de Ribes (3 versiones)', '✗ Crítico'],
    ['Website en GBP', 'casadelermitano.negocio.site → ERROR 404', '✗ Crítico'],
    ['Categoría principal', 'Entrenador de perros / Criadores mascotas', '✗ No optimizada'],
    ['Horario GBP', 'L-D 9:00 – 21:00', '⚠ Verificar'],
    ['Horario en directorios', 'Aparece como "24 horas" en algunos', '⚠ Inconsistente'],
    ['Reseñas externas', '5/5 — 10 opiniones (todas del 27/11/2023)', '⚠ Riesgo patrón'],
    ['Fotos', '1 foto (cachorro chihuahua en venta)', '✗ Crítico'],
    ['Google Posts', 'No detectados', '✗ Ausente'],
    ['Sección Q&A', 'No detectada', '✗ Ausente'],
    ['Servicios/Productos', 'No listados', '✗ Ausente'],
    ['Atributos', 'No configurados', '✗ Ausente'],
    ['Instagram', '@casadelermitano', '✓ Correcto'],
    ['Facebook', '@casadelermltano (falta la "i")', '⚠ Typo'],
]

col_w = [4.2*cm, 8.8*cm, 2.8*cm]
tbl = make_table(estado_data, col_w, font_size=8)
# Override alignment for last column
tbl.setStyle(TableStyle([
    ('ALIGN', (2, 0), (2, -1), 'CENTER'),
    ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
    # Color coding
    ('TEXTCOLOR', (2, 1), (2, 2), GREEN),   # OK rows
    ('TEXTCOLOR', (2, 16), (2, 16), GREEN),  # Instagram OK
    ('TEXTCOLOR', (2, 3), (2, 3), ORANGE),
    ('TEXTCOLOR', (2, 4), (2, 4), RED),
    ('TEXTCOLOR', (2, 5), (2, 5), RED),
    ('TEXTCOLOR', (2, 6), (2, 6), RED),
    ('TEXTCOLOR', (2, 7), (2, 7), ORANGE),
    ('TEXTCOLOR', (2, 8), (2, 8), ORANGE),
    ('TEXTCOLOR', (2, 9), (2, 9), ORANGE),
    ('TEXTCOLOR', (2, 10), (2, 10), RED),
    ('TEXTCOLOR', (2, 11), (2, 11), RED),
    ('TEXTCOLOR', (2, 12), (2, 12), RED),
    ('TEXTCOLOR', (2, 13), (2, 13), RED),
    ('TEXTCOLOR', (2, 14), (2, 14), RED),
    ('TEXTCOLOR', (2, 17), (2, 17), ORANGE),  # Facebook
]))
story.append(tbl)
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2 — PROBLEMAS CRÍTICOS
# ════════════════════════════════════════════════════════════════════════════
story.append(SectionHeader('02', 'PROBLEMAS CRÍTICOS — ACCIÓN INMEDIATA', RED, CONTENT_W))
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph(
    'Los siguientes problemas impactan directamente en el posicionamiento y en la conversión. '
    'Deben resolverse en la primera semana de trabajo.',
    S['body']
))
story.append(Spacer(1, 0.3*cm))

# Crítico 1
story.append(KeepTogether([
    AlertBox('critical', 'CRITICO 1 — Website de la ficha da ERROR 404', CONTENT_W - 0.2*cm),
    Spacer(1, 0.1*cm),
    Paragraph('<b>URL afectada:</b> casadelermitano.negocio.site → página no encontrada', S['body']),
    Spacer(1, 0.1*cm),
    Paragraph(
        'Google penaliza fichas con URLs rotas porque señalan abandono y falta de actividad. '
        'Además, cualquier usuario que haga clic en "Sitio web" desde Google Maps llega a una página de error, '
        'lo que destruye la credibilidad del negocio en el momento de mayor intención de compra.',
        S['body']
    ),
    Spacer(1, 0.15*cm),
    Paragraph('<b>Acción inmediata:</b>', S['bold']),
    bullet('Sustituir la URL del GBP por la nueva web en construcción en cuanto esté disponible.'),
    bullet('Mientras tanto, usar el perfil de Instagram (@casadelermitano) como URL temporal.'),
    bullet('Cualquier URL funcional es mejor que un 404.'),
    Spacer(1, 0.3*cm),
]))

# Crítico 2
story.append(KeepTogether([
    AlertBox('critical', 'CRITICO 2 — Descripcion del negocio habla de un cachorro en venta', CONTENT_W - 0.2*cm),
    Spacer(1, 0.1*cm),
    Paragraph('<b>Texto actual en Google Business:</b>', S['bold']),
    Paragraph(
        '"Disponemos de un maravilloso chihuahua macho cachorro de pelo largo con todas sus vacunas '
        'y chip puesto. Mas informacion por privado al 674091010."',
        S['quote']
    ),
    Paragraph(
        'Este texto no describe el negocio ni sus servicios. No contiene ninguna keyword de posicionamiento. '
        'Confunde al cliente sobre qué hace Eduardo. Y lo más grave: Google lo indexa como el snippet '
        'principal del negocio en Maps y en búsquedas orgánicas. Destruye el CTR y la relevancia local.',
        S['body']
    ),
    Spacer(1, 0.15*cm),
    Paragraph('<b>Descripcion optimizada propuesta</b> (usar exactamente este texto en la ficha):', S['bold']),
    Paragraph(
        '"Eduardo Mangas lleva desde 1998 dedicado a la Psicología, Etología y Adiestramiento Canino '
        'en el Garraf, Sitges y alrededores de Barcelona. Especialista en modificación de conducta, '
        'reactividad, miedos y agresividad canina. Trabajamos con método positivo, resultados visibles '
        'desde la primera sesión. Servicios: adiestramiento básico y avanzado, psicología canina, '
        'educación de cachorros y sesiones a domicilio. Más de 25 años de experiencia. Llámanos o '
        'escríbenos por WhatsApp: +34 674 091 010."',
        S['quote']
    ),
    Paragraph(
        'Keywords incluidas: psicología canina · adiestramiento canino · Sitges · Garraf · Barcelona · '
        'modificación de conducta · método positivo · cachorros · a domicilio · 25 años experiencia',
        S['body_small']
    ),
    Spacer(1, 0.3*cm),
]))

# Crítico 3
story.append(KeepTogether([
    AlertBox('critical', 'CRITICO 3 — Identidad dual criadero + adiestramiento diluye la señal', CONTENT_W - 0.2*cm),
    Spacer(1, 0.1*cm),
    Paragraph(
        'La ficha mezcla dos negocios muy distintos: <b>criadero de perros</b> y '
        '<b>adiestramiento/psicología canina</b>. Google no sabe a qué categoría principal asignarte. '
        'Esto fragmenta el posicionamiento y puede hacer que no aparezcas para ninguna de las dos búsquedas '
        'en el local pack.',
        S['body']
    ),
    Spacer(1, 0.15*cm),
    Paragraph('<b>Accion:</b>', S['bold']),
    bullet('Categoría principal → <b>"Adiestrador de perros"</b> (Dog Trainer) — sin excepciones.'),
    bullet('El criadero puede mantenerse como categoría secundaria si sigue activo.'),
    bullet('La categoría primaria debe reflejar el servicio de mayor valor y mayor volumen de búsqueda.'),
    Spacer(1, 0.3*cm),
]))

# Crítico 4
story.append(KeepTogether([
    AlertBox('critical', 'CRITICO 4 — Inconsistencia de direccion (NAP) en 3 ciudades distintas', CONTENT_W - 0.2*cm),
    Spacer(1, 0.1*cm),
    Paragraph(
        'El negocio aparece con tres variaciones de ciudad en distintas fuentes de datos:',
        S['body']
    ),
    Spacer(1, 0.1*cm),
]))

nap_data = [
    ['Fuente', 'Ciudad', 'C.P.', 'Estado'],
    ['Google Maps / GBP', 'Garraf', '08860', '— Referencia'],
    ['Infoisinfo / oopiniones.com', 'Sitges', '08870', 'DIFERENTE'],
    ['Moovit', 'Sant Pere de Ribes', '08810', 'DIFERENTE'],
]
story.append(make_table(nap_data, [5*cm, 4*cm, 2*cm, 4.8*cm], font_size=8.5))
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph(
    'Las inconsistencias NAP (Name, Address, Phone) en directorios online destruyen la autoridad local. '
    'Google reconcilia estas señales de múltiples fuentes y, cuando no son coherentes, la ficha '
    'pierde posiciones en el Local Pack de Google Maps.',
    S['body']
))
story.append(Spacer(1, 0.15*cm))
story.append(Paragraph('<b>Accion:</b> Unificar con la dirección del GBP (Garraf, 08860) en todos los directorios.', S['bold']))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3 — PROBLEMAS MEDIOS
# ════════════════════════════════════════════════════════════════════════════
story.append(SectionHeader('03', 'PROBLEMAS DE NIVEL MEDIO', ORANGE, CONTENT_W))
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph(
    'Estos problemas no bloquean el posicionamiento de forma inmediata pero limitan el crecimiento '
    'y la conversión a medio plazo. Abordarlos en las semanas 2-4.',
    S['body']
))
story.append(Spacer(1, 0.3*cm))

medios = [
    (
        'MEDIO 1 — Patron de resenas sospechoso',
        'Las 10 reseñas de oopiniones.com están todas fechadas el 27/11/2023 — el mismo día. '
        'Este patrón es una señal de alerta que Google puede interpretar como reviews artificiales. '
        'Si este mismo patrón se replicó en Google Business, la ficha está en riesgo de penalización '
        'o eliminación de reseñas.',
        ['Revisar el historial de reseñas de Google (fechas de cada una).',
         'Si hay pico en esa fecha, iniciar una estrategia orgánica de captación a largo plazo.',
         'Añadir en el protocolo de cierre de sesión: pedir reseña en Google de forma natural.',
         'Nunca solicitar varias reseñas al mismo tiempo ni desde el mismo dispositivo.']
    ),
    (
        'MEDIO 2 — Una sola foto y no representa el negocio',
        'Solo hay una foto visible: un cachorro chihuahua en venta. No hay ninguna imagen de Eduardo '
        'trabajando, de sesiones de adiestramiento, de instalaciones ni de resultados. Las fichas con '
        '10+ fotos reciben hasta un 35% más de clics que las fichas con pocas imágenes (dato de Google).',
        ['Foto de portada: Eduardo con un perro en el entorno natural del Garraf.',
         'Logo oficial del negocio como foto de perfil.',
         '3-4 fotos de sesiones de adiestramiento en acción.',
         '2 fotos "antes y después" de comportamiento (muy alto impacto visual).',
         '1-2 fotos del entorno (naturaleza Garraf/Sitges — atractivo para clientes de Barcelona).',
         '1 foto de Eduardo con clientes satisfechos y sus perros.']
    ),
    (
        'MEDIO 3 — Sin Google Posts activos',
        'Los Google Posts aparecen directamente en la ficha de Maps y en los resultados de búsqueda. '
        'Son gratuitos y generan engagement. Un perfil sin posts recientes envía señal de abandono a Google.',
        ['Post mensual de oferta: "Primera consulta gratuita para nuevos clientes".',
         'Post de contenido: consejo de comportamiento canino del mes.',
         'Post de novedad: nueva web, nuevo servicio, certificación.',
         'Post de evento si hay talleres o jornadas en la zona.']
    ),
    (
        'MEDIO 4 — Sin servicios ni precios listados',
        'Google permite listar servicios con nombre, descripción y precio directamente en la ficha. '
        'Listarlos mejora la relevancia para búsquedas como "adiestramiento canino precio Sitges" y '
        'responde preguntas antes de que el cliente tenga que llamar.',
        ['Adiestramiento Básico — 45€/sesión.',
         'Adiestramiento Avanzado — 55€/sesión.',
         'Psicología Canina — 65€/sesión.',
         'Sesión a domicilio — suplemento +20€/sesión.',
         'Cada servicio debe incluir una descripción de 2-3 líneas con keywords.']
    ),
    (
        'MEDIO 5 — Sin seccion Q&A (Preguntas y Respuestas)',
        'Esta sección aparece directamente en los resultados de Google. Eduardo puede añadir él mismo '
        'las preguntas y responderlas, controlando el mensaje antes de que lo haga un extraño.',
        ['"¿Trabajáis con perros agresivos o reactivos?" — Sí, es nuestra especialidad.',
         '"¿Hacéis sesiones a domicilio en Barcelona?" — Sí, en toda el área del Garraf y Barcelona.',
         '"¿Cuántas sesiones necesita un perro con ansiedad de separación?" — Depende del caso...',
         '"¿Cuál es la diferencia entre adiestramiento y psicología canina?" — El adiestramiento...']
    ),
    (
        'MEDIO 6 — Handle de Facebook con typo',
        'El handle actual @casadelermltano tiene un error tipográfico (falta la "i"). Las citas que '
        'Google recoge de Facebook apuntan al handle incorrecto, lo que debilita la coherencia de la '
        'identidad del negocio. Requiere corrección en Meta Business Suite.',
        ['Correcto: @casadelermitano',
         'Incorrecto actual: @casadelermltano (falta la "i" en "ermitano")',
         'Corregir en Meta Business Suite → Configuración → Información de la página.']
    ),
]

for title, desc, actions in medios:
    story.append(KeepTogether([
        AlertBox('medium', title, CONTENT_W - 0.2*cm),
        Spacer(1, 0.1*cm),
        Paragraph(desc, S['body']),
        Spacer(1, 0.1*cm),
        Paragraph('<b>Acciones:</b>', S['bold']),
    ] + [bullet(a) for a in actions] + [Spacer(1, 0.3*cm)]))

story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4 — QUICK WINS
# ════════════════════════════════════════════════════════════════════════════
story.append(SectionHeader('04', 'OPORTUNIDADES RAPIDAS — QUICK WINS', GREEN, CONTENT_W))
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph(
    'Acciones de bajo esfuerzo y alto impacto que se pueden implementar esta misma semana. '
    'Ordenadas por prioridad.',
    S['body']
))
story.append(Spacer(1, 0.3*cm))

qw_data = [
    ['#', 'Acción', 'Tiempo', 'Impacto'],
    ['1', 'Cambiar URL en GBP (Instagram como temporal)', '5 min', 'ALTO — elimina 404'],
    ['2', 'Reescribir descripcion con keywords', '15 min', 'ALTO — mejora CTR'],
    ['3', 'Cambiar categoría principal a "Adiestrador de perros"', '5 min', 'ALTO — ranking'],
    ['4', 'Subir 10 fotos de calidad', '30 min', 'MEDIO-ALTO'],
    ['5', 'Añadir servicios con precios', '30 min', 'MEDIO'],
    ['6', 'Crear 3 Google Posts', '20 min', 'MEDIO'],
    ['7', 'Añadir 5 preguntas Q&A', '15 min', 'MEDIO'],
    ['8', 'Corregir horarios en GBP', '5 min', 'BAJO-MEDIO'],
    ['9', 'Corregir NAP en Infoisinfo y otros directorios', '45 min', 'MEDIO'],
]
story.append(make_table(qw_data, [0.8*cm, 8.5*cm, 2.5*cm, 4*cm], font_size=8.5))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 5 — COMPETENCIA
# ════════════════════════════════════════════════════════════════════════════
story.append(SectionHeader('05', 'ANALISIS DE COMPETENCIA LOCAL', NAVY, CONTENT_W))
story.append(Spacer(1, 0.3*cm))

comp_data = [
    ['Competidor', 'Zona', 'Fortalezas detectadas'],
    ['La Escuela Canina', 'Penedès / Garraf / Baix Ll.', 'Web profesional, SEO trabajado, cursos estructurados'],
    ['Can Bugunya', 'Barcelona', 'Certificacion Consejo Veterinarios, modificacion conducta'],
    ['Sapiens Dog', 'Barcelona', 'Buena presencia online, gestion emocional canina'],
    ['Boncan', 'Barcelona', '15+ años experiencia, blog contenidos, SEO muy fuerte'],
    ['El Perro Negro', 'Barcelona', 'Educacion respetuosa, buena comunicacion digital'],
]
story.append(make_table(comp_data, [4*cm, 4*cm, 7.8*cm], font_size=8.5))
story.append(Spacer(1, 0.4*cm))

story.append(Paragraph('VENTAJA DIFERENCIAL DE EDUARDO — No comunicada actualmente', S['h2']))
story.append(Spacer(1, 0.2*cm))

ventajas = [
    ('25+ años de experiencia (desde 1998)',
     'Ningún competidor del Garraf tiene ese recorrido. Es el dato más poderoso que tiene Eduardo y no aparece en su ficha.'),
    ('Triple especialización: Psicología + Etología + Adiestramiento',
     'La mayoría de competidores solo hacen adiestramiento básico. Eduardo ofrece diagnóstico de fondo, no solo corrección de comportamiento.'),
    ('Ubicación en el Garraf',
     'Zona natural privilegiada — trabajar con perros al aire libre es diferenciador vs. entrenadores urbanos de Barcelona.'),
    ('Proximidad a Sitges',
     'Mercado con alto poder adquisitivo y dueños de mascotas muy involucrados. Dispuestos a pagar por calidad y experiencia.'),
]
for title, desc in ventajas:
    story.append(KeepTogether([
        Paragraph(f'<b>{title}</b>', S['h3']),
        Paragraph(desc, S['body']),
        Spacer(1, 0.15*cm),
    ]))

story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 6 — KEYWORDS
# ════════════════════════════════════════════════════════════════════════════
story.append(SectionHeader('06', 'KEYWORDS OBJETIVO PARA GBP', NAVY, CONTENT_W))
story.append(Spacer(1, 0.3*cm))

kw_groups = [
    ('Primarias — Alta intención de contratar', [
        'adiestramiento canino Sitges',
        'adiestramiento canino Garraf',
        'adiestrador de perros Sitges',
        'psicología canina Barcelona',
        'modificación de conducta perros Barcelona',
    ]),
    ('Secundarias — Búsquedas de problema', [
        'perro agresivo Sitges',
        'perro reactivo Barcelona',
        'adiestramiento cachorro Garraf',
        'ansiedad separacion perro Barcelona',
        'perro tira correa Sitges',
    ]),
    ('Long tail — Alta conversion', [
        'adiestrador canino a domicilio Sitges',
        'psicologo canino Garraf Barcelona',
        'educacion canina Vallpineda',
        'adiestramiento canino precio Sitges',
        'modificacion conducta perro Garraf',
    ]),
]
for group_title, kws in kw_groups:
    story.append(Paragraph(group_title, S['h2']))
    for kw in kws:
        story.append(Paragraph(f'<font color="#C8A96E">▸</font>  {kw}', S['kw_item']))
    story.append(Spacer(1, 0.2*cm))

story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 7 — HOJA DE RUTA
# ════════════════════════════════════════════════════════════════════════════
story.append(SectionHeader('07', 'HOJA DE RUTA — PLAN DE ACCION', NAVY, CONTENT_W))
story.append(Spacer(1, 0.3*cm))

roadmap = [
    ('SEMANA 1 — Correcciones críticas', RED, [
        'Reemplazar URL del GBP (Instagram como solución temporal)',
        'Reescribir descripcion con el texto optimizado propuesto',
        'Cambiar categoría principal a "Adiestrador de perros"',
        'Subir 10 fotos (portada, logo, sesiones, entorno)',
        'Verificar y unificar dirección en GBP (Garraf, 08860)',
    ]),
    ('SEMANA 2 — Contenido y servicios', ORANGE, [
        'Listar todos los servicios con descripcion y precio',
        'Añadir 5 preguntas Q&A redactadas',
        'Publicar el primer Google Post',
        'Configurar atributos (a domicilio, cita previa, etc.)',
        'Corregir handle Facebook en Meta Business Suite',
    ]),
    ('SEMANAS 3-4 — Autoridad y reseñas', colors.HexColor('#2471A3'), [
        'Auditar historial de reseñas de Google (verificar pico 27/11/2023)',
        'Implementar protocolo de captacion de reseñas post-sesion',
        'Corregir NAP en: Infoisinfo, Yelp, Páginas Amarillas, Foursquare',
        'Configurar enlace a la nueva web cuando esté lista',
        'Optimizar descripcion de servicios con keywords de long tail',
    ]),
    ('ONGOING — Mantenimiento mensual', GREEN, [
        '2 Google Posts al mes (oferta + contenido educativo)',
        'Responder todas las reseñas (Google y plataformas externas)',
        '5+ fotos nuevas al mes',
        'Monitorizar posicion en Local Pack para keywords objetivo',
    ]),
]

for week_title, color, tasks in roadmap:
    # Cabecera semana
    week_t = Table([[Paragraph(f'<b>{week_title}</b>',
        ParagraphStyle('wt', fontName='Helvetica-Bold', fontSize=10,
                       textColor=WHITE, leading=14))
    ]], colWidths=[CONTENT_W])
    week_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), color),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [color]),
    ]))
    story.append(week_t)
    for task in tasks:
        story.append(Paragraph(f'<font color="#C8A96E">○</font>  {task}', S['bullet']))
    story.append(Spacer(1, 0.3*cm))

story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 8 — KPIs
# ════════════════════════════════════════════════════════════════════════════
story.append(SectionHeader('08', 'KPIs A MONITORIZAR', NAVY, CONTENT_W))
story.append(Spacer(1, 0.3*cm))

kpi_data = [
    ['Metrica', 'Herramienta', 'Frecuencia'],
    ['Búsquedas en GBP (impresiones)', 'Google Business Profile > Insights', 'Mensual'],
    ['Clics en llamada telefonica', 'GBP Insights', 'Mensual'],
    ['Clics en "Como llegar"', 'GBP Insights', 'Mensual'],
    ['Posicion en Local Pack (keywords)', 'Manual / BrightLocal', 'Mensual'],
    ['Numero de reseñas y media', 'GBP', 'Mensual'],
    ['Visitas web desde GBP', 'Google Analytics / Search Console', 'Mensual'],
]
story.append(make_table(kpi_data, [6.5*cm, 6.5*cm, 2.8*cm], font_size=8.5))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 9 — RESUMEN + FIRMA
# ════════════════════════════════════════════════════════════════════════════
story.append(SectionHeader('09', 'RESUMEN EJECUTIVO', NAVY, CONTENT_W))
story.append(Spacer(1, 0.4*cm))

# Caja de resumen
resumen_box = Table([[
    Paragraph(
        'El negocio tiene una <b>base sólida</b>: 25 años de experiencia, especialización triple única '
        '(Psicología + Etología + Adiestramiento) y reseñas de 5 estrellas. Sin embargo, la ficha de '
        'Google Business está en un <b>estado crítico</b> que actualmente repele clientes y perjudica '
        'el posicionamiento en Maps.',
        ParagraphStyle('rb', fontName='Helvetica', fontSize=10, textColor=NAVY, leading=16,
                       alignment=TA_JUSTIFY)
    )
]], colWidths=[CONTENT_W - 0.6*cm])
resumen_box.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, -1), GREY_LIGHT),
    ('LEFTPADDING', (0, 0), (-1, -1), 16),
    ('RIGHTPADDING', (0, 0), (-1, -1), 16),
    ('TOPPADDING', (0, 0), (-1, -1), 14),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
    ('LINEAFTER', (0, 0), (0, -1), 4, ACCENT),
    ('LINEBEFORE', (0, 0), (0, -1), 4, ACCENT),
]))
story.append(resumen_box)
story.append(Spacer(1, 0.5*cm))

story.append(Paragraph('Los 3 problemas que hay que resolver esta semana:', S['h2']))
story.append(Spacer(1, 0.1*cm))

tres = [
    ('1.', 'URL rota (404)', 'Eliminar barrera de credibilidad inmediata. Cambiar a Instagram o nueva web.'),
    ('2.', 'Descripcion sobre un chihuahua en venta', 'Reescribir con el texto optimizado propuesto. Impacto en CTR desde la primera semana.'),
    ('3.', 'Categoría dual criadero/adiestramiento', 'Elegir una identidad principal clara. Categoria "Adiestrador de perros" como primaria.'),
]
for num, title, desc in tres:
    row = Table([[
        Paragraph(num, ParagraphStyle('nt', fontName='Helvetica-Bold', fontSize=14,
                                       textColor=ACCENT, leading=18, alignment=TA_CENTER)),
        Table([[
            Paragraph(title, ParagraphStyle('tt', fontName='Helvetica-Bold', fontSize=10,
                                             textColor=RED, leading=14)),
            Paragraph(desc, ParagraphStyle('td', fontName='Helvetica', fontSize=9,
                                            textColor=TEXT_BODY, leading=14)),
        ]], colWidths=[CONTENT_W - 2*cm - 1*cm])
    ]], colWidths=[1*cm, CONTENT_W - 1*cm])
    row.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, GREY_LINE),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ]))
    story.append(row)

story.append(Spacer(1, 0.4*cm))
story.append(Paragraph(
    'Con estas tres correcciones más la carga de fotos, el impacto en visibilidad y conversión '
    'debería ser visible en <b>4-6 semanas</b>.',
    S['body']
))

# ─── FIRMA ───────────────────────────────────────────────────────────────────
story.append(Spacer(1, 1.5*cm))
story.append(HRFlowable(width=CONTENT_W, thickness=1, color=GREY_LINE))
story.append(Spacer(1, 0.4*cm))

firma_data = [[
    Table([[
        Paragraph('Preparado por', S['caption']),
        Paragraph('Chus Carvajal', ParagraphStyle('fn', fontName='Helvetica-Bold',
            fontSize=14, textColor=NAVY, leading=18, alignment=TA_CENTER)),
        Paragraph('Carvajal Photos SEO', ParagraphStyle('ft2', fontName='Helvetica',
            fontSize=9, textColor=GREY_MID, leading=13, alignment=TA_CENTER)),
        Paragraph('carvajalphotos@gmail.com', ParagraphStyle('fe', fontName='Helvetica',
            fontSize=8.5, textColor=ACCENT, leading=13, alignment=TA_CENTER)),
        Spacer(1, 0.3*cm),
        Paragraph('Junio 2026', ParagraphStyle('fd', fontName='Helvetica',
            fontSize=8, textColor=GREY_MID, leading=12, alignment=TA_CENTER)),
    ]], colWidths=[CONTENT_W / 2 - 0.5*cm]),
    Table([[
        Paragraph('Documento preparado para', S['caption']),
        Paragraph('Eduardo Mangas', ParagraphStyle('cn2', fontName='Helvetica-Bold',
            fontSize=14, textColor=NAVY, leading=18, alignment=TA_CENTER)),
        Paragraph('Criadero Casa del Ermitano', ParagraphStyle('cc', fontName='Helvetica',
            fontSize=9, textColor=GREY_MID, leading=13, alignment=TA_CENTER)),
        Paragraph('Adiestramiento & Psicologia Canina', ParagraphStyle('ccc', fontName='Helvetica',
            fontSize=8.5, textColor=GREY_MID, leading=13, alignment=TA_CENTER)),
        Spacer(1, 0.3*cm),
        Paragraph('Sitges · Garraf · Barcelona', ParagraphStyle('cl', fontName='Helvetica',
            fontSize=8, textColor=GREY_MID, leading=12, alignment=TA_CENTER)),
    ]], colWidths=[CONTENT_W / 2 - 0.5*cm]),
]]
firma_tbl = Table(firma_data, colWidths=[CONTENT_W / 2, CONTENT_W / 2])
firma_tbl.setStyle(TableStyle([
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('LINERIGHT', (0, 0), (0, -1), 1, GREY_LINE),
    ('TOPPADDING', (0, 0), (-1, -1), 0),
    ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
]))
story.append(firma_tbl)
story.append(Spacer(1, 0.4*cm))
story.append(HRFlowable(width=CONTENT_W, thickness=0.5, color=GREY_LINE))
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph(
    'Este documento es confidencial y ha sido elaborado exclusivamente para Criadero Casa del Ermitaño. '
    'Prohibida su reproduccion o distribución sin autorización expresa de Carvajal Photos SEO.',
    S['caption']
))

# ─── BUILD ───────────────────────────────────────────────────────────────────
doc.build(story, onFirstPage=first_page, onLaterPages=later_pages)
print(f"PDF generado correctamente: {OUTPUT_PATH}")
