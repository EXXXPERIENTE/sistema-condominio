import sqlite3


def adicionar_tabelas():
    conn = sqlite3.connect('condominio.db')
    cursor = conn.cursor()

    # 1. Adicionar colunas novas na tabela pessoas (se não existirem)
    novas_colunas = [
        ("placa", "TEXT"),
        ("bloco", "TEXT"),
        ("cor", "TEXT DEFAULT '#3498db'"),
        ("observacoes", "TEXT")
    ]

    for coluna, tipo in novas_colunas:
        try:
            cursor.execute(f"ALTER TABLE pessoas ADD COLUMN {coluna} {tipo}")
            print(f"✅ Coluna '{coluna}' adicionada")
        except:
            print(f"⚠️ Coluna '{coluna}' já existe")

    # 2. Criar tabela de encomendas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS encomendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            condominio_id INTEGER,
            nome_destinatario TEXT NOT NULL,
            nome_entregador TEXT,
            data_recebimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_retirada TIMESTAMP,
            qrcode_recebimento TEXT,
            qrcode_retirada TEXT,
            retirado_por TEXT,
            status TEXT DEFAULT 'AGUARDANDO',
            observacao TEXT,
            FOREIGN KEY (condominio_id) REFERENCES condominios(id)
        )
    """)
    print("✅ Tabela 'encomendas' criada")

    # 3. Criar tabela de anotacoes coloridas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS anotacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            condominio_id INTEGER,
            titulo TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            tipo TEXT DEFAULT 'informacao',
            cor TEXT DEFAULT '#FFEB3B',
            palavra_chave TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (condominio_id) REFERENCES condominios(id)
        )
    """)
    print("✅ Tabela 'anotacoes' criada")

    conn.commit()
    conn.close()
    print("\n✅ Banco de dados atualizado com sucesso!")


if __name__ == '__main__':
    adicionar_tabelas()