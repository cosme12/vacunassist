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
    if form.validate_on_submit():
        print(form.data)
    else:
        print(form.errors)
    return render_template('admin/asignar_zona.html', titulo="Asignar zona", form=form, enfermeros=enfermeros)


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
