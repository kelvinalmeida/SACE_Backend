from flask import request, jsonify, current_app
import requests
from .bluprint import notificacao
from routes.login.token_required import token_required

@notificacao.route('/notificacao/send_all', methods=['POST'])
@token_required
def send_notification_to_all(current_user):

    # 1. Verificar permissão (ex: apenas supervisores podem enviar)
    if current_user.get("nivel_de_acesso") != "supervisor":
        return jsonify({"error": "Acesso negado: Apenas supervisores podem enviar notificações."}), 403

    # 2. Obter dados da requisição (JSON)
    data = request.json
    title = data.get('title')
    message = data.get('message')
    url = data.get('url')

    # Validar campos obrigatórios da API do PushAlert
    if not all([title, message, url]):
        return jsonify({"error": "Os campos 'title', 'message', e 'url' são obrigatórios."}), 400

    # 3. Obter a API Key da configuração do app
    api_key = current_app.config.get('PUSHALERT_API_KEY')
    if not api_key:
        return jsonify({"error": "Chave da API de notificação não configurada no servidor."}), 500

    # 4. Preparar a requisição para a API do PushAlert
    headers = {
        "Authorization": f"api_key={api_key}"
    }

    # Payload com os dados do formulário (data=)
    payload = {
        "title": title,
        "message": message,
        "url": url
        # Você pode adicionar outros campos opcionais aqui (ex: "icon")
    }

    # 5. Enviar a requisição
    try:
        response = requests.post(
            "https://api.pushalert.co/rest/v1/send",
            headers=headers,
            data=payload
        )

        # Verificar se a API do PushAlert retornou um erro
        response.raise_for_status() 

        # Retornar a resposta do PushAlert (ex: {"success": true, "id": 11})
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        # Capturar erros de conexão ou status HTTP (ex: 401 da API Key)
        if e.response is not None:
            return jsonify({
                "error": "Erro da API PushAlert", 
                "details": e.response.text
            }), e.response.status_code
        else:
            return jsonify({"error": f"Erro ao conectar com a API de notificação: {str(e)}"}), 500