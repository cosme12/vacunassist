from flask import render_template, redirect, url_for, session, flash
from app.forms import LoginForm, RegistroEnfermeroForm, EnviarEmailsAdminForm, AsignarZonaForm
from app.auth import login_required
from app import models
from app import app
from app.handlers.email_enviar import enviar_email
from app.models.usuarios import generar_reset_password_token


@app.route('/admin') # http://localhost:5000/admin
@login_required
def admin():
    return render_template('admin/admin.html', titulo="Admin")


@app.route('/admin/enviar-recordatorios', methods=['GET', 'POST'])
@login_required
def enviar_recordatorios():
    form = EnviarEmailsAdminForm()
    turnos_aprobados = models.get_turnos_aprobados()
    if form.validate_on_submit():
        for turno in turnos_aprobados:
            #print(f"Hola {turno['nombre']}, \n\nTe recordamos que mañana tenes turno para vacunarte.\n\nDatos del turno:\n\nVacuna: {turno['enfermedad']}\nFecha: {turno['fecha']}\nHora: {turno['hora']}hs\nZona: {turno[24]} {turno[25]}")
            if app.config['EMAIL_ENABLED']:
                enviar_email(turno["email"], "Vacunassist - Recordatorio de turno", f"Hola {turno['nombre']}, \n\nTe recordamos que mañana tenes turno para vacunarte.\n\nDatos del turno:\n\nVacuna: {turno['enfermedad']}\nFecha: {turno['fecha']}\nHora: {turno['hora']}hs\nZona: {turno[24]} {turno[25]}")
                flash("Se enviaron los emails con éxito.", "success")
    return render_template('admin/enviar_recordatorios.html', titulo="Envio de recordatorios", form=form, turnos_aprobados=turnos_aprobados, cant=len(turnos_aprobados))


@app.route('/admin/estadisticas')
def estadisticas():
    return render_template('admin/estadisticas.html', titulo="Estadisticas")


@app.route('/admin/registrar-enfermero', methods=['GET', 'POST'])
@login_required
def registrar_enfermero():
    """
    Ruta que se encarga de la logica del registro del enfermero
    """
    form = RegistroEnfermeroForm()
    if form.validate_on_submit():
        error = models.guardar_enfermero(form.data)
        if not error:
            usuario = models.get_user_data(form.dni.data)
            token = generar_reset_password_token(usuario["id"])  
            if app.config['EMAIL_ENABLED']:
                enviar_email(form.email.data, "Vacunassist - Recuperación de contraseña", f"Para recuperar su contraseña ingrese al siguiente link.\n\nhttp://127.0.0.1:5000/reset-password/{token}\n\n")
            flash(f"El registro fue exitoso. El enfermero recibirá un correo para reestablecer su contraseña.", "success")
            return redirect(url_for('registrar_enfermero'))
        else:
            flash(error, 'danger')
    return render_template('admin/registro.html', form=form)
    

@app.route('/admin/asignar-zona', methods=['GET', 'POST'])
def asignar_zona():
    form = AsignarZonaForm()
    enfermeros = models.get_enfermeros_ordenados_por_zona()
    cant_turnos_por_zona = models.get_cant_turnos_por_zona()
    cant_enfermeros_por_zona = models.get_cant_enfermeros_por_zona()
    total_enfermeros = len(enfermeros)
    if form.validate_on_submit():
        for enfermero in form.enfermeros.data:
            if enfermero["seleccionado"]:
                models.asignar_zona(enfermero["id_enfermero"], form.id_zona.data)
        flash("Se asignaron las zonas correctamente.", "success")
        return redirect(url_for('asignar_zona'))
    return render_template('admin/asignar_zona.html', titulo="Asignar zona", form=form, enfermeros=enfermeros, cant_turnos_por_zona=cant_turnos_por_zona, cant_enfermeros_por_zona=cant_enfermeros_por_zona, total_enfermeros=total_enfermeros)


@app.route('/admin/datos-vacunatorio', methods=['GET', 'POST'])
@login_required
def datos_vacunatorio():
    return render_template('admin/datos_vacunatorio.html', titulo="Datos del vacunatorio")


@app.route('/admin/gestion-pacientes')
@login_required
def gestion_pacientes():
    return render_template('admin/gestion_pacientes.html', titulo="Gestion de pacientes")


@app.route('/admin/gestion-enfermeros')
@login_required
def gestion_enfermeros():
    return render_template('admin/gestion_enfermeros.html', titulo="Gestion de enfermeros")


@app.route('/admin/ver-listado-enfermeros')
@login_required
def ver_listado_enfermeros():
    enfermeros = models.get_enfermeros()
    return render_template('admin/listado_enfermeros.html', titulo='Listado de enfermeros', enfermeros=enfermeros)

