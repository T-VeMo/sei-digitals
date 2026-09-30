import numpy as np
import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression

from utils import formato_clp


st.title("🔮 Módulo de IA Predictiva - Proyección de Ganancias (CLP)")
st.sidebar.image("app/static/logo.png", width=100)
st.write("Carga un Excel con las columnas `fecha` y `ganancias_clp`, o usa los datos de demostración.")

archivo = st.file_uploader("Historial de ganancias (Excel)", type=["xlsx", "xls"])

if archivo is None:
    generador = np.random.default_rng(42)
    fechas = pd.date_range(end=pd.Timestamp.today().normalize(), periods=1000, freq="D")
    tendencia = 500_000 + np.arange(1000) * 250
    ganancias = tendencia + generador.normal(0, 60_000, size=1000)
    historico = pd.DataFrame({"fecha": fechas, "ganancias_clp": ganancias})
    st.caption("Proyección basada en 1.000 registros diarios simulados.")
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

if len(historico) < 2:
    st.error("Se necesitan al menos dos registros válidos para entrenar el modelo.")
    st.stop()

historico["periodo"] = (historico["fecha"] - historico["fecha"].min()).dt.total_seconds() / 86400
variables = historico[["periodo"]]
objetivo = historico["ganancias_clp"]

modelo = LinearRegression()
modelo.fit(variables, objetivo)

frecuencia = pd.infer_freq(historico["fecha"])
if frecuencia is None:
    diferencias = historico["fecha"].sort_values().diff().dropna()
    paso = diferencias.median()
    frecuencia = "MS" if paso >= pd.Timedelta(days=27) else "D"

cantidad_periodos = 12 if frecuencia.startswith("M") else 30
fecha_futura = pd.date_range(
    start=historico["fecha"].max(),
    periods=cantidad_periodos + 1,
    freq=frecuencia,
)[1:]
periodo_futuro = (fecha_futura - historico["fecha"].min()).total_seconds() / 86400
predicciones = modelo.predict(pd.DataFrame({"periodo": periodo_futuro}))

grafico_historico = historico.set_index("fecha")["ganancias_clp"].rename("Histórico")
grafico_prediccion = pd.Series(predicciones, index=fecha_futura, name="Proyección")
grafico = pd.concat([grafico_historico, grafico_prediccion], axis=1)

st.subheader("Historial y proyección")
st.line_chart(grafico, y=["Histórico", "Proyección"])

unidad = "12 meses" if cantidad_periodos == 12 else "30 días"
total_proyectado = predicciones.sum()
st.metric(
    label=f"Ganancia total proyectada ({unidad})",
    value=f"{formato_clp(total_proyectado)} CLP",
)