import streamlit as st
from database.connection import get_connection

st.title("Prueba de PostgreSQL")

try:
    conn = get_connection()
    st.success("Conexión exitosa a PostgreSQL")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)

    tablas = cursor.fetchall()

    st.subheader("Tablas de la base de datos")

    for tabla in tablas:
        st.write(tabla[0])

    cursor.close()
    conn.close()

except Exception as e:
    st.error(f"Error: {e}")