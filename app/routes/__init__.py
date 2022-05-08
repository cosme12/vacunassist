from flask import render_template, redirect,url_for,session
from app.forms import LoginForm
from app.auth import login_required
from app import app


@app.route('/')  # http://localhost:5000/
@login_required
def index():
    usuario = session['usuario']
    return render_template('index.html', titulo="Inicio", usuario=usuario)


@app.route('/login', methods=['GET', 'POST'])  # http://localhost:5000/login
def login():
    formulario_de_login = LoginForm()
    if formulario_de_login.validate_on_submit():
        # Aca deberiamos validar el usuario y contraseña
        session['usuario'] = formulario_de_login.usuario.data
        return redirect(url_for('index'))
    return render_template('login_con_bootstrap.html', titulo="Login", formulario_de_login=formulario_de_login, esconder_navbar=True)

@app.route('/logout')
@login_required
def logout():
    session = None
    return redirect(url_for('login'))

