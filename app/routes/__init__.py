import datetime
from flask import render_template, redirect,url_for, session, flash, make_response
from app.forms import BookAppointmedForm, CambiarPasswordForm, ForgotPasswordForm, LoginForm, RegistroForm, ResetPasswordForm, EnviarEmailsAdminForm, VacunaAplicadaForm
from app.auth import login_required
from app import models
from app import app
from app.handlers.email_enviar import enviar_email
from app.models.usuarios import validar_contrasena, validar_inicio_sesion, generar_reset_password_token, verificar_reset_password_token, get_user_data_por_id
from app.models.turnos import get_turnos_aprobados
from app.handlers import *
import pdfkit
from app.routes.admin import *

from app.models.vacunas_aplicadas import tiene_vacuna_aplicada, get_vacuna_aplicada_covid1 ##pip install python-dateutil


@app.route('/')  # http://localhost:5000/
@login_required
def index():
    session["telefono_vacunatorio"] = models.get_telefono()["telefono"]
    usuario = models.get_user_data(session['dni'])
    habilitar_covid = models.apto_vacuna_covid(usuario["id"])
    tiene_covid1 = models.tiene_covid1(usuario["id"])
    habilitar_gripe = models.apto_vacuna_gripe(usuario["id"])
    habilitar_fiebre_amarilla = models.apto_vacuna_fiebre_amarilla(usuario["id"])
    return render_template('index.html', titulo="Inicio", usuario=usuario, habilitar_covid=habilitar_covid,
    tiene_covid1=tiene_covid1, habilitar_fiebre_amarilla=habilitar_fiebre_amarilla, habilitar_gripe=habilitar_gripe)


@app.route('/login', methods=['GET', 'POST'])  # http://localhost:5000/login
def login():
    session["telefono_vacunatorio"] = models.get_telefono()["telefono"]
    if "dni" in session:  # Si el usuario esta logueado, lo redirige a la pagina principal
        return redirect(url_for('index'))
    formulario_de_login = LoginForm()
    if formulario_de_login.validate_on_submit():
        # Valida el usuario y contraseña y token si es necesario
        validar_inicio, error = validar_inicio_sesion(formulario_de_login.dni.data, formulario_de_login.password.data, 
                                formulario_de_login.token.data)
        usuario = models.get_user_data(formulario_de_login.dni.data)
        if validar_inicio:
            session['dni'] = formulario_de_login.dni.data
            session['nombre'] = usuario["nombre"]
            session['apellido'] = usuario["apellido"]
            session['tipo'] = usuario["tipo"]
            session['id_zona'] = usuario["id_zona"]
            if session["tipo"] == 1:
                return redirect(url_for('index'))
            elif session["tipo"] == 2:
                return redirect(url_for('turnos_del_dia'))
            elif session["tipo"] == 3:
                return redirect(url_for('admin'))
        else:
            flash(error, 'danger')
    return render_template('login.html', titulo="Login", formulario_de_login=formulario_de_login)


@app.route('/logout') # http://localhost:5000/logout
@login_required
def logout():
    #session.pop('dni', None)
    session.clear()
    session["telefono_vacunatorio"] = models.get_telefono()["telefono"]
    return redirect(url_for('login'))


@app.route('/registro', methods=['GET', 'POST']) # http://localhost:5000/registro
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
            # Verificar que las vacunas cargardas sean correctas
            vacunas_seleccionadas = []
            vacunas_repetidas = False
            for vacuna in form.vacunas.data:
                if vacuna["id_vacuna"] in vacunas_seleccionadas:
                    vacunas_repetidas = True
                    break
                vacunas_seleccionadas.append(vacuna["id_vacuna"])
            if "3" in vacunas_seleccionadas and "4" not in vacunas_seleccionadas:  # Falta primera dosis
                flash("Falta seleccionar la primera dosis de la vacuna Covid-19.", 'danger')
            elif vacunas_repetidas:
                flash("No puede seleccionar más de una vez la misma vacuna.", 'danger')
            else:
                error, token = models.guardar_usuario(form.data)
                if not error:
                    id_usuario = models.get_user_data(form.dni.data)["id"]
                    models.guardar_vacunas_aplicadas(form.data, id_usuario)
                    flash(f"El registro fue exitoso. Hemos enviado un mail a {form.email.data} con un token que deberá usar junto con su contraseña para iniciar sesión.", "success")
                    if app.config['EMAIL_ENABLED']:
                        enviar_email(form.email.data, "Vacunassist - Registro exitoso", f"Hemos registrado su usuario exitosamente.\n\nSu token de seguridad es: {token}")
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
    if user_data["id_zona"]:
        zona = models.get_zona(user_data["id_zona"])
    else:
        zona = None
    return render_template('perfil.html', titulo="Perfil", usuario=usuario, user_data=user_data, zona=zona)


