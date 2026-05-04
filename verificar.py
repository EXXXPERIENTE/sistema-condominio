import sqlite3

conn = sqlite3.connect('condominio.db')
cursor = conn.cursor()

print("=" * 60)
print("VERIFICANDO DADOS DO BANCO")
print("=" * 60)

# Verificar visitantes
print("\n📋 VISITANTES:")
cursor.execute("SELECT id, nome, documento, placa, casa FROM pessoas WHERE tipo = 'VISITANTE' LIMIT 10")
visitantes = cursor.fetchall()
if visitantes:
    for v in visitantes:
        print(f"   ID: {v[0]} | Nome: {v[1]} | Doc: {v[2]} | Placa: {v[3]} | Casa: {v[4]}")
else:
    print("   Nenhum visitante encontrado!")

# Verificar moradores
print("\n📋 MORADORES:")
cursor.execute("SELECT id, nome, documento, telefone, casa FROM pessoas WHERE tipo = 'MORADOR' LIMIT 10")
moradores = cursor.fetchall()
if moradores:
    for m in moradores:
        print(f"   ID: {m[0]} | Nome: {m[1]} | Doc: {m[2]} | Tel: {m[3]} | Casa: {m[4]}")
else:
    print("   Nenhum morador encontrado!")

# Verificar registros
print("\n📋 REGISTROS:")
cursor.execute("SELECT id, tipo, titulo, status FROM registros LIMIT 10")
registros = cursor.fetchall()
if registros:
    for r in registros:
        print(f"   ID: {r[0]} | Tipo: {r[1]} | Título: {r[2]} | Status: {r[3]}")
else:
    print("   Nenhum registro encontrado!")

# Contagem total
cursor.execute("SELECT COUNT(*) FROM pessoas WHERE tipo = 'VISITANTE'")
total_visitantes = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM pessoas WHERE tipo = 'MORADOR'")
total_moradores = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM registros")
total_registros = cursor.fetchone()[0]

print("\n" + "=" * 60)
print("📊 ESTATÍSTICAS:")
print(f"   Total Visitantes: {total_visitantes}")
print(f"   Total Moradores: {total_moradores}")
print(f"   Total Registros: {total_registros}")
print("=" * 60)

conn.close()