"""
Punto de entrada principal para la aplicación Pocket.
Maneja la sesión de usuario y la navegación entre módulos.
"""

import streamlit as st
from src.ui import auth_ui, gastos_ui, graficos_ui, presupuestos_ui

st.set_page_config(page_title="Pocket", page_icon="💰")
st.title("💰 Pocket")

usuario = auth_ui.usuario_actual()

if usuario is None:
    st.write("Controla tus gastos personales. Inicia sesión o crea tu cuenta.")
    auth_ui.mostrar_autenticacion()
else:
    auth_ui.mostrar_barra_usuario()
    st.success(f"Bienvenida/o, {usuario['nombre']}.")
    
    # Menú lateral para cambiar entre Gastos y Presupuestos
    opcion = st.sidebar.radio("Navegación", ["Gastos", "Presupuestos"])
    
    if opcion == "Gastos":
        gastos_ui.mostrar_formulario_gasto(usuario["id"])
        gastos_ui.mostrar_lista_gastos(usuario["id"])
        graficos_ui.mostrar_grafico(usuario["id"])
    elif opcion == "Presupuestos":
        presupuestos_ui.mostrar_seccion_presupuestos(usuario["id"])