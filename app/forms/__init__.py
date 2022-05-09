from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, DateField, SelectField, FieldList
from wtforms.validators import DataRequired, InputRequired, EqualTo


class LoginForm(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired('Este campo es requerido')])
    password = PasswordField('Contraseña', validators=[DataRequired('Este campo es requerido')])
    token = StringField('Token')
    remember_me = BooleanField('Remember Me')
    enviar = SubmitField('Enviar')


class RegistroForm(FlaskForm):
    dni = StringField('DNI', validators=[DataRequired('Este campo es requerido')])
    nombre = StringField('Nombre', validators=[DataRequired('Este campo es requerido')])
    apellido = StringField('Apellido', validators=[DataRequired('Este campo es requerido')])
    email = EmailField('Email', validators=[DataRequired('Este campo es requerido')])
    password = PasswordField('Contraseña', [InputRequired(), EqualTo('confirmar', message='Las contraseñas deben coincidir')])
    confirmar  = PasswordField('Repetir contraseña')
    fecha_de_nacimiento = DateField('Fecha de nacimiento', validators=[DataRequired('Este campo es requerido')])
    telefono = StringField('Teléfono', validators=[])    
    paciente_de_riesgo = BooleanField('¿Es paciente de riesgo?')
    vacunas = FieldList(SelectField('¿Qué vacuna ya se aplicó?', choices=[("", "-"), ("covid1", "Covid 1era dosis"), ("covid2", "Covid 2da dosis"),
                                                                ("fiebre_amarilla", "Fiebre amarilla"), ("gripe", "Gripe")]),
                                                                min_entries=1, max_entries=5)
    #vacunas = StringField('¿Qué vacuna ya se aplicó?', min_entries=1, max_entries=5)
    enviar = SubmitField('Registrarse')

