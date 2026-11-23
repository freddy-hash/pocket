from datetime import date
import io
import pandas as pd
import streamlit as st
from src.database import db


def _generar_excel_bytes(df_gastos: pd.DataFrame, df_resumen: pd.DataFrame) -> bytes | None:
    """Genera un archivo .xlsx en memoria con las hojas Gastos del Mes y Resumen por Categoría."""
    try:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_gastos.to_excel(writer, sheet_name="Gastos del Mes", index=False)
            df_resumen.to_excel(writer, sheet_name="Resumen por Categoria", index=False)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception:
        return None


def mostrar_seccion_reportes(id_usuario: int):
    """Muestra los gastos del mes, el resumen por categoría y descargas en CSV y Excel."""
    st.subheader("📑 Reportes Mensuales de Gastos")

    gastos = db.listar_gastos(id_usuario)
    mes_actual = date.today().strftime("%Y-%m")

    if not gastos:
        st.info("Aún no tienes gastos registrados para generar reportes.")
        return

    df_all = pd.DataFrame(gastos)
    df_all["fecha_str"] = df_all["fecha"].astype(str)
    df_all["mes"] = df_all["fecha_str"].str.slice(0, 7)
    df_all["monto"] = pd.to_numeric(df_all["monto"], errors="coerce").fillna(0.0)

    meses_disponibles = sorted(set(df_all["mes"].dropna().tolist()) | {mes_actual}, reverse=True)
    mes_seleccionado = st.selectbox(
        "Selecciona el mes del reporte (AAAA-MM)",
        options=meses_disponibles,
        index=meses_disponibles.index(mes_actual) if mes_actual in meses_disponibles else 0,
    )

    df_mes = df_all[df_all["mes"] == mes_seleccionado].copy()

    if df_mes.empty:
        st.warning(f"No hay gastos registrados en el mes {mes_seleccionado}.")
        return

    total_mes = round(float(df_mes["monto"].sum()), 2)
    st.metric("Total gastado en el mes", f"${total_mes:.2f}")

    # Resumen por categoría
    resumen = (
        df_mes.groupby("categoria", as_index=False)
        .agg(
            cantidad_gastos=("monto", "count"),
            total_categoria=("monto", "sum"),
        )
        .sort_values(by="total_categoria", ascending=False)
    )
    resumen["total_categoria"] = resumen["total_categoria"].round(2)
    resumen["porcentaje_mes"] = ((resumen["total_categoria"] / total_mes) * 100.0).round(1) if total_mes > 0 else 0.0
    resumen_renombrado = resumen.rename(
        columns={
            "categoria": "Categoría",
            "cantidad_gastos": "Cantidad de Gastos",
            "total_categoria": "Total Gastado ($)",
            "porcentaje_mes": "% del Mes",
        }
    )

    st.markdown("### Resumen por Categoría")
    st.dataframe(resumen_renombrado, use_container_width=True, hide_index=True)

    # Tabla detallada de gastos del mes
    columnas_detalle = [c for c in ["fecha", "categoria", "descripcion", "monto"] if c in df_mes.columns]
    df_detalle = df_mes[columnas_detalle].sort_values(by="fecha", ascending=False).rename(
        columns={
            "fecha": "Fecha",
            "categoria": "Categoría",
            "descripcion": "Descripción",
            "monto": "Monto ($)",
        }
    )

    st.markdown("### Detalle de Gastos del Mes")
    st.dataframe(df_detalle, use_container_width=True, hide_index=True)

    # Descarga CSV (incluye resumen por categoría y detalle)
    csv_buffer = io.StringIO()
    csv_buffer.write(f"RESUMEN POR CATEGORIA ({mes_seleccionado})\n")
    resumen_renombrado.to_csv(csv_buffer, index=False)
    csv_buffer.write(f"\nDETALLE DE GASTOS ({mes_seleccionado})\n")
    df_detalle.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode("utf-8-sig")

    col_csv, col_xlsx = st.columns(2)

    with col_csv:
        st.download_button(
            label="⬇️ Descargar Reporte CSV",
            data=csv_bytes,
            file_name=f"reporte_gastos_{mes_seleccionado}.csv",
            mime="text/csv",
        )

    with col_xlsx:
        excel_bytes = _generar_excel_bytes(df_detalle, resumen_renombrado)
        if excel_bytes is not None:
            st.download_button(
                label="⬇️ Descargar Reporte Excel (.xlsx)",
                data=excel_bytes,
                file_name=f"reporte_gastos_{mes_seleccionado}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.info("Instala `openpyxl` (`pip install openpyxl`) para habilitar la descarga en `.xlsx`.")