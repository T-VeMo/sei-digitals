import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from data.database.connection import SessionLocal
from data.database.models import Sesion, Usuario
from app.utils import correo_valido

DURACION_SESION = timedelta(days=7)

def _hashear(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def _verificar(password: str, hash_guardado: str) -> bool:
    return bcrypt.checkpw(password.encode(), hash_guardado.encode())

def crear_usuario(nombre: str, correo: str, password: str):
    correo = correo.strip().lower()
    if not nombre.strip() or not correo or not password:
        return False, "Complete todos los campos."
    if not correo_valido(correo):
        return False, "Ingrese un correo válido."
    if len(password) < 8 or password.isalpha() or password.isdigit():
        return False, "La contraseña debe tener al menos 8 caracteres, con letras y números."

    try:
        with SessionLocal() as db:
            db.add(Usuario(nombre=nombre.strip(), correo=correo, password_hash=_hashear(password)))
            db.commit()
        return True, "Cuenta creada. Un administrador debe activarla antes de que puedas ingresar."
    except IntegrityError:
        return False, "Ya existe una cuenta con ese correo."
    except SQLAlchemyError:
        return False, "No se pudo crear la cuenta. Intente más tarde."

def autenticar(correo: str, password: str):
    correo = correo.strip().lower()
    try:
        with SessionLocal() as db:
            u = db.scalars(select(Usuario).where(Usuario.correo == correo)).first()
            if not u or not u.password_hash or not _verificar(password, u.password_hash):
                return None, "Correo o contraseña incorrectos."
            if not u.activo:
                return None, "Tu cuenta aún no ha sido activada por un administrador."
            return {"id": u.id_usuario, "nombre": u.nombre, "correo": u.correo, "rol": u.rol}, ""
    except SQLAlchemyError:
        return None, "Error de conexión con la base de datos."


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def crear_sesion(id_usuario: int):
    token = secrets.token_urlsafe(32)
    ahora = datetime.now(timezone.utc)
    try:
        with SessionLocal() as db:
            db.execute(delete(Sesion).where(Sesion.expira < ahora))
            db.add(Sesion(token_hash=_hash_token(token), id_usuario=id_usuario,
                          expira=ahora + DURACION_SESION))
            db.commit()
        return token
    except SQLAlchemyError:
        return None

def usuario_desde_token(token):
    if not token:
        return None
    ahora = datetime.now(timezone.utc)
    try:
        with SessionLocal() as db:
            u = db.scalars(
                select(Usuario)
                .join(Sesion, Sesion.id_usuario == Usuario.id_usuario)
                .where(Sesion.token_hash == _hash_token(token), Sesion.expira > ahora)
            ).first()
            if not u or not u.activo:
                return None
            return {"id": u.id_usuario, "nombre": u.nombre, "correo": u.correo, "rol": u.rol}
    except SQLAlchemyError:
        return None

def cerrar_sesion_token(token):
    if not token:
        return
    try:
        with SessionLocal() as db:
            db.execute(delete(Sesion).where(Sesion.token_hash == _hash_token(token)))
            db.commit()
    except SQLAlchemyError:
        pass


# ============================================================
# ADMINISTRACIÓN DE USUARIOS
# ============================================================

def listar_usuarios():
    with SessionLocal() as db:
        filas = db.scalars(select(Usuario).order_by(Usuario.activo, Usuario.nombre)).all()
        return [
            {"id": u.id_usuario, "nombre": u.nombre, "correo": u.correo,
             "rol": u.rol, "activo": u.activo}
            for u in filas
        ]


def actualizar_usuario(id_usuario: int, activo=None, rol=None):
    """Cambia el estado y/o el rol de un usuario. Devuelve (ok, mensaje)."""
    if rol is not None and rol not in ("admin", "tecnico"):
        return False, "Rol no válido."
    try:
        with SessionLocal() as db:
            u = db.get(Usuario, id_usuario)
            if not u:
                return False, "El usuario no existe."

            pierde_admin = u.activo and u.rol == "admin" and (
                activo is False or (rol is not None and rol != "admin")
            )
            if pierde_admin:
                otros = db.scalar(
                    select(func.count()).select_from(Usuario).where(
                        Usuario.rol == "admin", Usuario.activo.is_(True),
                        Usuario.id_usuario != id_usuario)
                )
                if not otros:
                    return False, "Debe quedar al menos un administrador activo."

            if activo is not None:
                u.activo = activo
                if not activo:  # al desactivar, se cierran sus sesiones
                    db.execute(delete(Sesion).where(Sesion.id_usuario == id_usuario))
            if rol is not None:
                u.rol = rol
            db.commit()
            return True, f"Usuario {u.nombre} actualizado."
    except SQLAlchemyError:
        return False, "No se pudo actualizar el usuario."