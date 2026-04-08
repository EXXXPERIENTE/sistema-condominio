import mysql.connector

# Lista de senhas comuns para testar
senhas = ['', 'root', '123456', 'password', 'mysql', 'admin', 'senha', '1234', 'usbw', '123', 'admin123']

print("🔍 Testando conexão MySQL...")
print("-" * 40)

for senha in senhas:
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=senha
        )
        print(f"✅ SENHA ENCONTRADA: '{senha}'")
        conn.close()
        break
    except:
        print(f"❌ Senha '{senha}' - incorreta")