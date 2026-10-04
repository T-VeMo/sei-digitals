--============================================================
--BASE DE DATOS: SEI DIGITALS
--============================================================

--------------------------------------------------------------
--TABLA: CLIENTE
--------------------------------------------------------------

CREATE TABLE cliente (
    rut VARCHAR(12) PRIMARY KEY,
    razon_social VARCHAR(150) NOT NULL,
    rubro VARCHAR(100),
    correo VARCHAR(150),
    telefono VARCHAR(20)
);


--------------------------------------------------------------
--TABLA: PROVEEDOR
--------------------------------------------------------------

CREATE TABLE proveedor (
    rut VARCHAR(12) PRIMARY KEY,
    razon_social VARCHAR(150) NOT NULL,
    rubro VARCHAR(100),
    correo VARCHAR(150),
    telefono VARCHAR(20)
);


--------------------------------------------------------------
--TABLA: PRESUPUESTO
--------------------------------------------------------------

CREATE TABLE presupuesto (
    id_presupuesto INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    total_mo NUMERIC(12) NOT NULL,
    total_materiales NUMERIC(12) NOT NULL,
    subtotal NUMERIC(12) NOT NULL,
    gastos_generales NUMERIC(12) NOT NULL,
    utilidades NUMERIC(12) NOT NULL,
    subtotal_neto NUMERIC(12) NOT NULL,
    iva NUMERIC(12) NOT NULL,
    total NUMERIC(12) NOT NULL
);


--------------------------------------------------------------
--TABLA: FACTURA_VENTA
--------------------------------------------------------------

CREATE TABLE factura_venta (
    nro_documento INTEGER PRIMARY KEY,
    rut_cliente VARCHAR(12) NOT NULL,
    fecha_emision DATE NOT NULL,
    total_neto NUMERIC(12) NOT NULL,
    iva NUMERIC(12) NOT NULL,
    total NUMERIC(12) NOT NULL,

    CONSTRAINT fk_factura_venta_cliente
        FOREIGN KEY (rut_cliente)
        REFERENCES cliente(rut)
);


--------------------------------------------------------------
--TABLA: FACTURA_COMPRA
--------------------------------------------------------------

CREATE TABLE factura_compra (
    nro_documento INTEGER PRIMARY KEY,
    proveedor VARCHAR(150),
    rut_proveedor VARCHAR(12) NOT NULL,
    fecha_compra DATE NOT NULL,
    total_neto NUMERIC(12) NOT NULL,
    iva NUMERIC(12) NOT NULL,
    total NUMERIC(12) NOT NULL,
	id_presupuesto INTEGER,

    CONSTRAINT fk_factura_compra_proveedor
        FOREIGN KEY (rut_proveedor)
        REFERENCES proveedor(rut),

	CONSTRAINT fk_factura_compra_presupuesto
		FOREIGN KEY (id_presupuesto)
		REFERENCES presupuesto(id_presupuesto)
);


--------------------------------------------------------------
--TABLA: PROYECTO
--------------------------------------------------------------

CREATE TABLE proyecto (
    id_proyecto INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    costo_total NUMERIC(12) NOT NULL,
    id_presupuesto INTEGER,
    nro_documento INTEGER,
    fecha_inicio DATE,
    fecha_termino DATE,

    CONSTRAINT fk_proyecto_presupuesto
        FOREIGN KEY (id_presupuesto)
        REFERENCES presupuesto(id_presupuesto),

    CONSTRAINT fk_proyecto_factura_venta
        FOREIGN KEY (nro_documento)
        REFERENCES factura_venta(nro_documento)
);