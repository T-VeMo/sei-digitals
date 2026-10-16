import os
import pandas as pd
from prophet import Prophet
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def train_prophet_model():
    """
    Extrae los datos históricos de facturación desde Supabase y entrena Prophet,
    incluyendo validaciones para evitar pantallas en negro si faltan datos.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("No se encontró la variable DATABASE_URL en el entorno.")
    
    engine = create_engine(database_url)
    
    query = text("""
        SELECT fecha_emision AS ds, total AS y 
        FROM factura_venta 
        ORDER BY fecha_emision ASC;
    """)
    
    with engine.connect() as connection:
        df = pd.read_sql_query(query, con=connection)
    
    # Validar si la tabla devolvió registros
    if df.empty:
        raise ValueError("La tabla 'factura_venta' no contiene registros para entrenar el modelo.")
    
    # Limpieza de fechas y valores nulos
    df['ds'] = pd.to_datetime(df['ds'], errors='coerce')
    df['y'] = pd.to_numeric(df['y'], errors='coerce')
    df = df.dropna(subset=['ds', 'y'])
    
    if len(df) < 5:
        raise ValueError(f"Se necesitan al menos 5 registros válidos para Prophet. Solo se encontraron {len(df)}.")
    
    # Inicialización y ajuste del modelo Prophet
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False
    )
    model.fit(df)
    
    # Generar proyecciones futuras
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    
    return model, forecast