from flask import Flask, render_template
from flask_cors import CORS
from config import Config
from routes.login.login import login
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

import os # Adicione esta importação no topo do arquivo
# Modifique a importação do Flask para incluir send_from_directory
from flask import Flask, render_template, send_from_directory 
from flask_cors import CORS
from config import Config

import os
from dotenv import load_dotenv

load_dotenv('config.env')

# doencas_confirmadas
from routes.doentes_confirmados.bluprint import doentes_confirmados_bp
from routes.doentes_confirmados import post_batch, get_all, get_by_id, update, delete

# notificacoes
from routes.notificacoes.bluprint import notificacao
from routes.notificacoes import send_all

# ciclos
from routes.ciclo.bluprint import ciclos
from routes.ciclo import get_anos_and_ciclos
from routes.ciclo import criar_ciclo
from routes.ciclo import finalizar_ciclo
from routes.ciclo import status

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
from routes.graficos import heatmap_data
from routes.graficos import heatmap_painel
from routes.graficos import heatmap_data_latest
from routes.graficos import heatmap_painel_latest
from routes.graficos import summary_pdf
from routes.graficos import total_doentes_confirmados

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
from routes.registro_de_campo import casos_confirmados
from routes.registro_de_campo import get_by_ciclo

# area_de_visita
from routes.area_de_visita.bluprint import area_para_visita
from routes.area_de_visita import get_all
from routes.area_de_visita import get_by_id
from routes.area_de_visita import post_several_areas
from routes.area_de_visita import update
from routes.area_de_visita import delete
from routes.area_de_visita import get_registros_by_area

# usuario
from routes.usuario.bluprint import usuario
from routes.usuario import post_sereval_users
from routes.usuario import get_all_users
from routes.usuario import get_agente_by_id
from routes.usuario import get_supervisor_by_id
from routes.usuario import area_de_visita_e_denuncias_agente
from routes.usuario import update_agente
from routes.usuario import update_supervisor
from routes.usuario import delete_agente
from routes.usuario import delete_supervisor

# denuncia
from routes.denuncia.bluprint import denuncia
from routes.denuncia import post_one_denuncia
from routes.denuncia import get_all
from routes.denuncia import by_id
from routes.denuncia import update
from routes.denuncia import delete

# artigo
from routes.artigo.bluprint import blu_artigo
from routes.artigo import post_one_artigo
from routes.artigo import get_all
from routes.artigo import by_id
from routes.artigo import download_img
from routes.artigo import update
from routes.artigo import delete


app = Flask(__name__)


CORS(app)

API_URL = "/static/openapi.yaml"
# API_URL = os.getenv('API_URL')
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
app.register_blueprint(notificacao)
app.register_blueprint(doentes_confirmados_bp)

print(app.url_map)

app.config.from_object(Config)

@app.route('/sw.js')
def serve_sw():
    """Serve o arquivo sw.js a partir do diretório static na raiz."""
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sw.js')

@app.route('/', methods=['GET'])
def rota_de_teste():
    """ Rota de teste para servir um HTML. """
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)