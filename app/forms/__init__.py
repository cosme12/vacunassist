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
    id_vacuna = SelectField('¿Qué vacuna ya se aplicó?', choices=[("4", "Covid 1era dosis"), ("3", "Covid 2da dosis"),
                                                                ("2", "Fiebre amarilla"), ("1", "Gripe")], 
                                                                validators=[DataRequired('Este campo es requerido')])
    fecha_aplicacion = DateField('Fecha de aplicación', validators=[DataRequired('Este campo es requerido')], render_kw={'min':'1900-01-01', 'max':datetime.datetime.now().strftime("%Y-%m-%d")})


class RegistroForm(FlaskForm):
    dni = StringField('DNI', validators=[DataRequired('Este campo es requerido'), Length(min=7, max=8, message='No es un dni válido')], render_kw={'onkeyup':'return validateNumber(event)'})
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

class CambiarPasswordForm(FlaskForm):
    actual_password = PasswordField('Contraseña actual', validators=[DataRequired('Este campo es requerido')])
    nueva_password = PasswordField('Contraseña nueva', [InputRequired(), EqualTo('confirmar', message='Las contraseñas deben coincidir')])
    confirmar  = PasswordField('Repetir contraseña')
    enviar = SubmitField('Cambiar contraseña', render_kw={'onkeyup':'return validateChars(event)'})

class ForgotPasswordForm(FlaskForm):
    dni = StringField('DNI', validators=[DataRequired('Este campo es requerido'), Length(min=7, max=8, message='No es un dni válido')])
    enviar = SubmitField('Recuperar contraseña', render_kw={'onkeyup':'return validateChars(event)'})