@app.route('/mis-turnos') # http://localhost:5000/mis-turnos
@login_required
def mis_turnos():
    usuario = session['dni']
    user_data = models.get_user_data(usuario)
    mis_turnos = models.get_appointment_from_user(user_data['id'])
    hoy= datetime.datetime.strptime((datetime.datetime.now() + datetime.timedelta(hours=8)).strftime("%d/%m/%Y %H:%M"), "%d/%m/%Y %H:%M")
    fechas_y_horas = []
    for turno in mis_turnos:
        fecha_y_hora = datetime.datetime.strptime((turno['fecha']+" "+ turno['hora']), "%d/%m/%Y %H:%M")
        fechas_y_horas.append(fecha_y_hora)
    return render_template ('mis_turnos.html', titulo='Mis turnos', usuario=usuario, mis_turnos=mis_turnos, hoy=hoy, fechas_y_horas=fechas_y_horas)


@app.route('/mis-vacunas') # http://localhost:5000/mis-vacunas
@login_required
def mis_vacunas():
    dni = session['dni']
    #usuario = models.get_user_data(dni)
    vacunas_aplicadas = models.get_vacunas_aplicadas(dni)
    return render_template ('mis_vacunas.html', titulo = "Vacunas aplicadas", vacunas=vacunas_aplicadas)


@app.route('/cancelar-turno/<int:id>') # http://localhost:5000/cancelar-turno/<id_turno>
@login_required
def cancelar_turno(id):
    models.cancel_appointment(id, 5)
    flash("Su turno ha sido cancelado.", "success")
    return redirect(url_for('mis_turnos'))


@app.route('/eliminar_cuenta/<int:id>') # http://localhost:5000/eliminar-cuenta/<id_usuario>
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
    flash("Cuenta eliminada del sistema","success")
    return redirect(url_for('logout'))


@app.route('/mis-vacunas/pdf/<int:id>') # http://localhost:5000/mis-vacunas/pdf/<id_vacuna_aplicada>
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


@app.route('/cambiar-password', methods=['GET', 'POST']) # http://localhost:5000/cambiar-password
@login_required
def cambiar_password():
    form = CambiarPasswordForm()
    if form.validate_on_submit():
        usuario = models.get_user_data(session['dni'])
        validar_password = validar_contrasena(form.actual_password.data, usuario["password"])      
        if validar_password:
            #cambiar password
            models.cambiar_password(session['dni'], form.nueva_password.data)                
            flash(f"La contraseña fue cambiada con éxito.","success")
        else:
            flash(f"Contraseña actual incorrecta.","danger")
    return render_template('cambiar_password.html', titulo="Cambiar contraseña", form=form)    


@app.route('/forgot-password', methods=['GET', 'POST']) # http://localhost:5000/forgot-password
def forgot_password():
    forgot_password_form = ForgotPasswordForm()
    if forgot_password_form.validate_on_submit():
        usuario = models.get_user_data(forgot_password_form.dni.data)
        if usuario:
            email = usuario["email"]
            token = generar_reset_password_token(usuario["id"])
            flash(f"Hemos enviado un mail a {email} para recuperar su contraseña.", "success")   
            if app.config['EMAIL_ENABLED']:
                enviar_email(email, "Vacunassist - Recuperación de contraseña", f"Para recuperar su contraseña ingrese al siguiente link.\n\nhttp://127.0.0.1:5000/reset-password/{token}\n\nSi usted no solicitó un cambio de contraseña, ignore este mensaje.")
            return redirect(url_for('login'))
            
        else:
            flash(f"El usuario con DNI {forgot_password_form.dni.data} no se encuentra registrado.","danger")
    return render_template('forgot_password.html', titulo="Contraseña olvidada", form=forgot_password_form)


@app.route('/reset-password/<token>', methods=['GET', 'POST']) # http://localhost:5000/forgot-password/<token>
def reset_password(token):
    usuario = verificar_reset_password_token(token)
    if usuario:
        reset_password_form = ResetPasswordForm()
        if reset_password_form.validate_on_submit():
            models.cambiar_password(usuario['dni'], reset_password_form.new_password.data)                
            flash(f"La contraseña fue cambiada con éxito.","success")
            return redirect(url_for('login'))
        return render_template('reset_password.html', titulo="Recuperar contraseña", form=reset_password_form)
    else:
        flash("El enlace es inválido o ha expirado", "danger")
        return redirect(url_for('login'))


