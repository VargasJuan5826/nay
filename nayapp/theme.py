"""CSS de la app.

Los tokens, keyframes y medidas son los mismos que `app/globals.css` y los estilos
inline del original en Next.js. El resto son los reset necesarios para que los widgets
de Streamlit se vean exactamente como los `<button>` originales.

Convenciones:
  * cada widget lleva `key="nay_..."` y Streamlit publica ese key como clase
    `st-key-nay_...`, así que los selectores usan `[class*="st-key-nay_opt_"]` para
    estilar familias completas de widgets;
  * los bloques de HTML propio se envuelven en `.nay` para ganarle en especificidad a
    los estilos del markdown de Streamlit.
"""

from __future__ import annotations

import streamlit as st

from . import content

TOKENS = """
:root {
  --bg: #f7f3ff;
  --card: #ffffff;
  --primary: #7c3aed;
  --primary-light: #ede9fe;
  --primary-dark: #5b21b6;
  --accent: #ec4899;
  --accent-light: #fce7f3;
  --green: #10b981;
  --green-light: #d1fae5;
  --text: #1e1b4b;
  --text-muted: #6b7280;
  --border: #e5e7eb;
  --shadow: 0 4px 24px rgba(124,58,237,0.12);
  --shadow-lg: 0 8px 40px rgba(124,58,237,0.18);
  --radius: 20px;
  --radius-sm: 12px;
  --mono: 'Fira Code', monospace;
  --sans: 'Nunito', sans-serif;
}
@media (max-width: 480px) {
  :root { --radius: 16px; --radius-sm: 10px; }
}
"""

KEYFRAMES = """
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
@keyframes fadeDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.08); } }
@keyframes pop { from { opacity: 0; transform: scale(0.8); } to { opacity: 1; transform: scale(1); } }
@keyframes rain { from { top: -50px; opacity: 1; } to { top: 110vh; opacity: 0; } }
"""