@app.route('/admin/eliminar-enfermero/<int:id>')
@login_required
def eliminar_enfermero(id):
    models.delete_user(id)
    return redirect(url_for('ver_listado_enfermeros'))


@app.route('/admin/ver-listado-pacientes')
@login_required
def ver_listado_pacientes():
    pacientes = models.get_pacientes()
    vacunas_aplicadas = {}
    edades= {}
    for paciente in pacientes:
        vacunas_aplicadas[paciente['dni']] = models.get_vacunas_aplicadas(paciente['dni'])
        edades[paciente['id']] = models.edad_de_usuario(paciente['id'])
    
    return render_template('admin/listado_pacientes.html', titulo='Listado de pacientes', pacientes=pacientes, edades=edades, vacunas_aplicadas=vacunas_aplicadas )


@app.route('/admin/vacunas-por-zona')
@login_required
def vacunas_por_zona():
    vacunas_zona1 = models.vacunas_por_zona(1)
    vacunas_zona2 = models.vacunas_por_zona(2)
    vacunas_zona3 = models.vacunas_por_zona(3)
    return render_template('admin/vacunas_por_zona.html', titulo='Vacunas por zona', vacunas_zona1=vacunas_zona1, vacunas_zona2=vacunas_zona2, vacunas_zona3=vacunas_zona3)

@app.route('/admin/vacunas-por-edad')
@login_required
def vacunas_por_edad():
    #menores18 = models.menores18()
    #entre18y60 = models.entre18y60()
    #mayores60 = models.mayores60()
    vacunas_menores18 = models.vacunas_menores18()
    vacunas_entre18y60 = models.vacunas_entre18y60()
    vacunas_mayores60 = models.vacunas_mayores60()
    return render_template('admin/vacunas_por_edad.html', titulo='Vacunas por edad', vacunas_menores18=vacunas_menores18, vacunas_entre18y60=vacunas_entre18y60, vacunas_mayores60=vacunas_mayores60)

@app.route('/admin/vacunas-por-enfermedad')
@login_required
def vacunas_por_enfermedad():
    vacunas_covid1 = models.get_vacunas_aplicadas_por_id(4)
    vacunas_covid2 = models.get_vacunas_aplicadas_por_id(3)
    vacunas_fiebre_amarilla = models.get_vacunas_aplicadas_por_id(2)
    vacunas_gripe = models.get_vacunas_aplicadas_por_id(1)
    return render_template('admin/vacunas_por_enfermedad.html', titulo='Vacunas por enfermedad', vacunas_covid1=vacunas_covid1, vacunas_covid2=vacunas_covid2, vacunas_fiebre_amarilla=vacunas_fiebre_amarilla, vacunas_gripe=vacunas_gripe)


@app.route('/admin/turnos-pendientes-de-fiebre-amarilla')
@login_required
def listado_pendientes_fiebre_amarilla():
    turnos = models.get_pendientes_fiebre_amarilla()
    vacunas_aplicadas = {}
    edades= {}
    for turno in turnos :
        print(turno['dni'])
        vacunas_aplicadas[turno['dni']] = models.get_vacunas_aplicadas(turno['dni'])
        edades[turno['id_usuario']] = models.edad_de_usuario(turno['id_usuario'])

    return render_template('admin/listado_pendientes_fiebre_amarilla.html', titulo = "Turnos pendientes de fiebre amarilla", turnos=turnos, vacunas_aplicadas=vacunas_aplicadas, edades=edades)  

@app.route('/admin/aprobar-turno/<int:id>')
@login_required
def aprobar_turno(id):
    turno = models.get_turno_por_id(id)
    usuario = models.get_user_data_por_id(turno['id_usuario'])
    models.aprobar_turno(id)
    if app.config['EMAIL_ENABLED']:
                enviar_email(usuario['email'], "Vacunassist - Aprobacion de turno Fiebre Amarilla", f"Hola {usuario['nombre']}\n\nSu turno para la vacuna la Fiebre amarilla el dia {turno['fecha']}, a las {turno['hora']} horas, en zona{turno['nombre']} {turno['direccion']} a sido aprobado.\n")
    return redirect(url_for('listado_pendientes_fiebre_amarilla'))


@app.route('/admin/rechazar-turno/<int:id>')
@login_required
def rechazar_turno(id):
    turno = models.get_turno_por_id(id)
    usuario = models.get_user_data_por_id(turno['id_usuario'])
    models.cancel_appointment(id,5)
    if app.config['EMAIL_ENABLED']:
                enviar_email(usuario['email'], "Vacunassist - Aprobacion de turno Fiebre Amarilla", f"Hola {usuario['nombre']}\n\nSu turno para la vacuna la Fiebre amarilla el dia {turno['fecha']}, a las {turno['hora']} horas, en zona{turno['nombre']} {turno['direccion']} a sido aprobado.\n")
    return redirect(url_for('listado_pendientes_fiebre_amarilla'))
