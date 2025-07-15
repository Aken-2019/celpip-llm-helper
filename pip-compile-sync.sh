source venv/bin/activate
pip-compile requirements-dev.in -o requirements-dev.txt
pip-sync requirements-dev.txt

pip-compile requirements.in -o requirements.txt