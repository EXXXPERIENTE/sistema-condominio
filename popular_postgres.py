import psycopg2
import os
import bcrypt
import random
from datetime import datetime, timedelta

# No início do arquivo, depois dos imports
import os
import sys

# Garantir que as tabelas sejam criadas automaticamente
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # ... resto do código ...
    except Exception as e:
        print(f"Erro: {e}")
        # Fallback para SQLite em caso de erro
        print("Usando SQLite como fallback...")
        # ... código do SQLite ...

print("Conectando ao PostgreSQL...")
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://condominio_user:Condominio@2024@localhost:5432/condominio_db')

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

print("Inserindo condomínios...")
condominios = [
    ('AMERICA 3', 'Rua das Flores, 123', '#3498db'),
    ('FENIX', 'Av. Brasil, 456', '#e74c3c'),
    ('GRAN PARADISO', 'Rua dos Ipês, 789', '#2ecc71'),
]

for cond in condominios:
    cursor.execute("INSERT INTO condominios (nome, endereco, cor) VALUES (%s, %s, %s) ON CONFLICT (nome) DO NOTHING", cond)

conn.commit()
print("✅ Condomínios inseridos")

print("Inserindo visitantes...")
visitantes = [
    (1, 'João Silva', '123.456.789-00', 'ABC-1234', 'Visitante 1'),
    (1, 'Maria Santos', '987.654.321-00', 'DEF-5678', 'Visitante 2'),
    (1, 'Pedro Oliveira', '456.789.123-00', 'GHI-9012', 'Visitante 3'),
]

for v in visitantes:
    cursor.execute("INSERT INTO pessoas (condominio_id, tipo, nome, documento, placa, observacao) VALUES (%s, 'VISITANTE', %s, %s, %s, %s)", v)

conn.commit()
print("✅ Visitantes inseridos")

print("Inserindo moradores...")
moradores = [
    (1, 'Ana Costa', '789.123.456-00', 'JKL-3456', '101', 'Moradora apto 101'),
    (1, 'Lucas Lima', '321.654.987-00', 'MNO-7890', '202', 'Morador apto 202'),
]

for m in moradores:
    cursor.execute("INSERT INTO pessoas (condominio_id, tipo, nome, documento, placa, casa, observacao) VALUES (%s, 'MORADOR', %s, %s, %s, %s, %s)", m)

conn.commit()
print("✅ Moradores inseridos")

# Inserir usuário Master
senha_hash = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
cursor.execute("SELECT COUNT(*) FROM usuarios WHERE perfil = 'MASTER'")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO usuarios (nome, email, senha, perfil, condominio_id, ativo) VALUES (%s, %s, %s, 'MASTER', NULL, 1)",
                   ('Administrador Master', 'master@condominio.com', senha_hash))
    print("✅ Usuário Master criado")

conn.commit()
cursor.close()
conn.close()

print("=" * 50)
print("✅ Banco de dados populado com sucesso!")
print("🔑 Login Master: master@condominio.com / 123456")
print("=" * 50)