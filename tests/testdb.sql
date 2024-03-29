--
-- File generated with SQLiteStudio v3.3.3 on vie. may. 13 00:05:27 2022
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: turno
DROP TABLE IF EXISTS turno;
CREATE TABLE turno (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, fecha DATETIME NOT NULL, hora DATETIME NOT NULL, estado INTEGER NOT NULL, id_usuario INTEGER REFERENCES usuario (id) ON DELETE SET NULL ON UPDATE SET NULL, id_vacuna INTEGER REFERENCES vacuna (id) NOT NULL, id_zona INTEGER REFERENCES zona (id));


-- Table: usuario
DROP TABLE IF EXISTS usuario;
CREATE TABLE usuario (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, nombre TEXT, apellido TEXT, password TEXT, email TEXT UNIQUE, dni TEXT UNIQUE NOT NULL, telefono TEXT, fecha_de_nacimiento DATE, token TEXT UNIQUE, tipo INTEGER NOT NULL, paciente_de_riesgo BOOLEAN, reset_password_token TEXT, id_zona INTEGER REFERENCES zona (id));

-- Table: vacuna
DROP TABLE IF EXISTS vacuna;
CREATE TABLE vacuna (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, enfermedad TEXT NOT NULL, descripcion TEXT);
INSERT INTO vacuna (id, enfermedad, descripcion) VALUES (1, 'Gripe', NULL);
INSERT INTO vacuna (id, enfermedad, descripcion) VALUES (2, 'Fiebre Amarilla', NULL);
INSERT INTO vacuna (id, enfermedad, descripcion) VALUES (3, 'Covid SEGUNDA DOSIS', NULL);
INSERT INTO vacuna (id, enfermedad, descripcion) VALUES (4, 'Covid PRIMERA DOSIS', NULL);

-- Table: vacuna_aplicada
DROP TABLE IF EXISTS vacuna_aplicada;
CREATE TABLE vacuna_aplicada (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, fecha DATETIME NOT NULL, lote TEXT, laboratorio TEXT, id_vacuna INTEGER REFERENCES vacuna (id) NOT NULL, id_usuario INTEGER REFERENCES usuario (id), id_zona INTEGER REFERENCES zona (id) ON DELETE SET NULL);

-- Table: zona
DROP TABLE IF EXISTS zona;
CREATE TABLE zona (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, nombre TEXT NOT NULL, direccion TEXT NOT NULL);
INSERT INTO zona (id, nombre, direccion) VALUES (1, 'terminal', '41 y 4');
INSERT INTO zona (id, nombre, direccion) VALUES (2, 'municipalidad', '51 y 12');
INSERT INTO zona (id, nombre, direccion) VALUES (3, 'cementerio', 'diag 74');

-- Table: vacunatorio
DROP TABLE IF EXISTS vacunatorio;
CREATE TABLE vacunatorio (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, telefono TEXT NOT NULL);
INSERT INTO vacunatorio (id, telefono) VALUES (1, '1234');


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
