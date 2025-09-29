from flask import Flask
from flask_cors import CORS
from config import Config
from routes.login.login import login
from routes.usuario.usuario import usuario
from routes.tela_inicial.tela_inicial import tela_inicial
from routes.registro_de_campo.registro_de_campo import registro_de_campo
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)


CORS(app)

API_URL = "/static/openapi.yaml"
SWAGGER_URL = "/api/docs"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "sace_backend_api"
    }
)

app.register_blueprint(swaggerui_blueprint)


app.register_blueprint(login)
app.register_blueprint(usuario)
app.register_blueprint(tela_inicial)
app.register_blueprint(registro_de_campo)

app.config.from_object(Config)

if __name__ == '__main__':
    app.run(debug=True)