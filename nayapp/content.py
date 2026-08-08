"""Textos, preguntas y assets de la salida."""

QUESTIONS = [
    {
        "id": 2,
        "tag": "// módulo: el_plan.config",
        "text": "📍 ¿Qué plan te tienta para la salida?",
        "options": [
            "🚶 Paseo",
            "🍸 Bar",
            "🍝 Cena",
            "☕ Cafetería",
            "🎸 Escuchar una banda en vivo",
        ],
    },
    {
        "id": 3,
        "tag": "// módulo: stack_gastronomico.dat",
        "text": "🍽 Elegí el stack gastronómico",
        "options": [
            "🍺 Un trago o una cerveza",
            "🧉 Un mate",
            "🥐 Una merienda",
            "🍣 Sushi",
            "🍔 La buena hamburguesa",
        ],
    },
    {
        "id": 4,
        "tag": "// módulo: dress_code.cfg",
        "text": "🧥 ¿Con qué outfit vas?",
        "options": [
            "👕 Casual",
            "👔 Classic",
            "✨ Elegante",
        ],
    },
    {
        "id": 5,
        "tag": "// módulo: logistica.sh",
        "text": "🛵 Logística — ¿cómo llegás a la salida?",
        "options": [
            "🏍️ Te paso a buscar",
            "🚗 Te invito un Uber",
            "🚶 Te hacés la fit y vas caminando (no recomendado)",
        ],
    },
]

QUESTION_HEADER_IMAGES = {
    2: "gatito4.png",
    3: "gatito5.png",
    4: "gatito6.png",
    5: "gatito3.png",
}

CAT_HEADER_IMG = "gatito7.png"
CAT_IMAGES_STEP1 = ["1.png", "2.png", "5.png"]
CAT_IMAGES_STEP2 = ["3.jpg", "4.png"]
FLOAT_CAT_SRCS = ["1.png", "2.png", "3.jpg", "4.png", "5.png"]

# Filas del resumen: (icono, etiqueta, clave de respuesta)
SUMMARY_ROWS = [
    ("📍", "plan://", 2),
    ("🍽", "gastronómico://", 3),
    ("🧥", "outfit://", 4),
    ("🛵", "logística://", 5),
    ("📅", "salida://", 6),
]

# Ícono del botón "Sí": arranca en el corazón y va rotando a medida que el "No" se
# achica (un ícono por intento, de 0 a 5), terminando en una risa cuando el "No" ya no
# existe. Indexado por `no_attempts`.
SI_ICONS = ["💜", "😸", "😼", "😏", "😎", "😂"]

TITLE = "¿Saldrías conmigo?"
SUBTITLE = "// ejecutando: peticion_random_v2.0.cat"

# Música de fondo: id del video de YouTube (arranca en el primer click, en loop).
MUSIC_VIDEO_ID = "YlU6N0fxr0o"
DAY_NAMES = ["D", "L", "M", "X", "J", "V", "S"]
MONTH_NAMES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]
