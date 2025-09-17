import os
from app import app
from models import db, Usuario, Sucursal, Empleado

with app.app_context():
    db.create_all()
    # Crear sucursales de prueba
    if not Sucursal.query.first():
        s1 = Sucursal(nombre="Taller Central")
        s2 = Sucursal(nombre="Planta Norte")
        db.session.add_all([s1, s2])
        db.session.commit()

    # Crear usuario dueño de prueba
    if not Usuario.query.filter_by(email="dueno@empresa.com").first():
        s = Sucursal.query.first()
        u = Usuario(nombre="Dueño", email="dueno@empresa.com", rol="dueno", sucursal=s)
        u.set_password(os.environ.get("DEFAULT_ADMIN_PASS","1234"))
        db.session.add(u)
        db.session.commit()

    print("DB inicializada ✅")
