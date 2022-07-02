import datetime
from flask import render_template, redirect, url_for, session, flash
from app.forms import LoginForm, RegistroEnfermeroForm, EnviarEmailsAdminForm, AsignarZonaForm, DatosVacunatorioForm
from app.auth import login_required
from app import models
from app import app
from app.handlers.email_enviar import enviar_email
from app.models.usuarios import generar_reset_password_token
from app.models.vacunas_aplicadas import fechas_y_zonas_de_vacunas_aplicadas


@app.route('/admin') # http://localhost:5000/admin
@login_required
def admin():
    return render_template('admin/admin1.html', titulo="Admin")


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
    data = {
        "zona_terminal": models.get_zona(1)["direccion"],
        "zona_municipalidad": models.get_zona(2)["direccion"],
        "zona_cementerio": models.get_zona(3)["direccion"],
        "telefono": models.get_telefono()["telefono"]
    }
    form = DatosVacunatorioForm(data=data)
    if form.validate_on_submit():
        models.set_direccion(1, form.zona_terminal.data)
        models.set_direccion(2, form.zona_municipalidad.data)
        models.set_direccion(3, form.zona_cementerio.data)
        models.set_telefono(form.telefono.data)
        session["telefono_vacunatorio"] = models.get_telefono()["telefono"]
        flash("Los datos se actualizaron correctamente.", "success")
    return render_template('admin/datos_vacunatorio.html', titulo="Datos del vacunatorio", form=form)


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

@app.route('/admin/eliminar-enfermeros')
@login_required
def eliminar_enfermeros():
    enfermeros = models.get_enfermeros()
    for enfermero in enfermeros:
        models.delete_user(enfermero['id'])
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

@app.route('/admin/eliminar-pacientes')
@login_required
def eliminar_pacientes():
    pacientes = models.get_pacientes()
    for paciente in pacientes:
        models.delete_user(paciente['id'])
    return redirect(url_for('ver_listado_pacientes'))


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
    fechas = fechas_y_zonas_de_vacunas_aplicadas()
    menores18 = []
    entre18y60 = []
    mayores60 = []
    zona1 = [[],[],[]]
    zona2 = [[],[],[]]
    zona3 = [[],[],[]]

    fecha_60 = (datetime.datetime.today() - datetime.timedelta(days=365*60))  
    fecha_18 = (datetime.datetime.today() - datetime.timedelta(days=365*18))

    for f in fechas:
        fecha = datetime.datetime.strptime(f["fecha_de_nacimiento"], "%d/%m/%Y")
        if (fecha > fecha_18):
            menores18.append({"fecha": f["fecha"], "zona": f["id_zona"]})
        elif (fecha >= fecha_60 and fecha <= fecha_18):
            entre18y60.append({"fecha": f["fecha"], "zona": f["id_zona"]})
        else:
            mayores60.append({"fecha": f["fecha"], "zona": f["id_zona"]})

    for item in menores18:
        if item['zona']==1:
            zona1[0].append(item['fecha'])
        elif item['zona']==2:
            zona2[0].append(item['fecha'])
        else:
            zona3[0].append(item['fecha'])
    for item in entre18y60:
        if item['zona']==1:
            zona1[1].append(item['fecha'])
        elif item['zona']==2:
            zona2[1].append(item['fecha'])
        else:
            zona3[1].append(item['fecha'])
    for item in mayores60:
        if item['zona']==1:
            zona1[2].append(item['fecha'])
        elif item['zona']==2:
            zona2[2].append(item['fecha'])
        else:
            zona3[2].append(item['fecha'])

    return render_template('admin/vacunas_por_edad.html', titulo='Vacunas por edad', menores18=menores18, entre18y60=entre18y60, mayores60=mayores60, zona1=zona1, zona2=zona2, zona3=zona3)

