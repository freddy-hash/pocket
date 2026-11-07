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


def mostrar_formulario_gasto(id_usuario):
    st.subheader("Registrar gasto")

    categorias = db.listar_categorias()
    nombres = [c["nombre"] for c in categorias]
    ids = {c["nombre"]: c["id"] for c in categorias}

    with st.form("form_gasto", clear_on_submit=True):
        monto = st.number_input("Monto (USD)", min_value=0.0, step=0.5, format="%.2f")
        descripcion = st.text_input("Descripción")
        fecha = st.date_input("Fecha", value=date.today())
        categoria = st.selectbox("Categoría", nombres)
        enviar = st.form_submit_button("Guardar gasto")

    if enviar:
        ok, mensaje = db.registrar_gasto(
            id_usuario, monto, descripcion, ids[categoria], fecha.isoformat()
        )
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