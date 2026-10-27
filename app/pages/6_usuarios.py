import streamlit as st

from core.auth.service import actualizar_usuario, listar_usuarios

yo = st.session_state.get("usuario")
if not yo or yo["rol"] != "admin":
    st.error("No tienes permisos para ver esta página.")
    st.stop()

st.title("👥 Administración de usuarios")

def cambiar_estado(id_usuario: int, nuevo_estado: bool):
    ok, mensaje = actualizar_usuario(id_usuario, activo=nuevo_estado)
    st.toast(mensaje, icon="✅" if ok else "⚠️")

def cambiar_rol(id_usuario: int, clave: str):
    ok, mensaje = actualizar_usuario(id_usuario, rol=st.session_state[clave])
    st.toast(mensaje, icon="✅" if ok else "⚠️")

usuarios = listar_usuarios()
pendientes = [u for u in usuarios if not u["activo"]]

col1, col2 = st.columns(2)
col1.metric("Usuarios registrados", len(usuarios))
col2.metric("Pendientes de activación", len(pendientes))

st.divider()

encabezados = st.columns([3, 4, 2, 2, 2])
for col, texto in zip(encabezados, ["Nombre", "Correo", "Rol", "Estado", "Acción"]):
    col.markdown(f"**{texto}**")

for u in usuarios:
    es_yo = u["id"] == yo["id"]
    c1, c2, c3, c4, c5 = st.columns([3, 4, 2, 2, 2])

    c1.write(u["nombre"] + (" (tú)" if es_yo else ""))
    c2.write(u["correo"])

    clave_rol = f"rol_{u['id']}"
    c3.selectbox(
        "Rol", ["tecnico", "admin"],
        index=0 if u["rol"] == "tecnico" else 1,
        key=clave_rol, label_visibility="collapsed", disabled=es_yo,
        on_change=cambiar_rol, args=(u["id"], clave_rol),
    )

    c4.write("🟢 Activo" if u["activo"] else "🟠 Pendiente")

    c5.button(
        "Desactivar" if u["activo"] else "Activar",
        key=f"estado_{u['id']}", disabled=es_yo,
        on_click=cambiar_estado, args=(u["id"], not u["activo"]),
    )