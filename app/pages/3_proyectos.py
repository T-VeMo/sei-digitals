import streamlit as st

from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from data.database.connection import SessionLocal
from data.database.models import (
    Cliente,
    Proveedor,
    Presupuesto,
    FacturaVenta,
    FacturaCompra,
    Proyecto,
)
from utils import formato_clp

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

proyectos_por_id = {
    p.id_proyecto: p for p in proyectos
}


def etiqueta_proyecto(id_proyecto):
    proyecto = proyectos_por_id[id_proyecto]
    cliente = clientes_por_rut.get(proyecto.rut_cliente)

    nombre_cliente = (
        cliente.razon_social
        if cliente
        else "Cliente no encontrado"
    )

    return (
    f"{proyecto.nombre} — Proyecto #{id_proyecto} "
    f"— {nombre_cliente}"
    )

def etiqueta_presupuesto(id_presupuesto):
    if id_presupuesto is None:
        return "Sin asociar"

    presupuesto = presupuestos_por_id.get(id_presupuesto)

    if presupuesto is None:
        return f"Presupuesto #{id_presupuesto}"

    return (
        f"Presupuesto #{id_presupuesto} — "
        f"{formato_clp(presupuesto.total)}"
    )
# ==========================================================
# PESTAÑA 1: PROYECTOS
# ==========================================================
with tab_proyectos:
    st.subheader("Registrar proyecto")

    st.info(
        "Cada proyecto debe estar asociado a un cliente. "
        "Los presupuestos y la factura de venta se vincularán "
        "al proyecto desde sus respectivas pestañas."
    )

    if not clientes:
        st.warning(
            "Debes registrar al menos un cliente en la pestaña "
            "Gestión de Clientes antes de registrar un proyecto."
        )
    else:
        with st.form("form_nuevo_proyecto", clear_on_submit=False):
            cliente_rut = st.selectbox(
                "Cliente",
                options=list(clientes_por_rut.keys()),
                format_func=lambda rut: (
                    f"{clientes_por_rut[rut].razon_social} — {rut}"
                ),
            )
            
            nombre_proyecto = st.text_input(
                "Nombre del proyecto",
                max_chars=150,
                key="nombre_proyecto"
            )

            descripcion_proyecto = st.text_area(
                "Descripción del proyecto",
                placeholder="Describe el trabajo que se realizará y su alcance...",
                key="descripcion_proyecto"
            )

            fecha_inicio = st.date_input(
                "Fecha de inicio",
                value=date.today(),
            )

            fecha_termino = st.date_input(
                "Fecha estimada de término",
                value=date.today(),
            )

            costo_total = st.number_input(
                "Costo total estimado ($)",
                min_value=0,
                value=0,
                step=10000,
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
                elif costo_total <= 0:
                    st.error(
                        "El costo total debe ser mayor que cero."
                    )
                elif not nombre_proyecto.strip():
                    st.error(
                        "El nombre del proyecto no puede estar vacío."
                    )
                elif not descripcion_proyecto.strip():
                    st.error(
                        "La descripción del proyecto no puede estar vacía."
                    )
                else:
                    try:
                        with SessionLocal() as db:
                            nuevo_proyecto = Proyecto(
                                nombre=nombre_proyecto.strip(),
                                descripcion=descripcion_proyecto.strip(),
                                rut_cliente=cliente_rut,
                                costo_total=costo_total,
                                fecha_inicio=fecha_inicio,
                                fecha_termino=fecha_termino,
                            )

                            db.add(nuevo_proyecto)
                            db.commit()

                        st.success(
                            "Proyecto registrado correctamente."
                        )
                        st.rerun()

                    except SQLAlchemyError as error:
                        st.error(
                            "No fue posible registrar el proyecto."
                        )
                        st.exception(error)

    
    st.divider()
    st.subheader("Proyectos registrados")

    if not proyectos:
        st.info("Todavía no hay proyectos registrados.")
    else:
        for proyecto in proyectos:
            cliente = clientes_por_rut.get(proyecto.rut_cliente)

            presupuestos_proyecto = [
                p for p in presupuestos
                if p.id_proyecto == proyecto.id_proyecto
            ]

            factura_venta = next(
                (
                    f for f in facturas_venta
                    if f.id_proyecto == proyecto.id_proyecto
                ),
                None,
            )

            with st.expander(
                f"Proyecto #{proyecto.id_proyecto} — "
                f"{proyecto.nombre} — "
                f"{formato_clp(proyecto.costo_total)}"
            ):
                st.write(
                    f"**Nombre del proyecto:** {proyecto.nombre}"
                )
                st.write(
                    f"**Descripción:** {proyecto.descripcion}"
                )
                st.write(
                    f"**Cliente:** "
                    f"{cliente.razon_social if cliente else 'No encontrado'}"
                )
                st.write(
                    f"**RUT del cliente:** {proyecto.rut_cliente}"
                )
                st.write(
                    f"**Fecha de inicio:** "
                    f"{proyecto.fecha_inicio or 'No registrada'}"
                )
                st.write(
                    f"**Fecha de término:** "
                    f"{proyecto.fecha_termino or 'No registrada'}"
                )

                st.write("**Presupuestos asociados:**")
                if presupuestos_proyecto:
                    for presupuesto in presupuestos_proyecto:
                        st.markdown(
                            f"**Presupuesto #{presupuesto.id_presupuesto}**"
                        )
                        st.write(
                            f"Total: {formato_clp(presupuesto.total)}"
                        )

                        # Buscar las facturas de compra del presupuesto.
                        compras_presupuesto = [
                            f for f in facturas_compra
                            if f.id_presupuesto == presupuesto.id_presupuesto
                        ]
                        if compras_presupuesto:
                            st.markdown("Facturas de compra:")

                            for compra in compras_presupuesto:
                                proveedor = proveedores_por_rut.get(
                                    compra.rut_proveedor
                                )

                                nombre_proveedor = (
                                    proveedor.razon_social
                                    if proveedor
                                    else compra.proveedor or compra.rut_proveedor
                                )

                                st.write(
                                    f"- Factura #{compra.nro_documento} - "
                                    f"{nombre_proveedor} - "
                                    f"{formato_clp(compra.total)}"
                                )
                        else:
                            st.caption("Sin facturas de compra asociadas.")

                        st.divider()

                else:
                    st.write("Sin presupuestos asociados.")

                # ------------------------------------------
                # EDITAR PROYECTO
                # ------------------------------------------
                st.markdown("#### Editar proyecto")

                with st.form(
                    f"editar_proyecto_{proyecto.id_proyecto}"
                ):
                    nombre_edit = st.text_input(
                        "Nombre del proyecto",
                        value=proyecto.nombre,
                        max_chars=150,
                        key=f"nombre_edit_{proyecto.id_proyecto}"
                    )

                    descripcion_edit = st.text_area(
                        "Descripción del proyecto",
                        value=proyecto.descripcion,
                        key=f"descripcion_edit_{proyecto.id_proyecto}"
                    )
                    
                    inicio_edit = st.date_input(
                        "Fecha de inicio",
                        value=proyecto.fecha_inicio or date.today(),
                        key=f"inicio_{proyecto.id_proyecto}",
                    )

                    termino_edit = st.date_input(
                        "Fecha estimada de término",
                        value=proyecto.fecha_termino or date.today(),
                        key=f"termino_{proyecto.id_proyecto}",
                    )

                    costo_edit = st.number_input(
                        "Costo total estimado ($)",
                        min_value=0,
                        value=int(proyecto.costo_total or 0),
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
                                "ser anterior a la fecha de inicio."
                            )
                        elif costo_edit <= 0:
                            st.error(
                                "El costo total debe ser mayor que cero."
                            )
                        elif not nombre_edit.strip():
                            st.error(
                                "El nombre del proyecto no puede estar vacío."
                            )
                        elif not descripcion_edit.strip():
                            st.error(
                                "La descripción del proyecto no puede estar vacía."
                            )
                        else:
                            try:
                                with SessionLocal() as db:
                                    registro = db.get(
                                        Proyecto,
                                        proyecto.id_proyecto,
                                    )

                                    if registro is None:
                                        st.error(
                                            "El proyecto ya no existe."
                                        )
                                    else:
                                        registro.fecha_inicio = inicio_edit
                                        registro.fecha_termino = termino_edit
                                        registro.costo_total = costo_edit
                                        db.commit()

                                        st.success(
                                            "Proyecto actualizado."
                                        )
                                        st.rerun()

                            except SQLAlchemyError as error:
                                st.error(
                                    "No fue posible actualizar el proyecto."
                                )
                                st.exception(error)

                # ------------------------------------------
                # ELIMINAR PROYECTO
                # ------------------------------------------
                st.divider()
                st.markdown("#### Eliminar proyecto")

                modo_eliminacion = st.radio(
                    "¿Qué deseas eliminar?",
                    options=[
                        "Solo el proyecto",
                        "Proyecto y registros relacionados",
                    ],
                    key=f"modo_eliminar_{proyecto.id_proyecto}",
                    help=(
                        "La segunda opción elimina el proyecto, sus "
                        "presupuestos, la factura de venta asociada "
                        "y las facturas de compra vinculadas a esos "
                        "presupuestos."
                    ),
                )

                confirmar = st.checkbox(
                    "Confirmo que deseo eliminar los registros seleccionados",
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

                            if registro is None:
                                st.error("El proyecto ya no existe.")
                            else:
                                presupuestos_db = db.scalars(
                                    select(Presupuesto).where(
                                        Presupuesto.id_proyecto
                                        == registro.id_proyecto
                                    )
                                ).all()

                                ids_presupuestos = [
                                    p.id_presupuesto
                                    for p in presupuestos_db
                                ]

                                factura_db = db.scalars(
                                    select(FacturaVenta).where(
                                        FacturaVenta.id_proyecto
                                        == registro.id_proyecto
                                    )
                                ).all()

                                if (
                                    modo_eliminacion == "Solo el proyecto"
                                    and (
                                        presupuestos_db or factura_db
                                    )
                                ):
                                    st.error(
                                        "No se puede eliminar solamente "
                                        "el proyecto porque tiene "
                                        "presupuestos o una factura "
                                        "asociada. Selecciona la opción "
                                        "para eliminar también los "
                                        "registros relacionados."
                                    )

                                else:
                                    if (
                                        modo_eliminacion
                                        == "Proyecto y registros relacionados"
                                    ):
                                        # Eliminar primero las facturas
                                        # de compra asociadas a los
                                        # presupuestos del proyecto.
                                        if ids_presupuestos:
                                            compras_db = db.scalars(
                                                select(FacturaCompra).where(
                                                    FacturaCompra.id_presupuesto
                                                    .in_(ids_presupuestos)
                                                )
                                            ).all()

                                            for compra in compras_db:
                                                db.delete(compra)

                                        # Eliminar las facturas de venta.
                                        for factura in factura_db:
                                            db.delete(factura)

                                        # Eliminar los presupuestos.
                                        for presupuesto in presupuestos_db:
                                            db.delete(presupuesto)

                                    # Finalmente, eliminar el proyecto.
                                    db.delete(registro)
                                    db.commit()

                                    st.success(
                                        "Proyecto y registros seleccionados "
                                        "eliminados correctamente."
                                        if modo_eliminacion
                                        == "Proyecto y registros relacionados"
                                        else "Proyecto eliminado."
                                    )
                                    st.rerun()

                    except SQLAlchemyError as error:
                        st.error(
                            "No fue posible completar la eliminación. "
                            "Verifica las relaciones entre los registros."
                        )
                        st.exception(error)
                        
        st.divider()
        st.subheader("Facturas de compra sin proyecto asociado")

        compras_independientes = [
            factura for factura in facturas_compra
            if factura.id_presupuesto is None
        ]

        if compras_independientes:
            for factura in compras_independientes:
                proveedor = proveedores_por_rut.get(
                    factura.rut_proveedor
                )

                nombre_proveedor = (
                    proveedor.razon_social
                    if proveedor
                    else factura.proveedor or factura.rut_proveedor
                )

                st.markdown(
                    f"**Factura #{factura.nro_documento}** — "
                    f"{nombre_proveedor}"
                )

                st.write(f"**RUT:** {factura.rut_proveedor}")
                st.write(f"**Fecha:** {factura.fecha_compra}")
                st.write(f"**Total neto:** {formato_clp(factura.total_neto)}")
                st.write(f"**IVA:** {formato_clp(factura.iva)}")
                st.write(f"**Total:** {formato_clp(factura.total)}")
                st.write(f"**Estado de pago:** {factura.estado_pago}")

                st.divider()
# ==========================================================
# PESTAÑA 2: PRESUPUESTOS
# ==========================================================
with tab_presupuesto:
    st.subheader("Crear presupuesto")

    if not proyectos:
        st.warning(
            "Debes registrar al menos un proyecto antes de crear "
            "un presupuesto."
        )
    else:
        with st.form("form_nuevo_presupuesto", clear_on_submit=False):
            proyecto_id = st.selectbox(
            "Proyecto asociado",
            options=list(proyectos_por_id.keys()),
            format_func=etiqueta_proyecto,
            )

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
            st.write(
                f"**IVA (19 %):** {formato_clp(calculo['iva'])}"
            )
            st.subheader(
                f"Total: {formato_clp(calculo['total'])}"
            )

            guardar_presupuesto = st.form_submit_button(
                "Guardar presupuesto",
                type="primary",
            )

            if guardar_presupuesto:
                if calculo["total"] <= 0:
                    st.error(
                        "El presupuesto debe tener un total mayor que cero."
                    )
                else:
                    try:
                        with SessionLocal() as db:
                            presupuesto = Presupuesto(
                                id_proyecto=proyecto_id,
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

                    except SQLAlchemyError as error:
                        st.error("No fue posible guardar el presupuesto.")
                        st.exception(error)

    st.divider()
    st.subheader("Presupuestos registrados")

    if not presupuestos:
        st.info("Todavía no hay presupuestos registrados.")
    else:
        for presupuesto in presupuestos:
            proyecto = proyectos_por_id.get(presupuesto.id_proyecto)

            with st.expander(
                f"Presupuesto #{presupuesto.id_presupuesto} — "
                f"{formato_clp(presupuesto.total)}"
            ):
                st.write(
                    f"**Proyecto asociado:** "
                    f"#{presupuesto.id_proyecto} - {proyecto.nombre if proyecto else 'No encontrado'}"
                    
                )

                if proyecto:
                    cliente = clientes_por_rut.get(proyecto.rut_cliente)
                    if cliente:
                        st.write(
                            f"**Cliente:** {cliente.razon_social}"
                        )

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
                    f"**Utilidades:** "
                    f"{formato_clp(presupuesto.utilidades)}"
                )
                st.write(
                    f"**Subtotal neto:** "
                    f"{formato_clp(presupuesto.subtotal_neto)}"
                )
                st.write(f"**IVA:** {formato_clp(presupuesto.iva)}")
                st.write(f"**Total:** {formato_clp(presupuesto.total)}")

                st.divider()

                confirmar_eliminacion = st.checkbox(
                    "Confirmo que deseo eliminar este presupuesto",
                    key=f"confirmar_presupuesto_{presupuesto.id_presupuesto}",
                )

                if st.button(
                    "🗑️ Eliminar presupuesto",
                    key=f"eliminar_presupuesto_{presupuesto.id_presupuesto}",
                    disabled=not confirmar_eliminacion,
                ):
                    try:
                        with SessionLocal() as db:
                            registro = db.get(
                                Presupuesto,
                                presupuesto.id_presupuesto,
                            )

                            if registro is None:
                                st.error("El presupuesto ya no existe.")
                            else:
                                # Las facturas de compra pueden existir
                                # sin un presupuesto asociado.
                                compras_asociadas = db.scalars(
                                    select(FacturaCompra).where(
                                        FacturaCompra.id_presupuesto
                                        == registro.id_presupuesto
                                    )
                                ).all()

                                for compra in compras_asociadas:
                                    compra.id_presupuesto = None

                                db.delete(registro)
                                db.commit()

                                st.success("Presupuesto eliminado.")
                                st.rerun()

                    except SQLAlchemyError as error:
                        st.error(
                            "No fue posible eliminar el presupuesto."
                        )
                        st.exception(error)

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

        # Un proyecto solo puede tener una factura de venta.
        proyectos_facturados = {
            factura.id_proyecto
            for factura in facturas_venta
        }

        proyectos_disponibles_venta = [
            proyecto
            for proyecto in proyectos
            if proyecto.id_proyecto not in proyectos_facturados
        ]

        if not proyectos:
            st.warning(
                "Primero debes registrar un proyecto en la "
                "pestaña Gestión de Proyectos."
            )
        elif not proyectos_disponibles_venta:
            st.info(
                "Todos los proyectos registrados ya tienen "
                "una factura de venta asociada."
            )
        else:
            with st.form("form_factura_venta", clear_on_submit=False):
                nro_venta = st.number_input(
                    "Número de documento",
                    min_value=1,
                    step=1,
                    format="%d",
                )

                proyecto_venta_id = st.selectbox(
                    "Proyecto asociado",
                    options=[
                        p.id_proyecto
                        for p in proyectos_disponibles_venta
                    ],
                    format_func=etiqueta_proyecto,
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

                st.write(
                    f"**IVA (19 %):** {formato_clp(iva_venta)}"
                )
                st.subheader(
                    f"Total: {formato_clp(total_venta)}"
                )

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
                                factura_existente = db.get(
                                    FacturaVenta,
                                    int(nro_venta),
                                )

                                proyecto_db = db.get(
                                    Proyecto,
                                    proyecto_venta_id,
                                )

                                factura_proyecto = db.scalars(
                                    select(FacturaVenta).where(
                                        FacturaVenta.id_proyecto
                                        == proyecto_venta_id
                                    )
                                ).first()

                                if factura_existente:
                                    st.error(
                                        "Ya existe una factura de venta "
                                        "con ese número."
                                    )
                                elif proyecto_db is None:
                                    st.error(
                                        "El proyecto seleccionado "
                                        "ya no existe."
                                    )
                                elif factura_proyecto:
                                    st.error(
                                        "El proyecto ya tiene una "
                                        "factura de venta asociada."
                                    )
                                else:
                                    factura = FacturaVenta(
                                        nro_documento=int(nro_venta),
                                        id_proyecto=proyecto_venta_id,
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

                        except SQLAlchemyError as error:
                            st.error(
                                "No fue posible registrar la factura "
                                "de venta. Verifica que el número de "
                                "documento y el proyecto sean válidos."
                            )
                            st.exception(error)

        st.divider()
        st.markdown("#### Facturas de venta registradas")

        if not facturas_venta:
            st.info("Todavía no hay facturas de venta.")
        else:
            for factura in facturas_venta:
                proyecto = proyectos_por_id.get(
                    factura.id_proyecto
                )

                cliente = (
                    clientes_por_rut.get(proyecto.rut_cliente)
                    if proyecto
                    else None
                )

                nombre_cliente = (
                    cliente.razon_social
                    if cliente
                    else "Cliente no encontrado"
                )

                with st.expander(
                    f"Factura #{factura.nro_documento} — "
                    f"{nombre_cliente} — "
                    f"{formato_clp(factura.total)}"
                ):
                    st.write(
                        f"**Proyecto asociado:** "
                        f"#{factura.id_proyecto} - {proyecto.nombre if proyecto else 'No encontrado'}"
                    )
                    st.write(
                        f"**Cliente:** {nombre_cliente}"
                    )

                    if proyecto:
                        st.write(
                            f"**RUT cliente:** {proyecto.rut_cliente}"
                        )

                    st.write(
                        f"**Fecha:** {factura.fecha_emision}"
                    )
                    st.write(
                        f"**Neto:** "
                        f"{formato_clp(factura.total_neto)}"
                    )
                    st.write(
                        f"**IVA:** {formato_clp(factura.iva)}"
                    )
                    st.write(
                        f"**Total:** {formato_clp(factura.total)}"
                    )
                    st.write(
                        f"**Estado de pago:** {factura.estado_pago}"
                    )

                    st.divider()

                    confirmar_eliminacion = st.checkbox(
                        "Confirmo que deseo eliminar esta factura",
                        key=f"confirmar_venta_{factura.nro_documento}",
                    )

                    if st.button(
                        "🗑️ Eliminar factura de venta",
                        key=f"eliminar_venta_{factura.nro_documento}",
                        disabled=not confirmar_eliminacion,
                    ):
                        try:
                            with SessionLocal() as db:
                                registro = db.get(
                                    FacturaVenta,
                                    factura.nro_documento,
                                )

                                if registro is None:
                                    st.error(
                                        "La factura ya no existe."
                                    )
                                else:
                                    # El proyecto se conserva.
                                    # Solo se elimina su factura.
                                    db.delete(registro)
                                    db.commit()

                                    st.success(
                                        "Factura de venta eliminada. "
                                        "El proyecto sigue registrado."
                                    )
                                    st.rerun()

                        except SQLAlchemyError as error:
                            st.error(
                                "No fue posible eliminar la factura "
                                "de venta."
                            )
                            st.exception(error)


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

            with st.form("form_factura_compra", clear_on_submit=False):
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
                    st.divider()
                    
                    confirmar_eliminacion = st.checkbox(
                        "Confirmo que deseo eliminar esta factura",
                        key=f"confirmar_compra_{factura.nro_documento}",
                    )
                    
                    if st.button(
                        "🗑️ Eliminar factura de compra",
                        key=f"eliminar_compra_{factura.nro_documento}",
                        disabled=not confirmar_eliminacion,
                    ):
                        try:
                            with SessionLocal() as db:
                                registro = db.get(
                                    FacturaCompra,
                                    factura.nro_documento,
                                )
                    
                                if registro:
                                    db.delete(registro)
                                    db.commit()
                    
                            st.success("Factura de compra eliminada.")
                            st.rerun()
                    
                        except SQLAlchemyError:
                            st.error(
                                "No fue posible eliminar la factura de compra."
                            )