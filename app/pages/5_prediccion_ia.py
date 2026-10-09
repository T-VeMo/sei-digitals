import numpy as np
import pandas as pd
import streamlit as st
from prophet import Prophet

from utils import formato_clp


st.title("🔮 Módulo de IA Predictiva - Proyección de Ganancias (CLP)")
st.sidebar.image("app/static/logo.png", width=100)
st.write("Carga un Excel con las columnas `fecha` y `ganancias_clp`, o usa los datos de demostración.")



archivo = st.file_uploader("Historial de ganancias (Excel)", type=["xlsx", "xls"])

if archivo is None:
    generador = np.random.default_rng(42)
    fechas = pd.date_range(end=pd.Timestamp.today().normalize(), periods=100, freq="D")
    tendencia = 500_000 + np.arange(100) * 250
    ganancias = tendencia + generador.normal(0, 60_000, size=100)
    historico = pd.DataFrame({"fecha": fechas, "ganancias_clp": ganancias})
    st.caption("Entrenamiento con 100 registros diarios ficticios.")
else:
    try:
        historico = pd.read_excel(archivo)
    except Exception as error:
        st.error(f"No se pudo leer el archivo Excel: {error}")
        st.stop()

    historico.columns = historico.columns.astype(str).str.strip().str.lower()
    columnas_requeridas = {"fecha", "ganancias_clp"}
    if not columnas_requeridas.issubset(historico.columns):
        st.error("El Excel debe incluir las columnas `fecha` y `ganancias_clp`.")
        st.stop()

    historico = historico[["fecha", "ganancias_clp"]].copy()
    historico["fecha"] = pd.to_datetime(historico["fecha"], errors="coerce")
    historico["ganancias_clp"] = pd.to_numeric(historico["ganancias_clp"], errors="coerce")
    historico = historico.dropna().sort_values("fecha").reset_index(drop=True)

if historico["fecha"].nunique() < 2:
    st.error("Se necesitan al menos dos fechas distintas para entrenar el modelo.")
    st.stop()

st.caption(f"Registros válidos para entrenar: {len(historico)}.")

datos_modelo = historico.rename(columns={"fecha": "ds", "ganancias_clp": "y"})
modelo = Prophet()
modelo.fit(datos_modelo[["ds", "y"]])

fechas_unicas = historico["fecha"].drop_duplicates().sort_values()
frecuencia = pd.infer_freq(fechas_unicas) if len(fechas_unicas) >= 3 else None
if frecuencia is None:
    diferencias = fechas_unicas.diff().dropna()
    paso = diferencias.median()
    frecuencia = "MS" if paso >= pd.Timedelta(days=27) else "D"

fecha_limite = historico["fecha"].max() + pd.DateOffset(months=1)
periodos_en_un_mes = pd.date_range(
    start=historico["fecha"].max(),
    end=fecha_limite,
    freq=frecuencia,
    inclusive="right",
)
cantidad_periodos = max(len(periodos_en_un_mes), 1)
fechas_futuras = modelo.make_future_dataframe(
    periods=cantidad_periodos,
    freq=frecuencia,
    include_history=False,
)
prediccion = modelo.predict(fechas_futuras)
fecha_futura = prediccion["ds"]
predicciones = prediccion["yhat"].to_numpy()

grafico_historico = historico.set_index("fecha")["ganancias_clp"].rename("Histórico")
grafico_prediccion = pd.Series(predicciones, index=fecha_futura, name="Proyección")
grafico = pd.concat([grafico_historico, grafico_prediccion], axis=1)

st.subheader("Historial y proyección")
st.line_chart(grafico, y=["Histórico", "Proyección"])

total_proyectado = predicciones.sum()
st.metric(
    label="Ganancia total proyectada para el próximo mes",
    value=f"{formato_clp(total_proyectado)} CLP",
)