import streamlit as st 

st.title("📦 Gestión de Proveedores")
st.sidebar.image("app/static/logo.png", width=100)

if "proveedores" not in st.session_state:
    st.session_state.proveedores = [
        {"nombre": "Proveedor A", 
         "email": "contacto@proveedorA.cl", 
         "telefono": 56911112222, 
         "categoria": "Eléctrico"},
        {"nombre": "Proveedor B", 
         "email": "contacto@proveedorB.cl", 
         "telefono": 56933334444, 
         "categoria": "Plomería"},
    ]

st.subheader("Registrar nuevo proveedor")

with st.form("form_nuevo_proveedor", clear_on_submit=True):
    nombre = st.text_input("Nombre del proveedor") 
    email = st.text_input("Email del proveedor")
    telefono = st.number_input("Teléfono del proveedor", min_value=0)
    categoria = st.text_input("Categoría del proveedor")

    enviado = st.form_submit_button("Registrar proveedor")

    if enviado:
        if nombre and email and telefono and categoria:
            st.session_state.proveedores.append({"nombre": nombre, "email": email, "telefono": telefono, "categoria": categoria})
            st.success(f"Proveedor {nombre} registrado exitosamente.")
        else:
            st.error("Por favor, complete todos los campos obligatorios.")

st.divider()
st.subheader("Proveedores registrados")

if len(st.session_state.proveedores) == 0:
    st.info("Aún no hay proveedores registrados")
else:
    for i, proveedor in enumerate(st.session_state.proveedores):

        with st.expander(f"{proveedor["nombre"]} - {proveedor["categoria"]}"):
            with st.form(f"form_editar_{i}"):
                nombre_edit =st.text_input("Nombre del proveedor", value=proveedor["nombre"])
                email_edit =st.text_input("Correo electronico", value=proveedor["email"])
                telefono_edit =st.number_input("Teléfono", min_value=0, value=proveedor["telefono"])
                Categoria_edit =st.text_input("Categoría", value=proveedor["categoria"])

                guardar = st.form_submit_button("Guardar cambios")

                if guardar:
                    if nombre_edit and email_edit:
                        st.session_state.proveedores[i] ["nombre"] = nombre_edit
                        st.session_state.proveedores[i] ["email"] = email_edit
                        st.session_state.proveedores[i] ["telefono"] = telefono_edit
                        st.session_state.proveedores[i] ["categoria"] = Categoria_edit
                        st.success(f"Proveedor {nombre_edit} actualizado exitosamente.")
                    else:
                        st.error("Por favor, complete todos los campos obligatorios.")

            if st.button("🗑️ Eliminar proveedor", key=f"eliminar_{i}"):
                st.session_state.proveedores.pop(i)
                st.rerun()