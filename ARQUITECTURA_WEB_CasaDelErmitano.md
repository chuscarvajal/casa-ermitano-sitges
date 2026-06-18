# Arquitectura Web & Páginas de Servicio — Casa del Ermitaño
*Zona: el Garraf (Sitges, Vilanova i la Geltrú, Sant Pere de Ribes, Cubelles), Barcelona. Solo servicios reales del negocio e intención transaccional.*

---

## PARTE 1 — IDEAS DE PÁGINAS / SERVICIOS

> Criterio de no-canibalización: cada página ataca un **problema o intención distinta**, con vocabulario distinto. La pata de "psicología canina" no tiene una página genérica (canibalizaría) — se desdobla en páginas **por problema**.

| # | Página de servicio | Por qué merece página propia (intención transaccional única) |
|---|---|---|
| 1 | **Modificación de conducta / perros agresivos y reactivos** | Intención muy diferenciada y urgente ("mi perro se ha vuelto agresivo / muerde / se vuelve loco con otros perros"). Cliente desesperado, baja sensibilidad al precio. Es el gran diferenciador de Eduardo (reconduce casos crónicos). No solapa con educación básica: el buscador usa otras palabras. |
| 2 | **Ansiedad por separación (destrozos y ladridos en soledad)** | Problema concreto con búsquedas propias ("perro destroza cuando me voy", "ladra todo el día solo", "ansiedad por separación"). Vocabulario y dolor distintos a la agresividad → no canibaliza con la #1 aunque ambas sean "psicología". |
| 3 | **Criadero de Chihuahua (cachorros con pedigree RSCE/FCI)** | Intención totalmente distinta: **comprar**, no adiestrar. Ticket altísimo (1.500–6.000 €) y alcance nacional/internacional. Mercado y buscador propios. Ojo: página sensible (no publicar dirección). |
| 4 | **Adiestramiento canino y obediencia (educación general)** | El núcleo de volumen ("adiestrar perro", "que me haga caso", "no tirar de la correa"). Puerta de entrada del embudo. Intención general distinta de los problemas graves de las #1/#2. |
| 5 | **Educación de cachorros (socialización temprana)** | Buscador y momento vital propios ("educar cachorro primerizo", "socializar cachorro"). El primerizo no se ve en la página de "obediencia de perro adulto". Capta pronto → fideliza para toda la vida del perro. |
| 6 | **Adiestramiento de perros potencialmente peligrosos (PPP)** | Audiencia y normativa específicas ("adiestrar pitbull", "perro PPP educación"). Eduardo trabaja razas de trabajo y PPP. Nicho premium, poca competencia local, intención propia. |
| 7 | **Residencia para perros pequeños (hasta 5 kg, sin jaulas)** | Intención de "dejar el perro", no de adiestrar. Búsqueda propia ("residencia canina perros pequeños", "guardería perro pequeño sin jaulas"). *Servicio puntual → prioridad baja, sin sobreprometer.* |
| 8 | **Clases online de adiestramiento** | Intención no-local ("adiestramiento canino online", "consulta etología online"). No canibaliza lo local porque el buscador busca explícitamente "online". *Servicio emergente → prioridad baja.* |

### Ideas descartadas a propósito (para no canibalizar)
- **"Adiestrador a domicilio"** como página aparte → **descartada**: el servicio a domicilio es la *modalidad por defecto* de Eduardo, no un servicio distinto. Se menciona como ventaja dentro de cada página de adiestramiento, en lugar de competir con ellas por el mismo intento.
- **"Psicología / etología canina" genérica** → **descartada como página única**: canibalizaría a las #1 y #2. Es el *pilar* (vive en la home/sobre-mí), pero las páginas que convierten son las de problema concreto.
- **"Miedos y fobias"** como página separada → **fusionada** dentro de #1/#2 según el caso, para no fragmentar en exceso el pilar de conducta.

---

## PARTE 2 — ARQUITECTURA WEB (árbol de URLs)

