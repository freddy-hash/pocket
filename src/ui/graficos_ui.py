import streamlit as st

from src.analytics import graficos


def mostrar_grafico(id_usuario):
    st.subheader("Gastos por categoría")

    figura = graficos.grafico_gastos_por_categoria(id_usuario)
    if figura is None:
        st.info("Registra tu primer gasto para ver el gráfico.")
        return

    st.plotly_chart(figura, use_container_width=True)