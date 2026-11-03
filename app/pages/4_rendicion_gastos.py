import streamlit as st
from sqlalchemy import select
from data.database.connection import SessionLocal
from data.database.models import RendicionGastos


st.title("Rendición de Gastos")
st.write("Registro y administración de los gastos generales de la empresa.")