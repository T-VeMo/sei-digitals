import streamlit as st
from datetime import date
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from data.database.connection import SessionLocal
from data.database.models import RendicionGastos


st.title("Rendición de Gastos")
st.write("Registro y administración de los gastos generales de la empresa.")

st.subheader("Registrar nueva rendición")

meses = {
    "Enero": 1,
    "Febrero": 2,
    "Marzo": 3,
    "Abril": 4,
    "Mayo": 5,
    "Junio": 6,
    "Julio": 7,
    "Agosto": 8,
    "Septiembre": 9,
    "Octubre": 10,
    "Noviembre": 11,
    "Diciembre": 12
}

with st.form("form_rendicion_gastos"):

    col1, col2 = st.columns(2)

    with col1:
        mes_seleccionado = st.selectbox(
            "Mes",
            options=list(meses.keys())
        )

    with col2:
        anio = st.number_input(
            "Año",
            min_value=2000,
            max_value=2100,
            value=date.today().year,
            step=1
        )

    monto_total = st.number_input(
        "Monto total de gastos ($)",
        min_value=1,
        value=1,
        step=1000,
        format="%d"
    )

    guardar = st.form_submit_button(
        "Registrar rendición",
        use_container_width=True
    )

    if guardar:
        mes = meses[mes_seleccionado]

        with SessionLocal() as db:
            existente = db.scalar(
                select(RendicionGastos).where(
                    RendicionGastos.mes == mes,
                    RendicionGastos.anio == anio
                )
            )

            if existente:
                st.error(
                    f"Ya existe una rendición para {mes_seleccionado} de {anio}."
                )
            else:
                nueva_rendicion = RendicionGastos(
                    mes=mes,
                    anio=anio,
                    monto_total=monto_total
                )

                try:
                    db.add(nueva_rendicion)
                    db.commit()
                    st.success("Rendición registrada correctamente.")
                    st.rerun()

                except IntegrityError:
                    db.rollback()
                    st.error(
                        "Ya existe una rendición para ese período."
                    )
                    
                    st.divider()

st.subheader("Historial de rendiciones")

with SessionLocal() as db:
    rendiciones = db.scalars(
        select(RendicionGastos).order_by(
            RendicionGastos.anio.desc(),
            RendicionGastos.mes.asc()
        )
    ).all()

    if not rendiciones:
        st.info("Todavía no existen rendiciones registradas.")

    else:
        nombres_meses = {v: k for k, v in meses.items()}

        anios = sorted(
            {rendicion.anio for rendicion in rendiciones},
            reverse=True
        )

        for anio_historial in anios:
            st.markdown(f"### {anio_historial}")

            rendiciones_anio = [
                r for r in rendiciones
                if r.anio == anio_historial
            ]

            total_anual = sum(
                r.monto_total for r in rendiciones_anio
            )

            st.metric(
                "Total de gastos del año",
                f"${total_anual:,.0f}".replace(",", ".")
            )

            datos = [
                {
                    "Mes": nombres_meses[r.mes],
                    "Monto total": f"${r.monto_total:,.0f}".replace(",", ".")
                }
                for r in rendiciones_anio
            ]

            st.dataframe(
                datos,
                use_container_width=True,
                hide_index=True
            )