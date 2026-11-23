import streamlit as st
from src.database import db
from src.utils.validaciones import validar_monto, validar_texto_no_vacio


def mostrar_seccion_metas(id_usuario: int):
    """Muestra el formulario para crear metas de ahorro y la lista interactiva con opciones de abono."""
    st.subheader("🎯 Metas de Ahorro")

    tab_crear, tab_listar = st.tabs(["Crear Meta", "Mis Metas"])

    with tab_crear:
        with st.form("form_meta"):
            nombre = st.text_input("Nombre de la Meta (ej. Fondo de emergencia, Viaje)")
            monto_objetivo = st.number_input("Monto Objetivo ($)", min_value=1.0, step=50.0, format="%.2f")
            ahorro_inicial = st.number_input("Ahorro Inicial ($)", min_value=0.0, step=10.0, format="%.2f")

            enviar = st.form_submit_button("Guardar Meta")

        if enviar:
            ok_nombre, nombre_limpio = validar_texto_no_vacio(nombre, "El nombre de la meta")
            if not ok_nombre:
                st.error(nombre_limpio)
                return

            ok_objetivo, objetivo_validado = validar_monto(monto_objetivo)
            if not ok_objetivo:
                st.error(objetivo_validado)
                return

            inicial_validado = 0.0
            if float(ahorro_inicial) > 0.0:
                ok_inicial, res_inicial = validar_monto(ahorro_inicial)
                if not ok_inicial:
                    st.error(res_inicial)
                    return
                inicial_validado = float(res_inicial)

            ok, mensaje = db.crear_meta(
                id_usuario=id_usuario,
                nombre=nombre_limpio,
                monto_objetivo=float(objetivo_validado),
            )

            if not ok:
                st.error(mensaje)
                return

            if inicial_validado > 0.0:
                metas_actuales = db.listar_metas(id_usuario)
                if metas_actuales:
                    meta_creada = metas_actuales[-1]
                    ok_abono, msg_abono = db.abonar_meta(id_usuario, meta_creada["id"], inicial_validado)
                    if not ok_abono:
                        st.warning(f"{mensaje} Sin embargo, no se pudo aplicar el ahorro inicial: {msg_abono}")
                        st.rerun()
                        return

            st.success(mensaje)
            st.rerun()

    with tab_listar:
        st.markdown("### Estado de tus Metas")
        metas = db.listar_metas(id_usuario)

        if not metas:
            st.info("Todavía no has registrado metas de ahorro.")
        else:
            for m in metas:
                ahorrado = float(m.get("monto_ahorrado", 0.0) or 0.0)
                objetivo = float(m.get("monto_objetivo", 0.0) or 0.0)

                porcentaje = (ahorrado / objetivo * 100.0) if objetivo > 0 else 0.0
                progreso = min(max(ahorrado / objetivo, 0.0), 1.0) if objetivo > 0 else 0.0

                st.markdown(f"#### 🏷️ {m['nombre']}")
                st.progress(progreso)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(
                        f"Ahorrado: **${ahorrado:.2f}** / ${objetivo:.2f} (**{porcentaje:.1f}%**)"
                    )
                with col2:
                    st.markdown(f"Creada: **{m['fecha_creacion']}**")
                with col3:
                    if st.button("Eliminar", key=f"del_meta_{m['id']}"):
                        ok, mensaje = db.borrar_meta(id_usuario, m["id"])
                        if ok:
                            st.success(mensaje)
                            st.rerun()
                        else:
                            st.error(mensaje)

                if objetivo > 0 and ahorrado >= objetivo:
                    st.success(f"🎉 Meta '{m['nombre']}' completada al {porcentaje:.1f}%.")

                with st.expander(f"Abonar a '{m['nombre']}'"):
                    with st.form(f"form_abonar_{m['id']}"):
                        monto_abono = st.number_input(
                            "Monto a abonar ($)",
                            min_value=0.1,
                            step=5.0,
                            format="%.2f",
                            key=f"input_abono_{m['id']}",
                        )
                        btn_abonar = st.form_submit_button("Confirmar Abono")

                    if btn_abonar:
                        ok_abono_val, abono_validado = validar_monto(monto_abono)
                        if not ok_abono_val:
                            st.error(abono_validado)
                        else:
                            ok_abono, msg_abono = db.abonar_meta(
                                id_usuario, m["id"], float(abono_validado)
                            )
                            if ok_abono:
                                st.success(msg_abono)
                                st.rerun()
                            else:
                                st.error(msg_abono)

                st.divider()