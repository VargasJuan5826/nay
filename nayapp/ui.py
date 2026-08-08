"""Bloques HTML que replican el markup del original.

Deliberadamente sólo se usan `div`, `span`, `img` y `br`: Streamlit aplica sus propios
estilos a `h1`/`p`/`small` dentro del markdown, y usar elementos neutros evita esa pelea
de especificidad.
"""

from __future__ import annotations

from datetime import date

from . import assets, content


def html(markup: str) -> str:
    """Compacta el markup para que Streamlit no lo interprete como bloque markdown."""
    return "".join(line.strip() for line in markup.strip().splitlines())


def header() -> str:
    return html(
        f"""
        <div class="nay nay-header">
          <img src="{assets.url('gatito1.png')}" alt="gatito1">
          <div class="nay-title">{content.TITLE}</div>
          <div class="nay-sub">{content.SUBTITLE}</div>
        </div>
        """
    )


def plea_card() -> str:
    return html(
        f"""
        <div class="nay nay-step">
          <div class="plea-card">
            <img src="{assets.url('gatito2.png')}" alt="Emoji gato">
            <div class="plea-text">
              Antes de responder... ¡responde esto primero! 🥺
              <span class="plea-note">/* se requiere una respuesta para continuar */</span>
            </div>
          </div>
        </div>
        """
    )


def step1_intro() -> str:
    images = "".join(
        f'<img src="{assets.url(src)}" alt="Imagen {index + 1}">'
        for index, src in enumerate(content.CAT_IMAGES_STEP1)
    )
    return html(
        f"""
        <div class="nay">
          <div class="step1-imgs">{images}</div>
          <div class="step1-q">¿Quieres tener una salida conmigo? 🥺💕</div>
        </div>
        """
    )


def no_message(attempts: int) -> str:
    text = (
        '// el "No" ya no existe en el sistema 😼💜'
        if attempts >= 5
        else "// error: opción no válida 😼"
    )
    return html(f'<div class="nay"><div class="nay-no-msg">{text}</div></div>')


def card_foot() -> str:
    return html('<div class="nay"><div class="nay-card-foot"></div></div>')


def step2_intro() -> str:
    first, second = content.CAT_IMAGES_STEP2
    return html(
        f"""
        <div class="nay">
          <div class="step2-imgs">
            <img src="{assets.url(first)}" alt="Corgi">
            <img src="{assets.url(second)}" alt="Gatito emocionado">
          </div>
          <span class="q-tag q-tag-agenda">// módulo: agenda.sync</span>
          <div class="step2-q">¿Cuándo estás disponible? 📅</div>
        </div>
        """
    )


def picker_label(text: str) -> str:
    return html(f'<div class="nay"><div class="picker-label">{text}</div></div>')


def month_label(value: date) -> str:
    name = content.MONTH_NAMES[value.month - 1]
    return html(f'<div class="nay"><div class="nay-cal-month">{name} de {value.year}</div></div>')


def weekdays() -> str:
    cells = "".join(f"<div>{day}</div>" for day in content.DAY_NAMES)
    return html(f'<div class="nay"><div class="nay-cal-week">{cells}</div></div>')


def clock_face(hour: int, minute: int) -> str:
    return html(
        f"""
        <div class="nay">
          <div class="nay-clock-face">
            <span class="hh">{hour:02d}</span>
            <span class="sep">:</span>
            <span class="mm">{minute:02d}</span>
          </div>
        </div>
        """
    )


def empty_day() -> str:
    return html('<div class="nay"><div class="nay-day-empty"></div></div>')


def progress(index: int) -> str:
    total = len(content.QUESTIONS)
    percent = round((index + 1) / total * 100)
    return html(
        f"""
        <div class="nay">
          <div class="nay-progress-label">pregunta {index + 1} / {total}</div>
          <div class="nay-progress-wrap">
            <div class="nay-progress-fill" style="width: {percent}%"></div>
          </div>
        </div>
        """
    )


def question_card(question: dict) -> str:
    image = content.QUESTION_HEADER_IMAGES.get(question["id"], content.CAT_HEADER_IMG)
    return html(
        f"""
        <div class="nay nay-step">
          <div class="nay-qhead"><img src="{assets.url(image)}" alt="Decoración"></div>
          <div class="q-card">
            <span class="q-tag">{question['tag']}</span>
            <div class="q-text">{question['text']}</div>
          </div>
        </div>
        """
    )


def error(text: str) -> str:
    return html(f'<div class="nay"><div class="err-msg">{text}</div></div>')


def summary(answers: dict) -> str:
    rows = []
    for position, (icon, label, key) in enumerate(content.SUMMARY_ROWS):
        value = answers.get(key) or "—"
        alt = " alt" if position % 2 == 1 else ""
        rows.append(
            f'<div class="summary-row{alt}"><span class="s-icon">{icon}</span>'
            f'<span class="s-label">{label}</span>'
            f'<span class="s-value">{value}</span></div>'
        )
    return html(
        f"""
        <div class="nay nay-step">
          <div class="summary-header">
            <img src="{assets.url(content.CAT_HEADER_IMG)}" alt="Gato grande">
            <div class="summary-title">Resumen de compatibilidad</div>
            <div class="summary-note">// análisis completado · match_score: calculando... 💜</div>
          </div>
          <div class="summary-table">{''.join(rows)}</div>
          <div class="final-card">
            <img src="{assets.url('gatito0.png')}" alt="Pregunta final">
            <div class="q-text">Entonces... ¿saldrías conmigo?</div>
            <div class="final-note">// advertencia: respuesta_incorrecta no existe</div>
          </div>
        </div>
        """
    )


def finale() -> str:
    return html(
        f"""
        <div class="nay">
          <div class="finale">
            <div class="finale-imgs">
              <img src="{assets.url('gatito0.png')}" alt="gatito0">
              <img src="{assets.url('gatito1.png')}" alt="gatito1">
              <img src="{assets.url('gatito0.png')}" alt="gatito0">
            </div>
            <div class="finale-title">¡Match confirmado!</div>
            <div class="finale-note">// status: ÉXITO<br>// salida.exe iniciada<br>// Mandame el pdf xq sino no me entero 🥺</div>
          </div>
        </div>
        """
    )


def cat_rain(cats: list[dict]) -> str:
    images = "".join(
        f'<img class="float-cat" src="{assets.url(content.FLOAT_CAT_SRCS[cat["pick"]])}"'
        f' style="left: {cat["left"]:.1f}%; animation-duration: {cat["duration"]:.2f}s;'
        f' animation-delay: {cat["delay"]:.2f}s" alt="">'
        for cat in cats
    )
    return html(f'<div class="nay nay-rain">{images}</div>')
