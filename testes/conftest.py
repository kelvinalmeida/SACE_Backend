import pytest
import os
from app import app as flask_app  # Import your main app instance

# --- 1. Point to the new 'db-test' service ---
# The hostname 'db-test' matches your compose.yaml service name
TEST_DATABASE_URL = "postgresql://user:secret@db-test:5432/postgres"

@pytest.fixture(scope='session')
def app():
    """
    Fixture for the Flask app instance.
    Configures the app for testing and uses the test database.
    """
    # Set environment variable *before* app is configured
    os.environ['DATABASE_URL'] = TEST_DATABASE_URL
    
    # Configure the app for testing
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "my-test-secret-key",
        "SQLALCHEMY_DATABASE_URI": TEST_DATABASE_URL
    })

    # We don't need to create/drop the DB here anymore,
    # the db-test container handles it!
    yield flask_app


@pytest.fixture(scope='function')
def client(app):
    """
    Fixture for the Flask test client.
    """
    return app.test_client()


@pytest.fixture(scope='function')
def auth_client(client):
    """
    Fixture for an *authenticated* test client.
    Logs in as the 'admin' supervisor user from your backup.sql.
    """
    response = client.post('/login', json={
        # conta do supervisor do seu backup.sql
        "username": "56789012345",
        "password": "senhaFin159"
    })
    
    if response.status_code != 200:
        pytest.fail("Failed to authenticate test client. Is the db-test service running?")

    token = response.json['token']
    
    # Set the Authorization header for future requests
    client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    
    return client

@pytest.fixture(scope='function')
def agente_client(client):
    """
    Cria um fixture de cliente autenticado como um AGENTE.
    Isso é necessário porque a rota de registro de campo exige um agente.
    
    Ele usa o usuário 'João da Silva' (agente_id=1) do seu arquivo backup.sql.
    """
    # Login como o Agente (cpf: '12345678901', senha: 'senhaSegura123')
    response = client.post('/login', json={
        "username": "12345678901",
        "password": "senhaSegura123"
    })
    
    if response.status_code != 200:
        pytest.fail("Falha ao autenticar o cliente agente. Verifique os dados no backup.sql.")

    token = response.json['token']
    
    # Adiciona o token de agente ao cabeçalho
    client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    
    return client


@pytest.fixture(scope='function')
def public_client(app):
    c = app.test_client()
    c.environ_base.pop('HTTP_AUTHORIZATION', None)
    return c
