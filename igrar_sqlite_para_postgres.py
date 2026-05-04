import sqlite3
import psycopg2
import bcrypt
from datetime import datetime

# Configurações
SQLITE_DB = 'condominio.db'

POSTGRES_CONFIG = {
    'host': 'localhost',
    'database': 'condominio_db',
    'user': 'condominio_user',
    'password': 'sua_senha_forte'
}


def migrar_tabela(cursor_sqlite, cursor_pg, tabela, colunas):
    """Migra dados de uma tabela"""
    cursor_sqlite.execute(f"SELECT {', '.join(colunas)} FROM {tabela}")
    dados = cursor_sqlite.fetchall()

    placeholders = ', '.join(['%s'] * len(colunas))
    colunas_str = ', '.join(colunas)

    for dado in dados:
        try:
            cursor_pg.execute(f"INSERT INTO {tabela} ({colunas_str}) VALUES ({placeholders})", dado)
        except Exception as e:
            print(f"Erro ao inserir em {tabela}: {e}")
            print(f"Dado: {dado}")

    print(f"✅ {len(dados)} registros migrados para {tabela}")


def migrar():
    print("=" * 50)
    print("MIGRANDO SQLITE PARA POSTGRESQL")
    print("=" * 50)

    # Conectar ao SQLite
    conn_sqlite = sqlite3.connect(SQLITE_DB)
    cursor_sqlite = conn_sqlite.cursor()

    # Conectar ao PostgreSQL
    conn_pg = psycopg2.connect(**POSTGRES_CONFIG)
    cursor_pg = conn_pg.cursor()

    # Tabelas e colunas
    tabelas = {
        'usuarios': ['id', 'nome', 'email', 'senha', 'perfil', 'condominio_id', 'ativo', 'created_at'],
        'condominios': ['id', 'nome', 'endereco', 'cor', 'created_at'],
        'pessoas': ['id', 'condominio_id', 'tipo', 'nome', 'documento', 'placa', 'telefone', 'casa', 'observacao',
                    'created_at', 'updated_at'],
        'registros': ['id', 'condominio_id', 'pessoa_id', 'tipo', 'titulo', 'descricao', 'data_hora', 'status', 'cor',
                      'acao', 'hora_entrada', 'hora_saida', 'visitando', 'entregador', 'destinatario', 'quem_recebeu',
                      'data_retirada', 'quem_retirou', 'quem_liberou', 'registrado_por', 'created_at']
    }

    for tabela, colunas in tabelas.items():
        migrar_tabela(cursor_sqlite, cursor_pg, tabela, colunas)

    # Resetar sequências (IDs)
    cursor_pg.execute("SELECT setval('usuarios_id_seq', COALESCE((SELECT MAX(id) FROM usuarios), 1));")
    cursor_pg.execute("SELECT setval('condominios_id_seq', COALESCE((SELECT MAX(id) FROM condominios), 1));")
    cursor_pg.execute("SELECT setval('pessoas_id_seq', COALESCE((SELECT MAX(id) FROM pessoas), 1));")
    cursor_pg.execute("SELECT setval('registros_id_seq', COALESCE((SELECT MAX(id) FROM registros), 1));")

    conn_pg.commit()
    cursor_sqlite.close()
    conn_sqlite.close()
    cursor_pg.close()
    conn_pg.close()

    print("\n✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")


if __name__ == "__main__":
    migrar()