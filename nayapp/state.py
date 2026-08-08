"""Estado de la sesión — equivalente 1:1 a los `useState` del componente original."""

from __future__ import annotations

import random
import time
from datetime import date

import streamlit as st

from . import content

# Ventana de gracia tras entrar al paso Sí/No: los escapes del "No" que lleguen antes se
# ignoran. Un tap/click real nunca ocurre tan rápido; sí un evento espurio del navegador
# (el "ghost click" de mobile, un replay al recargar, etc.), que hacía que el "No" se
# achicara solo apenas aparecía la pantalla. Es una guarda de servidor: no depende del
# navegador ni de la latencia de red.
ESCAPE_GRACE_SECONDS = 0.7

# Pasos que muestran una pregunta con opciones (hoy: 2 = el plan, 3 = gastronómico,
# 4 = outfit, 5 = logística).
QUESTION_STEPS = {question["id"] for question in content.QUESTIONS}
# Paso donde vive el calendario/reloj y paso del resumen final (después de las preguntas).
AGENDA_STEP = 6
SUMMARY_STEP = 7
# El calendario se habilita a partir del viernes 21 de agosto de 2026.
MIN_DATE = date(2026, 8, 21)


def _calendar_floor() -> date:
    """Primer día seleccionable: nunca antes del viernes 21 ni antes de hoy."""
    return max(date.today(), MIN_DATE)

DEFAULTS = {
    "step": 0,              # currentStep
    "answers": {},          # answers
    "no_attempts": 0,       # noAttempts
    "show_no_msg": False,   # showNoMsg
    "pick_error": {},       # pickError
    "show_finale": False,   # showFinale
    "no_pos": None,         # selectedPosition
    "selected_date": None,  # selectedDate
    "selected_time": "",    # selectedTime
    "picker": None,         # showPicker: 'date' | 'time' | None
    "temp_date": None,      # tempDate
    "temp_hour": 20,        # tempHour
    "temp_minute": 0,       # tempMinute
    "cats": [],             # gatitos de la lluvia final
    "step1_at": 0.0,        # momento en que se entró al paso Sí/No (guarda anti-espurio)
}


def init() -> None:
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value.copy() if isinstance(value, (dict, list)) else value
    if st.session_state.temp_date is None:
        st.session_state.temp_date = _calendar_floor()


def reset() -> None:
    for key in DEFAULTS:
        st.session_state.pop(key, None)
    init()


# --- Transiciones ------------------------------------------------------------
def reset_escape() -> None:
    """Deja el paso Sí/No como recién estrenado: el "No" grande, sin intentos previos.

    Se llama al entrar al paso, así cualquier estado de escape que hubiera quedado (por
    una sesión reusada, un back/forward o un rerun del navegador) no deja el "No"
    achicado/escapado al volver a entrar. Además marca el momento de entrada para la
    guarda anti-espurio de `escape_no`."""
    st.session_state.no_attempts = 0
    st.session_state.no_pos = None
    st.session_state.show_no_msg = False
    st.session_state.step1_at = time.time()


def go(from_step: int, to_step: int) -> None:
    """`go()` del original: valida que la pregunta esté respondida antes de avanzar."""
    if from_step in QUESTION_STEPS and not st.session_state.answers.get(from_step):
        st.session_state.pick_error[from_step] = True
        return
    st.session_state.pick_error[from_step] = False
    if to_step == 1:
        reset_escape()
    st.session_state.step = to_step


def pick(step: int, value: str) -> None:
    st.session_state.answers[step] = value
    st.session_state.pick_error[step] = False


def say_yes() -> None:
    st.session_state.answers[1] = "¡Sí! 💜"
    go(1, 2)


def escape_no() -> None:
    """`escapeNo()`: el "No" salta a una posición aleatoria y se encoge.

    El desplazamiento horizontal se guarda como fracción (0..1) del ancho disponible en
    lugar de un valor fijo en px: así el "No" salta dentro de la tarjeta en cualquier
    pantalla (desktop o mobile) sin empujar el layout ni generar scroll horizontal.
    """
    # Guarda anti-espurio: si el escape llega apenas se entró al paso, es un evento
    # fantasma del navegador (no un tap real) y se ignora, así el "No" no se achica solo.
    if time.time() - st.session_state.get("step1_at", 0.0) < ESCAPE_GRACE_SECONDS:
        return
    st.session_state.no_attempts = min(st.session_state.no_attempts + 1, 5)
    st.session_state.show_no_msg = True
    st.session_state.no_pos = (
        random.random(),
        random.random() * 100 - 20,
    )


def confirm_date() -> None:
    """`pickDate()`: exige fecha y hora, y arma el string del resumen."""
    selected_date = st.session_state.selected_date
    selected_time = st.session_state.selected_time
    if not selected_date or not selected_time:
        st.session_state.pick_error[AGENDA_STEP] = True
        return
    st.session_state.pick_error[AGENDA_STEP] = False
    st.session_state.answers[AGENDA_STEP] = (
        f"{selected_date.day:02d}/{selected_date.month:02d}/{selected_date.year}"
        f" a las {selected_time}"
    )
    st.session_state.step = SUMMARY_STEP


def open_picker(which: str) -> None:
    st.session_state.picker = which
    if which == "date":
        st.session_state.temp_date = st.session_state.selected_date or _calendar_floor()


def close_picker() -> None:
    st.session_state.picker = None


def shift_month(delta: int) -> None:
    current = st.session_state.temp_date
    month = current.month + delta
    year = current.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    st.session_state.temp_date = date(year, month, 1)


def choose_day(day: int) -> None:
    current = st.session_state.temp_date
    st.session_state.selected_date = date(current.year, current.month, day)
    st.session_state.picker = None


def shift_hour(delta: int) -> None:
    st.session_state.temp_hour = (st.session_state.temp_hour + delta) % 24


def set_minute(minute: int) -> None:
    st.session_state.temp_minute = minute


def confirm_time() -> None:
    st.session_state.selected_time = (
        f"{st.session_state.temp_hour:02d}:{st.session_state.temp_minute:02d}"
    )
    st.session_state.picker = None


def celebrate() -> None:
    """`celebrate()` + `spawnCats()`: 16 gatitos con posición y ritmo aleatorios."""
    st.session_state.show_finale = True
    st.session_state.cats = [
        {
            "index": index,
            "left": random.random() * 95,
            "duration": 3 + random.random() * 4,
            "delay": index * 0.2,
            "pick": random.randrange(5),
        }
        for index in range(16)
    ]
