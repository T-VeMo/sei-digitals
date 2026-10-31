import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from prophet import Prophet
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

HORIZONTE_DIAS = 30


@st.cache_resource
def get_engine():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("No se encontró la variable DATABASE_URL en el entorno.")
    return create_engine(database_url, pool_pre_ping=True)


def cargar_historial():
    query = text("""
        SELECT fecha_emision AS ds, total AS y
        FROM factura_venta
        ORDER BY fecha_emision ASC;
    """)
    with get_engine().connect() as connection:
        df = pd.read_sql_query(query, con=connection)

    if df.empty:
        raise ValueError("La tabla 'factura_venta' no contiene registros para entrenar el modelo.")

    df["ds"] = pd.to_datetime(df["ds"], errors="coerce")
    df["y"] = pd.to_numeric(df["y"], errors="coerce")
    df = df.dropna(subset=["ds", "y"])

    if len(df) < 5:
        raise ValueError(f"Se necesitan al menos 5 registros válidos para Prophet. Solo se encontraron {len(df)}.")

    return df


def entrenar_prophet(df):
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
    )
    model.fit(df)

    future = model.make_future_dataframe(periods=HORIZONTE_DIAS)
    forecast = model.predict(future)

    # Solo las fechas futuras (después del último dato real)
    ultima_fecha_real = df["ds"].max()
    forecast_futuro = forecast[forecast["ds"] > ultima_fecha_real].copy()

    return model, forecast, forecast_futuro


# --- INTERFAZ ---
st.title("Módulo de IA Predictiva")
st.markdown("Genera proyecciones financieras basadas en el historial de facturación de Supabase utilizando **Prophet**.")
st.divider()

if "forecast_futuro" not in st.session_state:
    st.session_state.forecast_futuro = None
if "model" not in st.session_state:
    st.session_state.model = None
if "forecast_completo" not in st.session_state:
    st.session_state.forecast_completo = None
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("🚀 Generar Predicción con IA", type="primary"):
    with st.spinner("Entrenando modelo Prophet y calculando proyección..."):
        try:
            df = cargar_historial()
            model, forecast, forecast_futuro = entrenar_prophet(df)

            st.session_state.model = model
            st.session_state.forecast_completo = forecast
            st.session_state.forecast_futuro = forecast_futuro

            st.success("¡Modelo entrenado y proyección generada con éxito!")
        except Exception as e:
            st.error(f"Ocurrió un error al procesar el modelo: {e}")

# Gráfico (se muestra si ya hay un forecast calculado)
if st.session_state.forecast_completo is not None:
    fig, ax = plt.subplots(figsize=(10, 5))
    st.session_state.model.plot(st.session_state.forecast_completo, ax=ax)
    ax.set_title("Pronóstico de Ventas — Prophet", fontsize=14)
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Monto / Total")
    st.pyplot(fig)
    plt.close(fig)

