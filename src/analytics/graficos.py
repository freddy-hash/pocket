import pandas as pd
import plotly.express as px

from src.database.db import listar_gastos


def gastos_por_categoria(id_usuario):
    """Devuelve un DataFrame con el total gastado por categoría (columnas: categoria, total)."""
    gastos = listar_gastos(id_usuario)
    if not gastos:
        return pd.DataFrame(columns=["categoria", "total"])

    df = pd.DataFrame(gastos)
    resumen = df.groupby("categoria", as_index=False)["monto"].sum()
    resumen = resumen.rename(columns={"monto": "total"})
    resumen["total"] = resumen["total"].round(2)
    return resumen.sort_values("total", ascending=False).reset_index(drop=True)


def grafico_gastos_por_categoria(id_usuario):
    """Devuelve el gráfico de barras de gastos por categoría, o None si el usuario no tiene gastos."""
    resumen = gastos_por_categoria(id_usuario)
    if resumen.empty:
        return None

    fig = px.bar(
        resumen,
        x="categoria",
        y="total",
        color="categoria",
        text="total",
        title="Gastos por categoría",
        labels={"categoria": "Categoría", "total": "Total gastado (USD)"},
    )
    fig.update_traces(texttemplate="$%{text:.2f}", textposition="outside")
    fig.update_layout(xaxis_title=None, showlegend=False)
    return fig  