@app.route('/admin/vacunas-por-enfermedad')
@login_required
def vacunas_por_enfermedad():
    vacunas_covid1 = models.get_vacunas_aplicadas_por_id(4)
    vacunas_covid2 = models.get_vacunas_aplicadas_por_id(3)
    vacunas_fiebre_amarilla = models.get_vacunas_aplicadas_por_id(2)
    vacunas_gripe = models.get_vacunas_aplicadas_por_id(1)
    zona1 = [[],[],[],[]]
    zona2 = [[],[],[],[]]
    zona3 = [[],[],[],[]]

    for item in vacunas_covid1:
        if item['id_zona']==1:
            zona1[0].append(item['fecha'])
        elif item['id_zona']==2:
            zona2[0].append(item['fecha'])
        else:
            zona3[0].append(item['fecha'])

    for item in vacunas_covid2:
        if item['id_zona']==1:
            zona1[1].append(item['fecha'])
        elif item['id_zona']==2:
            zona2[1].append(item['fecha'])
        else:
            zona3[1].append(item['fecha'])

    for item in vacunas_fiebre_amarilla:
        if item['id_zona']==1:
            zona1[2].append(item['fecha'])
        elif item['id_zona']==2:
            zona2[2].append(item['fecha'])
        else:
            zona3[2].append(item['fecha'])

    for item in vacunas_gripe:
        if item['id_zona']==1:
            zona1[3].append(item['fecha'])
        elif item['id_zona']==2:
            zona2[3].append(item['fecha'])
        else:
            zona3[3].append(item['fecha'])
    
    return render_template('admin/vacunas_por_enfermedad.html', titulo='Vacunas por enfermedad', vacunas_covid1=vacunas_covid1, vacunas_covid2=vacunas_covid2, vacunas_fiebre_amarilla=vacunas_fiebre_amarilla, vacunas_gripe=vacunas_gripe, zona1=zona1, zona2=zona2, zona3=zona3)


@app.route('/admin/cancelados-por-vacuna')
@login_required
def cancelados_por_vacuna():
    cancelados_covid1 = models.get_turnos_cancelados_por_vacuna(4)
    cancelados_covid2 = models.get_turnos_cancelados_por_vacuna(3)
    cancelados_fiebre_amarilla = models.get_turnos_cancelados_por_vacuna(2)
    cancelados_gripe = models.get_turnos_cancelados_por_vacuna(1)

    zona1 = [[],[],[],[]]
    zona2 = [[],[],[],[]]
    zona3 = [[],[],[],[]]

    for item in cancelados_covid1:
        if item['id_zona']==1:
            zona1[0].append(item['fecha'])
        elif item['id_zona']==2:
            zona2[0].append(item['fecha'])
        else:
            zona3[0].append(item['fecha'])
    for item in cancelados_covid2:
        if item['id_zona']==1:
            zona1[1].append(item['fecha'])
        elif item['id_zona']==2:
            zona2[1].append(item['fecha'])
        else:
            zona3[1].append(item['fecha'])
    for item in cancelados_gripe:
        if item['id_zona']==1:
            zona1[2].append(item['fecha'])
        elif item['id_zona']==2:
            zona2[2].append(item['fecha'])
        else:
            zona3[2].append(item['fecha'])
    for item in cancelados_fiebre_amarilla:
        if item['id_zona']==1:
            zona1[3].append(item['fecha'])
        elif item['id_zona']==2:
            zona2[3].append(item['fecha'])
        else:
            zona3[3].append(item['fecha'])
    
    return render_template('admin/cancelados_por_vacuna.html', titulo='Turnos cancelados', cancelados_covid1=cancelados_covid1, cancelados_covid2=cancelados_covid2, cancelados_fiebre_amarilla=cancelados_fiebre_amarilla, cancelados_gripe=cancelados_gripe, zona1=zona1, zona2=zona2, zona3=zona3)


@app.route('/admin/turnos-pendientes-de-fiebre-amarilla')
@login_required
def listado_pendientes_fiebre_amarilla():
    turnos = models.get_pendientes_fiebre_amarilla()
    vacunas_aplicadas = {}
    edades= {}
    for turno in turnos :
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
    flash("Se aprobó el turno correctamente. Se envió un email informando la actualización de estado del turno al paciente correspondiente.", "success")
    return redirect(url_for('listado_pendientes_fiebre_amarilla'))


@app.route('/admin/rechazar-turno/<int:id>')
@login_required
def rechazar_turno(id):
    turno = models.get_turno_por_id(id)
    usuario = models.get_user_data_por_id(turno['id_usuario'])
    models.cancel_appointment(id,5)
    if app.config['EMAIL_ENABLED']:
                enviar_email(usuario['email'], "Vacunassist - Rechazo de turno Fiebre Amarilla", f"Hola {usuario['nombre']}\n\nSu turno para la vacuna la Fiebre amarilla el dia {turno['fecha']}, a las {turno['hora']} horas, en zona{turno['nombre']} {turno['direccion']} a sido rechazado.\n Ante cualquier consulta comuniquese al 221- 5412345")
    flash("Se rechazó el turno correctamente. Se envió un email informando la actualización de estado del turno al paciente correspondiente.", "success")
    return redirect(url_for('listado_pendientes_fiebre_amarilla'))

