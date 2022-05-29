from flask import render_template, redirect, url_for, session, flash
from app.forms import RegistroEnfermeroForm
from app.auth import login_required
from app import models
from app import app


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
            flash(f"El registro del enfermero fue exitoso. Utilice el dni para autenticarse.", "success")
            return redirect(url_for('registrar_enfermero'))
        else:
            flash(error, 'danger')
    return render_template('admin/registro.html', form=form)
    

