USE inventarios;

CREATE TABLE categorias (
  categoria_id  INT AUTO_INCREMENT PRIMARY KEY,
  nombre        VARCHAR(100) NOT NULL,
  descripcion   TEXT,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE proveedores (
  proveedor_id  INT AUTO_INCREMENT PRIMARY KEY,
  nombre        VARCHAR(150) NOT NULL,
  ruc           VARCHAR(20) UNIQUE,
  email         VARCHAR(100),
  telefono      VARCHAR(20),
  ciudad        VARCHAR(80),
  pais          VARCHAR(60) DEFAULT 'Ecuador',
  activo        TINYINT(1) DEFAULT 1,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE productos (
  producto_id     INT AUTO_INCREMENT PRIMARY KEY,
  sku             VARCHAR(50) UNIQUE NOT NULL,
  nombre          VARCHAR(200) NOT NULL,
  descripcion     TEXT,
  precio_unitario DECIMAL(12,2) NOT NULL,
  peso_kg         DECIMAL(8,3),
  categoria_id    INT NOT NULL,
  proveedor_id    INT NOT NULL,
  activo          TINYINT(1) DEFAULT 1,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_prod_cat  FOREIGN KEY (categoria_id)
    REFERENCES categorias(categoria_id),
  CONSTRAINT fk_prod_prov FOREIGN KEY (proveedor_id)
    REFERENCES proveedores(proveedor_id)
);

CREATE TABLE bodegas (
  bodega_id    INT AUTO_INCREMENT PRIMARY KEY,
  codigo       VARCHAR(20) UNIQUE NOT NULL,
  nombre       VARCHAR(150) NOT NULL,
  ciudad       VARCHAR(80),
  capacidad_m3 DECIMAL(10,2),
  activo       TINYINT(1) DEFAULT 1
);

CREATE TABLE inventario_ubicacion (
  inv_id               BIGINT AUTO_INCREMENT PRIMARY KEY,
  producto_id          INT NOT NULL,
  bodega_id            INT NOT NULL,
  cantidad             DECIMAL(12,3) NOT NULL DEFAULT 0,
  stock_minimo         DECIMAL(12,3) DEFAULT 0,
  stock_maximo         DECIMAL(12,3),
  ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_inv_prod FOREIGN KEY (producto_id)
    REFERENCES productos(producto_id),
  CONSTRAINT fk_inv_bod  FOREIGN KEY (bodega_id)
    REFERENCES bodegas(bodega_id),
  UNIQUE KEY uq_prod_bod (producto_id, bodega_id)
);

SHOW TABLES;