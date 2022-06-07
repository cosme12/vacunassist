from flask import render_template, redirect, url_for, session, flash
from app.forms import RegistroEnfermeroForm
from app.auth import login_required
from app import models
from app import app
from app.handlers.email_enviar import enviar_email
from app.models.usuarios import generar_reset_password_token


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
    

