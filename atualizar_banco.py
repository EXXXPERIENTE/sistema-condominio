import sqlite3
import hashlib


def atualizar_banco():
    conn = sqlite3.connect('condominio.db')
    cursor = conn.cursor()

    # Adicionar novas colunas na tabela pessoas
    try:
        cursor.execute("ALTER TABLE pessoas ADD COLUMN placa TEXT")
        print("✅ Coluna 'placa' adicionada")
    except:
        print("⚠️ Coluna 'placa' já existe")

    try:
        cursor.execute("ALTER TABLE pessoas ADD COLUMN qrcode TEXT")
        print("✅ Coluna 'qrcode' adicionada")
    except:
        print("⚠️ Coluna 'qrcode' já existe")

    try:
        cursor.execute("ALTER TABLE pessoas ADD COLUMN cor TEXT DEFAULT '#FFFFFF'")
        print("✅ Coluna 'cor' adicionada")
    except:
        print("⚠️ Coluna 'cor' já existe")

    try:
        cursor.execute("ALTER TABLE pessoas ADD COLUMN bloco TEXT")
        print("✅ Coluna 'bloco' adicionada")
    except:
        print("⚠️ Coluna 'bloco' já existe")

    # Nova tabela para controle de recebimento
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recebimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registro_id INTEGER,
            status TEXT DEFAULT 'AGUARDANDO',
            recebido_por TEXT,
            data_recebimento TIMESTAMP,
            observacao TEXT,
            FOREIGN KEY (registro_id) REFERENCES registros(id)
        )
    """)
    print("✅ Tabela 'recebimentos' criada")

    conn.commit()
    conn.close()
    print("\n✅ Banco de dados atualizado com sucesso!")


if __name__ == '__main__':
    atualizar_banco()