import sqlite3

conn = sqlite3.connect('condominio.db')
cursor = conn.cursor()

# Contar antes
cursor.execute("SELECT COUNT(*) FROM registros WHERE tipo = 'TECNICO'")
total_registros = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM pessoas WHERE tipo = 'TECNICO'")
total_pessoas = cursor.fetchone()[0]

print(f"📊 Registros TÉCNICO encontrados: {total_registros}")
print(f"👥 Pessoas TÉCNICO encontradas: {total_pessoas}")

if total_registros > 0 or total_pessoas > 0:
    resposta = input("Deseja remover todos? (s/N): ")
    if resposta.lower() == 's':
        cursor.execute("DELETE FROM registros WHERE tipo = 'TECNICO'")
        cursor.execute("DELETE FROM pessoas WHERE tipo = 'TECNICO'")
        conn.commit()
        print("✅ Removido com sucesso!")
    else:
        print("❌ Operação cancelada.")
else:
    print("✅ Nenhum registro TÉCNICO encontrado.")

conn.close()