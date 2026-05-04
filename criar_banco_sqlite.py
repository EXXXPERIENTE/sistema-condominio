import sqlite3
import hashlib
import os

print("📝 Criando banco de dados SQLite...")

# Conectar ao banco (cria automaticamente)
conn = sqlite3.connect('condominio.db')
cursor = conn.cursor()

# Criar tabela usuarios
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    login TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    tipo TEXT NOT NULL,
    condominio_id INTEGER,
    ativo INTEGER DEFAULT 1
)
''')
print("  ✅ Tabela usuarios criada")

# Criar tabela condominios
cursor.execute('''
CREATE TABLE IF NOT EXISTS condominios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    endereco TEXT,
    telefone TEXT
)
''')
print("  ✅ Tabela condominios criada")

# Criar tabela pessoas
cursor.execute('''
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
''')
print("  ✅ Tabela pessoas criada")

# Criar tabela registros
cursor.execute('''
CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pessoa_id INTEGER,
    data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_registro INTEGER,
    observacao TEXT
)
''')
print("  ✅ Tabela registros criada")

# Criar tabela avisos
cursor.execute('''
CREATE TABLE IF NOT EXISTS avisos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    mensagem TEXT NOT NULL,
    tipo TEXT DEFAULT 'info',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo INTEGER DEFAULT 1,
    condominio_id INTEGER
)
''')
print("  ✅ Tabela avisos criada")

# Criar tabela ocorrencias
cursor.execute('''
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
''')
print("  ✅ Tabela ocorrencias criada")

# Criar tabela permissoes
cursor.execute('''
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
''')
print("  ✅ Tabela permissoes criada")

print("\n📝 Inserindo dados iniciais...")

# Inserir condomínios
cursor.execute("INSERT OR IGNORE INTO condominios (id, nome) VALUES (1, 'Condomínio Vila Verde')")
cursor.execute("INSERT OR IGNORE INTO condominios (id, nome) VALUES (2, 'Condomínio Parque das Árvores')")
print("  ✅ Condomínios inseridos")

# Inserir usuário master (senha: admin123)
senha_master = hashlib.sha256('admin123'.encode()).hexdigest()
cursor.execute('''
INSERT OR IGNORE INTO usuarios (id, nome, login, senha, tipo) 
VALUES (1, 'Administrador Master', 'master', ?, 'master')
''', (senha_master,))
print("  ✅ Usuário master criado (login: master / senha: admin123)")

# Inserir permissões master
cursor.execute('''
INSERT OR IGNORE INTO permissoes (usuario_id, pode_apagar_banco, pode_editar_cadastros, 
    pode_deletar_registros, pode_gerenciar_porteiros, pode_criar_avisos, pode_gerenciar_ocorrencias)
VALUES (1, 1, 1, 1, 1, 1, 1)
''')
print("  ✅ Permissões master inseridas")

# Inserir porteiros
senha_porteiro = hashlib.sha256('123456'.encode()).hexdigest()
cursor.execute('''
INSERT OR IGNORE INTO usuarios (id, nome, login, senha, tipo, condominio_id) 
VALUES (2, 'João Porteiro', 'joao', ?, 'porteiro', 1)
''', (senha_porteiro,))
cursor.execute("INSERT OR IGNORE INTO permissoes (usuario_id, pode_editar_cadastros) VALUES (2, 1)")
print("  ✅ Porteiro João criado (login: joao / senha: 123456)")

cursor.execute('''
INSERT OR IGNORE INTO usuarios (id, nome, login, senha, tipo, condominio_id) 
VALUES (3, 'Maria Porteira', 'maria', ?, 'porteiro', 2)
''', (senha_porteiro,))
cursor.execute("INSERT OR IGNORE INTO permissoes (usuario_id, pode_editar_cadastros) VALUES (3, 1)")
print("  ✅ Porteira Maria criada (login: maria / senha: 123456)")

# Inserir pessoas exemplo
cursor.execute('''
INSERT OR IGNORE INTO pessoas (nome, tipo, apartamento, telefone, condominio_id, status) 
VALUES ('Ana Silva', 'morador', '101', '(11) 99999-1111', 1, 'ATIVO')
''')
cursor.execute('''
INSERT OR IGNORE INTO pessoas (nome, tipo, apartamento, telefone, condominio_id, status) 
VALUES ('Carlos Souza', 'morador', '202', '(11) 99999-2222', 1, 'ATIVO')
''')
cursor.execute('''
INSERT OR IGNORE INTO pessoas (nome, tipo, apartamento, telefone, condominio_id, status) 
VALUES ('Mariana Oliveira', 'morador', '303', '(11) 99999-3333', 2, 'ATIVO')
''')
print("  ✅ Pessoas exemplo inseridas")

# Commitar e fechar
conn.commit()
conn.close()

print("\n" + "=" * 50)
print("✅ BANCO DE DADOS CRIADO COM SUCESSO!")
print("=" * 50)
print("\n🔑 CREDENCIAIS DE ACESSO:")
print("   👑 Master: master / admin123")
print("   👔 Porteiro: joao / 123456")
print("   👔 Porteiro: maria / 123456")
print("\n📁 Arquivo: condominio.db")
print("=" * 50)