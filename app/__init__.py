from flask import Flask
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
bootstrap = Bootstrap5(app)

# Permite configurar el estilo de los botones
app.config['BOOTSTRAP_BTN_STYLE'] = 'success'

from app import routes