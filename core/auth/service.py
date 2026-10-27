import bcrypt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from data.database.connection import SessionLocal
from data.database.models import Usuario
from app.utils import correo_valido

def _hashear(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def _verificar(password: str, hash_guardado: str) -> bool:
    return bcrypt.checkpw(password.encode(), hash_guardado.encode())

def crear_usuario(nombre: str, correo: str, password: str):
    correo = correo.strip().lower()
    if not nombre.strip() or not correo or not password:
        return False, "Complete todos los campos."
    if not correo_valido(correo):
        return False, "ingrese un correo valido."
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
        return False, "No se pudo crear la cuenta. Intente mas tarde"

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