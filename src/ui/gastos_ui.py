from datetime import date

import streamlit as st

from src.database import db


def _sugerir_categoria(descripcion):
    """Pide la sugerencia al modelo de Dixy. Si no existe o falla, devuelve None."""
    try:
        from src.ml.clasificador import sugerir_categoria
        return sugerir_categoria(descripcion)
    except Exception:
        return None


def _al_cambiar_descripcion():
    """Se ejecuta al presionar Enter en la descripción: pone la categoría sugerida."""
    sugerida = _sugerir_categoria(st.session_state.get("gasto_descripcion", ""))
    nombres = [c["nombre"] for c in db.listar_categorias()]
    if sugerida in nombres:
        st.session_state["gasto_categoria"] = sugerida


def _guardar_gasto(id_usuario):
    """Guarda el gasto y limpia el formulario si todo sale bien."""
    ids = {c["nombre"]: c["id"] for c in db.listar_categorias()}
    ok, mensaje = db.registrar_gasto(
        id_usuario,
        st.session_state["gasto_monto"],
        st.session_state["gasto_descripcion"],
        ids[st.session_state["gasto_categoria"]],
        st.session_state["gasto_fecha"].isoformat(),
    )
    st.session_state["gasto_resultado"] = (ok, mensaje)
    if ok:
        st.session_state["gasto_monto"] = 0.0
        st.session_state["gasto_descripcion"] = ""
        st.session_state["gasto_fecha"] = date.today()


def mostrar_formulario_gasto(id_usuario):
    st.subheader("Registrar gasto")

    nombres = [c["nombre"] for c in db.listar_categorias()]

    st.session_state.setdefault("gasto_monto", 0.0)
    st.session_state.setdefault("gasto_descripcion", "")
    st.session_state.setdefault("gasto_fecha", date.today())
    st.session_state.setdefault("gasto_categoria", nombres[0])

    st.text_input(
        "Descripción (presiona Enter para sugerir la categoría)",
        key="gasto_descripcion",
        on_change=_al_cambiar_descripcion,
    )
    st.number_input("Monto (USD)", min_value=0.0, step=0.5, format="%.2f", key="gasto_monto")
    st.date_input("Fecha", key="gasto_fecha")
    st.selectbox("Categoría (sugerida automáticamente, puedes cambiarla)", nombres, key="gasto_categoria")

    st.button("Guardar gasto", on_click=_guardar_gasto, args=(id_usuario,))

    resultado = st.session_state.pop("gasto_resultado", None)
    if resultado:
        ok, mensaje = resultado
        if ok:
            st.success(mensaje)
        else:
            st.error(mensaje)


def mostrar_lista_gastos(id_usuario):
    st.subheader("Mis gastos")

    gastos = db.listar_gastos(id_usuario)
    if not gastos:
        st.info("Todavía no has registrado gastos.")
        return

    st.metric("Total gastado", f"${sum(g['monto'] for g in gastos):,.2f}")
    st.dataframe(
        gastos,
        hide_index=True,
        use_container_width=True,
        column_config={
            "id": None,
            "fecha": "Fecha",
            "monto": st.column_config.NumberColumn("Monto", format="$%.2f"),
            "descripcion": "Descripción",
            "categoria": "Categoría",
        },
    )