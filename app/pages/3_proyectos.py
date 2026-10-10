
import streamlit as st
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from data.database.connection import SessionLocal
from data.database.models import (
    Cliente,
    Proveedor,
    Presupuesto,
    FacturaVenta,
    FacturaCompra,
    Proyecto,
)
from utils import formato_clp, rut_valido, normalizar_rut

IVA_PORCENTAJE = Decimal("0.19")
MONEDA = Decimal("1")


def calcular_iva(monto):
    return (
        Decimal(str(monto)) * IVA_PORCENTAJE
    ).quantize(MONEDA, rounding=ROUND_HALF_UP)


def calcular_presupuesto(total_mo, total_materiales,
                         gastos_generales, utilidades):
    subtotal = total_mo + total_materiales
    subtotal_neto = subtotal + gastos_generales + utilidades
    iva = calcular_iva(subtotal_neto)
    total = subtotal_neto + iva

    return {
        "subtotal": subtotal,
        "subtotal_neto": subtotal_neto,
        "iva": iva,
        "total": total,
    }


def cargar_datos():
    with SessionLocal() as db:
        proyectos = db.scalars(
            select(Proyecto).order_by(Proyecto.id_proyecto.desc())
        ).all()

        presupuestos = db.scalars(
            select(Presupuesto).order_by(Presupuesto.id_presupuesto.desc())
        ).all()

        facturas_venta = db.scalars(
            select(FacturaVenta).order_by(
                FacturaVenta.fecha_emision.desc()
            )
        ).all()

        facturas_compra = db.scalars(
            select(FacturaCompra).order_by(
                FacturaCompra.fecha_compra.desc()
            )
        ).all()

        clientes = db.scalars(
            select(Cliente).order_by(Cliente.razon_social)
        ).all()

        proveedores = db.scalars(
            select(Proveedor).order_by(Proveedor.razon_social)
        ).all()

        return (
            proyectos,
            presupuestos,
            facturas_venta,
            facturas_compra,
            clientes,
            proveedores,
        )


st.title("📁 Gestión de Proyectos")
st.sidebar.image("app/static/logo.png", width=100)

tab_proyectos, tab_presupuesto, tab_facturacion = st.tabs(
    ["📁 Proyectos", "💰 Presupuesto", "🧾 Facturación"]
)

try:
    (
        proyectos,
        presupuestos,
        facturas_venta,
        facturas_compra,
        clientes,
        proveedores,
    ) = cargar_datos()

except SQLAlchemyError as error:
    st.error("No fue posible consultar la base de datos.")
    st.exception(error)
    st.stop()


presupuestos_por_id = {
    p.id_presupuesto: p for p in presupuestos
}
facturas_venta_por_id = {
    f.nro_documento: f for f in facturas_venta
}
clientes_por_rut = {
    c.rut: c for c in clientes
}
proveedores_por_rut = {
    p.rut: p for p in proveedores
}

