import streamlit as st

from src.database import db


def _inicializar_sesion():
    """Crea las variables de sesión si todavía no existen."""
    if "usuario" not in st.session_state:
        st.session_state["usuario"] = None


def usuario_actual():
    """Devuelve el diccionario del usuario con sesión iniciada, o None."""
    _inicializar_sesion()
    return st.session_state["usuario"]


def cerrar_sesion():
    st.session_state["usuario"] = None


def _formulario_login():
    with st.form("form_login"):
        usuario = st.text_input("Usuario")
        contrasena = st.text_input("Contraseña", type="password")
        enviar = st.form_submit_button("Iniciar sesión")

    if enviar:
        ok, resultado = db.iniciar_sesion(usuario, contrasena)
        if ok:
            st.session_state["usuario"] = resultado
            st.rerun()
        else:
            st.error(resultado)


def _formulario_registro():
    with st.form("form_registro"):
        nombre = st.text_input("Nombre completo")
        usuario = st.text_input("Usuario")
        contrasena = st.text_input("Contraseña (6 a 72 caracteres)", type="password")
        enviar = st.form_submit_button("Crear cuenta")

    if enviar:
        ok, mensaje = db.registrar_usuario(nombre, usuario, contrasena)
        if not ok:
            st.error(mensaje)
            return

        # Registro exitoso: iniciar sesión automáticamente
        ok, resultado = db.iniciar_sesion(usuario, contrasena)
        if ok:
            st.session_state["usuario"] = resultado
            st.rerun()
        else:
            st.success(mensaje + " Ahora puedes iniciar sesión.")


def mostrar_autenticacion():
    """Muestra las pestañas de inicio de sesión y registro."""
    _inicializar_sesion()
    tab_login, tab_registro = st.tabs(["Iniciar sesión", "Registrarse"])
    with tab_login:
        _formulario_login()
    with tab_registro:
        _formulario_registro()


def mostrar_barra_usuario():
    """Muestra el nombre del usuario y el botón de cerrar sesión en la barra lateral."""
    usuario = usuario_actual()
    if usuario:
        st.sidebar.write(f"👤 {usuario['nombre']}")
        if st.sidebar.button("Cerrar sesión"):
            cerrar_sesion()
            st.rerun()