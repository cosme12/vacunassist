from flask import redirect, url_for, session, request, flash
from functools import wraps
from app.models.turnos import get_appointment_from_user
from app.models.usuarios import edad_de_usuario, get_user_data
from app.models.turnos import tiene_appointment_covid1_from_user, tiene_turno_pendiente
from app.models.vacunas_aplicadas import tiene_vacuna_aplicada, tiene_vacuna_gripe


def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'dni' not in session:
            return redirect(url_for('login'))
        else:
            if session["tipo"] == 1:
                if request.path != url_for('perfil') and request.path != url_for('logout') and 'eliminar_cuenta' not in request.path and 'sacar-turno' not in request.path:
                    usuario = get_user_data(session['dni'])
                    edad = edad_de_usuario(usuario['id'])
                    tiene_turno_covid = tiene_appointment_covid1_from_user(usuario['id'])
                    vucuna_covid_1 = tiene_vacuna_aplicada(usuario['id'], 4)
                    vacuna_gripe = tiene_vacuna_gripe(usuario['id'])
                    tiene_turno_gripe = tiene_turno_pendiente(usuario['id'], 1)
                    if not vucuna_covid_1 and not tiene_turno_covid and (usuario['paciente_de_riesgo'] or edad > 60):
                        flash("Antes de poder acceder al resto del sitio debe reservar un turno para aplicarse la primera dosis de la vacuna de COVID-19.", "danger")
                        return redirect(url_for('sacar_turno', id_vacuna=4))
                    elif not vacuna_gripe and not tiene_turno_gripe and edad > 60:
                        flash("Antes de poder acceder al resto del sitio debe reservar un turno para aplicarse la vacuna de la GRIPE.", "danger")
                        return redirect(url_for('sacar_turno', id_vacuna=1))
            elif session["tipo"]==2:
                if request.path != url_for('perfil') and request.path != url_for('turnos_del_dia') and request.path != url_for('logout') and request.path != url_for('cancelar_turnos_del_dia') and request.path != url_for('cambiar_password') :
                    return redirect(url_for('turnos_del_dia'))
            elif session["tipo"]==3:
                if request.path != url_for('admin') and request.path != url_for('enviar_recordatorios') and request.path != url_for('logout') and request.path != url_for('registrar_enfermero') and request.path != url_for('asignar_zona') \
                and request.path != url_for('ver_listado_enfermeros')  and request.path != url_for('ver_listado_pacientes') and request.path != url_for('vacunas_por_edad') \
                and request.path != url_for('vacunas_por_enfermedad') and request.path != url_for('cancelados_por_vacuna') and request.path != url_for('listado_pendientes_fiebre_amarilla') :
                    return redirect(url_for('admin'))
        return func(*args, **kwargs)
    return decorated_function