SHELL = """
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stToolbarActions"],
[data-testid="stActionButton"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stBottomBlockContainer"],
[data-testid="stAppDeployButton"],
#MainMenu, footer, .stAppDeployButton,
/* Badges que inyecta Streamlit Community Cloud en el deploy (link al repo de GitHub,
   "Fork", avatar del dueño y el badge "Hosted with Streamlit"). No aparecen en local. */
[class*="viewerBadge"],
[class*="_profileContainer"],
[class*="_viewerBadge"],
a[href*="streamlit.io/cloud"],
a[href*="share.streamlit.io"] { display: none !important; }

.stApp, [data-testid="stAppViewContainer"] {
  background-color: var(--bg);
  background-image:
    radial-gradient(circle at 20% 20%, rgba(124,58,237,0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(236,72,153,0.06) 0%, transparent 50%);
  background-attachment: fixed;
  font-family: var(--sans);
  color: var(--text);
}
@media (max-width: 480px) {
  .stApp, [data-testid="stAppViewContainer"] {
    background-image:
      radial-gradient(circle at 20% 10%, rgba(124,58,237,0.06) 0%, transparent 40%),
      radial-gradient(circle at 80% 90%, rgba(236,72,153,0.04) 0%, transparent 40%);
  }
}

/* El original mide 560px y queda centrado vertical y horizontalmente. */
[data-testid="stMainBlockContainer"] {
  max-width: 560px !important;
  width: 100% !important;
  padding: 16px 12px !important;
  margin: 0 auto !important;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
/* El centrado va con `margin: auto` y no con `justify-content`: cuando el paso es más
   alto que la ventana (el calendario abierto, por ejemplo) los márgenes automáticos
   colapsan a 0 y el contenido sigue siendo alcanzable en vez de recortarse. */
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
  flex: 0 0 auto;
  margin-top: auto;
  margin-bottom: auto;
}

/* Sin gaps automáticos: el espaciado lo dan los márgenes del diseño original. */
[data-testid="stVerticalBlock"] { gap: 0 !important; }
[data-testid="stHorizontalBlock"] { gap: 0 !important; align-items: center; flex-wrap: nowrap !important; }
/* Streamlit apila las columnas cuando la ventana es angosta; acá las filas (calendario,
   minutos, presets) tienen que mantenerse horizontales siempre. */
[data-testid="stColumn"] { min-width: 0 !important; }
[data-testid="stLayoutWrapper"] { width: 100%; }
/* Streamlit compensa el margen de sus <p> con un margin-bottom negativo en el contenedor
   de markdown. Este port no usa <p>, así que ese -16px se comería el espaciado. */
[data-testid="stMarkdown"], [data-testid="stMarkdownContainer"] { width: 100%; }
[data-testid="stMarkdownContainer"] { margin-bottom: 0 !important; }
[data-testid="stMarkdownContainer"] p { margin: 0; }
[data-testid="stIFrame"] { display: block; border: 0; color-scheme: normal; }
.nay, .nay * { box-sizing: border-box; }
/* `globals.css` del original aplica esto a TODAS las imágenes del documento, no sólo a
   las propias. Importa replicarlo así: html2canvas mide la línea base de cada fuente con
   una sonda que incluye un <img>, y si ese <img> no es `block` el texto del PDF sale
   corrido 3px. */
img { max-width: 100%; display: block; }
/* Streamlit fuerza `object-fit: scale-down`; el original usa el default del navegador,
   que sí deforma la imagen del corgi a 90x120. */
.nay img { object-fit: fill; }

/* El original declara 'Nunito'/'Fira Code' sin cargarlas: cae en las genéricas del
   sistema. Se replica el mismo stack para obtener idéntico renderizado, y se neutraliza
   la tipografía propia de Streamlit. */
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] * { font-family: var(--sans); }
.stButton > button, .stButton > button * { font-family: var(--sans) !important; }
/* `body` vuelve al `normal` del navegador, como en el original. Además de la vista, esto
   importa para el PDF: html2canvas calcula la línea base con una sonda que hereda el
   line-height del body, y con el de Streamlit el texto salía 3px más arriba. */
body { line-height: normal; }
.nay { line-height: normal; }
/* El <body> del original mide 16px: fija el strut de las líneas y lo que heredan los
   elementos que no declaran tamaño. */
.nay { font-size: 16px; }
"""

BUTTON_BASE = """
.stButton > button {
  font-family: var(--sans);
  min-height: 0 !important;
  line-height: normal;
  transition: all 0.2s ease;
  box-shadow: none;
  cursor: pointer;
}
.stButton > button:focus, .stButton > button:focus-visible, .stButton > button:active {
  outline: none !important;
}
/* La etiqueta viaja dentro de div > span > markdown > p: que todo herede del <button>
   y que el <p> no aporte el margen del markdown. */
.stButton > button > div,
.stButton > button span,
.stButton > button [data-testid="stMarkdownContainer"],
.stButton > button p {
  font-family: inherit !important;
  font-size: inherit !important;
  font-weight: inherit !important;
  color: inherit !important;
  line-height: inherit !important;
  letter-spacing: inherit !important;
  margin: 0 !important;
  padding: 0 !important;
}

/* .btn-next del original: el botón degradado de ancho completo. */
.st-key-nay_start .stButton > button,
.st-key-nay_confirm_date .stButton > button,
[class*="st-key-nay_next_"] .stButton > button {
  width: 100%;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: 12px 20px;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 12px rgba(124,58,237,0.3);
  white-space: normal;
}
.st-key-nay_start .stButton > button:hover,
.st-key-nay_confirm_date .stButton > button:hover,
[class*="st-key-nay_next_"] .stButton > button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(124,58,237,0.4);
  color: #fff;
  border: none;
}
.st-key-nay_start .stButton > button { padding: 14px 20px; font-size: 14px; }
.st-key-nay_confirm_date { margin-top: 16px; }
[class*="st-key-nay_next_"] { margin-top: 12px; }
"""

