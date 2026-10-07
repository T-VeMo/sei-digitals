import streamlit as st
from sqlalchemy import inspect, text
from data.database.connection import engine

st.title("Prueba de conexión a PostgreSQL")


try:

    # PRUEBA DE CONEXIÓN
    with engine.connect() as connection:

        resultado = connection.execute(
            text("SELECT version();")
        )

        version = resultado.fetchone()[0]

        st.success("Conexión exitosa a PostgreSQL")

        st.subheader("Versión de PostgreSQL")

        st.code(version)

    # OBTENER TABLAS
    inspector = inspect(engine)

    tablas = inspector.get_table_names()

    st.subheader("Tablas encontradas")

    if tablas:

        for tabla in tablas:
            st.write(f"✓ {tabla}")

    else:

        st.warning("No se encontraron tablas.")


except Exception as e:

    st.error("No fue posible conectarse a PostgreSQL")

    st.exception(e)