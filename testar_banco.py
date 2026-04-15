import sqlite3
import hashlib

print("=" * 50)
print("TESTE DO BANCO DE DADOS")
print("=" * 50)

conn = sqlite3.connect('condominio.db')
cursor = conn.cursor()

# 1. Verificar tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tabelas = cursor.fetchall()
print("\n📋 Tabelas encontradas:")
for t in tabelas:
    print(f"   - {t[0]}")

# 2. Verificar usuário master
cursor.execute("SELECT * FROM usuarios WHERE login = 'master'")
master = cursor.fetchone()

if master:
    print(f"\n✅ Master encontrado: {master[1]}")
else:
    print("\n❌ Master NÃO encontrado")
    senha_hash = hashlib.sha256('admin123'.encode()).hexdigest()
    cursor.execute("INSERT INTO usuarios (nome, login, senha, tipo) VALUES (?, ?, ?, ?)",
                   ('Administrador Master', 'master', senha_hash, 'master'))
    conn.commit()
    print("✅ Master criado com sucesso!")

# 3. Verificar condomínios
cursor.execute("SELECT * FROM condominios")
condominios = cursor.fetchall()
print(f"\n🏢 Condomínios encontrados: {len(condominios)}")
for c in condominios:
    print(f"   - ID: {c[0]}, Nome: {c[1]}")

# 4. Cadastrar pessoa de teste
try:
    cursor.execute("""
        INSERT INTO pessoas (nome, tipo, apartamento, telefone, condominio_id, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('João Teste', 'morador', '101', '(11) 99999-1111', 1, 'ATIVO'))
    conn.commit()
    print("\n✅ Pessoa cadastrada com sucesso!")
except Exception as e:
    print(f"\n❌ Erro ao cadastrar pessoa: {e}")

# 5. Listar pessoas
cursor.execute("SELECT id, nome, tipo, apartamento FROM pessoas")
pessoas = cursor.fetchall()
print(f"\n📋 Pessoas cadastradas: {len(pessoas)}")
for p in pessoas:
    print(f"   - ID: {p[0]}, Nome: {p[1]}, Tipo: {p[2]}, Apartamento: {p[3]}")

conn.close()
print("\n" + "=" * 50)
print("✅ Teste concluído!")