# Imagen base: Python 3.12 en su versión liviana (slim)
FROM python:3.12-slim

# Carpeta de trabajo dentro del contenedor
WORKDIR /code

# Evita archivos .pyc y hace que los logs salgan en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 1) Copiar SOLO requirements.txt e instalar dependencias
#    (Docker guarda esta capa en caché: si requirements no cambia, no reinstala)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Copiar el resto del proyecto
COPY . .

# Puerto que usa Streamlit
EXPOSE 8501

# Comando que se ejecuta al iniciar el contenedor.
# address=0.0.0.0 es obligatorio en Docker: sin eso la app no es visible desde tu navegador
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]