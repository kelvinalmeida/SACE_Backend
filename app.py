from flask import Flask
from flask_cors import CORS
from config import Config
from routes.login.login import login
from routes.usuario.usuario import usuario
from routes.tela_inicial.tela_inicial import tela_inicial

app = Flask(__name__)


CORS(app)

app.register_blueprint(login)
app.register_blueprint(usuario)
app.register_blueprint(tela_inicial)

app.config.from_object(Config)

if __name__ == '__main__':
    app.run(debug=True)