# ==========================================================
# PESTAÑA 1: PROYECTOS
# ==========================================================
with tab_proyectos:
    st.subheader("Registrar proyecto")

    st.info(
        "El modelo actual no contiene nombre ni estado del proyecto. "
        "Por ello, cada proyecto se identifica mediante su ID. "
        "El costo total se obtiene del presupuesto asociado o se ingresa "
        "manualmente si todavía no existe uno."
    )

    if not clientes:
        st.warning(
            "Debes registrar al menos un cliente en la pestaña "
            "Gestión de Clientes antes de registrar una factura de venta."
        )

    presupuestos_ids = [None] + [
        p.id_presupuesto for p in presupuestos
    ]
    facturas_ids = [None] + [
        f.nro_documento for f in facturas_venta
    ]

    def etiqueta_presupuesto(id_presupuesto):
        if id_presupuesto is None:
            return "Sin presupuesto asociado"
        presupuesto = presupuestos_por_id[id_presupuesto]
        return (
            f"Presupuesto #{id_presupuesto} — "
            f"{formato_clp(presupuesto.total)}"
        )

    def etiqueta_factura(id_factura):
        if id_factura is None:
            return "Sin factura de venta asociada"
        factura = facturas_venta_por_id[id_factura]
        return (
            f"Factura #{id_factura} — "
            f"{formato_clp(factura.total)}"
        )

    with st.form("form_nuevo_proyecto", clear_on_submit=True):
        fecha_inicio = st.date_input(
            "Fecha de inicio",
            value=date.today(),
        )

        fecha_termino = st.date_input(
            "Fecha estimada de término",
            value=date.today(),
        )

        presupuesto_seleccionado = st.selectbox(
            "Presupuesto asociado",
            options=presupuestos_ids,
            format_func=etiqueta_presupuesto,
            key="nuevo_proyecto_presupuesto",
        )

        factura_seleccionada = st.selectbox(
            "Factura de venta asociada (opcional)",
            options=facturas_ids,
            format_func=etiqueta_factura,
            key="nuevo_proyecto_factura",
        )

        if presupuesto_seleccionado is None:
            costo_total = st.number_input(
                "Costo total estimado ($)",
                min_value=0,
                value=0,
                step=10000,
            )
        else:
            presupuesto_actual = presupuestos_por_id[
                presupuesto_seleccionado
            ]
            costo_total = int(presupuesto_actual.total)

            st.metric(
                "Costo total calculado",
                formato_clp(costo_total),
            )

        registrar = st.form_submit_button(
            "Registrar proyecto",
            type="primary",
        )

        if registrar:
            if fecha_termino < fecha_inicio:
                st.error(
                    "La fecha de término no puede ser anterior "
                    "a la fecha de inicio."
                )
            elif (
                presupuesto_seleccionado is None
                and costo_total <= 0
            ):
                st.error(
                    "Ingresa un costo total mayor que cero "
                    "o selecciona un presupuesto."
                )
            else:
                try:
                    with SessionLocal() as db:
                        nuevo_proyecto = Proyecto(
                            costo_total=costo_total,
                            id_presupuesto=presupuesto_seleccionado,
                            nro_documento=factura_seleccionada,
                            fecha_inicio=fecha_inicio,
                            fecha_termino=fecha_termino,
                        )

                        db.add(nuevo_proyecto)
                        db.commit()

                    st.success("Proyecto registrado correctamente.")
                    st.rerun()

                except SQLAlchemyError:
                    st.error(
                        "No fue posible registrar el proyecto. "
                        "Verifica las asociaciones y la conexión."
                    )

    st.divider()
    st.subheader("Proyectos registrados")

    if not proyectos:
        st.info("Todavía no hay proyectos registrados.")
    else:
        for proyecto in proyectos:
            presupuesto = presupuestos_por_id.get(
                proyecto.id_presupuesto
            )
            factura = facturas_venta_por_id.get(
                proyecto.nro_documento
            )

            with st.expander(
                f"Proyecto #{proyecto.id_proyecto} — "
                f"{formato_clp(proyecto.costo_total)}"
            ):
                st.write(
                    f"**Fecha de inicio:** "
                    f"{proyecto.fecha_inicio or 'No registrada'}"
                )
                st.write(
                    f"**Fecha de término:** "
                    f"{proyecto.fecha_termino or 'No registrada'}"
                )
                st.write(
                    "**Presupuesto:** "
                    + (
                        f"#{presupuesto.id_presupuesto}"
                        if presupuesto else "Sin asociar"
                    )
                )
                st.write(
                    "**Factura de venta:** "
                    + (
                        f"#{factura.nro_documento}"
                        if factura else "Sin asociar"
                    )
                )

                with st.form(
                    f"editar_proyecto_{proyecto.id_proyecto}"
                ):
                    inicio_edit = st.date_input(
                        "Fecha de inicio",
                        value=proyecto.fecha_inicio or date.today(),
                        key=f"inicio_{proyecto.id_proyecto}",
                    )

                    termino_edit = st.date_input(
                        "Fecha de término",
                        value=proyecto.fecha_termino or date.today(),
                        key=f"termino_{proyecto.id_proyecto}",
                    )

                    presupuesto_edit = st.selectbox(
                        "Presupuesto",
                        options=presupuestos_ids,
                        index=(
                            presupuestos_ids.index(
                                proyecto.id_presupuesto
                            )
                            if proyecto.id_presupuesto in presupuestos_ids
                            else 0
                        ),
                        format_func=etiqueta_presupuesto,
                        key=f"presupuesto_{proyecto.id_proyecto}",
                    )

                    factura_edit = st.selectbox(
                        "Factura de venta",
                        options=facturas_ids,
                        index=(
                            facturas_ids.index(proyecto.nro_documento)
                            if proyecto.nro_documento in facturas_ids
                            else 0
                        ),
                        format_func=etiqueta_factura,
                        key=f"factura_{proyecto.id_proyecto}",
                    )

                    if presupuesto_edit is not None:
                        costo_edit = int(
                            presupuestos_por_id[presupuesto_edit].total
                        )
                        st.write(
                            f"**Costo total:** {formato_clp(costo_edit)}"
                        )
                    else:
                        costo_edit = st.number_input(
                            "Costo total estimado ($)",
                            min_value=0,
                            value=int(proyecto.costo_total),
                            step=10000,
                            key=f"costo_{proyecto.id_proyecto}",
                        )

                    guardar = st.form_submit_button(
                        "Guardar cambios"
                    )

                    if guardar:
                        if termino_edit < inicio_edit:
                            st.error(
                                "La fecha de término no puede "
                                "ser anterior al inicio."
                            )
                        elif costo_edit <= 0:
                            st.error("El costo total debe ser mayor que cero.")
                        else:
                            try:
                                with SessionLocal() as db:
                                    registro = db.get(
                                        Proyecto,
                                        proyecto.id_proyecto,
                                    )

                                    if registro:
                                        registro.fecha_inicio = inicio_edit
                                        registro.fecha_termino = termino_edit
                                        registro.id_presupuesto = presupuesto_edit
                                        registro.nro_documento = factura_edit
                                        registro.costo_total = costo_edit
                                        db.commit()

                                st.success("Proyecto actualizado.")
                                st.rerun()

                            except SQLAlchemyError:
                                st.error(
                                    "No fue posible actualizar el proyecto."
                                )

                confirmar = st.checkbox(
                    "Confirmar eliminación",
                    key=f"confirmar_eliminar_{proyecto.id_proyecto}",
                )

                if st.button(
                    "🗑️ Eliminar proyecto",
                    key=f"eliminar_proyecto_{proyecto.id_proyecto}",
                    disabled=not confirmar,
                ):
                    try:
                        with SessionLocal() as db:
                            registro = db.get(
                                Proyecto,
                                proyecto.id_proyecto,
                            )
                            if registro:
                                db.delete(registro)
                                db.commit()

                        st.success("Proyecto eliminado.")
                        st.rerun()

                    except SQLAlchemyError:
                        st.error(
                            "No fue posible eliminar el proyecto."
                        )


