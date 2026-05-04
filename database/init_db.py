import psycopg2
import psycopg2.extras
import bcrypt
import os
from dotenv import load_dotenv
from contextlib import contextmanager
import urllib.parse as urlparse

load_dotenv()


def get_db_config():
    """Retorna configuração do banco para Render"""

    # Para Render (PostgreSQL)
    database_url = os.environ.get('DATABASE_URL')

    if database_url:
        # Parse da URL do banco
        result = urlparse.urlparse(database_url)
        return {
            'host': result.hostname,
            'database': result.path[1:],
            'user': result.username,
            'password': result.password,
            'port': result.port or 5432
        }

    # Desenvolvimento local
    return {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'database': os.environ.get('DB_NAME', 'condominio_db'),
        'user': os.environ.get('DB_USER', 'condominio_user'),
        'password': os.environ.get('DB_PASSWORD', 'Condominio@2024'),
        'port': os.environ.get('DB_PORT', 5432)
    }


def get_db_connection():
    """Retorna conexão com PostgreSQL"""
    config = get_db_config()

    try:
        conn = psycopg2.connect(
            host=config['host'],
            database=config['database'],
            user=config['user'],
            password=config['password'],
            port=config['port']
        )
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
        raise


@contextmanager
def get_db():
    """Context manager para conexão com banco"""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def hash_senha(senha):
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verificar_senha(senha, hash_senha):
    return bcrypt.checkpw(senha.encode('utf-8'), hash_senha.encode('utf-8'))


def init_db():
    """Inicializa o banco de dados PostgreSQL"""
    conn = get_db_connection()
    cursor = conn.cursor()

    print("=" * 60)
    print("  INICIALIZANDO BANCO DE DADOS POSTGRESQL")
    print("=" * 60)

    # Criar tabela usuarios
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
            condominio_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            nome TEXT NOT NULL,
            documento TEXT,
            placa TEXT,
            telefone TEXT,
            casa TEXT,
            observacao TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (condominio_id) REFERENCES condominios(id) ON DELETE CASCADE
        )
    ''')

    # Tabela de registros
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id SERIAL PRIMARY KEY,
            condominio_id INTEGER NOT NULL,
            pessoa_id INTEGER,
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (condominio_id) REFERENCES condominios(id) ON DELETE CASCADE,
            FOREIGN KEY (pessoa_id) REFERENCES pessoas(id) ON DELETE SET NULL
        )
    ''')

    # Criar índices
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pessoas_condominio ON pessoas(condominio_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_registros_condominio ON registros(condominio_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_registros_data ON registros(data_hora DESC);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);')

    # Criar usuario master
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
    print("=" * 60)


def verificar_conexao():
    """Verifica se a conexão com o banco está funcionando"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"✅ Conectado ao PostgreSQL: {version[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False


if __name__ == "__main__":
    verificar_conexao()