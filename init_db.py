import os
import sys
import sqlite3
import hashlib

print("=" * 50)
print("INICIALIZANDO BANCO DE DADOS SQLITE")
print("=" * 50)

db_path = 'condominio.db'

if os.path.exists(db_path):
    print(f"📁 Banco já existe: {db_path}")
else:
    print(f"📁 Criando banco: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Criar tabelas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS condominios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            endereco TEXT,
            telefone TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            login TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            tipo TEXT NOT NULL,
            condominio_id INTEGER,
            ativo INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pessoas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            documento TEXT,
            telefone TEXT,
            veiculo_placa TEXT,
            veiculo_modelo TEXT,
            condominio_id INTEGER,
            apartamento TEXT,
            bloqueado INTEGER DEFAULT 0,
            motivo_bloqueio TEXT,
            status TEXT DEFAULT 'ATIVO'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pessoa_id INTEGER,
            data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usuario_registro INTEGER,
            observacao TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS permissoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            pode_apagar_banco INTEGER DEFAULT 0,
            pode_editar_cadastros INTEGER DEFAULT 1,
            pode_deletar_registros INTEGER DEFAULT 0,
            pode_gerenciar_porteiros INTEGER DEFAULT 0,
            pode_criar_avisos INTEGER DEFAULT 0,
            pode_gerenciar_ocorrencias INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS avisos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            mensagem TEXT NOT NULL,
            tipo TEXT DEFAULT 'info',
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo INTEGER DEFAULT 1,
            condominio_id INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ocorrencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            tipo TEXT DEFAULT 'reclamacao',
            status TEXT DEFAULT 'aberto',
            prioridade TEXT DEFAULT 'media',
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            condominio_id INTEGER,
            responsavel TEXT
        )
    """)

    # Inserir dados iniciais
    print("📝 Inserindo dados iniciais...")

    # Condomínios
    cursor.execute("INSERT OR IGNORE INTO condominios (id, nome) VALUES (1, 'Condomínio Vila Verde')")
    cursor.execute("INSERT OR IGNORE INTO condominios (id, nome) VALUES (2, 'Condomínio Parque das Árvores')")

    # Usuário master
    senha_hash = hashlib.sha256('admin123'.encode()).hexdigest()
    cursor.execute("""
        INSERT OR IGNORE INTO usuarios (id, nome, login, senha, tipo) 
        VALUES (1, 'Administrador Master', 'master', ?, 'master')
    """, (senha_hash,))

    # Permissões master
    cursor.execute("""
        INSERT OR IGNORE INTO permissoes (usuario_id, pode_apagar_banco, pode_editar_cadastros, 
            pode_deletar_registros, pode_gerenciar_porteiros, pode_criar_avisos, pode_gerenciar_ocorrencias)
        VALUES (1, 1, 1, 1, 1, 1, 1)
    """)

    # Porteiros
    senha_porteiro = hashlib.sha256('123456'.encode()).hexdigest()
    cursor.execute("""
        INSERT OR IGNORE INTO usuarios (id, nome, login, senha, tipo, condominio_id) 
        VALUES (2, 'João Porteiro', 'joao', ?, 'porteiro', 1)
    """, (senha_porteiro,))
    cursor.execute("INSERT OR IGNORE INTO permissoes (usuario_id, pode_editar_cadastros) VALUES (2, 1)")

    cursor.execute("""
        INSERT OR IGNORE INTO usuarios (id, nome, login, senha, tipo, condominio_id) 
        VALUES (3, 'Maria Porteira', 'maria', ?, 'porteiro', 2)
    """, (senha_porteiro,))
    cursor.execute("INSERT OR IGNORE INTO permissoes (usuario_id, pode_editar_cadastros) VALUES (3, 1)")

    conn.commit()
    conn.close()

    print("✅ Banco de dados criado com sucesso!")

print("=" * 50)