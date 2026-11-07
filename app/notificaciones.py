import pandas as pd
import streamlit as st
from sqlalchemy import text

# Facturas pendientes de pago: compra (fecha_compra) y venta (fecha_emision)
QUERY_PENDIENTES = text("""
    SELECT 'Compra' AS tipo, nro_documento, fecha_compra AS fecha, total
    FROM factura_compra
    WHERE estado_pago = 'Pendiente'
    UNION ALL
    SELECT 'Venta' AS tipo, nro_documento, fecha_emision AS fecha, total
    FROM factura_venta
    WHERE estado_pago = 'Pendiente'
    ORDER BY fecha ASC;
""")


def obtener_pendientes(engine):
    with engine.connect() as conn:
        return pd.read_sql_query(QUERY_PENDIENTES, con=conn)


def mostrar_campanita(engine):
    df = obtener_pendientes(engine)
    cantidad = len(df)

    # Campana sola, o campana con punto rojo y el número de pendientes
    etiqueta = f"🔔{cantidad}" if cantidad else "🔔"

    # Columna angosta a la derecha para que la campana quede arriba a la derecha
    _, col = st.columns([0.80, 0.15])
    with col:
        with st.popover(etiqueta):
            st.markdown("**Facturas pendientes de pago**")
            if cantidad == 0:
                st.success("No tienes facturas pendientes.")
            else:
                tabla = df.rename(columns={
                    "tipo": "Tipo",
                    "nro_documento": "N° documento",
                    "fecha": "Fecha",
                    "total": "Total",
                })
                st.dataframe(tabla, hide_index=True, use_container_width=True)