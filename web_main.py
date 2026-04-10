#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_app.api import app
from database.db_manager import DatabaseManager

if __name__ == '__main__':
    # Criar banco de dados se não existir
    print("=" * 60)
    print("  INICIANDO SISTEMA DE CONDOMÍNIOS")
    print("=" * 60)

    # Verificar/Criar banco de dados
    db = DatabaseManager()
    if not os.path.exists('condominio.db'):
        print("📁 Criando banco de dados...")
        db.create_database()
        print("✅ Banco de dados criado com sucesso!")
    else:
        print("📁 Banco de dados já existe")

    print()
    print("🌐 Servidor iniciado!")
    print("📱 Acesse: http://localhost:5000")
    print()
    print("=" * 60)

    app.run(debug=False, host='0.0.0.0', port=5000)