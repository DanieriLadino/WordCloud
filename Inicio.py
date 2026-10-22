"""
☁️ WordCloud Studio — Nube de Palabras
Aplicación Streamlit con diseño suave tipo "cielo"

Instalación:
    pip install streamlit wordcloud matplotlib pandas Pillow numpy

Ejecución:
    streamlit run wordcloud_app.py
"""

import io
import re
import random
from collections import Counter

import numpy as np
import pandas as pd
import streamlit as st
from wordcloud import WordCloud, STOPWORDS

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="WordCloud Studio",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# NUBECITA SVG (con carita y animación flotante)
# ─────────────────────────────────────────────
NUBECITA_SVG = """
<svg class="nubecita" viewBox="0 0 220 140" xmlns="http://www.w3.org/2000/svg" aria-label="Nubecita">
  <defs>
    <linearGradient id="gNube" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"  stop-color="#ffffff"/>
      <stop offset="100%" stop-color="#e0ecff"/>
    </linearGradient>
    <filter id="sombra" x="-20%" y="-20%" width="140%" height="160%">
      <feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#3b82f6" flood-opacity="0.18"/>
    </filter>
  </defs>
  <g filter="url(#sombra)">
    <circle cx="70"  cy="80" r="38" fill="url(#gNube)"/>
    <circle cx="112" cy="58" r="48" fill="url(#gNube)"/>
    <circle cx="155" cy="82" r="34" fill="url(#gNube)"/>
    <rect x="62" y="78" width="100" height="40" rx="20" fill="url(#gNube)"/>
  </g>
  <!-- carita -->
  <ellipse cx="96"  cy="80" rx="5" ry="6.5" fill="#1e293b"/>
  <ellipse cx="130" cy="80" rx="5" ry="6.5" fill="#1e293b"/>
  <circle  cx="98"  cy="77.5" r="1.6" fill="#ffffff"/>
  <circle  cx="132" cy="77.5" r="1.6" fill="#ffffff"/>
  <path d="M104 92 Q113 101 122 92" stroke="#1e293b" stroke-width="3" fill="none" stroke-linecap="round"/>
  <ellipse cx="84"  cy="93" rx="7" ry="4" fill="#fda4af" opacity="0.6"/>
  <ellipse cx="142" cy="93" rx="7" ry="4" fill="#fda4af" opacity="0.6"/>
  <!-- gotitas de palabras -->
  <text x="18"  y="40" font-family="Plus Jakarta Sans, sans-serif" font-size="13" font-weight="700" fill="#60a5fa" opacity="0.85">datos</text>
  <text x="168" y="30" font-family="Plus Jakarta Sans, sans-serif" font-size="11" font-weight="700" fill="#a78bfa" opacity="0.85">ideas</text>
  <text x="178" y="128" font-family="Plus Jakarta Sans, sans-serif" font-size="10" font-weight="700" fill="#f472b6" opacity="0.8">texto</text>
</svg>
"""

# ─────────────────────────────────────────────
# ESTILOS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

:root{
  --cielo-1:#eef5ff; --cielo-2:#f7f3ff;
  --tinta:#0f172a; --tinta-2:#334155; --tenue:#64748b;
  --azul:#3b82f6; --violeta:#8b5cf6; --rosa:#ec4899;
  --borde:#e2e8f0; --card:#ffffffcc;
}

html, body, [class*="css"] { font-family:'Plus Jakarta Sans', sans-serif; }

