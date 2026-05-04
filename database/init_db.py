import psycopg2
import os
import bcrypt
from psycopg2.extras import RealDictCursor
import sys


# Configuração do banco de dados
def get_db_connection():
    """Retorna conexão com PostgreSQL"""

    # Para produção (PythonAnywhere)
    if 'PYTHONANYWHERE_DOMAIN' in os.environ:
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'seuusuario.postgres.pythonanywhere-services.com'),
            database=os.environ.get('DB_NAME', 'seuusuario$condominio'),
            user=os.environ.get('DB_USER', 'seuusuario'),
            password=os.environ.get('DB_PASSWORD', 'sua_senha')
        )
    else:
        # Para desenvolvimento local
        conn = psycopg2.connect(
            host='localhost',
            database='condominio_db',
            user='condominio_user',
            password='sua_senha_forte'
        )

    return conn


def get_db():
    """Retorna conexão (compatível com código existente)"""
    return get_db_connection()


def hash_senha(senha):
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verificar_senha(senha, hash_senha):
    return bcrypt.checkpw(senha.encode('utf-8'), hash_senha.encode('utf-8'))


def init_db():
    """Inicializa o banco de dados PostgreSQL"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Criar extensão UUID (opcional)
    cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    # Tabela de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT NOT NULL,
            condominio_id INTEGER,
            ativo INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de condominios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS condominios (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL UNIQUE,
            endereco TEXT,
            cor TEXT DEFAULT '#3498db',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de pessoas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pessoas (
            id SERIAL PRIMARY KEY,
            condominio_id INTEGER NOT NULL REFERENCES condominios(id) ON DELETE CASCADE,
            tipo TEXT NOT NULL,
            nome TEXT NOT NULL,
            documento TEXT,
            placa TEXT,
            telefone TEXT,
            casa TEXT,
            observacao TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de registros
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id SERIAL PRIMARY KEY,
            condominio_id INTEGER NOT NULL REFERENCES condominios(id) ON DELETE CASCADE,
            pessoa_id INTEGER REFERENCES pessoas(id) ON DELETE SET NULL,
            tipo TEXT NOT NULL,
            titulo TEXT NOT NULL,
            descricao TEXT,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'AGUARDANDO',
            cor TEXT DEFAULT '#3498db',
            acao TEXT DEFAULT 'LIBERADO',
            hora_entrada TIMESTAMP,
            hora_saida TIMESTAMP,
            visitando TEXT,
            entregador TEXT,
            destinatario TEXT,
            quem_recebeu TEXT,
            data_retirada TIMESTAMP,
            quem_retirou TEXT,
            quem_liberou TEXT,
            registrado_por TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Criar índices para performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pessoas_condominio ON pessoas(condominio_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_registros_condominio ON registros(condominio_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_registros_data ON registros(data_hora DESC);')

    # Verificar se existe usuario master
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE perfil = 'MASTER'")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO usuarios (nome, email, senha, perfil, condominio_id, ativo)
            VALUES (%s, %s, %s, 'MASTER', NULL, 1)
        ''', ('Administrador Master', 'master@condominio.com', hash_senha('123456')))
        print("✅ Usuário Master criado!")

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Banco de dados PostgreSQL inicializado com sucesso!")
    print("🔑 Login Master: master@condominio.com / 123456")