import sqlite3
import bcrypt
import os

DB_PATH = 'condominio.db'


def hash_senha(senha):
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def corrigir_banco():
    # Se o banco existir, deletar
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Banco antigo removido!")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Criar tabela usuarios com a coluna ativo
    cursor.execute('''
        CREATE TABLE usuarios (
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

    # Criar tabela condominios
    cursor.execute('''
        CREATE TABLE condominios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            endereco TEXT,
            cor TEXT DEFAULT '#3498db',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Criar tabela pessoas
    cursor.execute('''
        CREATE TABLE pessoas (
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
            FOREIGN KEY (condominio_id) REFERENCES condominios(id)
        )
    ''')

    # Criar tabela registros
    cursor.execute('''
        CREATE TABLE registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            condominio_id INTEGER NOT NULL,
            pessoa_id INTEGER,
            tipo TEXT NOT NULL,
            titulo TEXT NOT NULL,
            descricao TEXT,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'AGUARDANDO',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (condominio_id) REFERENCES condominios(id),
            FOREIGN KEY (pessoa_id) REFERENCES pessoas(id)
        )
    ''')

    # Inserir condomínios padrão
    condominios = [
        'AMERICA 3', 'FENIX', 'GRAN PARADISO', 'M. RIBAAS',
        'VI HAEE ANAZONA', 'PASSAROS II', 'CARLA AZUL III',
        'MIRAR BEN', 'MOVERELLO'
    ]

    cores = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
             '#1abc9c', '#e67e22', '#34495e', '#16a085']

    for i, cond in enumerate(condominios):
        cursor.execute("INSERT INTO condominios (nome, cor) VALUES (?, ?)",
                       (cond, cores[i % len(cores)]))

    # Inserir usuário MASTER
    cursor.execute('''
        INSERT INTO usuarios (nome, email, senha, perfil, condominio_id, ativo)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('Administrador Master', 'master@condominio.com', hash_senha('123456'), 'MASTER', None, 1))

    # Buscar IDs dos condomínios
    cursor.execute("SELECT id FROM condominios")
    conds = cursor.fetchall()

    # Inserir porteiros de exemplo
    for i, cond in enumerate(conds[:3]):
        cursor.execute('''
            INSERT INTO usuarios (nome, email, senha, perfil, condominio_id, ativo)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
        f'Porteiro do Condominio {i + 1}', f'porteiro{i + 1}@teste.com', hash_senha('123456'), 'PORTEIRO', cond[0], 1))

    conn.commit()
    conn.close()

    print("✅ Banco de dados corrigido com sucesso!")
    print("\n🔑 Credenciais:")
    print("   Master: master@condominio.com / 123456")
    print("   Porteiro 1: porteiro1@teste.com / 123456")
    print("   Porteiro 2: porteiro2@teste.com / 123456")
    print("   Porteiro 3: porteiro3@teste.com / 123456")
    print("\n🎨 Condomínios criados com cores diferentes!")


if __name__ == "__main__":
    corrigir_banco()