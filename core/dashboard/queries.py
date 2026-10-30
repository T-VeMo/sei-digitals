from sqlalchemy import func, select

from data.database.connection import SessionLocal
from data.database.models import  (
    Cliente, FacturaCompra, FacturaVenta, Proveedor, Proyecto
)

import pandas as pd

def _a_float(valor):
    """Numeric de Postgres llega como Decimal; Plotly y st.metric prefieren float."""
    return float(valor or 0)

def obtener_kpis():
    with SessionLocal() as db:  
        ingresos = db.scalar(select(func.sum(FacturaVenta.total)))
        costos = db.scalar(select(func.sum(FacturaCompra.total)))
        total_clientes = db.scalar(select(func.count(Cliente.rut)))
        total_proyectos = db.scalar(select(func.count(Proyecto.id_proyecto)))

    ingresos = _a_float(ingresos)
    costos = _a_float(costos)
    return {
        "ingresos": ingresos,
        "costos": costos,
        "ganancia": ingresos - costos,
        "clientes": total_clientes or 0,
        "proyectos": total_proyectos or 0,
    }

def ventas_por_cliente(limite=5):
    consulta = (
        select(Cliente.razon_social, func.sum(FacturaVenta.total).label("ventas"))
        .join(Proyecto, Proyecto.rut_cliente == Cliente.rut)
        .join(FacturaVenta,FacturaVenta.id_proyecto == Proyecto.id_proyecto)
        .group_by(Cliente.razon_social)
        .order_by(func.sum(FacturaVenta.total).desc())
        .limit(limite)
    )
    with SessionLocal() as db:
        filas = db.execute(consulta).all()
    df = pd.DataFrame(filas, columns = ["cliente", "ventas"])
    df["ventas"] = df["ventas"].astype(float)
    return df

def compras_por_proveedor(limite=5):
    consulta = (
        select(Proveedor.razon_social, func.count(FacturaCompra.nro_documento).label("transacciones"))
        .join(FacturaCompra, FacturaCompra.rut_proveedor == Proveedor.rut)
        .group_by(Proveedor.razon_social)
        .order_by(func.count(FacturaCompra.nro_documento).desc())
        .limit(limite)
    )
    with SessionLocal() as db:
        filas = db.execute(consulta).all()
    return pd.DataFrame(filas, columns=["proveedor", "transacciones"])


def facturas_por_estado():
    consulta = select(FacturaVenta.estado_pago, func.count()).group_by(FacturaVenta.estado_pago)
    with SessionLocal() as db:
        filas = db.execute(consulta).all()
    return pd.DataFrame(filas, columns=["estado", "cantidad"])