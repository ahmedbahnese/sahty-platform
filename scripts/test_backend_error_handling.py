import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import app


def main():
    client = app.test_client()
    checks = {
        'healthz': client.get('/healthz'),
        'readyz': client.get('/readyz'),
        'api_404': client.get('/api/not-found'),
    }
    for name, response in checks.items():
        print(name, response.status_code, response.is_json, response.get_json(silent=True))
    assert checks['healthz'].status_code == 200
    assert checks['readyz'].status_code in (200, 503)
    assert checks['api_404'].status_code == 404
    assert checks['api_404'].is_json


if __name__ == '__main__':
    main()
