# Activa el virtualenv y arranca Waitress para servir la app WSGI
Push-Location $PSScriptRoot
. .\.venv\Scripts\Activate.ps1
python run_waitress.py
Pop-Location