BLOCKS = """
.nay-header { text-align: center; margin-bottom: 20px; animation: fadeDown .6s ease; }
.nay-header img { width: 100px; height: auto; border-radius: 16px; margin: 0 auto 12px;
  filter: drop-shadow(0 0 20px rgba(192,132,252,0.5)); }
.nay .nay-title { font-size: 22px; font-weight: 900; line-height: 1.2; margin: 0; padding: 0;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.nay .nay-sub { font-family: var(--mono); font-size: 10px; color: var(--text-muted);
  margin-top: 4px; }

.nay-step { animation: slideUp .4s cubic-bezier(.34,1.56,.64,1); }

.nay .plea-card { background: var(--primary-light); border: 2px solid rgba(124,58,237,0.2);
  border-radius: var(--radius); padding: 14px 16px; display: flex; gap: 12px;
  align-items: center; margin-bottom: 16px; }
.nay .plea-card img { width: 56px; height: 56px; border-radius: 12px; flex-shrink: 0; }
.nay .plea-text { font-size: 14px; font-weight: 700; color: var(--primary-dark); line-height: 1.4; }
.nay .plea-note { display: block; font-size: 11px; font-family: var(--mono);
  color: var(--primary); opacity: .8; font-weight: 400; margin-top: 4px; }

.nay .q-card { background: var(--card); border-radius: var(--radius); box-shadow: var(--shadow);
  padding: 16px; margin-bottom: 12px; border: 1px solid var(--border); }
.nay .q-tag { font-family: var(--mono); font-size: 10px; background: var(--primary-light);
  color: var(--primary); padding: 3px 8px; border-radius: 100px; display: inline-block;
  margin-bottom: 8px; font-weight: 500; }
.nay .q-text { font-size: 15px; font-weight: 800; color: var(--text); line-height: 1.4; }

.nay .nay-progress-label { font-family: var(--mono); font-size: 10px; color: var(--text-muted);
  margin-bottom: 6px; display: block; }
.nay .nay-progress-wrap { background: var(--border); border-radius: 100px; height: 5px;
  margin-bottom: 16px; overflow: hidden; }
.nay .nay-progress-fill { height: 100%; background: linear-gradient(90deg, var(--primary), var(--accent));
  border-radius: 100px; transition: width .5s cubic-bezier(.34,1.56,.64,1); }
.nay .nay-qhead { text-align: center; margin: 0 0 8px; }
.nay .nay-qhead img { margin: 0 auto; width: 100%; max-width: 200px; height: auto; }

.nay .err-msg { font-family: var(--mono); font-size: 10px; color: #dc2626; background: #fef2f2;
  border: 1px solid #fecaca; border-radius: 6px; padding: 6px 10px; margin-top: 8px; }

/* La tarjeta del PDF: fuera de pantalla, sólo existe para que html2canvas la fotografíe
   (ver nayapp/pdf.py). */
.nay #pdf-confirmation {
  position: absolute; left: -9999px; top: 0; width: 148mm;
  background: #fff; font-family: var(--sans);
}

.nay-rain { position: relative; }
.nay .float-cat { position: fixed; height: 100px; width: auto; pointer-events: none;
  animation-name: rain; animation-timing-function: linear; animation-fill-mode: forwards;
  z-index: 9999; top: -120px; }
@media (max-width: 480px) { .nay .float-cat { height: 70px; } }
"""

CARDS = """
/* Los pasos 1 y 2 tienen widgets dentro de la tarjeta: la tarjeta es un container. */
/* Sólo el markdown propio se centra; la etiqueta de los botones no (el campo de fecha
   lleva su texto a la izquierda y el emoji a la derecha). */
.st-key-nay_card1 [data-testid="stMarkdown"] [data-testid="stMarkdownContainer"],
.st-key-nay_card2 [data-testid="stMarkdown"] [data-testid="stMarkdownContainer"] { text-align: center; }
[data-testid="stVerticalBlock"].st-key-nay_card1,
[data-testid="stVerticalBlock"].st-key-nay_card2 {
  background: var(--card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  padding: 16px;
  margin-bottom: 16px;
  text-align: center;
}
"""

