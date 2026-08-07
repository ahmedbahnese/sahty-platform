"""WSGI entry point for production servers such as Gunicorn."""

from main import app as application

app = application