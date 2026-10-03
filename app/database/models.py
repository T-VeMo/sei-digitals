from datetime import date

from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# BASE
class Base(DeclarativeBase):
    pass

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
    facturas_venta: Mapped[list["FacturaVenta"]] = relationship(
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

    proyectos: Mapped[list["Proyecto"]] = relationship(
        back_populates="presupuesto"
    )

# TABLA FACTURA_VENTA
class FacturaVenta(Base):
    __tablename__ = "factura_venta"

    nro_documento: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    rut_cliente: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("cliente.rut"),
        nullable=False
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

    # Relaciones
    cliente: Mapped["Cliente"] = relationship(
        back_populates="facturas_venta"
    )

    proyectos: Mapped[list["Proyecto"]] = relationship(
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

    costo_total: Mapped[float] = mapped_column(
        Numeric(12),
        nullable=False
    )

    id_presupuesto: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("presupuesto.id_presupuesto"),
        nullable=True
    )

    nro_documento: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("factura_venta.nro_documento"),
        nullable=True
    )

    fecha_inicio: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    fecha_termino: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    # Relaciones
    presupuesto: Mapped["Presupuesto | None"] = relationship(
        back_populates="proyectos"
    )

    factura_venta: Mapped["FacturaVenta | None"] = relationship(
        back_populates="proyectos"
    )