STEP1 = """
.nay .step1-imgs { display: flex; gap: 6px; justify-content: center; flex-wrap: wrap;
  margin-bottom: 12px; }
.nay .step1-imgs img { width: 30%; max-width: 90px; height: auto; border-radius: 12px;
  animation: float 3s ease-in-out infinite; }
.nay .step1-imgs img:nth-child(2) { animation-delay: .5s; }
.nay .step1-imgs img:nth-child(3) { animation-delay: 1s; }
.nay .step1-q { font-size: 18px; font-weight: 800; color: var(--text); line-height: 1.4;
  margin-bottom: 16px; text-align: center; }

/* Fila Sí/No: el container es el marco de referencia del botón que escapa. */
[data-testid="stVerticalBlock"].st-key-nay_yesno {
  position: relative;
  flex-direction: row !important;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 12px !important;
  min-height: 70px;
  padding: 8px 0;
}
.st-key-nay_si .stButton > button {
  font-size: 16px;
  padding: 12px 32px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: #fff;
  border: none;
  font-weight: 400;
  box-shadow: 0 8px 20px rgba(124,58,237,0.24);
  transition: transform .2s ease, box-shadow .2s ease, all .2s ease;
  white-space: nowrap;
}
.st-key-nay_si .stButton > button:hover { transform: translateY(-2px) scale(1.03); color: #fff; }
.st-key-nay_no .stButton > button {
  font-size: 12px;
  padding: 10px 20px;
  border-radius: 999px;
  background: linear-gradient(135deg, #ffd5d5, #ff9292);
  color: #fff;
  border: 2px solid rgba(255,255,255,0.45);
  font-weight: 400;
  box-shadow: 0 8px 16px rgba(75,85,99,0.18);
  transition: transform .2s ease, all .2s ease;
  white-space: nowrap;
}
.st-key-nay_no .stButton > button:hover { color: #fff; }
.nay .nay-no-msg { margin-top: 10px; font-family: var(--mono); font-size: 10px;
  color: var(--accent); text-align: center; }
.nay .nay-card-foot { height: 0; }
"""

