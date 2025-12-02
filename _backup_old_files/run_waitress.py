"""Tiny runner for Waitress WSGI server.
Usage: python run_waitress.py
This serves the Django WSGI app (config.wsgi.application) on 127.0.0.1:8000.
"""
from waitress import serve
from config.wsgi import application

if __name__ == '__main__':
    print('Starting Waitress on 127.0.0.1:8000')
    serve(application, host='127.0.0.1', port=8000)
