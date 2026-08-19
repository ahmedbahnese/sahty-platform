"""
Test configuration — forces SQLite in-memory so tests never touch the real DB.
"""
import os
import uuid
import random

# Override database URL before importing app so SQLAlchemy never connects to prod
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ.setdefault('SESSION_SECRET', 'test-secret-key-for-testing-only')
# Tests use the in-memory limiter and must not be treated as a production boot.
os.environ.setdefault('FLASK_ENV', 'development')

import pytest
from main import app as flask_app
from src.models.user import db as _db


@pytest.fixture(scope='session')
def app():
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,
        'JWT_SECRET_KEY': 'test-jwt-secret',
        'DEBUG': False,
    })
    ctx = flask_app.app_context()
    ctx.push()
    _db.create_all()
    yield flask_app
    _db.drop_all()
    ctx.pop()


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()


def unique_nid():
    """Generate a unique 14-digit national ID."""
    return '2' + ''.join(str(random.randint(0, 9)) for _ in range(13))