STEP2 = """
.nay .step2-imgs { display: flex; gap: 8px; justify-content: center; flex-wrap: wrap;
  margin-bottom: 12px; }
.nay .step2-imgs img:first-child { margin-top: 10px; height: 80px; width: auto;
  border-radius: 12px; animation: pulse 2s ease-in-out infinite; }
.nay .step2-imgs img:last-child { margin-top: -10px; height: 120px; width: 90px;
  border-radius: 12px; animation: pulse 2s ease-in-out infinite; animation-delay: .5s; }
/* El tag de agenda.sync separa 10px; el de las preguntas, 8px. */
.nay .q-tag-agenda { margin-bottom: 10px; }
.nay .step2-q { font-size: 16px; font-weight: 800; color: var(--text); line-height: 1.4;
  margin-top: 8px; margin-bottom: 16px; }
.nay .picker-label { font-family: var(--mono); font-size: 11px; color: var(--text-muted);
  text-align: left; margin-bottom: 6px; }
.st-key-nay_field_date { margin-bottom: 16px; }

[class*="st-key-nay_field_"] .stButton > button > div {
  flex: 1 1 auto; justify-content: flex-start; text-align: left;
}
[class*="st-key-nay_field_"] .stButton > button {
  width: 100%;
  padding: 14px 16px;
  background: var(--bg);
  border: 2px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 15px;
  font-weight: 700;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: none;
  white-space: normal;
}
.st-key-nay_field_date .stButton > button::after { content: "📅"; font-size: 18px; }
.st-key-nay_field_time .stButton > button::after { content: "⏰"; font-size: 18px; }

/* Paneles emergentes de fecha y hora */
[data-testid="stVerticalBlock"].st-key-nay_cal,
[data-testid="stVerticalBlock"].st-key-nay_clock {
  margin-top: 16px;
  background: var(--card);
  border-radius: var(--radius);
  box-shadow: var(--shadow-lg);
}
[data-testid="stVerticalBlock"].st-key-nay_cal { border: 2px solid var(--primary); padding: 16px; }
[data-testid="stVerticalBlock"].st-key-nay_clock { border: 2px solid var(--accent); padding: 20px; }

[data-testid="stVerticalBlock"].st-key-nay_cal_head {
  flex-direction: row !important;
  justify-content: space-between;
  align-items: center;
}
.st-key-nay_cal_head [data-testid="stElementContainer"] { width: auto; flex: 0 0 auto; }
.st-key-nay_cal_head [data-testid="stMarkdown"] { flex: 1; }
[class*="st-key-nay_calnav_"] .stButton > button {
  width: 36px; height: 36px; min-height: 36px; padding: 0; border-radius: 50%;
  background: var(--primary-light); border: none; font-size: 16px; color: var(--text);
  display: flex; align-items: center; justify-content: center;
}

.nay .nay-cal-month { font-weight: 800; font-size: 14px; color: var(--primary-dark);
  text-align: center; }
.st-key-nay_cal_head { margin-bottom: 12px; }
.nay .nay-cal-week { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px;
  margin-bottom: 8px; }
.nay .nay-cal-week div { text-align: center; font-size: 10px; font-weight: 700;
  color: var(--text-muted); padding: 4px 0; }
/* Las filas del calendario separan 4px; el -4px del contenedor descuenta la última. */
.st-key-nay_cal_grid { margin-bottom: -4px; }
.st-key-nay_cal_grid [data-testid="stHorizontalBlock"] { gap: 4px !important; margin-bottom: 4px; }
.st-key-nay_cal_grid [data-testid="stColumn"] { min-width: 0 !important; }
[class*="st-key-nay_day_"] { display: flex; justify-content: center; }
[class*="st-key-nay_day_"] .stButton > button {
  width: 32px; height: 32px; min-height: 32px; padding: 0; border-radius: 50%;
  border: none; background: transparent; color: var(--text);
  font-size: 12px; font-weight: 600; display: flex; align-items: center; justify-content: center;
}
[class*="st-key-nay_day_"] .stButton > button:hover { background: var(--primary-light);
  color: var(--primary-dark); }
[class*="st-key-nay_day_"] .stButton > button:disabled {
  background: var(--bg); color: var(--text-muted); opacity: .4; cursor: not-allowed; border: none;
}
.nay .nay-day-empty { height: 32px; }
.st-key-nay_cal_done, .st-key-nay_time_done { margin-top: 12px; }
.st-key-nay_cal_done .stButton > button, .st-key-nay_time_done .stButton > button {
  width: 100%; padding: 10px; background: var(--primary); color: #fff; border: none;
  border-radius: var(--radius-sm); font-weight: 700; font-size: 13px;
}
.st-key-nay_time_done .stButton > button { background: var(--accent); }

[data-testid="stVerticalBlock"].st-key-nay_clock_row {
  flex-direction: row !important;
  justify-content: center;
  align-items: center;
  gap: 8px !important;
}
.st-key-nay_clock_row [data-testid="stElementContainer"] { width: auto; flex: 0 0 auto; }
[class*="st-key-nay_clocknav_"] .stButton > button {
  width: 40px; height: 40px; min-height: 40px; padding: 0; border-radius: 50%;
  background: var(--accent-light); border: none; font-size: 18px; color: var(--text);
  display: flex; align-items: center; justify-content: center;
}

.nay .nay-clock-face { display: flex; align-items: baseline; gap: 4px; justify-content: center; }
.nay .nay-clock-face .hh, .nay .nay-clock-face .mm { font-size: 36px; font-weight: 900;
  color: var(--primary-dark); }
.nay .nay-clock-face .sep { font-size: 24px; color: var(--accent); }
.st-key-nay_clock_row { margin-bottom: 16px; }
.st-key-nay_minutes { margin-bottom: 16px; }
.st-key-nay_minutes [data-testid="stHorizontalBlock"] { gap: 8px !important; }
[class*="st-key-nay_min_"] .stButton > button {
  width: 100%; padding: 8px; border-radius: var(--radius-sm); border: 2px solid var(--border);
  background: transparent; color: var(--text); font-weight: 700; font-size: 13px;
}
"""

