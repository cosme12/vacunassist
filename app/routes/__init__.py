from dataclasses import dataclass
from flask import render_template, redirect,url_for, session, flash
from app.forms import LoginForm, RegistroForm
from app.auth import login_required
from app import models
from app import app


@app.route('/')  # http://localhost:5000/
@login_required
def index():
    usuario = session['usuario']
    todos_los_usuarios = models.get_usuarios()
    return render_template('index.html', titulo="Inicio", usuario=usuario, todos_los_usuarios=todos_los_usuarios)


@app.route('/login', methods=['GET', 'POST'])  # http://localhost:5000/login
def login():
    formulario_de_login = LoginForm()
    if formulario_de_login.validate_on_submit():
        # Aca deberiamos validar el usuario y contraseña
        session['usuario'] = formulario_de_login.usuario.data
        return redirect(url_for('index'))
    return render_template('login.html', titulo="Login", formulario_de_login=formulario_de_login, esconder_navbar=True)


@app.route('/logout')
@login_required
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """
    Ruta que se encarga de la logica del registro
    """
    if "usuario" in session:  # Si el usuario esta logueado, lo redirige a la pagina principal
        return redirect(url_for('index'))
    form = RegistroForm()
    if form.validate_on_submit():
        if form.dni.data == "00000000":
            flash("No pudo validarse su identidad.", 'danger')
        else:
            error = models.guardar_usuario(form.data)
            if not error:
                flash(f"El registro fue exitoso. Hemos enviado un mail a {form.email.data} con un token que deberá usar junto con su contraseña para iniciar sesión.", "success")
                return redirect(url_for('login'))
            else:
                flash(error, 'danger')
    return render_template('registro.html', titulo="Registro", form=form)

@app.route('/perfil')  # http://localhost:5000/perfil
@login_required
def perfil():  
    usuario = session['usuario']
    user_data = models.get_user_data(usuario)
    return render_template('perfil.html', titulo="Perfil", usuario=usuario, user_data=user_data)

@app.route('/mis-turnos') # http://localhost:5000/mis-turnos
@login_required
def mis_turnos():
        usuario = session ['usuario']
        user_data = models.get_user_data(usuario)
        mis_turnos = models.get_turnos_from_usuario(user_data['id']) 
        print(mis_turnos)
        return render_template ('mis_turnos.html', titulo='Mis turnos', usuario=usuario, mis_turnos=mis_turnos)

@app.route('/mis-vacunas') # http://localhost:5000/mis-vacunas
@login_required
def mis_vacunas():
    usuario = session["usuario"]
    vacunas_aplicadas = models.get_vacunas_aplicadas(usuario)
    return render_template ('mis_vacunas.html', titulo = "Vacunas aplicadas", usuario = usuario, vacunas = vacunas_aplicadas)