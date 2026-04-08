import mysql.connector
from mysql.connector import Error


def corrigir_banco():
    # CONFIGURE SUAS CREDENCIAIS DO MySQL AQUI
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',  # Coloque sua senha do MySQL aqui
        'database': 'condominio_db'
    }

    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        print("🔧 Corrigindo estrutura do banco de dados...")

        # 1. Adicionar coluna 'status' na tabela pessoas
        try:
            cursor.execute("ALTER TABLE pessoas ADD COLUMN status VARCHAR(20) DEFAULT 'ATIVO'")
            print("✅ Coluna 'status' adicionada em pessoas")
        except Exception as e:
            if "Duplicate column" in str(e):
                print("⚠️ Coluna 'status' já existe")
            else:
                print(f"⚠️ {e}")

        # 2. Adicionar coluna 'motivo_bloqueio' na tabela pessoas
        try:
            cursor.execute("ALTER TABLE pessoas ADD COLUMN motivo_bloqueio TEXT NULL")
            print("✅ Coluna 'motivo_bloqueio' adicionada")
        except Exception as e:
            if "Duplicate column" in str(e):
                print("⚠️ Coluna 'motivo_bloqueio' já existe")
            else:
                print(f"⚠️ {e}")

        # 3. Adicionar coluna 'usuario' na tabela registros
        try:
            cursor.execute("ALTER TABLE registros ADD COLUMN usuario VARCHAR(100) NULL")
            print("✅ Coluna 'usuario' adicionada em registros")
        except Exception as e:
            if "Duplicate column" in str(e):
                print("⚠️ Coluna 'usuario' já existe")
            else:
                print(f"⚠️ {e}")

        # 4. Adicionar coluna 'documento' na tabela pessoas
        try:
            cursor.execute("ALTER TABLE pessoas ADD COLUMN documento VARCHAR(50) NULL")
            print("✅ Coluna 'documento' adicionada")
        except Exception as e:
            if "Duplicate column" in str(e):
                print("⚠️ Coluna 'documento' já existe")
            else:
                print(f"⚠️ {e}")

        # 5. Adicionar coluna 'veiculo_placa' na tabela pessoas
        try:
            cursor.execute("ALTER TABLE pessoas ADD COLUMN veiculo_placa VARCHAR(20) NULL")
            print("✅ Coluna 'veiculo_placa' adicionada")
        except Exception as e:
            if "Duplicate column" in str(e):
                print("⚠️ Coluna 'veiculo_placa' já existe")
            else:
                print(f"⚠️ {e}")

        # 6. Adicionar coluna 'veiculo_modelo' na tabela pessoas
        try:
            cursor.execute("ALTER TABLE pessoas ADD COLUMN veiculo_modelo VARCHAR(50) NULL")
            print("✅ Coluna 'veiculo_modelo' adicionada")
        except Exception as e:
            if "Duplicate column" in str(e):
                print("⚠️ Coluna 'veiculo_modelo' já existe")
            else:
                print(f"⚠️ {e}")

        # 7. Adicionar coluna 'telefone' na tabela condominios
        try:
            cursor.execute("ALTER TABLE condominios ADD COLUMN telefone VARCHAR(20) NULL")
            print("✅ Coluna 'telefone' adicionada em condominios")
        except Exception as e:
            if "Duplicate column" in str(e):
                print("⚠️ Coluna 'telefone' já existe")
            else:
                print(f"⚠️ {e}")

        conn.commit()
        cursor.close()
        conn.close()

        print("\n" + "=" * 50)
        print("✅ Banco de dados corrigido com sucesso!")
        print("=" * 50)
        print("\nAgora reinicie o servidor: python web_main.py")

    except Error as e:
        print(f"\n❌ Erro ao conectar no MySQL: {e}")
        print("\nVerifique suas credenciais no arquivo corrigir_banco.py")
        print("Edite a variável 'password' com sua senha do MySQL")


if __name__ == '__main__':
    corrigir_banco()