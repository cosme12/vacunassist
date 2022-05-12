from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, DateField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired, InputRequired, EqualTo


class LoginForm(FlaskForm):
    dni = StringField('DNI', validators=[DataRequired('Este campo es requerido')])
    password = PasswordField('Contraseña', validators=[DataRequired('Este campo es requerido')])
    token = StringField('Token')
    iniciar_sesion = SubmitField('Iniciar sesión')


class HistorialVacunasForm(Form):
    vacuna = SelectField('¿Qué vacuna ya se aplicó?', choices=[("", "-"), ("covid1", "Covid 1era dosis"), ("covid2", "Covid 2da dosis"),
                                                                ("fiebre_amarilla", "Fiebre amarilla"), ("gripe", "Gripe")])
    fecha_aplicacion = DateField('Fecha de aplicación', validators=[])


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
    vacunas = FieldList(FormField(HistorialVacunasForm), min_entries=1, max_entries=5)
    enviar = SubmitField('Registrarse')


