from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, DateField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired, InputRequired, EqualTo, Length, NumberRange, Regexp
import datetime


class LoginForm(FlaskForm):
    dni = StringField('DNI', validators=[DataRequired('Este campo es requerido')])
    password = PasswordField('Contraseña', validators=[DataRequired('Este campo es requerido')])
    token = StringField('Token')
    iniciar_sesion = SubmitField('Iniciar sesión')


class HistorialVacunasForm(Form):
    vacuna = SelectField('¿Qué vacuna ya se aplicó?', choices=[("", "-"), ("covid1", "Covid 1era dosis"), ("covid2", "Covid 2da dosis"),
                                                                ("fiebre_amarilla", "Fiebre amarilla"), ("gripe", "Gripe")])
    fecha_aplicacion = DateField('Fecha de aplicación', validators=[], render_kw={'min':'1900-01-01', 'max':datetime.datetime.now().strftime("%Y-%m-%d")})


class RegistroForm(FlaskForm):
    dni = StringField('DNI', validators=[DataRequired('Este campo es requerido'), Length(min=8, max=8, message='No es un dni válido')], render_kw={'onkeyup':'return validateNumber(event)'})
    nombre = StringField('Nombre', validators=[DataRequired('Este campo es requerido')], render_kw={'onkeyup':'return validateChars(event)'})
    apellido = StringField('Apellido', validators=[DataRequired('Este campo es requerido')], render_kw={'onkeyup':'return validateChars(event)'})
    email = EmailField('Email', validators=[DataRequired('Este campo es requerido')])
    password = PasswordField('Contraseña', [InputRequired(), EqualTo('confirmar', message='Las contraseñas deben coincidir')])
    confirmar  = PasswordField('Repetir contraseña')
    fecha_de_nacimiento = DateField('Fecha de nacimiento', validators=[DataRequired('Este campo es requerido')], render_kw={'min':'1900-01-01', 'max':datetime.datetime.now().strftime("%Y-%m-%d")})
    telefono = StringField('Teléfono', validators=[])    
    paciente_de_riesgo = BooleanField('¿Es paciente de riesgo?')
    vacunas = FieldList(FormField(HistorialVacunasForm), min_entries=0, max_entries=5)
    enviar = SubmitField('Registrarse', render_kw={'onkeyup':'return validateChars(event)'})


