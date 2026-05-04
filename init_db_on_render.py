import sqlite3
import psycopg2
import os
import bcrypt


def init_render_db():
    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        print("❌ DATABASE_URL não configurada!")
        return

    print(f"Conectando ao PostgreSQL...")

    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

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

        # Criar tabela condominios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS condominios (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL UNIQUE,
                endereco TEXT,
                cor TEXT DEFAULT '#3498db',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Criar usuario master
        senha_hash = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE perfil = 'MASTER'")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO usuarios (nome, email, senha, perfil, condominio_id, ativo)
                VALUES (%s, %s, %s, 'MASTER', NULL, 1)
            ''', ('Administrador Master', 'master@condominio.com', senha_hash))
            print("✅ Usuário Master criado!")

        conn.commit()
        cursor.close()
        conn.close()

        print("✅ Banco PostgreSQL inicializado com sucesso!")
        print("🔑 Login: master@condominio.com / 123456")

    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    init_render_db()