OPTIONS = """
.st-key-nay_options { margin-top: 0; }
[class*="st-key-nay_opt_"] { margin-bottom: 8px; }
[class*="st-key-nay_opt_"] .stButton > button {
  width: 100%;
  background: var(--bg);
  border: 2px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  font-family: var(--sans);
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 8px;
  text-align: left;
  line-height: 1.3;
  white-space: normal;
  word-break: break-word;
  box-shadow: none;
}
[class*="st-key-nay_opt_"] .stButton > button:hover { border-color: var(--primary); }
[class*="st-key-nay_opt_"] .stButton > button::before {
  width: 22px; height: 22px; background: var(--border); border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--mono); font-size: 10px; font-weight: 600; color: var(--text);
  flex-shrink: 0;
}
[class*="st-key-nay_opt_"] .stButton > button > div {
  flex: 1; text-align: left; min-width: 0; display: block;
}
"""

SUMMARY = """
.nay .summary-header { text-align: center; margin-bottom: 16px; }
.nay .summary-header img { margin: 0 auto 10px; width: 120px; height: 120px; object-fit: contain;
  animation: pulse 2s ease-in-out infinite; }
.nay .summary-title { font-size: 20px; font-weight: 900;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.nay .summary-note { font-family: var(--mono); font-size: 10px; color: var(--text-muted);
  margin-top: 4px; }
.nay .summary-table { background: var(--card); border-radius: var(--radius);
  box-shadow: var(--shadow); overflow: hidden; border: 1px solid var(--border);
  margin-bottom: 12px; font-size: 11px; }
.nay .summary-row { display: flex; align-items: center; padding: 10px 12px; gap: 8px;
  border-bottom: 1px solid var(--border); }
.nay .summary-row.alt { background: var(--bg); }
.nay .summary-row:last-child { border-bottom: none; }
.nay .s-icon { font-size: 16px; flex-shrink: 0; width: 24px; text-align: center; }
.nay .s-label { font-family: var(--mono); font-size: 9px; color: var(--text-muted); flex-shrink: 0; }
.nay .s-value { font-weight: 700; font-size: 11px; color: var(--text); flex: 1;
  word-break: break-word; }

.nay .final-card { border: 2px solid var(--accent); text-align: center; padding: 16px;
  border-radius: var(--radius); background: var(--card); box-shadow: var(--shadow); }
.nay .final-card img { margin: 0 auto 8px; width: 80px; height: 80px; object-fit: contain; }
.nay .final-card .q-text { font-size: 18px; line-height: 1.4; margin: 0; }
.nay .final-note { font-family: var(--mono); font-size: 9px; color: var(--text-muted);
  margin-top: 6px; }

.st-key-nay_celebrate { margin-top: 12px; }
.st-key-nay_celebrate .stButton > button {
  width: 100%; background: linear-gradient(135deg, var(--accent), #db2777); color: #fff;
  border: none; border-radius: var(--radius-sm); padding: 14px 20px; font-size: 13px;
  font-weight: 800; letter-spacing: .5px; box-shadow: 0 4px 12px rgba(236,72,153,0.3);
  white-space: normal;
}
.st-key-nay_celebrate .stButton > button:hover { transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(236,72,153,0.4); color: #fff; }

.nay .finale { text-align: center; padding: 16px; background: var(--green-light);
  border: 2px solid rgba(16,185,129,0.3); border-radius: var(--radius);
  animation: pop .5s cubic-bezier(.34,1.56,.64,1); margin-top: 12px; }
.nay .finale-imgs { display: flex; justify-content: center; align-items: center; gap: 8px;
  margin-bottom: 10px; }
.nay .finale-imgs img { object-fit: contain; }
.nay .finale-imgs img:nth-child(odd) { width: 50px; height: 50px; }
.nay .finale-imgs img:nth-child(2) { width: 80px; height: 80px; }
.nay .finale-title { font-size: 18px; font-weight: 900; color: var(--green); margin-bottom: 6px; }
.nay .finale-note { font-family: var(--mono); font-size: 10px; color: #065f46; line-height: 1.5; }
"""


