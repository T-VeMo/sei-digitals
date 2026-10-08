from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from data.database.connection import SessionLocal
from data.database.models import Cliente

def _a_dict(cliente):
    return {
        "rut": cliente.rut,
        "razon_social": cliente.razon_social,
        "rubro": cliente.rubro,
        "correo": cliente.correo,
        "telefono": cliente.telefono
    }

def listar_clientes():
    with SessionLocal() as db:
        clientes = db.scalars(select(Cliente).order_by(Cliente.razon_social)).all()
        return [_a_dict(c) for c in clientes]

def crear_cliente(rut, razon_social, correo, telefono, rubro=None):
    with SessionLocal() as db:
        try:
            db.add(Cliente(rut=rut, razon_social=razon_social, correo=correo, telefono=telefono, rubro=rubro))
            db.commit()
            return True, "Cliente creado exitosamente"
        except Exception as e:
            db.rollback()
            return False, "Ya existe un cliente con ese RUT"

def actualizar_cliente(rut, razon_social, correo, telefono, rubro=None):
    with SessionLocal() as db:
        cliente = db.get(Cliente, rut)
        if cliente is None:
            return False, "El cliente no existe"
        cliente.razon_social = razon_social
        cliente.rubro = rubro
        cliente.correo = correo
        cliente.telefono = telefono
        db.commit()
        return True, "Cliente actualizado exitosamente"

def eliminar_cliente(rut):
    with SessionLocal() as db:
        cliente = db.get(Cliente, rut)
        if cliente is None:
            return False, "El cliente no existe"
        try:
            db.delete(cliente)
            db.commit()
            return True, "Cliente eliminado" 
        except IntegrityError:
            db.rollback()
            return False, "No se puede eliminar el cliente porque tiene facturas asociadas"