import datetime
from flask import render_template, redirect,url_for, session, flash, make_response
from app.forms import CambiarPasswordForm, LoginForm, RegistroForm
from app.auth import login_required
from app import models
from app import app
from app.models.usuarios import validar_contrasena, validar_inicio_sesion
import pdfkit

from app.models.vacunas_aplicadas import tiene_vacuna_aplicada ##pip install python-dateutil
import math

@app.route('/')  # http://localhost:5000/
@login_required
def index():
    usuario = models.get_user_data(session['dni'])

    calcular_edad = models.edad_de_usuario(usuario['id']) 
    edad = int(calcular_edad['edad'])
    tiene_fa = models.tiene_vacuna_aplicada(usuario['id'],2)
    tiene_covid_1= models.tiene_vacuna_aplicada(usuario['id'],4)
    tiene_covid_2 = models.tiene_vacuna_aplicada(usuario['id'],3)

    return render_template('index.html', titulo="Inicio", usuario=usuario, tiene_fa=tiene_fa)

@app.route('/login', methods=['GET', 'POST'])  # http://localhost:5000/login
def login():
    if "dni" in session:  # Si el usuario esta logueado, lo redirige a la pagina principal
        return redirect(url_for('index'))
    formulario_de_login = LoginForm()
    if formulario_de_login.validate_on_submit():
        # Valida el usuario y contraseña y token si es necesario
        validar_inicio, error = validar_inicio_sesion(formulario_de_login.dni.data, formulario_de_login.password.data, 
                                formulario_de_login.token.data)
        if validar_inicio:
            session['dni'] = formulario_de_login.dni.data
            return redirect(url_for('index'))
        else:
            flash(error, 'danger')
    return render_template('login.html', titulo="Login", formulario_de_login=formulario_de_login)


@app.route('/logout')
@login_required
def logout():
    #session.pop('dni', None)
    session.clear()
    return redirect(url_for('login'))


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """
    Ruta que se encarga de la logica del registro
    """
    if "dni" in session:  # Si el usuario esta logueado, lo redirige a la pagina principal
        return redirect(url_for('index'))
    form = RegistroForm()
    if form.validate_on_submit():
        if form.dni.data == "00000000":
            flash("No pudo validarse su identidad.", 'danger')
        else:
            error = models.guardar_usuario(form.data)
            if not error:
                id_usuario = models.get_user_data(form.dni.data)["id"]
                models.guardar_vacunas_aplicadas(form.data, id_usuario)
                flash(f"El registro fue exitoso. Hemos enviado un mail a {form.email.data} con un token que deberá usar junto con su contraseña para iniciar sesión.", "success")
                return redirect(url_for('login'))
            else:
                flash(error, 'danger')
    hoy = datetime.date.today()
    return render_template('registro.html', titulo="Registro", form=form, hoy=hoy)

@app.route('/perfil')  # http://localhost:5000/perfil
@login_required
def perfil():  
    usuario = session['dni']
    user_data = models.get_user_data(usuario)
    return render_template('perfil.html', titulo="Perfil", usuario=usuario, user_data=user_data)

@app.route('/mis-turnos') # http://localhost:5000/mis-turnos
@login_required
def mis_turnos():
    usuario = session['dni']
    user_data = models.get_user_data(usuario)
    mis_turnos = models.get_appointment_from_user(user_data['id']) 
    return render_template ('mis_turnos.html', titulo='Mis turnos', usuario=usuario, mis_turnos=mis_turnos)

@app.route('/mis-vacunas') # http://localhost:5000/mis-vacunas
@login_required
def mis_vacunas():
    dni = session['dni']
    #usuario = models.get_user_data(dni)
    vacunas_aplicadas = models.get_vacunas_aplicadas(dni)
    return render_template ('mis_vacunas.html', titulo = "Vacunas aplicadas", vacunas=vacunas_aplicadas)

@app.route('/cancelar-turno/<int:id>')
@login_required
def cancelar_turno(id):
    ## Falta agregar la ventana de confirmacion
    models.cancel_appointment(id)
    return redirect(url_for('mis_turnos'))


@app.route('/eliminar_cuenta/<int:id>')
@login_required
def eliminar_cuenta(id):

    ## obtener turnos del paciente
    usuario = session['dni']
    user_data = models.get_user_data(usuario)
    mis_turnos = models.get_appointment_from_user(user_data['id']) 

    ## cancelar sus turnos
    for turno in mis_turnos:
        models.cancel_appointment(turno['id'])

    ## eliminar paciente
    models.delete_user(user_data['id'])
    ## redirigir a pagina de incio de sesion
    flash(f"Cuenta eliminada del sistema","success")
    return redirect(url_for('logout'))

@app.route('/mis-vacunas/pdf/<int:id>')
@login_required
def pdf_template(id):
         # Pase la ruta absoluta del programa wkhtmltopdf.exe al objeto de configuración
    path_wkthmltopdf = r'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

    dni = session['dni']
    usuario = models.get_user_data(dni)

    vacuna_aplicada = models.get_vacuna_aplicada(id)
    #zona = models.get_nombre_zona(vacuna["id_zona"])

    rendered = render_template('pdf.html', usuario = usuario, vacuna = vacuna_aplicada)

    pdf = pdfkit.from_string(rendered, False, configuration=config)
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=certificado.pdf'

    return response

@app.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    form = CambiarPasswordForm()
    if form.validate_on_submit():
        usuario = models.get_user_data(session['dni'])
        validar_password = validar_contrasena(form.actual_password.data, usuario["password"])      
        if validar_password:
            #cambiar password
            flash(f"La contraseña fue cambiada con éxito.","success")
            return redirect(url_for('perfil'))
        else:
            flash(f"Contraseña incorrecta.","danger")
    return render_template('cambiar_password.html', titulo="cambiar-password", form=form)    
