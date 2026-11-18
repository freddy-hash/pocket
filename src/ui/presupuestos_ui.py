"""
Módulo de interfaz de usuario para la gestión de presupuestos mensuales en Pocket.
Permite definir límites de gasto por categoría y consultar el estado del mes.
"""

from datetime import date
import streamlit as st
from src.database import db


def mostrar_seccion_presupuestos(id_usuario: int):
    """Muestra el formulario para establecer presupuestos y la lista de presupuestos actuales."""
    st.subheader("🎯 Presupuestos Mensuales")

    tab_crear, tab_listar = st.tabs(["Establecer Presupuesto", "Ver Presupuestos"])

    # Obtener categorías y mes actual (AAAA-MM)
    categorias = db.listar_categorias()
    cat_dict = {cat["nombre"]: cat["id"] for cat in categorias}
    mes_actual = date.today().strftime("%Y-%m")

    with tab_crear:
        with st.form("form_presupuesto"):
            if cat_dict:
                categoria_nombre = st.selectbox("Categoría", list(cat_dict.keys()))
            else:
                st.warning("No hay categorías disponibles.")
                categoria_nombre = None

            limite_input = st.number_input("Límite de Gasto ($)", min_value=0.0, step=10.0, format="%.2f")
            mes_input = st.text_input("Mes (AAAA-MM)", value=mes_actual)
            
            enviar = st.form_submit_button("Guardar Presupuesto")

        if enviar:
            if not categoria_nombre:
                st.error("Selecciona una categoría válida.")
                return

            id_cat = cat_dict.get(categoria_nombre)
            ok, mensaje = db.guardar_presupuesto(
                id_usuario=id_usuario,
                id_categoria=id_cat,
                limite=limite_input,
                mes=mes_input
            )

            if ok:
                st.success(mensaje)
                st.rerun()
            else:
                st.error(mensaje)

    with tab_listar:
        st.markdown(f"### Presupuestos para el mes: {mes_actual}")
        presupuestos = db.listar_presupuestos(id_usuario, mes=mes_actual)

        if not presupuestos:
            st.info("No has establecido presupuestos para este mes.")
        else:
            for p in presupuestos:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(f"**{p['categoria']}**")
                with col2:
                    st.markdown(f"Límite: **${p['limite']:.2f}**")
                with col3:
                    if st.button("Eliminar", key=f"del_pres_{p['id']}"):
                        ok, mensaje = db.borrar_presupuesto(id_usuario, p['id'])
                        if ok:
                            st.success(mensaje)
                            st.rerun()
                        else:
                            st.error(mensaje)
                st.divider()