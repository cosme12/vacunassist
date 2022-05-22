from flask import redirect, url_for, session, request, flash
from functools import wraps
from app.models.turnos import get_appointment_from_user
from app.models.usuarios import edad_de_usuario, get_user_data
from app.models.turnos import tiene_appointment_covid1_from_user
from app.models. vacunas_aplicadas import tiene_vacuna_aplicada


def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'dni' not in session:
            return redirect(url_for('login'))
        else:
            if request.path != url_for('perfil') and request.path != url_for('logout') and 'eliminar_cuenta' not in request.path and 'sacar-turno' not in request.path:
                usuario = get_user_data(session['dni'])
                edad = edad_de_usuario(usuario['id'])
                tiene_turno_covid = tiene_appointment_covid1_from_user(usuario['id'])
                vucuna_covid_1 = tiene_vacuna_aplicada(usuario['id'], 4)
                if not vucuna_covid_1 and not tiene_turno_covid and (usuario['paciente_de_riesgo'] or edad > 60):
                    flash("Antes de poder acceder al resto del sitio debe reservar un turno para aplicarse la primera dosis de la vacuna de COVID-19.", "danger")
                    return redirect(url_for('sacar_turno', id_vacuna=4))
        return func(*args, **kwargs)
    return decorated_function

