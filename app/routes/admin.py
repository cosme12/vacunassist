from flask import render_template, redirect, url_for, session, flash
from app.forms import RegistroEnfermeroForm
from app.auth import login_required
from app import models
from app import app


@app.route('/admin/registrar-enfermero')
@login_required
def registrar_enfermero():
    form = RegistroEnfermeroForm()
    return render_template('admin/registro.html', form=form)
    

