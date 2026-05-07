import os
import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    """Retorna conexão com o banco de dados (PostgreSQL ou SQLite)"""
    database_url = os.environ.get('DATABASE_URL')

    if database_url:
        # PostgreSQL (Railway) - ADICIONE O RealDictCursor AQUI
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        conn.autocommit = True
        return conn, 'postgresql'
    else:
        # SQLite (desenvolvimento local)
        import sqlite3
        conn = sqlite3.connect('database/condominio.db')
        conn.row_factory = sqlite3.Row
        return conn, 'sqlite'

def get_db():
    """Versão simplificada para compatibilidade"""
    conn, _ = get_db_connection()
    return conn


def is_postgresql():
    """Verifica se está usando PostgreSQL"""
    return os.environ.get('DATABASE_URL') is not None


def hash_senha(senha):
    """Gera hash da senha usando bcrypt"""
    if isinstance(senha, str):
        senha = senha.encode('utf-8')
    return bcrypt.hashpw(senha, bcrypt.gensalt()).decode('utf-8')


def verificar_senha(senha, hash_senha_db):
    """Verifica se a senha corresponde ao hash"""
    if isinstance(senha, str):
        senha = senha.encode('utf-8')
    if isinstance(hash_senha_db, str):
        hash_senha_db = hash_senha_db.encode('utf-8')
    return bcrypt.checkpw(senha, hash_senha_db)


def execute_query(cursor, query, params=None):
    """Executa query adaptando placeholders para PostgreSQL ou SQLite"""
    if params is None:
        params = []

    # Se for SQLite, converte %s para ?
    if not is_postgresql():
        query = query.replace('%s', '?')

    if params:
        return cursor.execute(query, params)
    else:
        return cursor.execute(query)


def init_db():
    """Inicializa as tabelas do banco de dados"""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()

    print(f"🗄️ Inicializando banco de dados ({db_type})")

    if is_postgresql():
        # PostgreSQL - criar tabelas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                perfil TEXT DEFAULT 'PORTEIRO',
                condominio_id INTEGER,
                ativo INTEGER DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS condominios (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                endereco TEXT,
                cor TEXT DEFAULT '#007bff',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pessoas (
                id SERIAL PRIMARY KEY,
                condominio_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                bloco TEXT,
                numero TEXT,
                documento TEXT,
                telefone TEXT,
                email TEXT,
                observacoes TEXT,
                status TEXT DEFAULT 'morador',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (condominio_id) REFERENCES condominios(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registros (
                id SERIAL PRIMARY KEY,
                condominio_id INTEGER NOT NULL,
                pessoa_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                descricao TEXT,
                usuario_nome TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (condominio_id) REFERENCES condominios(id),
                FOREIGN KEY (pessoa_id) REFERENCES pessoas(id)
            )
        """)
    else:
        # SQLite - criar tabelas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                perfil TEXT DEFAULT 'PORTEIRO',
                condominio_id INTEGER,
                ativo INTEGER DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS condominios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                endereco TEXT,
                cor TEXT DEFAULT '#007bff',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pessoas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                condominio_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                bloco TEXT,
                numero TEXT,
                documento TEXT,
                telefone TEXT,
                email TEXT,
                observacoes TEXT,
                status TEXT DEFAULT 'morador',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (condominio_id) REFERENCES condominios(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                condominio_id INTEGER NOT NULL,
                pessoa_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                descricao TEXT,
                usuario_nome TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (condominio_id) REFERENCES condominios(id),
                FOREIGN KEY (pessoa_id) REFERENCES pessoas(id)
            )
        """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Banco de dados inicializado com sucesso!")


def criar_admin_padrao():
    """Cria usuário administrador padrão se não existir"""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()

    email = "admin@admin.com"
    senha_hash = hash_senha("admin123")

    # Verificar se admin já existe
    if is_postgresql():
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
    else:
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))

    if not cursor.fetchone():
        if is_postgresql():
            cursor.execute(
                "INSERT INTO usuarios (nome, email, senha, perfil) VALUES (%s, %s, %s, %s)",
                ("Administrador", email, senha_hash, "MASTER")
            )
        else:
            cursor.execute(
                "INSERT INTO usuarios (nome, email, senha, perfil) VALUES (?, ?, ?, ?)",
                ("Administrador", email, senha_hash, "MASTER")
            )
        conn.commit()
        print("✅ Usuário admin criado: admin@admin.com / admin123")
    else:
        print("ℹ️ Usuário admin já existe")

    cursor.close()
    conn.close()


# Inicializar ao importar
try:
    init_db()
    criar_admin_padrao()
except Exception as e:
    print(f"⚠️ Erro na inicialização: {e}")
    import traceback

    traceback.print_exc()