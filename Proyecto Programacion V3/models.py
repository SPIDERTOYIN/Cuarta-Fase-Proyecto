from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    rol = db.Column(db.String(20), default="admin")  # "admin" o "dueno"
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Usuario {self.nombre} ({self.rol})>"


class Sucursal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    usuarios = db.relationship('Usuario', backref='sucursal', lazy=True)
    empleados = db.relationship('Empleado', backref='sucursal', lazy=True)

    def __repr__(self):
        return f"<Sucursal {self.nombre}>"


class Empleado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    huella_id = db.Column(db.Integer, unique=True, nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'))
    asistencias = db.relationship('Asistencia', backref='empleado', lazy=True)

    def __repr__(self):
        return f"<Empleado {self.nombre} (Huella {self.huella_id})>"


class Asistencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleado.id'))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Asistencia {self.empleado_id} - {self.timestamp}>"
