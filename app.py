"""nay — ¿Saldrías conmigo? 🐱

Una salida con onda nerd y gatitos, en Streamlit: confirmás, elegís el plan y el stack
gastronómico, agendás fecha y hora, y cierra con el match y un PDF de confirmación.
"""

import streamlit as st

from nayapp import content, music, state, steps, theme, ui

st.set_page_config(
    page_title="¿Saldrías conmigo? 🐱",
    page_icon="🐱",
    layout="centered",
    initial_sidebar_state="collapsed",
)

state.init()
theme.inject(steps.dynamic_css())
st.markdown(ui.header(), unsafe_allow_html=True)
steps.render()

# Música de fondo (arranca en el primer click, sobrevive a los pasos). Va al final para no
# afectar el layout; el player real se inyecta en el documento padre.
music.background(content.MUSIC_VIDEO_ID)