**Idioma:** slugs en castellano para la v1. Para el bilingüe ES/CA acordado, espejo bajo `/ca/` (misma estructura).
**Principio geográfico:** las páginas de servicio se anclan a **"el Garraf"** (comarca = paraguas). Las **páginas de ciudad** son hijas del servicio estrella (#1 y #4) y atacan "adiestrador en [pueblo]" — un intento local distinto del de comarca, por eso no canibalizan.

### Árbol (ordenado de MAYOR a MENOR potencial de negocio)

```
/                                                           ← HOME (hub)
│   Casa del Ermitaño — Adiestramiento, psicología y criadero de Chihuahua en el Garraf
│   Reparte autoridad y enlaza a todas las páginas hijas. No vende un servicio: presenta a Eduardo y deriva.
│
├── /perros-agresivos-reactivos-garraf/        ① MÁXIMO potencial
│       Modificación de conducta y agresividad. Ticket alto (65€/ses.), su gran diferenciador, cliente urgente.
│
├── /ansiedad-por-separacion-perros-garraf/    ②
│       Destrozos y ladridos en soledad. Mismo pilar premium, problema muy común y urgente.
│
├── /criadero-chihuahua-cataluna/              ③
│       Venta de cachorros RSCE/FCI. Ticket máximo (1.500–6.000€) y alcance nacional/internacional,
│       pero volumen limitado y página sensible (sin dirección). Por eso va tras el pilar de conducta.
│
├── /adiestramiento-canino-garraf/             ④  (servicio estrella de VOLUMEN)
│       Educación y obediencia general. Mayor tráfico y puerta de entrada del embudo.
│       │
│       ├── /adiestrador-canino-sitges/                 ← páginas de ciudad (hijas, intento local)
│       ├── /adiestrador-canino-vilanova-i-la-geltru/
│       ├── /adiestrador-canino-sant-pere-de-ribes/
│       └── /adiestrador-canino-cubelles/
│
├── /educacion-de-cachorros-garraf/            ⑤
│       Socialización temprana. Capta pronto y fideliza (alto valor de vida del cliente).
│
├── /adiestramiento-perros-ppp-garraf/         ⑥
│       Razas de trabajo y potencialmente peligrosos. Nicho premium, poca competencia.
│
├── /residencia-perros-pequenos-garraf/        ⑦  (prioridad baja — servicio puntual)
│       Guardería para perros de hasta 5 kg, sin jaulas, videollamada diaria.
│
├── /clases-online-adiestramiento-canino/      ⑧  (prioridad baja — emergente, no-local)
│       Asesoramiento y adiestramiento a distancia. Único intento "online", amplía alcance.
│
└── /contacto/                                  (transversal: tel / WhatsApp / formulario / zona de servicio)
```

### Notas de arquitectura
- **Home subordinante, no competidora:** la `/` es el centro que enlaza y transmite autoridad; **no** intenta posicionar por un servicio concreto (evita canibalizar a sus hijas).
- **Páginas de ciudad solo donde compensa:** se abren bajo el servicio #4 (el de más volumen) y, en una segunda fase, podrían replicarse para el #1. **No** crear ciudad×servicio para todo: generaría páginas finas y canibalización. Cada página de ciudad debe ser *genuinamente local* (zonas, desplazamiento, casos de la zona), no un calco con el nombre cambiado.
- **Barcelona:** no tiene página propia de captación (Eduardo solo va con suplemento). Se nombra como "cobertura ampliada bajo presupuesto" dentro de las páginas, sin prometer servicio estándar.
- **Por qué este orden de negocio (no de volumen):** ① y ② son el pilar de **mayor margen y diferenciación** (precio premium, cliente cautivo, irremplazable). ③ tiene el **ticket más alto** pero volumen limitado y es sensible. ④–⑤ son **gran volumen pero menor precio** (embudo y fidelización). ⑥ es nicho. ⑦–⑧ son **oportunistas** y aún sin recorrido probado.
