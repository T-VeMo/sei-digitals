from datetime import date, datetime

from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Boolean,
    DateTime,
    UniqueConstraint,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# BASE
class Base(DeclarativeBase):
    pass

#TABLA USUARIO
class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    correo: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    rol: Mapped[str] = mapped_column(String(20), nullable=False, default="tecnico", server_default="tecnico")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")


# TABLA SESION
class Sesion (Base):
    __tablename__ = "sesion"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    id_usuario: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), nullable=False
    )
    expira: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


# TABLA CLIENTE
class Cliente(Base):
    __tablename__ = "cliente"

    rut: Mapped[str] = mapped_column(
        String(12),
        primary_key=True
    )

    razon_social: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    rubro: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    correo: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    telefono: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    # Relaciones
    proyectos: Mapped[list["Proyecto"]] = relationship(
    back_populates="cliente"
)

# TABLA PROVEEDOR
class Proveedor(Base):
    __tablename__ = "proveedor"

    rut: Mapped[str] = mapped_column(
        String(12),
        primary_key=True
    )

    razon_social: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    rubro: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    correo: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    telefono: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    # Relaciones
    facturas_compra: Mapped[list["FacturaCompra"]] = relationship(
        back_populates="proveedor_rel"
    )

# TABLA PRESUPUESTO
class Presupuesto(Base):
    __tablename__ = "presupuesto"

    id_presupuesto: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    id_proyecto: Mapped[int] = mapped_column(
    Integer,
    ForeignKey("proyecto.id_proyecto"),
    nullable=False
    )

    total_mo: Mapped[float] = mapped_column(
        Numeric(12),
        nullable=False
    )

    total_materiales: Mapped[float] = mapped_column(
        Numeric(12),
        nullable=False
    )

    subtotal: Mapped[float] = mapped_column(
        Numeric(12),
        nullable=False
    )

    gastos_generales: Mapped[float] = mapped_column(
        Numeric(12),
        nullable=False
    )

    utilidades: Mapped[float] = mapped_column(
        Numeric(12),
        nullable=False
    )

    subtotal_neto: Mapped[float] = mapped_column(
        Numeric(12),
        nullable=False
    )

    iva: Mapped[float] = mapped_column(
        Numeric(12),
        nullable=False
    )

    total: Mapped[float] = mapped_column(
        Numeric(12),
        nullable=False
    )

    # Relaciones
    facturas_compra: Mapped[list["FacturaCompra"]] = relationship(
        back_populates="presupuesto"
    )

    proyecto: Mapped["Proyecto"] = relationship(
    back_populates="presupuestos"
)

# TABLA FACTURA_VENTA
class FacturaVenta(Base):
    __tablename__ = "factura_venta"
        
    __table_args__ = (
        UniqueConstraint(
            "id_proyecto",
            name="uq_factura_venta_proyecto"
        ),
    )

    nro_documento: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    fecha_emision: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    total_neto: Mapped[float] = mapped_column(
        Numeric(12),
        nullable=False
    )

    iva: Mapped[float] = mapped_column(
        Numeric(12),
        nullable=False
    )

    total: Mapped[float] = mapped_column(
        Numeric(12),
        nullable=False
    )
    
    estado_pago: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="Pendiente",
        server_default="Pendiente",
    )

    # Relaciones
    id_proyecto: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("proyecto.id_proyecto"),
        nullable=False
    )

    proyecto: Mapped["Proyecto"] = relationship(
        back_populates="factura_venta"
    )

# TABLA FACTURA_COMPRA
class FacturaCompra(Base):
    __tablename__ = "factura_compra"

    nro_documento: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    proveedor: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    rut_proveedor: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("proveedor.rut"),
        nullable=False
    )

    fecha_compra: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    total_neto: Mapped[float] = mapped_column(
        Numeric(12),
        nullable=False
    )

    iva: Mapped[float] = mapped_column(
        Numeric(12),
        nullable=False
    )

    total: Mapped[float] = mapped_column(
        Numeric(12),
        nullable=False
    )

    id_presupuesto: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("presupuesto.id_presupuesto"),
        nullable=True
    )
    
    estado_pago: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="Pendiente",
        server_default="Pendiente",
    )

    # Relaciones
    proveedor_rel: Mapped["Proveedor"] = relationship(
        back_populates="facturas_compra"
    )

    presupuesto: Mapped["Presupuesto | None"] = relationship(
        back_populates="facturas_compra"
    )


# TABLA PROYECTO
class Proyecto(Base):
    __tablename__ = "proyecto"

    id_proyecto: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)

    rut_cliente: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("cliente.rut"),
        nullable=False
    )

    costo_total: Mapped[float] = mapped_column(
        Numeric(12),
        nullable=False
    )

    fecha_inicio: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    fecha_termino: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    cliente: Mapped["Cliente"] = relationship(
        back_populates="proyectos"
    )

    presupuestos: Mapped[list["Presupuesto"]] = relationship(
        back_populates="proyecto"
    )

    factura_venta: Mapped["FacturaVenta | None"] = relationship(
        back_populates="proyecto",
        uselist=False
    )