@app.route('/sacar-turno/<int:id_vacuna>', methods=['GET', 'POST'])# http://localhost:5000/sacar-turnos/<id_vacuna>
@login_required
def sacar_turno(id_vacuna):
    ## variable para formulario
    form = BookAppointmedForm()
    vaccine_data= models.get_vacuna(id_vacuna)
    vaccine_name = vaccine_data['enfermedad']
    
    #Seteo de la fecha minima habilitada para turno de vacuna covid2
    if id_vacuna == 3: 
        usuario = models.get_user_data(session['dni'])
        id_usuario = usuario["id"]
        vacuna_covid1 = models.get_vacuna_aplicada_covid1(id_usuario)
        fecha_covid1 = datetime.datetime.strptime(vacuna_covid1['fecha'], "%d/%m/%Y").date()
        fecha_min_covid2 = fecha_covid1 + datetime.timedelta(21)
        la_semana_que_viene = datetime.datetime.strptime((datetime.datetime.now() + datetime.timedelta(7)).strftime("%d/%m/%Y"), "%d/%m/%Y").date()
        if (fecha_min_covid2 < la_semana_que_viene):
            fecha_min_covid2 = la_semana_que_viene
        form.fecha.render_kw = {'min':(fecha_min_covid2).strftime("%Y-%m-%d")}

    if form.validate_on_submit():
        user_data = models.get_user_data(session['dni'])
        print(form.hora.data)
        print(type(form.hora.data))
        models.reservar_turno(form.fecha.data, user_data['id'], id_vacuna, form.id_zona.data, form.hora.data)
        if id_vacuna == 2:
            flash("Su turno fue solicitado y está pendiente de aprobación. Le enviaremos un email cuando el mismo sea aprobado.", "success")
        else:
            flash("Su turno se a registrado con éxito. Le enviaremos un recordatorio a su email 24 horas antes del mismo.", "success")
        return redirect(url_for('index'))

    return render_template('sacar_turno.html', titulo="Sacar Titulo", form=form,vaccine_name=vaccine_name)

@app.route('/turnos-del-dia/', methods=['GET', 'POST']) #http://localhost:5000/turnos-del-dia/<id_zona>
@login_required
def turnos_del_dia():
    id_zona = session['id_zona']
    zona = models.get_nombre_zona(id_zona)
    hoy = datetime.date.today().strftime("%d/%m/%Y")
    turnos = models.get_turnos_del_dia(hoy, id_zona)
    vacunas_aplicadas = {}
    edades= {}
    for turno in turnos :
        vacunas_aplicadas[turno['dni']] = models.get_vacunas_aplicadas(turno['dni'])
        edades[turno['id_usuario']] = models.edad_de_usuario(turno['id_usuario'])
        
    form = VacunaAplicadaForm()
    if form.validate_on_submit():
        models.cargar_vacuna_aplicada(hoy,form.lote.data,form.laboratorio.data, form.id_vacuna.data, form.id_usuario.data ,id_zona)
        models.finalizar_turno(form.id_turno.data)        
        #registra turno automatico para 2da dosis COVID
        if form.id_vacuna.data == '4':
            turno = models.get_turno_por_id(form.id_turno.data)
            fecha_2da_dosis = (datetime.datetime.now() + datetime.timedelta(21))
            hora = datetime.datetime.strptime(turno['hora'], '%H:%M').time()
            models.reservar_turno(fecha_2da_dosis, form.id_usuario.data, 3, id_zona, hora)
            if app.config['EMAIL_ENABLED']:
                usuario = models.get_user_data_por_id(form.id_usuario.data)
                zona = models.get_zona(id_zona)
                print(f'Hola {usuario["nombre"]}, tu turno para la segunda dosis de la vacuna contra el covid es el {fecha_2da_dosis} a las {turno["hora"]} en el vacunatorio zona {zona["nombre"]} {zona["direccion"]}.\n\nPodés reprogramarlo desde tu cuenta.\n\nTe enviaremos un recordatorio a este mail 24 hs antes del mismo.')
                enviar_email(usuario["email"], "Vacunassist - Turno covid 2da dosis",f'Hola {usuario["nombre"]}, tu turno para la segunda dosis de la vacuna contra el covid es el {fecha_2da_dosis.strftime("%d/%m/%Y")} a las {turno["hora"]} en el vacunatorio zona {zona["nombre"]} {zona["direccion"]}.\n\nPodés reprogramarlo desde tu cuenta.\n\nTe enviaremos un recordatorio a este mail 24 hs antes del mismo.')
        flash('La vacuna fue cargada con éxito. Turno finalizado.',"success")
        return redirect (url_for('turnos_del_dia'))
    else:
        print(form.errors)
    return render_template('turnos_del_dia.html', titulo="Turnos del dia", zona=zona, turnos=turnos, hoy=hoy, vacunas_aplicadas=vacunas_aplicadas, form=form, edades=edades)


@app.route('/cancelar-turnos-del-dia') #http://localhost:5000//cancelar-turnos-del-dia/<hoy>
@login_required
def cancelar_turnos_del_dia():
    hoy = datetime.date.today().strftime("%d/%m/%Y")
    id_zona = session['id_zona']
    turnos = models.get_turnos_del_dia(hoy, id_zona)
    for turno in turnos:
        models.cancel_appointment(turno['id'], 4)
    flash("Los turnos han sido cancelados.", "success")
    return redirect(url_for('turnos_del_dia'))