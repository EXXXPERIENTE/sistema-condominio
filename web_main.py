#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import sqlite3

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Garantir que o banco de dados tem permissões corretas
db_path = 'condominio.db'

# Verificar se o banco existe e tem permissões
if os.path.exists(db_path):
    # Garantir permissões de escrita
    os.chmod(db_path, 0o666)
    print(f"✅ Permissões ajustadas para {db_path}")
else:
    print(f"⚠️ Banco {db_path} não encontrado, será criado na primeira execução")

from web_app.api import app

if __name__ == '__main__':
    print()
    print("=" * 60)
    print("  SISTEMA DE CONTROLE DE CONDOMÍNIOS - VERSÃO WEB")
    print("=" * 60)
    print()
    print("🌐 Servidor iniciado!")
    print("📱 Acesse: http://localhost:5000")
    print()
    print("=" * 60)

    app.run(debug=False, host='0.0.0.0', port=5000)