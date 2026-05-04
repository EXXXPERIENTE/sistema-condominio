import sqlite3
import bcrypt
import os

# Caminho do banco de dados no Render
DB_PATH = '/opt/render/project/src/condominio.db'


# Para desenvolvimento local, descomente a linha abaixo e comente a de cima
# DB_PATH = 'condominio.db'

def get_db():
    """Retorna conexão com o banco de dados SQLite"""
    return sqlite3.connect(DB_PATH)


def hash_senha(senha):
    """Criptografa senha com bcrypt"""
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verificar_senha(senha, hash_senha):
    """Verifica senha com bcrypt"""
    return bcrypt.checkpw(senha.encode('utf-8'), hash_senha.encode('utf-8'))


def init_db():
    """Inicializa o banco de dados SQLite com todas as tabelas"""
    conn = get_db()
    cursor = conn.cursor()

    print("=" * 60)
    print("  INICIALIZANDO BANCO DE DADOS SQLITE")
    print("=" * 60)

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

    # Tabela de registros (completa)
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

    # Criar índices para melhor performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pessoas_condominio ON pessoas(condominio_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pessoas_nome ON pessoas(nome);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_registros_condominio ON registros(condominio_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_registros_data ON registros(data_hora DESC);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_registros_tipo ON registros(tipo);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);')

    # Verificar se existe usuario master
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE perfil = 'MASTER'")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO usuarios (nome, email, senha, perfil, condominio_id, ativo)
            VALUES (?, ?, ?, 'MASTER', NULL, 1)
        ''', ('Administrador Master', 'master@condominio.com', hash_senha('123456')))
        print("✅ Usuário Master criado!")

    # Criar condomínio padrão se não existir
    cursor.execute("SELECT COUNT(*) FROM condominios")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO condominios (nome, endereco, cor)
            VALUES (?, ?, ?)
        ''', ('AMERICA 3', 'Rua das Flores, 123, Jardim America', '#3498db'))
        print("✅ Condomínio padrão criado!")

    conn.commit()

    # Verificar se tudo foi criado corretamente
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM condominios")
    total_condominios = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pessoas")
    total_pessoas = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM registros")
    total_registros = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    print("✅ Banco de dados SQLite inicializado com sucesso!")
    print(f"📊 Estatísticas:")
    print(f"   👥 Usuários: {total_usuarios}")
    print(f"   🏘️ Condomínios: {total_condominios}")
    print(f"   👤 Pessoas: {total_pessoas}")
    print(f"   📋 Registros: {total_registros}")
    print("🔑 Login Master: master@condominio.com / 123456")
    print("=" * 60)


def verificar_conexao():
    """Verifica se a conexão com o banco está funcionando"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"✅ Conectado ao SQLite versão: {version}")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False


def backup_banco():
    """Faz backup do banco de dados"""
    import shutil
    from datetime import datetime

    backup_dir = os.path.join(os.path.dirname(DB_PATH), 'backups')
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f'backup_{timestamp}.db')

    shutil.copy2(DB_PATH, backup_file)
    print(f"✅ Backup criado: {backup_file}")
    return backup_file


def restaurar_backup(backup_file):
    """Restaura backup do banco"""
    import shutil

    if not os.path.exists(backup_file):
        print(f"❌ Arquivo de backup não encontrado: {backup_file}")
        return False

    shutil.copy2(backup_file, DB_PATH)
    print(f"✅ Backup restaurado: {backup_file}")
    return True


if __name__ == "__main__":
    verificar_conexao()
    init_db()