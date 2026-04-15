#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import sqlite3
import hashlib

print("=" * 60)
print("  INICIANDO SISTEMA DE CONDOMÍNIOS NO RENDER")
print("=" * 60)

# 1. Configurar o banco de dados SQLite
db_path = 'condominio.db'

# Forçar a recriação do banco para evitar inconsistências
if os.path.exists(db_path):
    print(f"🗑️ Banco antigo encontrado. Removendo...")
    os.remove(db_path)
    print(f"   Banco antigo removido.")

print(f"📁 Criando novo banco de dados: {db_path}")

# Criar conexão e tabelas
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Tabela de usuários (essencial para o login)
cursor.execute("""
    CREATE TABLE usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        login TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        tipo TEXT NOT NULL,
        condominio_id INTEGER,
        ativo INTEGER DEFAULT 1
    )
""")

# Tabela de condomínios
cursor.execute("""
    CREATE TABLE condominios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        endereco TEXT,
        telefone TEXT
    )
""")

# Inserir dados iniciais
print("📝 Inserindo dados iniciais...")

# Condomínio padrão
cursor.execute("INSERT INTO condominios (id, nome) VALUES (1, 'Condomínio Vila Verde')")
cursor.execute("INSERT INTO condominios (id, nome) VALUES (2, 'Condomínio Parque das Árvores')")

# Usuário Master (login: master, senha: admin123)
senha_master = hashlib.sha256('admin123'.encode()).hexdigest()
cursor.execute("""
    INSERT INTO usuarios (id, nome, login, senha, tipo)
    VALUES (1, 'Administrador Master', 'master', ?, 'master')
""", (senha_master,))
print("   ✅ Usuário MASTER criado.")

# Porteiros de exemplo
senha_porteiro = hashlib.sha256('123456'.encode()).hexdigest()
cursor.execute("""
    INSERT INTO usuarios (id, nome, login, senha, tipo, condominio_id)
    VALUES (2, 'João Porteiro', 'joao', ?, 'porteiro', 1)
""", (senha_porteiro,))
cursor.execute("""
    INSERT INTO usuarios (id, nome, login, senha, tipo, condominio_id)
    VALUES (3, 'Maria Porteira', 'maria', ?, 'porteiro', 2)
""", (senha_porteiro,))
print("   ✅ Porteiros de exemplo criados.")

conn.commit()
conn.close()

print("✅ Banco de dados criado e populado com sucesso!")
print("=" * 60)

# 2. Importar e iniciar o aplicativo Flask
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from web_app.api import app

if __name__ == '__main__':
    print()
    print("🌐 Servidor iniciado!")
    print("📱 Acesse: https://sistema-condominio-5i53.onrender.com")
    print()
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=10000)