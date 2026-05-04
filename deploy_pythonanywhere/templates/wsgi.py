import sys
import os

# Adicionar o caminho do projeto
path = '/home/seuusuario/gestor_sindico'
if path not in sys.path:
    sys.path.append(path)

# Ativar virtual env
activate_this = '/home/seuusuario/.virtualenvs/gestor_sindico/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from app import app as application