# ==========================================================
# PESTAÑA 2: PRESUPUESTOS
# ==========================================================

with tab_presupuesto:
    st.subheader("Crear presupuesto")

    with st.form("form_nuevo_presupuesto", clear_on_submit=True):
        total_mo = st.number_input(
            "Total mano de obra ($)",
            min_value=0,
            value=0,
            step=10000,
        )

        total_materiales = st.number_input(
            "Total materiales ($)",
            min_value=0,
            value=0,
            step=10000,
        )

        gastos_generales = st.number_input(
            "Gastos generales ($)",
            min_value=0,
            value=0,
            step=10000,
        )

        utilidades = st.number_input(
            "Utilidades ($)",
            min_value=0,
            value=0,
            step=10000,
        )

        calculo = calcular_presupuesto(
            total_mo,
            total_materiales,
            gastos_generales,
            utilidades,
        )

        st.divider()
        st.write(
            f"**Subtotal:** {formato_clp(calculo['subtotal'])}"
        )
        st.write(
            f"**Subtotal neto:** "
            f"{formato_clp(calculo['subtotal_neto'])}"
        )
        st.write(f"**IVA (19 %):** {formato_clp(calculo['iva'])}")
        st.subheader(f"Total: {formato_clp(calculo['total'])}")

        guardar_presupuesto = st.form_submit_button(
            "Guardar presupuesto",
            type="primary",
        )

        if guardar_presupuesto:
            if calculo["total"] <= 0:
                st.error("El presupuesto debe tener un total mayor que cero.")
            else:
                try:
                    with SessionLocal() as db:
                        presupuesto = Presupuesto(
                            total_mo=total_mo,
                            total_materiales=total_materiales,
                            subtotal=calculo["subtotal"],
                            gastos_generales=gastos_generales,
                            utilidades=utilidades,
                            subtotal_neto=calculo["subtotal_neto"],
                            iva=calculo["iva"],
                            total=calculo["total"],
                        )

                        db.add(presupuesto)
                        db.commit()

                    st.success("Presupuesto guardado correctamente.")
                    st.rerun()

                except SQLAlchemyError:
                    st.error("No fue posible guardar el presupuesto.")

    st.divider()
    st.subheader("Presupuestos registrados")

    if not presupuestos:
        st.info("Todavía no hay presupuestos registrados.")
    else:
        for presupuesto in presupuestos:
            with st.expander(
                f"Presupuesto #{presupuesto.id_presupuesto} — "
                f"{formato_clp(presupuesto.total)}"
            ):
                st.write(
                    f"**Mano de obra:** "
                    f"{formato_clp(presupuesto.total_mo)}"
                )
                st.write(
                    f"**Materiales:** "
                    f"{formato_clp(presupuesto.total_materiales)}"
                )
                st.write(
                    f"**Subtotal:** {formato_clp(presupuesto.subtotal)}"
                )
                st.write(
                    f"**Gastos generales:** "
                    f"{formato_clp(presupuesto.gastos_generales)}"
                )
                st.write(
                    f"**Utilidades:** {formato_clp(presupuesto.utilidades)}"
                )
                st.write(
                    f"**Subtotal neto:** "
                    f"{formato_clp(presupuesto.subtotal_neto)}"
                )
                st.write(f"**IVA:** {formato_clp(presupuesto.iva)}")
                st.write(f"**Total:** {formato_clp(presupuesto.total)}")


