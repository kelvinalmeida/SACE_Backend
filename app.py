from flask import Flask
from flask_cors import CORS
from config import Config
from routes.login.login import login
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint


# ciclos
from routes.ciclo.bluprint import ciclos
from routes.ciclo import get_anos_and_ciclos
from routes.ciclo import criar_ciclo
from routes.ciclo import finalizar_ciclo


# graficos
from routes.graficos.bluprint import graficos
from routes.graficos import focos_positovos
from routes.graficos import depositos_identificados
from routes.graficos import imoveis_trabalhados
from routes.graficos import depositos_tratados
from routes.graficos import taxa_de_reincidencia
from routes.graficos import casos_comfirmados
from routes.graficos import atividades_realizadas
from routes.graficos import acoes_de_bloqueio_por_ciclo
from routes.graficos import depositos_por_ciclos
from routes.graficos import casos_por_ciclos


# registro_de_campo
from routes.registro_de_campo.bluprint import registro_de_campo
from routes.registro_de_campo import get_all
from routes.registro_de_campo import by_id
from routes.registro_de_campo import post_one_registro_de_campo
from routes.registro_de_campo import update
from routes.registro_de_campo import update_larvicida
from routes.registro_de_campo import update_adulticida
from routes.registro_de_campo import delete
from routes.registro_de_campo import delete_larvicida
from routes.registro_de_campo import delete_adulticida


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
from routes.usuario import area_de_visita_e_denuncias_agente

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
from routes.artigo import download_img


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
app.register_blueprint(registro_de_campo)
app.register_blueprint(area_para_visita)
app.register_blueprint(denuncia)
app.register_blueprint(blu_artigo)
app.register_blueprint(graficos)
app.register_blueprint(ciclos)

print(app.url_map)

app.config.from_object(Config)

if __name__ == '__main__':
    app.run(debug=True)