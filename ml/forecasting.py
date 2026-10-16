import os
import pandas as pd
from prophet import Prophet
from dotenv import load_dotenv

load_dotenv()

def train_prophet_model():
    """
    Extrae los datos históricos de facturación desde Supabase pasando la URI directamente 
    a pandas y entrena el modelo de series temporales con Meta Prophet.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("No se encontró la variable DATABASE_URL en el entorno.")
    
    # Consulta SQL como cadena de texto plana
    query = """
        SELECT fecha_emision AS ds, total AS y 
        FROM factura_venta 
        ORDER BY fecha_emision ASC;
    """
    
    # Pasar directamente el string de la URI de conexión evita conflictos con SQLAlchemy 2.0
    df = pd.read_sql(query, con=database_url)
    
    # Validación y limpieza de formato para Prophet
    df['ds'] = pd.to_datetime(df['ds'])
    df = df.dropna(subset=['ds', 'y'])
    
    # Inicialización y ajuste del modelo predictivo
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False
    )
    model.fit(df)
    
    # Generación de proyecciones a 30 días futuros
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    
    return model, forecast