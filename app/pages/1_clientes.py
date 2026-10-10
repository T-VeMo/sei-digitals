
import streamlit as st
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from data.database.connection import SessionLocal
from data.database.models import Cliente
from utils import (
    normalizar_rut,
    rut_valido,
    telefono_valido,
    correo_valido,
)


st.title("👥 Gestión de Clientes")
st.sidebar.image("app/static/logo.png", width=100)


# ============================================================
# OBTENER CLIENTES DESDE SUPABASE
# ============================================================

def obtener_clientes():
    with SessionLocal() as db:
        consulta = select(Cliente).order_by(Cliente.razon_social)
        return db.scalars(consulta).all()


# ============================================================
# REGISTRAR NUEVO CLIENTE
# ============================================================

st.subheader("Registrar nuevo cliente")

with st.form("form_nuevo_cliente", clear_on_submit=True):

    rut = st.text_input(
        "RUT",
        placeholder="12.345.678-9"
    )

    razon_social = st.text_input(
        "Razón social"
    )

    rubro = st.text_input(
        "Rubro",
        placeholder="Ej.: Construcción"
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
            key="prefijo_nuevo"
        )

    with col_numero:
        telefono = st.text_input(
            "Número de teléfono",
            placeholder="12345678",
            max_chars=8,
            label_visibility="collapsed"
        )

    enviado = st.form_submit_button("Registrar cliente")

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

                    cliente_existente = db.get(
                        Cliente,
                        rut_normalizado
                    )

                    if cliente_existente:
                        st.error(
                            "Ya existe un cliente registrado con ese RUT."
                        )

                    else:
                        nuevo_cliente = Cliente(
                            rut=rut_normalizado,
                            razon_social=razon_social.strip(),
                            rubro=rubro.strip() or None,
                            correo=correo.strip(),
                            telefono=f"+569{telefono}"
                        )

                        db.add(nuevo_cliente)
                        db.commit()

                        st.success(
                            f"Cliente {razon_social.strip()} "
                            "registrado exitosamente."
                        )

                        st.rerun()

            except IntegrityError:
                st.error(
                    "No se pudo registrar el cliente. "
                    "Compruebe que el RUT no esté duplicado."
                )

            except SQLAlchemyError:
                st.error(
                    "Ocurrió un error al guardar el cliente "
                    "en la base de datos."
                )


# ============================================================
# LISTAR, EDITAR Y ELIMINAR CLIENTES
# ============================================================

st.divider()
st.subheader("Clientes registrados")

try:
    clientes = obtener_clientes()

    if not clientes:
        st.info("Aún no hay clientes registrados.")

    for cliente in clientes:

        with st.expander(
            f"{cliente.razon_social} — {cliente.rut}"
        ):

            st.caption(f"RUT: {cliente.rut}")

            # ------------------------------------------------
            # EDITAR CLIENTE
            # ------------------------------------------------

            with st.form(f"form_editar_{cliente.rut}"):

                razon_social_edit = st.text_input(
                    "Razón social",
                    value=cliente.razon_social,
                    key=f"razon_{cliente.rut}"
                )

                rubro_edit = st.text_input(
                    "Rubro",
                    value=cliente.rubro or "",
                    key=f"rubro_{cliente.rut}"
                )

                correo_edit = st.text_input(
                    "Correo electrónico",
                    value=cliente.correo or "",
                    key=f"correo_{cliente.rut}"
                )

                telefono_actual = cliente.telefono or ""
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
                        key=f"prefijo_{cliente.rut}"
                    )

                with col_numero_edit:
                    telefono_edit = st.text_input(
                        "Número de teléfono",
                        value=numero_actual,
                        max_chars=8,
                        label_visibility="collapsed",
                        key=f"telefono_{cliente.rut}"
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

                                cliente_db = db.get(
                                    Cliente,
                                    cliente.rut
                                )

                                if cliente_db is None:
                                    st.error(
                                        "El cliente ya no existe "
                                        "en la base de datos."
                                    )

                                else:
                                    cliente_db.razon_social = (
                                        razon_social_edit.strip()
                                    )

                                    cliente_db.rubro = (
                                        rubro_edit.strip() or None
                                    )

                                    cliente_db.correo = (
                                        correo_edit.strip() or None
                                    )

                                    cliente_db.telefono = (
                                        f"+569{telefono_edit}"
                                        if telefono_edit.strip()
                                        else None
                                    )

                                    db.commit()

                                    st.success(
                                        "Cliente actualizado exitosamente."
                                    )

                                    st.rerun()

                        except SQLAlchemyError:
                            st.error(
                                "No fue posible actualizar el cliente."
                            )

            # ------------------------------------------------
            # ELIMINAR CLIENTE
            # ------------------------------------------------

            confirmar_eliminacion = st.checkbox(
                "Confirmar eliminación de este cliente",
                key=f"confirmar_eliminar_{cliente.rut}"
            )

            if st.button(
                "🗑️ Eliminar cliente",
                key=f"eliminar_{cliente.rut}"
            ):

                if not confirmar_eliminacion:
                    st.warning(
                        "Marca la casilla de confirmación "
                        "antes de eliminar."
                    )

                else:
                    try:
                        with SessionLocal() as db:

                            cliente_db = db.get(
                                Cliente,
                                cliente.rut
                            )

                            if cliente_db is None:
                                st.warning(
                                    "El cliente ya no existe."
                                )

                            else:
                                db.delete(cliente_db)
                                db.commit()

                                st.success(
                                    "Cliente eliminado exitosamente."
                                )

                                st.rerun()

                    except IntegrityError:
                        st.error(
                            "No se puede eliminar este cliente porque "
                            "tiene facturas de venta asociadas."
                        )

                    except SQLAlchemyError:
                        st.error(
                            "No fue posible eliminar el cliente."
                        )

except SQLAlchemyError:
    st.error(
        "No fue posible cargar los clientes desde Supabase."
    )
