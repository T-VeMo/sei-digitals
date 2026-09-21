import streamlit as st
from utils import telefono_valido

st.title("👥 Gestión de Clientes")
st.sidebar.image("app/static/logo.png", width=100)

#ESTO GUARDA LA INFORMACIÓN DE LOS CLIENTES EN LA SESIÓN
if "clientes" not in st.session_state:
    st.session_state.clientes = [
        {"nombre": "Constructora Andes SpA", 
         "email": "contacto@andes.cl", 
         "telefono": "+56912345678"},
        {"nombre": "Inmobiliaria Costa Azul",
          "email": "contacto@costaazul.cl",
          "telefono": "+56987654321"},
    ]

st.subheader("Registrar nuevo cliente")
#FORMULARIO PARA REGISTRAR NUEVO CLIENTE
with st.form("form_nuevo_cliente", clear_on_submit=True):
    nombre = st.text_input("Nombre del cliente")
    email = st.text_input("Correo electrónico")

    st.write("Teléfono")
    col_prefijo, col_numero = st.columns([1, 4])
    with col_prefijo:
        st.text_input("prefijo", value="+569", disabled=True, label_visibility="collapsed")
    with col_numero:
        telefono = st.text_input("Número de teléfono", placeholder="123456789", max_chars=8, label_visibility="collapsed")

    enviado= st.form_submit_button("Registrar cliente")

    if enviado:
        if nombre and email and telefono_valido(telefono):
            telefono_completo = f"+569{telefono}"
            st.session_state.clientes.append({"nombre": nombre, "email": email, "telefono": telefono_completo})
            st.success(f"Cliente {nombre} registrado exitosamente.")
        else:
            st.error("Por favor, complete todos los campos obligatorios.")

st.divider()
st.subheader("Clientes registrados")

if len(st.session_state.clientes) == 0:
    st.info("Aún no hay clientes nuevos")
else:
    for i, cliente in enumerate(st.session_state.clientes):

        with st.expander(f" {cliente['nombre']} - {cliente['email']} - {cliente['telefono']}"):
            with st.form(f"form_editar_{i}"):
                nombre_edit = st.text_input("Nombre del cliente", value=cliente["nombre"])
                email_edit = st.text_input("Correo electronico", value=cliente["email"])

                telefono_sin_prefijo = cliente["telefono"].replace("+569", "")

                col_prefijo, col_numero = st.columns([1, 4])
                with col_prefijo:
                    st.text_input("prefijo", value="+569", disabled=True, label_visibility="collapsed", key=f"prefijo_edit_{i}")
                with col_numero:
                    telefono_edit = st.text_input("Número de teléfono", value=telefono_sin_prefijo, max_chars=8, label_visibility="collapsed", key=f"numero_edit_{i}")

                guardar = st.form_submit_button("Guardar cambios")

                if guardar:
                    if nombre_edit and email_edit and telefono_valido(str(telefono_edit)):
                        telefono_completo_edit = f"+569{telefono_edit}"
                        st.session_state.clientes[i] ["nombre"] = nombre_edit
                        st.session_state.clientes[i] ["email"] = email_edit
                        st.session_state.clientes[i] ["telefono"] = telefono_completo_edit
                        st.success(f"Cliente {nombre_edit} actualizado exitosamente.")
                    else:
                        st.error("Por favor, complete todos los campos obligatorios.")

            if st.button("🗑️ Eliminar Cliente", key=f"eliminar_{i}"):
                st.session_state.clientes.pop(i)
                st.rerun()