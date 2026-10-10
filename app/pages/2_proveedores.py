
import streamlit as st
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from data.database.connection import SessionLocal
from data.database.models import Proveedor
from utils import (
    normalizar_rut,
    rut_valido,
    telefono_valido,
    correo_valido,
)


st.title("📦 Gestión de Proveedores")
st.sidebar.image("app/static/logo.png", width=100)


# ============================================================
# OBTENER PROVEEDORES DESDE SUPABASE
# ============================================================

def obtener_proveedores():
    with SessionLocal() as db:
        consulta = select(Proveedor).order_by(Proveedor.razon_social)
        return db.scalars(consulta).all()


# ============================================================
# REGISTRAR NUEVO PROVEEDOR
# ============================================================

st.subheader("Registrar nuevo proveedor")

with st.form("form_nuevo_proveedor", clear_on_submit=False):

    rut = st.text_input(
        "RUT",
        placeholder="12.345.678-9"
    )

    razon_social = st.text_input(
        "Razón social"
    )

    rubro = st.text_input(
        "Rubro del proveedor",
        placeholder="Ej.: Eléctrico"
    )

    correo = st.text_input(
        "Correo electrónico"
    )

    st.write("Teléfono móvil")

    col_prefijo, col_numero = st.columns([1, 4])

    with col_prefijo:
        st.text_input(
            "Prefijo",
            value="+569",
            disabled=True,
            label_visibility="collapsed",
            key="prefijo_nuevo_proveedor"
        )

    with col_numero:
        telefono = st.text_input(
            "Número de teléfono",
            placeholder="12345678",
            max_chars=8,
            label_visibility="collapsed"
        )

    enviado = st.form_submit_button("Registrar proveedor")

    if enviado:

        rut_normalizado = normalizar_rut(rut)

        if (
            not rut.strip()
            or not razon_social.strip()
            or not correo.strip()
            or not telefono.strip()
        ):
            st.error(
                "Complete los campos obligatorios: "
                "RUT, razón social, correo y teléfono."
            )

        elif not rut_valido(rut_normalizado):
            st.error("El RUT ingresado no es válido.")

        elif not correo_valido(correo):
            st.error("Ingrese un correo electrónico válido.")

        elif not telefono_valido(telefono):
            st.error(
                "Ingrese los 8 dígitos del número móvil después de +569."
            )

        else:
            try:
                with SessionLocal() as db:

                    proveedor_existente = db.get(
                        Proveedor,
                        rut_normalizado
                    )

                    if proveedor_existente:
                        st.error(
                            "Ya existe un proveedor registrado con ese RUT."
                        )

                    else:
                        nuevo_proveedor = Proveedor(
                            rut=rut_normalizado,
                            razon_social=razon_social.strip(),
                            rubro=rubro.strip() or None,
                            correo=correo.strip(),
                            telefono=f"+569{telefono}"
                        )

                        db.add(nuevo_proveedor)
                        db.commit()

                        st.success(
                            f"Proveedor {razon_social.strip()} "
                            "registrado exitosamente."
                        )

                        st.rerun()

            except IntegrityError:
                st.error(
                    "No se pudo registrar el proveedor. "
                    "Compruebe que el RUT no esté duplicado."
                )

            except SQLAlchemyError:
                st.error(
                    "Ocurrió un error al guardar el proveedor "
                    "en la base de datos."
                )


# ============================================================
# LISTAR, EDITAR Y ELIMINAR PROVEEDORES
# ============================================================

st.divider()
st.subheader("Proveedores registrados")