def _letters_css() -> str:
    """Badge A/B/C/D/… de cada opción (el original lo dibuja con un <span>)."""
    return "\n".join(
        f'.st-key-nay_opt_{question["id"]}_{index} .stButton > button::before'
        f' {{ content: "{chr(65 + index)}"; }}'
        for question in content.QUESTIONS
        for index in range(len(question["options"]))
    )


def _options_last_css() -> str:
    """Sin margen inferior en la última opción de cada pregunta."""
    selectors = ",\n".join(
        f'.st-key-nay_opt_{question["id"]}_{len(question["options"]) - 1}'
        for question in content.QUESTIONS
    )
    return f"{selectors} {{ margin-bottom: 0; }}"


BASE_CSS = "\n".join(
    [
        TOKENS, KEYFRAMES, SHELL, BUTTON_BASE, BLOCKS, CARDS,
        STEP1, STEP2, OPTIONS, SUMMARY, _letters_css(), _options_last_css(),
    ]
)


def selected_option_css(question_id: int, index: int) -> str:
    """Estado `.selected` de una opción: borde y badge en primary."""
    key = f".st-key-nay_opt_{question_id}_{index} .stButton > button"
    return (
        f"{key} {{ border-color: var(--primary) !important; color: var(--primary-dark) !important;"
        f" box-shadow: 0 0 0 2px rgba(124,58,237,0.15) !important; }}"
        f"{key}::before {{ background: var(--primary) !important; color: #fff !important; }}"
    )


def filled_field_css(field: str) -> str:
    """Campo de fecha/hora ya elegido."""
    key = f".st-key-nay_field_{field} .stButton > button"
    return (
        f"{key} {{ background: linear-gradient(135deg, var(--primary-light), #fff) !important;"
        f" border-color: var(--primary) !important; color: var(--primary-dark) !important;"
        f" box-shadow: 0 0 0 3px rgba(124,58,237,0.1) !important; }}"
    )


def selected_day_css(day: int) -> str:
    key = f".st-key-nay_day_{day} .stButton > button"
    return (
        f"{key} {{ background: var(--primary) !important; color: #fff !important;"
        f" font-weight: 800 !important; }}"
    )


def selected_minute_css(minute: int) -> str:
    key = f".st-key-nay_min_{minute} .stButton > button"
    return (
        f"{key} {{ border-color: var(--accent) !important;"
        f" background: var(--accent-light) !important; color: var(--accent) !important; }}"
    )


def escaping_no_css(attempts: int, left: float, top: float) -> str:
    """Réplica de `escapeNo()`: el "No" se encoge y salta, el "Sí" crece.

    `left` es una fracción (0..1): el desplazamiento se resuelve con `calc()` sobre el
    ancho de la tarjeta, reservando 84px para el ancho del botón, así el "No" nunca se
    sale de pantalla (clave en mobile) y sigue esquivando en cualquier ancho.
    """
    if attempts <= 0:
        return ""
    size = max(14 - attempts, 8)
    pad_y = max(12 - attempts * 2, 4)
    pad_x = max(24 - attempts * 3, 8)
    yes_size = min(18 + attempts * 4, 42)
    # El original topea el padding vertical en 32px pero calcula el horizontal a partir
    # del valor sin topear (llega a 60px en el último intento): se replica tal cual.
    yes_pad = min(16 + attempts * 4, 32)
    yes_pad_x = min(16 + attempts * 4 + 24, 64)
    return (
        f".st-key-nay_no {{ position: absolute !important;"
        f" left: calc((100% - 84px) * {left:.3f}) !important;"
        f" top: {top:.0f}px !important; z-index: 3; }}"
        f".st-key-nay_no .stButton > button {{ font-size: {size}px !important;"
        f" padding: {pad_y}px {pad_x}px !important; }}"
        f".st-key-nay_si .stButton > button {{ font-size: {yes_size}px !important;"
        f" padding: {yes_pad}px {yes_pad_x}px !important; }}"
    )


def inject(extra: str = "") -> None:
    st.markdown(f"<style>{BASE_CSS}\n{extra}</style>", unsafe_allow_html=True)