# ==========================================================
# PESTAÑA 3: FACTURACIÓN
# ==========================================================

with tab_facturacion:
    st.subheader("Facturas de venta y compra")

    tab_ventas, tab_compras = st.tabs(
        ["📤 Facturas de venta", "📥 Facturas de compra"]
    )

    # ------------------------------------------------------
    # FACTURAS DE VENTA
    # ------------------------------------------------------

    with tab_ventas:
        st.markdown("#### Registrar factura de venta")

        if not clientes:
            st.warning(
                "Primero debes registrar clientes en la página "
                "Gestión de Clientes."
            )
        else:
            with st.form("form_factura_venta", clear_on_submit=True):
                nro_venta = st.number_input(
                    "Número de documento",
                    min_value=1,
                    step=1,
                    format="%d",
                )

                cliente_rut = st.selectbox(
                    "Cliente",
                    options=list(clientes_por_rut.keys()),
                    format_func=lambda rut: (
                        f"{clientes_por_rut[rut].razon_social} — {rut}"
                    ),
                )

                fecha_venta = st.date_input(
                    "Fecha de emisión",
                    value=date.today(),
                )

                neto_venta = st.number_input(
                    "Total neto ($)",
                    min_value=0,
                    value=0,
                    step=10000,
                )
                  
                estado_pago_venta = st.selectbox(
                    "Estado de pago",
                    options=["Pendiente", "Pagada"],
                    index=0,
                )


                iva_venta = calcular_iva(neto_venta)
                total_venta = Decimal(str(neto_venta)) + iva_venta

                st.write(f"**IVA (19 %):** {formato_clp(iva_venta)}")
                st.subheader(f"Total: {formato_clp(total_venta)}")

                guardar_venta = st.form_submit_button(
                    "Registrar factura de venta",
                    type="primary",
                )

                if guardar_venta:
                    if nro_venta <= 0 or neto_venta <= 0:
                        st.error(
                            "El número de documento y el neto "
                            "deben ser mayores que cero."
                        )
                    else:
                        try:
                            with SessionLocal() as db:
                                if db.get(
                                    FacturaVenta,
                                    int(nro_venta),
                                ):
                                    st.error(
                                        "Ya existe una factura de venta "
                                        "con ese número."
                                    )
                                else:
                                    factura = FacturaVenta(
                                        nro_documento=int(nro_venta),
                                        rut_cliente=cliente_rut,
                                        fecha_emision=fecha_venta,
                                        total_neto=neto_venta,
                                        iva=iva_venta,
                                        total=total_venta,
                                        estado_pago=estado_pago_venta,
                                    )
                                    db.add(factura)
                                    db.commit()

                                    st.success(
                                        "Factura de venta registrada."
                                    )
                                    st.rerun()

                        except SQLAlchemyError:
                            st.error(
                                "No fue posible registrar la factura de venta."
                            )

        st.divider()
        st.markdown("#### Facturas de venta registradas")

        if not facturas_venta:
            st.info("Todavía no hay facturas de venta.")
        else:
            for factura in facturas_venta:
                cliente = clientes_por_rut.get(factura.rut_cliente)
                nombre_cliente = (
                    cliente.razon_social if cliente else factura.rut_cliente
                )

                with st.expander(
                    f"Factura #{factura.nro_documento} — "
                    f"{nombre_cliente} — {formato_clp(factura.total)}"
                ):
                    st.write(f"**RUT cliente:** {factura.rut_cliente}")
                    st.write(f"**Fecha:** {factura.fecha_emision}")
                    st.write(f"**Neto:** {formato_clp(factura.total_neto)}")
                    st.write(f"**IVA:** {formato_clp(factura.iva)}")
                    st.write(f"**Total:** {formato_clp(factura.total)}")
                    st.write(f"**Estado de pago:** {factura.estado_pago}")

    # ------------------------------------------------------
    # FACTURAS DE COMPRA
    # ------------------------------------------------------

    with tab_compras:
        st.markdown("#### Registrar factura de compra")

        if not proveedores:
            st.warning(
                "Primero debes registrar proveedores en la página "
                "Gestión de Proveedores."
            )
        else:
            presupuestos_compra_ids = [None] + [
                p.id_presupuesto for p in presupuestos
            ]

            with st.form("form_factura_compra", clear_on_submit=True):
                nro_compra = st.number_input(
                    "Número de documento",
                    min_value=1,
                    step=1,
                    format="%d",
                    key="nro_factura_compra",
                )

                proveedor_rut = st.selectbox(
                    "Proveedor",
                    options=list(proveedores_por_rut.keys()),
                    format_func=lambda rut: (
                        f"{proveedores_por_rut[rut].razon_social} — {rut}"
                    ),
                )

                fecha_compra = st.date_input(
                    "Fecha de compra",
                    value=date.today(),
                )

                neto_compra = st.number_input(
                    "Total neto ($)",
                    min_value=0,
                    value=0,
                    step=10000,
                )
                
                estado_pago_compra = st.selectbox(
                    "Estado de pago",
                    options=["Pendiente", "Pagada"],
                    index=0,
                )

                iva_compra = calcular_iva(neto_compra)
                total_compra = Decimal(str(neto_compra)) + iva_compra

                presupuesto_compra = st.selectbox(
                    "Presupuesto asociado (opcional)",
                    options=presupuestos_compra_ids,
                    format_func=etiqueta_presupuesto,
                    key="presupuesto_factura_compra",
                )

                st.write(f"**IVA (19 %):** {formato_clp(iva_compra)}")
                st.subheader(f"Total: {formato_clp(total_compra)}")

                guardar_compra = st.form_submit_button(
                    "Registrar factura de compra",
                    type="primary",
                )

                if guardar_compra:
                    if nro_compra <= 0 or neto_compra <= 0:
                        st.error(
                            "El número de documento y el neto "
                            "deben ser mayores que cero."
                        )
                    else:
                        try:
                            with SessionLocal() as db:
                                if db.get(
                                    FacturaCompra,
                                    int(nro_compra),
                                ):
                                    st.error(
                                        "Ya existe una factura de compra "
                                        "con ese número."
                                    )
                                else:
                                    proveedor_obj = proveedores_por_rut[
                                        proveedor_rut
                                    ]

                                    factura = FacturaCompra(
                                        nro_documento=int(nro_compra),
                                        proveedor=proveedor_obj.razon_social,
                                        rut_proveedor=proveedor_rut,
                                        fecha_compra=fecha_compra,
                                        total_neto=neto_compra,
                                        iva=iva_compra,
                                        total=total_compra,
                                        id_presupuesto=presupuesto_compra,
                                        estado_pago=estado_pago_compra,
                                    )

                                    db.add(factura)
                                    db.commit()

                                    st.success(
                                        "Factura de compra registrada."
                                    )
                                    st.rerun()

                        except SQLAlchemyError:
                            st.error(
                                "No fue posible registrar la factura de compra."
                            )

        st.divider()
        st.markdown("#### Facturas de compra registradas")

        if not facturas_compra:
            st.info("Todavía no hay facturas de compra.")
        else:
            for factura in facturas_compra:
                proveedor = proveedores_por_rut.get(
                    factura.rut_proveedor
                )
                nombre_proveedor = (
                    proveedor.razon_social
                    if proveedor
                    else factura.proveedor or factura.rut_proveedor
                )

                with st.expander(
                    f"Factura #{factura.nro_documento} — "
                    f"{nombre_proveedor} — {formato_clp(factura.total)}"
                ):
                    st.write(f"**RUT proveedor:** {factura.rut_proveedor}")
                    st.write(f"**Fecha:** {factura.fecha_compra}")
                    st.write(f"**Neto:** {formato_clp(factura.total_neto)}")
                    st.write(f"**IVA:** {formato_clp(factura.iva)}")
                    st.write(f"**Total:** {formato_clp(factura.total)}")
                    st.write(f"**Estado de pago:** {factura.estado_pago}")
                    st.write(
                        "**Presupuesto asociado:** "
                        + (
                            f"#{factura.id_presupuesto}"
                            if factura.id_presupuesto
                            else "Sin asociar"
                        )
                    )