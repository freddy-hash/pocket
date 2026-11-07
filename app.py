import streamlit as st

from src.ui import auth_ui

st.set_page_config(page_title="Pocket", page_icon="💰")

st.title("💰 Pocket")

usuario = auth_ui.usuario_actual()

if usuario is None:
    st.write("Controla tus gastos personales. Inicia sesión o crea tu cuenta.")
    auth_ui.mostrar_autenticacion()
else:
    auth_ui.mostrar_barra_usuario()
    st.success(f"Bienvenida/o, {usuario['nombre']}.")
    st.info("Aquí irán el registro de gastos y los gráficos.")