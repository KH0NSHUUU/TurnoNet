CREATE SCHEMA `TurnoNet`;

USE TurnoNet;

CREATE TABLE clientes (
  dni int NOT NULL,
  nombre varchar(60) NOT NULL,
  apellido varchar(60) NOT NULL,
  contacto varchar(10) NOT NULL,
  correo varchar(50) NOT NULL,
  contraseña varchar(16) NOT NULL,
  rol varchar(20) NOT NULL,
  PRIMARY KEY (dni)
);

CREATE TABLE empleados (
  dni int NOT NULL,
  nombre varchar(60) NOT NULL,
  apellido varchar(60) NOT NULL,
  contacto varchar(10) NOT NULL,
  correo varchar(50) NOT NULL,
  contraseña varchar(16) NOT NULL,
  rol varchar(20) NOT NULL,
  PRIMARY KEY (dni)
);

CREATE TABLE pago (
  id int NOT NULL AUTO_INCREMENT,
  importe double NOT NULL,
  metodo varchar(16) DEFAULT NULL,
  PRIMARY KEY (id)
); 

CREATE TABLE usuarios (
  dni int NOT NULL,
  nombre varchar(60) NOT NULL,
  apellido varchar(30) NOT NULL,
  contacto varchar(10) NOT NULL,
  correo varchar(50) NOT NULL,
  contraseña varchar(16) NOT NULL,
  rol varchar(20) NOT NULL,
  PRIMARY KEY (dni)
); 

CREATE TABLE servicios (
  id int NOT NULL AUTO_INCREMENT,
  nombre varchar(16) NOT NULL,
  descripcion varchar(30) NOT NULL,
  precio double NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE turnos (
  id int NOT NULL AUTO_INCREMENT,
  fecha datetime NOT NULL,
  estado varchar(10) NOT NULL,
  id_empleado int NOT NULL,
  id_cliente int NOT NULL,
  id_servicio int NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (id_empleado) REFERENCES empleados(dni),
  FOREIGN KEY (id_cliente) REFERENCES clientes(dni),
  FOREIGN KEY (id_servicio) REFERENCES servicios(id)
);

CREATE TABLE facturacion (
  id int NOT NULL AUTO_INCREMENT,
  fecha datetime NOT NULL,
  importeTotal double NOT NULL,
  id_turno int NOT NULL,
  id_cliente int NOT NULL,
  id_servicio int NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (id_turno) REFERENCES turnos(id),
  FOREIGN KEY (id_cliente) REFERENCES clientes(dni),
  FOREIGN KEY (id_servicio) REFERENCES servicios(id)
);