from flask import Flask
from flask_cors import CORS
from config import Config
from routes.login.login import login

app = Flask(__name__)


CORS(app)

app.register_blueprint(login)

app.config.from_object(Config)

if __name__ == '__main__':
    app.run(debug=True)