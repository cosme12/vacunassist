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
        models.guardar_usuario(form.data)
        flash(f"El registro fue exitoso. Hemos enviado un mail a {form.email.data} con un token que deberá usar junto con su contraseña para iniciar sesión.")
        return redirect(url_for('login'))
    return render_template('registro.html', titulo="Registro", form=form)

