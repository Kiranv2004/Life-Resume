def test_register_and_login(client):
    payload = {"email": "test@example.com", "password": "strongpass"}
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 200
    login = client.post("/auth/login", json=payload)
    assert login.status_code == 200
    assert "access_token" in login.json()
