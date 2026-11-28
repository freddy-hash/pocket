import streamlit as st
from src.ui import auth_ui, estilos, gastos_ui, graficos_ui, presupuestos_ui, metas_ui, reportes_ui

st.set_page_config(page_title="Pocket", page_icon="💰")
estilos.aplicar_estilos()
st.title("💰 Pocket")

usuario = auth_ui.usuario_actual()

if usuario is None:
    st.write("Controla tus gastos personales. Inicia sesión o crea tu cuenta.")
    auth_ui.mostrar_autenticacion()
else:
    auth_ui.mostrar_barra_usuario()
    st.success(f"Bienvenida/o, {usuario['nombre']}.")
    
    # Menú lateral para cambiar entre módulos
    opcion = st.sidebar.radio("Navegación", ["Gastos", "Presupuestos", "Metas de Ahorro", "Reportes"])
    
    if opcion == "Gastos":
        gastos_ui.mostrar_formulario_gasto(usuario["id"])
        gastos_ui.mostrar_lista_gastos(usuario["id"])
        graficos_ui.mostrar_grafico(usuario["id"])
    elif opcion == "Presupuestos":
        presupuestos_ui.mostrar_seccion_presupuestos(usuario["id"])
    elif opcion == "Metas de Ahorro":
        metas_ui.mostrar_seccion_metas(usuario["id"])
    elif opcion == "Reportes":
        reportes_ui.mostrar_seccion_reportes(usuario["id"])