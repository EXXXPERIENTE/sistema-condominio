#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# No início do web_main.py, antes de rodar o app
from database.db_manager import DatabaseManager
db = DatabaseManager()
if not db.connect():
    db.create_database()
    db.connect()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_app.api import app

if __name__ == '__main__':
    print("=" * 60)
    print("  SISTEMA DE CONTROLE DE CONDOMÍNIOS - VERSÃO WEB")
    print("=" * 60)
    print()
    print("🌐 Servidor iniciado!")
    print("📱 Acesse no seu celular: http://SEU_IP:5000")
    print("💻 Acesse no computador: http://localhost:5000")
    print()
    print("🔑 Credenciais:")
    print("   Master: master / admin123")
    print("   Porteiro: credenciais fornecidas pelo administrador")
    print()
    print("=" * 60)

    app.run(debug=False, host='0.0.0.0', port=5000)