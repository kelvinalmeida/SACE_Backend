from functools import wraps
from flask import request, jsonify, current_app
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1] # "Bearer <token>"

        if not token:
            return jsonify({"error": "O token está faltando!"}), 401

        try:
            # Decodifica o token e guarda os dados
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            # 'data' agora contém: {"username": cpf, "exp": ..., "agente_id": ...}
            
            # Aqui está a mudança principal!
            # Passamos 'data' como o primeiro argumento para a sua função de rota.
            # O nome da variável pode ser qualquer um, mas 'current_user' ou 'token_data' é comum.
            current_user = data 
        
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "O token expirou!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido!"}), 401

        # Executa a função de rota original (send_registro_de_campo)
        # passando o usuário decodificado junto com os outros argumentos
        return f(current_user, *args, **kwargs) 
    return decorated