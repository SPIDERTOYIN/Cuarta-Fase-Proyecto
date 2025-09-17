import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort, flash
from models import db, Usuario, Empleado, Asistencia, Sucursal

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-dev")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# API keys por sucursal (ejemplo)
API_KEYS = set(os.environ.get("API_KEYS", "branchkey1").split(","))


@app.before_first_request
def create_tables():
    db.create_all()
    # Crear admin por defecto si env var lo permite
    if os.environ.get("CREATE_DEFAULT_ADMIN","false").lower() == "true":
        if not Usuario.query.filter_by(email="dueno@empresa.com").first():
            sucursal = Sucursal(nombre="Central")
            db.session.add(sucursal)
            dueno = Usuario(nombre="Dueño", email="dueno@empresa.com", rol="dueno", sucursal=sucursal)
            dueno.set_password(os.environ.get("DEFAULT_ADMIN_PASS","1234"))
            db.session.add(dueno)
            db.session.commit()


# ----------- LOGIN -------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = Usuario.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["rol"] = user.rol
            session.permanent = True
            return redirect(url_for("dashboard"))
        flash("Credenciales incorrectas")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ----------- DASHBOARD -------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = Usuario.query.get(session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("login"))

    if user.rol == "dueno":
        sucursales = Sucursal.query.all()
    else:
        sucursales = [user.sucursal]

    return render_template("dashboard.html", usuario=user, sucursales=sucursales)


# ----------- API PARA ARDUINO -------------
@app.route("/api/asistencia", methods=["POST"])
def api_asistencia():
    key = request.headers.get("X-API-KEY")
    if key not in API_KEYS:
        return jsonify({"status":"error","msg":"API key inválida"}), 401

    data = request.get_json(silent=True)
    if not data or "huella_id" not in data or "sucursal_id" not in data:
        return jsonify({"status":"error","msg":"payload inválido"}), 400

    huella = data["huella_id"]
    suc = data["sucursal_id"]
    empleado = Empleado.query.filter_by(huella_id=huella, sucursal_id=suc).first()

    if not empleado:
        return jsonify({"status": "error", "msg": "Empleado no encontrado"}), 404

    # Crear asistencia
    nueva = Asistencia(empleado_id=empleado.id)
    db.session.add(nueva)
    db.session.commit()

    return jsonify({"status":"ok", "empleado": empleado.nombre})


# ----------- VISTA SUCURSAL -------------
@app.route("/sucursal/<int:id>")
def ver_sucursal(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = Usuario.query.get(session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("login"))

    sucursal = Sucursal.query.get(id)
    if not sucursal:
        abort(404)

    if user.rol == "admin" and user.sucursal_id != sucursal.id:
        abort(403)

    return render_template("sucursal.html", sucursal=sucursal)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
