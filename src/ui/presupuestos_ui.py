from datetime import date
import re
import streamlit as st
from src.database import db
from src.utils.validaciones import validar_fecha_iso, validar_monto


def _validar_mes_aaaamm(mes_str: str) -> tuple[bool, str]:
    """Valida que el mes tenga formato AAAA-MM usando validar_fecha_iso."""
    mes_limpio = (mes_str or "").strip()
    if not re.fullmatch(r"\d{4}-\d{2}", mes_limpio):
        return False, "El mes debe tener el formato AAAA-MM (ejemplo: 2026-11)."
    ok_fecha, _ = validar_fecha_iso(f"{mes_limpio}-01")
    if not ok_fecha:
        return False, "El mes ingresado no es válido (usa formato AAAA-MM)."
    return True, mes_limpio


def _obtener_gasto_categoria_mes(id_usuario: int, id_categoria: int, categoria_nombre: str, mes: str) -> float:
    """Calcula el total gastado por el usuario en una categoría y mes (AAAA-MM)."""
    if not hasattr(db, "listar_gastos"):
        return 0.0

    try:
        gastos = db.listar_gastos(id_usuario)
    except TypeError:
        try:
            gastos = db.listar_gastos(id_usuario=id_usuario)
        except Exception:
            return 0.0
    except Exception:
        return 0.0

    if not gastos:
        return 0.0

    total = 0.0
    for g in gastos:
        fecha_gasto = str(g.get("fecha", ""))
        if not fecha_gasto.startswith(mes):
            continue

        coincide_cat = False
        if "id_categoria" in g and g["id_categoria"] is not None:
            coincide_cat = g["id_categoria"] == id_categoria
        if not coincide_cat and "categoria" in g and g["categoria"] is not None:
            coincide_cat = str(g["categoria"]).strip().lower() == categoria_nombre.strip().lower()

        if coincide_cat:
            try:
                total += float(g.get("monto", 0.0) or 0.0)
            except (TypeError, ValueError):
                continue

    return round(total, 2)


def _obtener_meses_disponibles(id_usuario: int, mes_actual: str) -> list[str]:
    """Reúne el mes actual y los meses presentes en los presupuestos del usuario."""
    meses = {mes_actual}
    try:
        todos_presupuestos = db.listar_presupuestos(id_usuario)
        if isinstance(todos_presupuestos, list):
            for p in todos_presupuestos:
                m = str(p.get("mes", "")).strip()
                if re.fullmatch(r"\d{4}-\d{2}", m):
                    meses.add(m)
    except TypeError:
        # Si listar_presupuestos exige el parámetro mes, conservamos al menos mes_actual
        pass
    except Exception:
        pass

    return sorted(meses, reverse=True)


def mostrar_seccion_presupuestos(id_usuario: int):
    """Muestra el formulario para establecer presupuestos y el seguimiento por mes."""
    st.subheader("🎯 Presupuestos Mensuales")

    tab_crear, tab_listar = st.tabs(["Establecer Presupuesto", "Ver Presupuestos"])

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

            ok_monto, res_monto = validar_monto(limite_input)
            if not ok_monto:
                st.error(res_monto)
                return

            ok_mes, res_mes = _validar_mes_aaaamm(mes_input)
            if not ok_mes:
                st.error(res_mes)
                return

            id_cat = cat_dict.get(categoria_nombre)
            ok, mensaje = db.guardar_presupuesto(
                id_usuario=id_usuario,
                id_categoria=id_cat,
                limite=res_monto,
                mes=res_mes,
            )

            if ok:
                st.success(mensaje)
                st.rerun()
            else:
                st.error(mensaje)

    with tab_listar:
        meses_opciones = _obtener_meses_disponibles(id_usuario, mes_actual)
        col_sel, col_custom = st.columns([2, 2])
        with col_sel:
            mes_seleccionado = st.selectbox(
                "Selecciona el mes a consultar",
                options=meses_opciones,
                index=meses_opciones.index(mes_actual) if mes_actual in meses_opciones else 0,
            )
        with col_custom:
            mes_manual = st.text_input(
                "O escribe otro mes (AAAA-MM)",
                value="",
                placeholder="Ej. 2026-12",
            )

        mes_a_mostrar = mes_seleccionado
        if mes_manual.strip():
            ok_m, mes_validado = _validar_mes_aaaamm(mes_manual)
            if not ok_m:
                st.warning(mes_validado)
            else:
                mes_a_mostrar = mes_validado

        st.markdown(f"### Presupuestos para el mes: **{mes_a_mostrar}**")
        presupuestos = db.listar_presupuestos(id_usuario, mes=mes_a_mostrar)

        if not presupuestos:
            st.info(f"No has establecido presupuestos para {mes_a_mostrar}.")
        else:
            for p in presupuestos:
                cat_nombre = p.get("categoria", "Sin categoría")
                id_cat = p.get("id_categoria")
                limite = float(p.get("limite", 0.0) or 0.0)
                gastado = _obtener_gasto_categoria_mes(id_usuario, id_cat, cat_nombre, mes_a_mostrar)

                porcentaje = (gastado / limite * 100.0) if limite > 0 else 0.0
                progreso = min(max(gastado / limite, 0.0), 1.0) if limite > 0 else 0.0

                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(f"**{cat_nombre}**")
                    st.caption(f"Gastado: **\\${gastado:.2f}** / Límite: **\\${limite:.2f}** ({porcentaje:.1f}%)")
                with col2:
                    st.progress(progreso)
                with col3:
                    if st.button("Eliminar", key=f"del_pres_{mes_a_mostrar}_{p['id']}"):
                        ok, mensaje = db.borrar_presupuesto(id_usuario, p["id"])
                        if ok:
                            st.success(mensaje)
                            st.rerun()
                        else:
                            st.error(mensaje)

                if porcentaje >= 100.0:
                    st.error(f"🚨 Alerta (100%): Se alcanzó o superó el límite de **{cat_nombre}** en {mes_a_mostrar} (\\${gastado:.2f} de \\${limite:.2f}).")
                elif porcentaje >= 80.0:
                    st.warning(f"⚠️ Alerta (80%): Ya llevas el **{porcentaje:.1f}%** del presupuesto de **{cat_nombre}** en {mes_a_mostrar} (\\${gastado:.2f} de \\${limite:.2f}).")
                st.divider()