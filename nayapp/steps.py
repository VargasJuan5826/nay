"""Los pasos del flujo de la salida.

0 intro · 1 confirmación (Sí/No) · 2 el plan · 3 gastronómico · 4 outfit · 5 logística ·
6 agenda · 7 resumen + final
"""

from __future__ import annotations

import calendar
from datetime import date

import streamlit as st

from . import content, enhance, pdf, state, theme, ui


def _md(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


# --- CSS dependiente del estado ---------------------------------------------
def dynamic_css() -> str:
    """Los estados visuales (opción elegida, día elegido, "No" escapando) se pintan
    generando CSS por rerun en vez de mutar el DOM."""
    rules = []
    answers = st.session_state.answers

    for question in content.QUESTIONS:
        chosen = answers.get(question["id"])
        if chosen in question["options"]:
            rules.append(
                theme.selected_option_css(question["id"], question["options"].index(chosen))
            )

    if st.session_state.selected_date:
        rules.append(theme.filled_field_css("date"))
        showing = st.session_state.temp_date
        chosen = st.session_state.selected_date
        if (chosen.year, chosen.month) == (showing.year, showing.month):
            rules.append(theme.selected_day_css(chosen.day))
    if st.session_state.selected_time:
        rules.append(theme.filled_field_css("time"))

    rules.append(theme.selected_minute_css(st.session_state.temp_minute))

    if st.session_state.no_attempts and st.session_state.no_pos:
        left, top = st.session_state.no_pos
        rules.append(theme.escaping_no_css(st.session_state.no_attempts, left, top))

    return "\n".join(rules)


# --- Paso 0 ------------------------------------------------------------------
def step_intro() -> None:
    _md(ui.plea_card())
    st.button(
        "[ INICIAR PROTOCOLO → ]",
        key="nay_start",
        on_click=state.go,
        args=(0, 1),
        width="stretch",
    )


# --- Paso 1 ------------------------------------------------------------------
def step_confirm() -> None:
    attempts = st.session_state.no_attempts
    si_icon = content.SI_ICONS[min(attempts, len(content.SI_ICONS) - 1)]
    with st.container(key="nay_card1"):
        _md(ui.step1_intro())
        with st.container(key="nay_yesno"):
            st.button(f"Sí {si_icon}", key="nay_si", on_click=state.say_yes)
            if attempts < 5:
                st.button("No", key="nay_no", on_click=state.escape_no)
        if st.session_state.show_no_msg:
            _md(ui.no_message(attempts))
        else:
            _md(ui.card_foot())
    if attempts < 5:
        enhance.hover_to_click(f"a{attempts}")


# --- Paso 2 ------------------------------------------------------------------
def _calendar_panel() -> None:
    showing = st.session_state.temp_date
    with st.container(key="nay_cal"):
        # Fila con los extremos separados: el CSS la vuelve horizontal, igual que el
        # `justify-content: space-between` del original.
        with st.container(key="nay_cal_head"):
            st.button("←", key="nay_calnav_prev", on_click=state.shift_month, args=(-1,))
            _md(ui.month_label(showing))
            st.button("→", key="nay_calnav_next", on_click=state.shift_month, args=(1,))

        _md(ui.weekdays())

        first_weekday = (date(showing.year, showing.month, 1).weekday() + 1) % 7
        days_in_month = calendar.monthrange(showing.year, showing.month)[1]
        cells = [None] * first_weekday + list(range(1, days_in_month + 1))
        floor = state._calendar_floor()

        with st.container(key="nay_cal_grid"):
            for offset in range(0, len(cells), 7):
                week = cells[offset:offset + 7]
                week += [None] * (7 - len(week))
                columns = st.columns(7, gap=None)
                for column, day in zip(columns, week):
                    with column:
                        if day is None:
                            _md(ui.empty_day())
                            continue
                        st.button(
                            str(day),
                            key=f"nay_day_{day}",
                            on_click=state.choose_day,
                            args=(day,),
                            disabled=date(showing.year, showing.month, day) < floor,
                        )

        st.button("Listo ✓", key="nay_cal_done", on_click=state.close_picker, width="stretch")


def _clock_panel() -> None:
    with st.container(key="nay_clock"):
        # Los tres controles van agrupados y centrados con 8px de separación.
        with st.container(key="nay_clock_row"):
            st.button("-", key="nay_clocknav_minus", on_click=state.shift_hour, args=(-1,))
            _md(ui.clock_face(st.session_state.temp_hour, st.session_state.temp_minute))
            st.button("+", key="nay_clocknav_plus", on_click=state.shift_hour, args=(1,))

        with st.container(key="nay_minutes"):
            for column, minute in zip(st.columns(4, gap=None), (0, 15, 30, 45)):
                with column:
                    st.button(
                        f":{minute:02d}",
                        key=f"nay_min_{minute}",
                        on_click=state.set_minute,
                        args=(minute,),
                        width="stretch",
                    )

        st.button("Listo ✓", key="nay_time_done", on_click=state.confirm_time, width="stretch")


def step_agenda() -> None:
    selected_date = st.session_state.selected_date
    selected_time = st.session_state.selected_time

    with st.container(key="nay_card2"):
        _md(ui.step2_intro())

        _md(ui.picker_label("Fecha:"))
        st.button(
            f"{selected_date.day:02d}/{selected_date.month:02d}/{selected_date.year}"
            if selected_date else "Selecciona una fecha",
            key="nay_field_date",
            on_click=state.open_picker,
            args=("date",),
            width="stretch",
        )

        _md(ui.picker_label("Hora:"))
        st.button(
            selected_time or "Selecciona una hora",
            key="nay_field_time",
            on_click=state.open_picker,
            args=("time",),
            width="stretch",
        )

        if st.session_state.picker == "date":
            _calendar_panel()
        elif st.session_state.picker == "time":
            _clock_panel()

        if st.session_state.pick_error.get(state.AGENDA_STEP):
            _md(ui.error("// error: selecciona fecha y hora para continuar 🗓️"))

        st.button(
            "[ CONFIRMAR FECHA → ]",
            key="nay_confirm_date",
            on_click=state.confirm_date,
            width="stretch",
        )


# --- Pasos 3 a 6 -------------------------------------------------------------
def step_question(step: int) -> None:
    index, question = next(
        (position, item)
        for position, item in enumerate(content.QUESTIONS)
        if item["id"] == step
    )
    _md(ui.progress(index))
    _md(ui.question_card(question))

    with st.container(key="nay_options"):
        for option_index, option in enumerate(question["options"]):
            st.button(
                option,
                key=f"nay_opt_{step}_{option_index}",
                on_click=state.pick,
                args=(step, option),
                width="stretch",
            )

    if st.session_state.pick_error.get(step):
        _md(ui.error("⚠ ¡Elige algo porfa! el algoritmo espera 🙏"))

    st.button(
        "[ SIGUIENTE PARÁMETRO → ]",
        key=f"nay_next_{step}",
        on_click=state.go,
        args=(step, step + 1),
        width="stretch",
    )


# --- Paso 7 ------------------------------------------------------------------
def step_summary() -> None:
    _md(ui.summary(st.session_state.answers))

    if not st.session_state.show_finale:
        st.button(
            "✨ [ SÍ, ACEPTO LOS TÉRMINOS Y CONDICIONES ] ✨",
            key="nay_celebrate",
            on_click=state.celebrate,
            width="stretch",
        )
    else:
        _md(ui.finale())
        _md(pdf.card(st.session_state.answers))
        pdf.download_button()
        _md(ui.cat_rain(st.session_state.cats))


# Flujo: 0 intro · 1 confirmación (Sí/No) · 2-5 preguntas · 6 agenda · 7 resumen + final
ROUTES = {
    0: step_intro,
    1: step_confirm,
    6: step_agenda,
    7: step_summary,
}


def render() -> None:
    step = st.session_state.step
    if step in state.QUESTION_STEPS:
        step_question(step)
        return
    ROUTES.get(step, step_intro)()
