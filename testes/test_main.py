# tests/test_main.py

def test_login_success(client):
    """
    Tests if a valid supervisor can log in.
    Uses the 'admin' user from backup.sql
    """
    response = client.post('/login', json={
        "username": "admin",
        "password": "123456"
    })
    
    assert response.status_code == 200
    data = response.json
    assert data['username'] == 'admin'
    assert data['nivel_de_acesso'] == 'supervisor'
    assert 'token' in data

def test_login_failure(client):
    """
    Tests if login fails with incorrect credentials.
    """
    response = client.post('/login', json={
        "username": "admin",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401

def test_status_route_unauthenticated(client):
    """
    Tests that a protected route returns 401 without a token.
    """
    response = client.get('/ciclos/status')
    assert response.status_code == 401 # 401 Unauthorized

def test_status_route_authenticated(auth_client):
    """
    Tests that a protected route works with a valid token
    by using the 'auth_client' fixture.
    """
    response = auth_client.get('/ciclos/status')
    assert response.status_code == 200
    data = response.json
    assert 'status' in data
    
    # Based on your backup, the last ciclo is active
    assert data['status'] == 'ativo'