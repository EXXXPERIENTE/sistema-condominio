import sqlite3
import os
import bcrypt

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'condominio.db')


def get_db():
    return sqlite3.connect(DB_PATH)


def hash_senha(senha):
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verificar_senha(senha, hash_senha):
    return bcrypt.checkpw(senha.encode('utf-8'), hash_senha.encode('utf-8'))


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Tabela de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT NOT NULL,
            condominio_id INTEGER,
            ativo INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de condominios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS condominios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            endereco TEXT,
            cor TEXT DEFAULT '#3498db',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de pessoas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pessoas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            condominio_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            nome TEXT NOT NULL,
            documento TEXT,
            placa TEXT,
            telefone TEXT,
            casa TEXT,
            observacao TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (condominio_id) REFERENCES condominios(id) ON DELETE CASCADE
        )
    ''')

    # Tabela de registros COMPLETA com todas as colunas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            condominio_id INTEGER NOT NULL,
            pessoa_id INTEGER,
            tipo TEXT NOT NULL,
            titulo TEXT NOT NULL,
            descricao TEXT,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'AGUARDANDO',
            cor TEXT DEFAULT '#3498db',
            acao TEXT DEFAULT 'LIBERADO',
            hora_entrada DATETIME,
            hora_saida DATETIME,
            visitando TEXT,
            entregador TEXT,
            destinatario TEXT,
            quem_recebeu TEXT,
            data_retirada DATETIME,
            quem_retirou TEXT,
            quem_liberou TEXT,
            registrado_por TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (condominio_id) REFERENCES condominios(id) ON DELETE CASCADE,
            FOREIGN KEY (pessoa_id) REFERENCES pessoas(id) ON DELETE SET NULL
        )
    ''')

    # Verificar se existe usuario master
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE perfil = 'MASTER'")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO usuarios (nome, email, senha, perfil, condominio_id, ativo)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Administrador Master', 'master@condominio.com', hash_senha('123456'), 'MASTER', None, 1))
        print("✅ Usuário Master criado!")

    conn.commit()
    conn.close()
    print("✅ Banco de dados inicializado com sucesso!")
    print("🔑 Login Master: master@condominio.com / 123456")