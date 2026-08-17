"""Regression coverage for platform startup and health contracts."""


def test_liveness_endpoint(client):
    response = client.get('/healthz')

    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}


def test_readiness_endpoint_reports_database(client):
    response = client.get('/readyz')

    assert response.status_code == 200
    assert response.get_json() == {'status': 'ready', 'database': 'ok'}


def test_api_health_endpoint_reports_database(client):
    response = client.get('/api/health')

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['status'] == 'ok'
    assert payload['database'] == 'ok'


def test_spa_root_is_served_after_frontend_build(client):
    response = client.get('/')

    assert response.status_code == 200
    assert 'text/html' in response.content_type