.stApp{
  background:
    radial-gradient(1200px 500px at 10% -10%, #dbeafe 0%, transparent 60%),
    radial-gradient(900px 500px at 100% 0%, #ede9fe 0%, transparent 55%),
    linear-gradient(180deg, var(--cielo-1), var(--cielo-2));
}

/* Sidebar */
[data-testid="stSidebar"]{
  background:#ffffffe6 !important;
  backdrop-filter: blur(8px);
  border-right:1px solid var(--borde);
}
[data-testid="stSidebar"] h3{
  color:var(--tenue) !important; font-size:.74rem !important; font-weight:800 !important;
  letter-spacing:1.4px !important; text-transform:uppercase !important; margin-bottom:.3rem !important;
}
[data-testid="stSidebar"] label{ color:var(--tinta-2) !important; font-weight:600 !important; font-size:.86rem !important; }

/* Inputs */
textarea, input[type="text"]{
  border-radius:12px !important; border:1px solid var(--borde) !important;
  background:#fff !important; color:var(--tinta) !important;
}
textarea:focus, input[type="text"]:focus{
  border-color:var(--azul) !important; box-shadow:0 0 0 3px #3b82f633 !important;
}
[data-baseweb="select"] > div{ border-radius:12px !important; border:1px solid var(--borde) !important; background:#fff !important; }

/* Títulos y texto */
h1,h2,h3,h4{ color:var(--tinta) !important; font-family:'Plus Jakarta Sans',sans-serif !important; }
p, li{ color:var(--tinta-2) !important; line-height:1.65 !important; }

/* Botones */
.stButton > button{
  background:linear-gradient(135deg, var(--azul), var(--violeta)) !important;
  color:#fff !important; border:none !important; border-radius:999px !important;
  font-weight:700 !important; letter-spacing:.3px !important; padding:.65rem 1.4rem !important;
  box-shadow:0 6px 18px #6366f140 !important; transition:transform .15s, box-shadow .15s !important;
}
.stButton > button:hover{ transform:translateY(-1px); box-shadow:0 10px 24px #6366f155 !important; }
[data-testid="stDownloadButton"] button{
  background:#fff !important; color:var(--tinta) !important; border:1px solid var(--borde) !important;
  border-radius:999px !important; font-weight:700 !important;
}
[data-testid="stDownloadButton"] button:hover{ border-color:var(--azul) !important; color:var(--azul) !important; }

/* Métricas (compatibles con versiones viejas y nuevas de Streamlit) */
[data-testid="stMetric"], [data-testid="metric-container"]{
  background:var(--card); border:1px solid var(--borde); border-radius:18px;
  padding:16px 20px; box-shadow:0 4px 18px #1e3a8a0d;
}
[data-testid="stMetricLabel"] p{ color:var(--tenue) !important; font-size:.75rem !important; font-weight:700 !important; text-transform:uppercase; letter-spacing:.8px; }
[data-testid="stMetricValue"]{ color:var(--tinta) !important; font-weight:800 !important; }

/* Header */
.hero{
  display:flex; align-items:center; justify-content:space-between; gap:24px;
  background:linear-gradient(135deg,#ffffffee,#ffffffb3);
  border:1px solid var(--borde); border-radius:24px;
  padding:26px 34px; margin-bottom:22px; box-shadow:0 10px 40px #3b82f614;
}
.hero h1{ margin:0; font-size:2.1rem; font-weight:800; letter-spacing:-.8px; }
.hero h1 span{
  background:linear-gradient(90deg,var(--azul),var(--violeta),var(--rosa));
  -webkit-background-clip:text; background-clip:text; color:transparent;
}
.hero p{ margin:6px 0 0; color:var(--tenue) !important; }
.nubecita{ width:190px; flex-shrink:0; animation:flotar 4s ease-in-out infinite; }
@keyframes flotar{ 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }

/* Tarjetas */
.card{
  background:var(--card); border:1px solid var(--borde); border-radius:20px;
  padding:22px 26px; margin-bottom:16px; box-shadow:0 4px 18px #1e3a8a0a;
}
.info-item{
  display:flex; gap:14px; align-items:flex-start; padding:12px 14px;
  border-radius:14px; background:#f8faff; border:1px solid #eef2ff; margin-bottom:8px;
}
.info-ico{
  width:38px; height:38px; border-radius:12px; display:grid; place-items:center; font-size:1.1rem;
  background:linear-gradient(135deg,#dbeafe,#ede9fe); flex-shrink:0;
}
.chip{
  display:inline-block; padding:6px 14px; margin:4px 3px; border-radius:999px;
  background:#fff; border:1px solid var(--borde); font-size:.84rem; font-weight:600; color:var(--tinta-2);
}
.swatch-row{ display:flex; align-items:center; justify-content:space-between; padding:7px 0; border-bottom:1px dashed #e2e8f0; }
.swatch-row span.nom{ font-size:.86rem; font-weight:600; color:var(--tinta-2); }
.swatch{ display:flex; gap:3px; }
.swatch i{ width:16px; height:16px; border-radius:50%; display:inline-block; border:1px solid #0000000d; }

/* Frecuencias */
.freq-row{
  display:flex; align-items:center; gap:12px; padding:7px 12px; margin:5px 0;
  background:#fff; border:1px solid #eef2ff; border-radius:12px; transition:transform .12s;
}
.freq-row:hover{ transform:translateX(3px); }
.rank{ font-family:'JetBrains Mono',monospace; font-size:.74rem; font-weight:500; color:var(--tenue);
       background:#f1f5f9; border-radius:8px; padding:2px 8px; min-width:38px; text-align:center; }
.palabra{ font-weight:700; color:var(--tinta); min-width:130px; font-size:.92rem; }
.pista{ flex:1; height:9px; background:#f1f5f9; border-radius:99px; overflow:hidden; }
.barra{ height:100%; border-radius:99px; background:linear-gradient(90deg,var(--azul),var(--violeta),var(--rosa)); }
.num{ font-family:'JetBrains Mono',monospace; font-size:.86rem; color:var(--tinta-2); min-width:30px; text-align:right; }

.wc-box{ background:#fff; border:1px solid var(--borde); border-radius:22px; padding:14px; box-shadow:0 10px 30px #1e3a8a12; }
.wc-meta{ color:var(--tenue); font-size:.86rem; margin:0 0 10px 4px; }

div[data-testid="stExpander"]{ border-radius:16px !important; border:1px solid var(--borde) !important; background:#fff !important; }
hr{ border-color:#e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# STOPWORDS (con y sin tildes)
# ─────────────────────────────────────────────
_STOP_ES_BASE = """
de la el en y a los del se las un por con no una su para es al lo como mas más pero sus le ya o
este esta estos estas si sí porque entre cuando muy sin sobre tambien también me hasta hay donde dónde
quien quién desde nos durante ni contra ese eso esa esos esas ante bajo tras que qué fue son han ha
ser era eran estan están siendo sido he has hemos habian habían tiene tienen hacer puede pueden asi así
tan parte todo todos todas cada otro otra otros otras mismo misma nuestro nuestra ellos ellas nosotros
les aquel aquella aquellos aqui aquí alli allí ahi ahí cual cuál cuales cuáles yo tu tú te mi mis él
ella uno dos sea son estar está estaba estamos fueron será sera
"""
STOPWORDS_ES = set(_STOP_ES_BASE.split())


def obtener_stopwords(idioma):
    if idioma == "Ninguno":
        return set()
    sw = set()
    if idioma in ("Inglés", "Ambos"):
        sw |= set(STOPWORDS)
    if idioma in ("Español", "Ambos"):
        sw |= STOPWORDS_ES
    return sw


# ─────────────────────────────────────────────
# PALETAS
# ─────────────────────────────────────────────
PALETAS = {
    "Cielo pastel":        ["#1d4ed8", "#2563eb", "#3b82f6", "#60a5fa", "#7c3aed", "#a78bfa", "#38bdf8"],
    "Atardecer":           ["#9d174d", "#db2777", "#f43f5e", "#fb7185", "#f97316", "#fbbf24", "#7c3aed"],
    "Aurora":              ["#0f766e", "#14b8a6", "#22d3ee", "#6366f1", "#a855f7", "#10b981", "#0ea5e9"],
    "Algodón de azúcar":   ["#ec4899", "#f472b6", "#a78bfa", "#818cf8", "#60a5fa", "#f9a8d4", "#c084fc"],
    "Azul corporativo":    ["#1e3a5f", "#1d4ed8", "#2563eb", "#3b82f6", "#60a5fa", "#0f2942", "#1e40af"],
    "Verde institucional": ["#064e3b", "#065f46", "#047857", "#059669", "#10b981", "#34d399", "#0f766e"],
    "Terracota":           ["#7c2d12", "#9a3412", "#c2410c", "#ea580c", "#f97316", "#b45309", "#78350f"],
    "Escala de grises":    ["#111827", "#1f2937", "#374151", "#4b5563", "#6b7280", "#9ca3af", "#0f172a"],
}

FONDOS = {
    "Blanco": "#ffffff",
    "Cielo":  "#eef5ff",
    "Noche":  "#0f172a",
}

FORMAS = ["Nube ☁️", "Rectángulo", "Círculo"]


# ─────────────────────────────────────────────
# MÁSCARAS
# ─────────────────────────────────────────────
def mascara_nube(w=1000, h=600):
    """Dibuja una nube con círculos + base redondeada. 0 = zona dibujable, 255 = fuera."""
    y, x = np.ogrid[:h, :w]
    dentro = np.zeros((h, w), dtype=bool)
    # (centro_x, centro_y, radio) relativos al alto/ancho
    bolitas = [
        (0.26, 0.62, 0.21),
        (0.40, 0.46, 0.26),
        (0.58, 0.38, 0.31),
        (0.76, 0.58, 0.22),
        (0.50, 0.62, 0.22),
    ]
    for cx, cy, r in bolitas:
        dentro |= (x - cx * w) ** 2 + (y - cy * h) ** 2 <= (r * h) ** 2
    # base plana con puntas redondeadas
    base_top, base_bot = int(0.58 * h), int(0.83 * h)
    radio_base = (base_bot - base_top) / 2
    cy_base = (base_top + base_bot) / 2
    x_izq, x_der = 0.22 * w, 0.80 * w
    dentro |= (y >= base_top) & (y <= base_bot) & (x >= x_izq) & (x <= x_der)
    dentro |= (x - x_izq) ** 2 + (y - cy_base) ** 2 <= radio_base ** 2
    dentro |= (x - x_der) ** 2 + (y - cy_base) ** 2 <= radio_base ** 2
    return np.where(dentro, 0, 255).astype(np.uint8)


def mascara_circulo(size=600):
    y, x = np.ogrid[:size, :size]
    c = size // 2
    m = np.full((size, size), 255, dtype=np.uint8)
    m[(x - c) ** 2 + (y - c) ** 2 <= (c - 10) ** 2] = 0
    return m


def obtener_mascara(forma):
    if forma.startswith("Nube"):
        return mascara_nube()
    if forma == "Círculo":
        return mascara_circulo()
    return None


# ─────────────────────────────────────────────
# FUNCIONES CORE
# ─────────────────────────────────────────────
def limpiar_texto(texto, stopwords, min_longitud):
    texto = texto.lower()
    texto = re.sub(r"http\S+|www\S+", " ", texto)
    texto = re.sub(r"[^a-záéíóúüñàâèêîôùûäëïöç\s]", " ", texto)
    palabras = [p for p in texto.split() if p not in stopwords and len(p) >= min_longitud]
    return " ".join(palabras)


def contar_palabras(texto_limpio, n=50):
    return pd.DataFrame(Counter(texto_limpio.split()).most_common(n),
                        columns=["Palabra", "Frecuencia"])


@st.cache_data(show_spinner=False)
def generar_wordcloud_png(texto_limpio, paleta_nombre, max_words, fondo_hex, forma, semilla):
    colores = PALETAS[paleta_nombre]
    rng_local = random.Random(semilla)

    def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        # Palabras grandes → tonos más intensos (primeros de la paleta)
        if font_size > 70:
            return colores[rng_local.randint(0, 2)]
        return colores[rng_local.randint(0, len(colores) - 1)]

    mascara = obtener_mascara(forma)
    es_nube = forma.startswith("Nube")
    contorno = "#c7d2fe" if fondo_hex != "#0f172a" else "#334155"

    wc = WordCloud(
        width=1200, height=650,
        max_words=max_words,
        background_color=fondo_hex,
        color_func=color_func,
        mask=mascara,
        contour_width=4 if mascara is not None else 0,
        contour_color=contorno,
        collocations=False,
        min_font_size=10, max_font_size=140,
        prefer_horizontal=0.85 if es_nube else 0.75,
        relative_scaling=0.5, margin=4,
        random_state=semilla, scale=2,
    ).generate(texto_limpio)

    buf = io.BytesIO()
    wc.to_image().save(buf, format="PNG")
    return buf.getvalue()


# ─────────────────────────────────────────────
# ESTADO
# ─────────────────────────────────────────────
st.session_state.setdefault("generado", False)
st.session_state.setdefault("texto_area", "")
st.session_state.setdefault("semilla", 42)

EJEMPLOS = {
    "Inteligencia Artificial": """
    La inteligencia artificial es una disciplina de la informática orientada a desarrollar
    sistemas capaces de ejecutar tareas que requieren capacidades cognitivas humanas.
    El aprendizaje automático, las redes neuronales profundas y el procesamiento del
    lenguaje natural constituyen los pilares técnicos de los sistemas modernos de
    inteligencia artificial. Los modelos de lenguaje de gran escala, la visión
    computacional y la robótica autónoma representan aplicaciones de vanguardia.
    La inteligencia artificial transforma sectores como la salud, la educación,
    la manufactura, las finanzas y el transporte, generando eficiencias significativas.
    """,
    "Colombia": """
    Colombia es una nación situada en el extremo noroccidental de América del Sur,
    reconocida por su excepcional biodiversidad, riqueza cultural y diversidad de paisajes.
    Bogotá es la capital y principal centro económico, seguida de Medellín, Cali y
    Barranquilla como ciudades de relevancia nacional. El café colombiano goza de
    reconocimiento internacional por su calidad y perfil aromático. La floricultura
    colombiana abastece mercados globales con alta competitividad. El país alberga
    ecosistemas del Amazonas, los Andes, el Caribe y el Pacífico, constituyéndose
    como uno de los territorios con mayor biodiversidad del planeta.
    """,
    "Tecnología 4.0": """
    La cuarta revolución industrial redefine los modelos productivos mediante la
    convergencia de tecnologías digitales avanzadas. El Internet de las cosas,
    la inteligencia artificial, el análisis de grandes datos, la robótica colaborativa
    y la automatización inteligente son pilares estratégicos de la industria moderna.
    Las fábricas inteligentes integran sensores, conectividad y analítica para
    optimizar procesos en tiempo real. La manufactura aditiva, los gemelos digitales
    y la realidad aumentada transforman la ingeniería de producción. La computación
    en la nube y la ciberseguridad son habilitadores fundamentales de la
    transformación digital empresarial.
    """,
}


def cargar_ejemplo():
    st.session_state["texto_area"] = " ".join(EJEMPLOS[st.session_state["ejemplo_sel"]].split())


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:10px;margin:4px 0 6px;">'
        '<span style="font-size:1.7rem;">☁️</span>'
        '<span style="font-weight:800;font-size:1.15rem;color:#0f172a;">WordCloud Studio</span></div>',
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown("### Fuente de texto")
    fuente = st.radio("fuente", ["✍️ Escribir / Pegar", "📂 Subir archivo"],
                      label_visibility="collapsed", horizontal=True)
    texto_input = ""

    if fuente == "✍️ Escribir / Pegar":
        texto_input = st.text_area(
            "Texto:", key="texto_area", height=190,
            placeholder="Pega aquí un artículo, reseña, discurso, encuesta…",
        )
        with st.expander("✨ Probar con un ejemplo"):
            st.selectbox("Ejemplo:", list(EJEMPLOS.keys()), key="ejemplo_sel",
                         label_visibility="collapsed")
            st.button("Cargar ejemplo", on_click=cargar_ejemplo, use_container_width=True)
    else:
        archivo = st.file_uploader("Archivo:", type=["txt", "csv"], label_visibility="collapsed")
        if archivo:
            if archivo.name.lower().endswith(".txt"):
                texto_input = archivo.read().decode("utf-8", errors="ignore")
            else:
                df_csv = pd.read_csv(archivo)
                col_txt = st.selectbox("Columna de texto:", df_csv.columns.tolist())
                texto_input = " ".join(df_csv[col_txt].dropna().astype(str).tolist())
            st.success(f"Archivo cargado · {len(texto_input):,} caracteres")

    st.divider()
    st.markdown("### Procesamiento")
    idioma = st.selectbox("Stopwords:", ["Español", "Inglés", "Ambos", "Ninguno"])
    min_longitud = st.slider("Longitud mínima de palabra", 2, 8, 3)
    palabras_extra = st.text_input("Excluir palabras:", placeholder="ej: también, así, aquí")

    st.divider()
    st.markdown("### Apariencia")
    forma_sel = st.selectbox("Forma:", FORMAS)
    paleta_sel = st.selectbox("Paleta:", list(PALETAS.keys()))
    fondo_sel = st.radio("Fondo:", list(FONDOS.keys()), horizontal=True)
    max_words = st.slider("Máximo de palabras:", 20, 250, 100)

    st.divider()
    c1, c2 = st.columns([3, 1])
    with c1:
        if st.button("Generar nube ☁️", use_container_width=True):
            st.session_state["generado"] = True
    with c2:
        if st.button("🎲", help="Otra distribución", use_container_width=True):
            st.session_state["semilla"] = random.randint(0, 10_000)
            st.session_state["generado"] = True


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <div>
    <h1>WordCloud <span>Studio</span></h1>
    <p>Convierte cualquier texto en una nube de palabras y descubre de qué habla de verdad.</p>
  </div>
  {NUBECITA_SVG}
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# BIENVENIDA
# ─────────────────────────────────────────────
if not st.session_state["generado"] or not texto_input.strip():
    col_izq, col_der = st.columns([3, 2], gap="large")

    with col_izq:
        items = "".join(
            f'<div class="info-item"><div class="info-ico">{ico}</div>'
            f'<div><strong style="color:#0f172a;">{tit}</strong>'
            f'<p style="margin:2px 0 0;font-size:.88rem;color:#64748b !important;">{desc}</p></div></div>'
            for ico, tit, desc in [
                ("📊", "Análisis de frecuencia", "Encuentra los términos que dominan tu texto."),
                ("🧹", "Limpieza inteligente", "Quita palabras vacías en español e inglés, con y sin tildes."),
                ("🎨", "Formas y paletas", "Nube, círculo o rectángulo, con paletas suaves o corporativas."),
                ("⬇️", "Exporta todo", "Imagen PNG en alta resolución y tabla de frecuencias en CSV."),
            ]
        )
        st.markdown(
            '<div class="card"><h3 style="margin-top:0;">¿Cómo funciona?</h3>'
            '<p>Las palabras que más se repiten aparecen más grandes. Así ves de un vistazo los temas centrales de un texto.</p>'
            f'{items}'
            '<p style="margin-top:14px;"><strong>1.</strong> Pega o sube un texto · '
            '<strong>2.</strong> Elige forma y paleta · <strong>3.</strong> Pulsa <strong>Generar nube ☁️</strong></p>'
            '</div>',
            unsafe_allow_html=True,
        )

    with col_der:
        chips = "".join(f'<span class="chip">{c}</span>' for c in [
            "📰 Prensa", "📋 Encuestas abiertas", "💬 Reseñas", "🎓 Textos académicos",
            "🗳️ Discursos", "📚 Literatura", "📊 Informes",
        ])
        st.markdown(f'<div class="card"><h3 style="margin-top:0;">Ideal para</h3>{chips}</div>',
                    unsafe_allow_html=True)

        filas = "".join(
            f'<div class="swatch-row"><span class="nom">{nom}</span>'
            f'<span class="swatch">{"".join(f"<i style=background:{c}></i>" for c in cols[:6])}</span></div>'
            for nom, cols in PALETAS.items()
        )
        st.markdown(f'<div class="card"><h3 style="margin-top:0;">Paletas</h3>{filas}</div>',
                    unsafe_allow_html=True)

    if st.session_state["generado"] and not texto_input.strip():
        st.warning("Primero escribe o sube un texto en el panel lateral 🙂")
    st.stop()


# ─────────────────────────────────────────────
# PROCESAMIENTO
# ─────────────────────────────────────────────
stopwords_set = obtener_stopwords(idioma)
if palabras_extra.strip():
    stopwords_set |= {p.strip().lower() for p in palabras_extra.split(",") if p.strip()}

texto_limpio = limpiar_texto(texto_input, stopwords_set, min_longitud)
if not texto_limpio.strip():
    st.error("Después de limpiar no quedó ninguna palabra. Baja la longitud mínima o cambia las stopwords.")
    st.stop()

df_freq = contar_palabras(texto_limpio)
total_palabras = len(texto_limpio.split())
vocabulario = len(set(texto_limpio.split()))

m1, m2, m3, m4 = st.columns(4)
m1.metric("Palabras procesadas", f"{total_palabras:,}")
m2.metric("Vocabulario único", f"{vocabulario:,}")
m3.metric("Término estrella", df_freq.iloc[0]["Palabra"])
m4.metric("Frecuencia máxima", int(df_freq.iloc[0]["Frecuencia"]))

st.write("")

with st.spinner("Inflando la nube…"):
    img_bytes = generar_wordcloud_png(
        texto_limpio, paleta_sel, max_words, FONDOS[fondo_sel],
        forma_sel, st.session_state["semilla"],
    )

st.markdown(
    f'<div class="wc-box"><p class="wc-meta">☁️ {forma_sel} · {paleta_sel} · fondo {fondo_sel.lower()} · '
    f'hasta {max_words} palabras</p>',
    unsafe_allow_html=True,
)
st.image(img_bytes, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.download_button("⬇️ Descargar imagen PNG", data=img_bytes,
                   file_name="nube_de_palabras.png", mime="image/png",
                   use_container_width=True)

st.divider()

col_freq, col_tabla = st.columns([3, 2], gap="large")

with col_freq:
    st.markdown("### Top 20 palabras")
    top20 = df_freq.head(20)
    max_freq = top20["Frecuencia"].max()
    filas = "".join(
        f'<div class="freq-row"><span class="rank">#{i:02d}</span>'
        f'<span class="palabra">{row.Palabra}</span>'
        f'<div class="pista"><div class="barra" style="width:{max(6, row.Frecuencia / max_freq * 100):.0f}%"></div></div>'
        f'<span class="num">{row.Frecuencia}</span></div>'
        for i, row in enumerate(top20.itertuples(), 1)
    )
    st.markdown(filas, unsafe_allow_html=True)

with col_tabla:
    st.markdown("### Tabla de frecuencias")
    st.dataframe(
        df_freq.head(30).style.background_gradient(subset=["Frecuencia"], cmap="BuPu"),
        use_container_width=True, height=520, hide_index=True,
    )
    st.download_button("⬇️ Exportar tabla (.csv)",
                       data=df_freq.to_csv(index=False).encode("utf-8"),
                       file_name="frecuencias.csv", mime="text/csv",
                       use_container_width=True)

st.divider()

with st.expander("Ver texto procesado (sin stopwords)"):
    preview = texto_limpio[:2500] + ("…" if len(texto_limpio) > 2500 else "")
    st.markdown(
        f'<p style="font-family:JetBrains Mono,monospace;font-size:.84rem;background:#f8faff;'
        f'padding:16px;border-radius:14px;border:1px solid #e2e8f0;line-height:1.8;">{preview}</p>',
        unsafe_allow_html=True,
    )
 