try:
    proveedores = obtener_proveedores()

    if not proveedores:
        st.info("Aún no hay proveedores registrados.")

    for proveedor in proveedores:

        with st.expander(
            f"{proveedor.razon_social} — {proveedor.rut}"
        ):

            st.caption(f"RUT: {proveedor.rut}")

            # ------------------------------------------------
            # EDITAR PROVEEDOR
            # ------------------------------------------------

            with st.form(f"form_editar_proveedor_{proveedor.rut}"):

                razon_social_edit = st.text_input(
                    "Razón social",
                    value=proveedor.razon_social,
                    key=f"razon_proveedor_{proveedor.rut}"
                )

                rubro_edit = st.text_input(
                    "Rubro del proveedor",
                    value=proveedor.rubro or "",
                    key=f"rubro_proveedor_{proveedor.rut}"
                )

                correo_edit = st.text_input(
                    "Correo electrónico",
                    value=proveedor.correo or "",
                    key=f"correo_proveedor_{proveedor.rut}"
                )

                telefono_actual = proveedor.telefono or ""
                numero_actual = telefono_actual

                if numero_actual.startswith("+569"):
                    numero_actual = numero_actual[4:]

                col_prefijo_edit, col_numero_edit = st.columns([1, 4])

                with col_prefijo_edit:
                    st.text_input(
                        "Prefijo",
                        value="+569",
                        disabled=True,
                        label_visibility="collapsed",
                        key=f"prefijo_proveedor_{proveedor.rut}"
                    )

                with col_numero_edit:
                    telefono_edit = st.text_input(
                        "Número de teléfono",
                        value=numero_actual,
                        max_chars=8,
                        label_visibility="collapsed",
                        key=f"telefono_proveedor_{proveedor.rut}"
                    )

                guardar = st.form_submit_button("Guardar cambios")

                if guardar:

                    if not razon_social_edit.strip():
                        st.error("La razón social es obligatoria.")

                    elif (
                        correo_edit.strip()
                        and not correo_valido(correo_edit)
                    ):
                        st.error("Ingrese un correo electrónico válido.")

                    elif (
                        telefono_edit.strip()
                        and not telefono_valido(telefono_edit)
                    ):
                        st.error("Ingrese los 8 dígitos del número móvil.")

                    else:
                        try:
                            with SessionLocal() as db:

                                proveedor_db = db.get(
                                    Proveedor,
                                    proveedor.rut
                                )

                                if proveedor_db is None:
                                    st.error(
                                        "El proveedor ya no existe "
                                        "en la base de datos."
                                    )

                                else:
                                    proveedor_db.razon_social = (
                                        razon_social_edit.strip()
                                    )

                                    proveedor_db.rubro = (
                                        rubro_edit.strip() or None
                                    )

                                    proveedor_db.correo = (
                                        correo_edit.strip() or None
                                    )

                                    proveedor_db.telefono = (
                                        f"+569{telefono_edit}"
                                        if telefono_edit.strip()
                                        else None
                                    )

                                    db.commit()

                                    st.success(
                                        "Proveedor actualizado exitosamente."
                                    )

                                    st.rerun()

                        except SQLAlchemyError:
                            st.error(
                                "No fue posible actualizar el proveedor."
                            )

            # ------------------------------------------------
            # ELIMINAR PROVEEDOR
            # ------------------------------------------------

            confirmar_eliminacion = st.checkbox(
                "Confirmar eliminación de este proveedor",
                key=f"confirmar_eliminar_proveedor_{proveedor.rut}"
            )

            if st.button(
                "🗑️ Eliminar proveedor",
                key=f"eliminar_proveedor_{proveedor.rut}"
            ):

                if not confirmar_eliminacion:
                    st.warning(
                        "Marca la casilla de confirmación "
                        "antes de eliminar."
                    )

                else:
                    try:
                        with SessionLocal() as db:

                            proveedor_db = db.get(
                                Proveedor,
                                proveedor.rut
                            )

                            if proveedor_db is None:
                                st.warning(
                                    "El proveedor ya no existe."
                                )

                            else:
                                db.delete(proveedor_db)
                                db.commit()

                                st.success(
                                    "Proveedor eliminado exitosamente."
                                )

                                st.rerun()

                    except IntegrityError:
                        st.error(
                            "No se puede eliminar este proveedor porque "
                            "tiene facturas de compra asociadas."
                        )

                    except SQLAlchemyError:
                        st.error(
                            "No fue posible eliminar el proveedor.")

except SQLAlchemyError:
    st.error(
        "No fue posible cargar los proveedores desde Supabase."
    )
