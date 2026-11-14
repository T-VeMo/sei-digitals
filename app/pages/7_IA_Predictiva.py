import os
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from prophet import Prophet
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from openai import OpenAI
from datetime import date
import streamlit as st

load_dotenv()

HORIZONTE_DIAS = 30

SYSTEM_BASE = """Eres el asistente de negocio de SEI Digitals, plataforma de FL Servicios Eléctricos Integrales SpA.
Respondes en español chileno, claro y breve. Los montos son en pesos chilenos (CLP).
Para preguntas del pronóstico usa la sección DATOS: los totales ya vienen calculados, NO sumes tú.
# AQUÍ VA (NUEVO): la siguiente línea
En DATOS está el contenido de las tablas tal cual. Cuando pidan facturas u otros registros, muéstralos con el nombre de la tabla, número de documento, fecha y monto, sin inventar nada.
Si lo que piden no está en los datos, dilo tal cual.
Si la pregunta no tiene que ver con el negocio, responde en una frase y vuelve al tema."""

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

TABLAS_IA = ["cliente", "proveedor", "proyecto", "presupuesto", "factura_venta", "factura_compra"]

@st.cache_data(ttl=60)
def leer_tablas(limite=100):
    bloques = []
    with get_engine().connect() as conn:
        for tabla in TABLAS_IA:
            try:
                df = pd.read_sql_query(text(f"SELECT * FROM {tabla} LIMIT :n"), con=conn, params={"n": limite})
                bloques.append(f"TABLA {tabla} ({len(df)} filas):\n" + df.to_csv(index=False))
            except Exception as e:
                bloques.append(f"TABLA {tabla}: no se pudo leer ({e})")
    return "\n".join(bloques)

def construir_contexto(futuro, historial):
    total = futuro["yhat"].sum()
    promedio = futuro["yhat"].mean()
    fila_max = futuro.loc[futuro["yhat"].idxmax()]
    fila_min = futuro.loc[futuro["yhat"].idxmin()]

    diario = "\n".join(
        f"{r.ds:%Y-%m-%d}: ${r.yhat:,.0f} (rango ${r.yhat_lower:,.0f} a ${r.yhat_upper:,.0f})"
        for r in futuro.itertuples()
    )
    mensual = historial.set_index("ds")["y"].resample("MS").sum().tail(6)
    hist = "\n".join(f"{f:%Y-%m}: ${v:,.0f}" for f, v in mensual.items())

    return f"""Pronóstico Prophet para los próximos {HORIZONTE_DIAS} días:
- Total proyectado: ${total:,.0f}
- Promedio diario: ${promedio:,.0f}
- Día más alto: {fila_max.ds:%Y-%m-%d} con ${fila_max.yhat:,.0f}
- Día más bajo: {fila_min.ds:%Y-%m-%d} con ${fila_min.yhat:,.0f}

Detalle día a día:
{diario}

Facturación real de los últimos meses:
{hist}

CONTENIDO DE LA BASE DE DATOS (tal cual):
{leer_tablas()}"""

def responder_con_openrouter(prompt, contexto, historial):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "Falta OPENROUTER_API_KEY en el .env."

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    mensajes = [{"role": "system", "content": f"{SYSTEM_BASE}\n\nDATOS:\n{contexto}"}]
    mensajes += historial
    mensajes.append({"role": "user", "content": prompt})

    try:
        resp = client.chat.completions.create(
            model="nvidia/nemotron-3.5-super-vl:free",
            messages=mensajes,
            max_tokens=2000,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"No pude consultar al modelo: {e}"

def responder_con_ia(prompt):
    futuro = st.session_state.forecast_futuro
    if futuro is None or futuro.empty:
        return "Primero genera la predicción con el botón superior para que pueda analizar los datos."

    contexto = construir_contexto(futuro, st.session_state.df_hist)
    historial = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[-10:]
        if m["role"] in ("user", "assistant")
    ]
    return responder_con_openrouter(prompt, contexto, historial)

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

            st.session_state.df_hist = df
            st.session_state.model = model
            st.session_state.forecast_completo = forecast
            st.session_state.forecast_futuro = forecast_futuro

            st.success("¡Modelo entrenado y proyección generada con éxito!")
        except Exception as e:
            st.error(f"Ocurrió un error al procesar el modelo: {e}")

if st.session_state.forecast_completo is not None:
    fig, ax = plt.subplots(figsize=(10, 5))
    st.session_state.model.plot(st.session_state.forecast_completo, ax=ax)
    ax.set_title("Pronóstico de Ventas — Prophet", fontsize=14)
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Monto / Total")
    st.pyplot(fig)
    plt.close(fig)

st.divider()
st.subheader("Asistente IA - Consultas sobre el Pronostico")
st.markdown("Preguntale al asistente sobre las tendencias o el flujo de ventas basado en el pronóstico generado por Prophet.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ej: ¿Cómo se ve el flujo de ventas en los próximos 5 días?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analizando el pronóstico..."):
            respuesta = responder_con_ia(prompt)
        st.markdown(respuesta)

    st.session_state.messages.append({"role": "assistant", "content": respuesta})