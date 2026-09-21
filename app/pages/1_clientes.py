import streamlit as st

st.title("👥 Gestión de Clientes")
st.sidebar.image("app/static/logo.png", width=100)

#ESTO GUARDA LA INFORMACIÓN DE LOS CLIENTES EN LA SESIÓN
if "clientes" not in st.session_state:
    st.session_state.clientes = [
        {"nombre": "Constructora Andes SpA", 
         "email": "contacto@andes.cl", 
         "telefono": "+56 9 1234 5678"},
        {"nombre": "Inmobiliaria Costa Azul",
          "email": "contacto@costaazul.cl",
          "telefono": "+56 9 8765 4321"},
    ]

st.subheader("Registrar nuevo cliente")
#FORMULARIO PARA REGISTRAR NUEVO CLIENTE
with st.form("form_nuevo_cliente", clear_on_submit=True):
    nombre = st.text_input("Nombre del cliente")
    email = st.text_input("Correo electrónico")
    telefono = st.text_input("Teléfono")

    enviado= st.form_submit_button("Registrar cliente")

    if enviado:
        if nombre and email and telefono:
            st.session_state.clientes.append({"nombre": nombre, "email": email, "telefono": telefono})
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
                telefono_edit = st.text_input("Teléfono", value=cliente["telefono"])

                guardar = st.form_submit_button("Guardar cambios")

                if guardar:
                    if nombre_edit and email_edit and telefono_edit:
                        st.session_state.clientes[i] ["nombre"] = nombre_edit
                        st.session_state.clientes[i] ["email"] = email_edit
                        st.session_state.clientes[i] ["telefono"] = telefono_edit
                        st.success(f"Cliente {nombre_edit} actualizado exitosamente.")
                    else:
                        st.error("Por favor, complete todos los campos obligatorios.")

            if st.button("🗑️ Eliminar proyecto", key=f"eliminar_{i}"):
                st.session_state.clientes.pop(i)
                st.rerun()