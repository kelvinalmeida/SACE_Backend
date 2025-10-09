from flask import Flask
from flask_cors import CORS
from config import Config
from routes.login.login import login
from routes.tela_inicial.tela_inicial import tela_inicial
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint


# registro_de_campo
from routes.registro_de_campo.bluprint import registro_de_campo
from routes.registro_de_campo import get_all
from routes.registro_de_campo import by_id
from routes.registro_de_campo import post_one_registro_de_campo


# area_de_visita
from routes.area_de_visita.bluprint import area_para_visita
from routes.area_de_visita import get_all
from routes.area_de_visita import get_by_id
from routes.area_de_visita import post_several_areas
from routes.area_de_visita import update
from routes.area_de_visita import delete

# usuario
from routes.usuario.bluprint import usuario
from routes.usuario import post_sereval_users
from routes.usuario import get_all_users
from routes.usuario import by_id

# denuncia
from routes.denuncia.bluprint import denuncia
from routes.denuncia import post_one_denuncia
from routes.denuncia import get_all
from routes.denuncia import by_id

# artigo
from routes.artigo.bluprint import blu_artigo
from routes.artigo import post_one_artigo
from routes.artigo import get_all
from routes.artigo import by_id


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
app.register_blueprint(area_para_visita)
app.register_blueprint(denuncia)
app.register_blueprint(blu_artigo)

print(app.url_map)

app.config.from_object(Config)

if __name__ == '__main__':
    app.run(debug=True)