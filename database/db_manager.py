import sqlite3
import hashlib
from datetime import datetime
import os


class DatabaseManager:
    def __init__(self, database='condominio.db'):
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.database, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False

    def close(self):
        if self.connection:
            self.connection.close()

    def dict_fetch(self, cursor):
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def dict_fetch_one(self, cursor):
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Erro na query: {e}")
            return False

    def fetch_all(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = self.dict_fetch(cursor)
            cursor.close()
            return result
        except Exception as e:
            print(f"Erro ao buscar dados: {e}")
            return []

    def fetch_one(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = self.dict_fetch_one(cursor)
            cursor.close()
            return result
        except Exception as e:
            print(f"Erro: {e}")
            return None

    def create_database(self):
        """Cria todas as tabelas e dados iniciais"""
        try:
            conn = sqlite3.connect(self.database)
            cursor = conn.cursor()

            print("📝 Criando tabelas...")

            # Tabela condominios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS condominios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    endereco TEXT,
                    telefone TEXT
                )
            """)

            # Tabela usuarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    login TEXT UNIQUE NOT NULL,
                    senha TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    condominio_id INTEGER,
                    ativo INTEGER DEFAULT 1
                )
            """)

            # Tabela pessoas
            cursor.execute("""
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
            """)

            # Tabela registros
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS registros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pessoa_id INTEGER,
                    data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usuario_registro INTEGER,
                    observacao TEXT
                )
            """)

            # Tabela permissoes
            cursor.execute("""
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
            """)

            # Tabela avisos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS avisos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    mensagem TEXT NOT NULL,
                    tipo TEXT DEFAULT 'info',
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ativo INTEGER DEFAULT 1,
                    condominio_id INTEGER,
                    criado_por INTEGER
                )
            """)

            # Tabela ocorrencias
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ocorrencias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    tipo TEXT DEFAULT 'reclamacao',
                    status TEXT DEFAULT 'aberto',
                    prioridade TEXT DEFAULT 'media',
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    condominio_id INTEGER,
                    responsavel TEXT,
                    criado_por INTEGER
                )
            """)

            print("✅ Tabelas criadas")

            # Verificar se já existem dados
            cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            count = cursor.fetchone()[0]

            if count == 0:
                print("📝 Inserindo dados iniciais...")

                # Inserir condomínios
                cursor.execute("INSERT INTO condominios (id, nome) VALUES (1, 'Condomínio Vila Verde')")
                cursor.execute("INSERT INTO condominios (id, nome) VALUES (2, 'Condomínio Parque das Árvores')")

                # Usuário master (senha: admin123)
                senha_hash = hashlib.sha256('admin123'.encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO usuarios (id, nome, login, senha, tipo) 
                    VALUES (1, 'Administrador Master', 'master', ?, 'master')
                """, (senha_hash,))

                # Permissões master
                cursor.execute("""
                    INSERT INTO permissoes (usuario_id, pode_apagar_banco, pode_editar_cadastros, 
                        pode_deletar_registros, pode_gerenciar_porteiros, pode_criar_avisos, pode_gerenciar_ocorrencias)
                    VALUES (1, 1, 1, 1, 1, 1, 1)
                """)

                # Porteiros
                senha_porteiro = hashlib.sha256('123456'.encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO usuarios (id, nome, login, senha, tipo, condominio_id) 
                    VALUES (2, 'João Porteiro', 'joao', ?, 'porteiro', 1)
                """, (senha_porteiro,))
                cursor.execute("INSERT INTO permissoes (usuario_id, pode_editar_cadastros) VALUES (2, 1)")

                cursor.execute("""
                    INSERT INTO usuarios (id, nome, login, senha, tipo, condominio_id) 
                    VALUES (3, 'Maria Porteira', 'maria', ?, 'porteiro', 2)
                """, (senha_porteiro,))
                cursor.execute("INSERT INTO permissoes (usuario_id, pode_editar_cadastros) VALUES (3, 1)")

                # Pessoas exemplo
                cursor.execute("""
                    INSERT INTO pessoas (nome, tipo, apartamento, telefone, condominio_id, status) 
                    VALUES ('Ana Silva', 'morador', '101', '(11) 99999-1111', 1, 'ATIVO')
                """)
                cursor.execute("""
                    INSERT INTO pessoas (nome, tipo, apartamento, telefone, condominio_id, status) 
                    VALUES ('Carlos Souza', 'morador', '202', '(11) 99999-2222', 1, 'ATIVO')
                """)
                cursor.execute("""
                    INSERT INTO pessoas (nome, tipo, apartamento, telefone, condominio_id, status) 
                    VALUES ('Mariana Oliveira', 'morador', '303', '(11) 99999-3333', 2, 'ATIVO')
                """)

                print("✅ Dados iniciais inseridos")
                print("   Master: master / admin123")
                print("   Porteiro: joao / 123456")
                print("   Porteiro: maria / 123456")

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao criar banco: {e}")
            return False

    def authenticate_user(self, login, senha):
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE login = ? AND senha = ? AND ativo = 1",
                           (login, senha_hash))
            result = self.dict_fetch_one(cursor)
            cursor.close()
            return result
        except Exception as e:
            print(f"Erro na autenticação: {e}")
            return None

    def get_user_permissions(self, user_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM permissoes WHERE usuario_id = ?", (user_id,))
            result = self.dict_fetch_one(cursor)
            cursor.close()
            if result:
                return result
        except:
            pass
        return {
            'pode_apagar_banco': False,
            'pode_editar_cadastros': True,
            'pode_deletar_registros': False,
            'pode_gerenciar_porteiros': False,
            'pode_criar_avisos': False,
            'pode_gerenciar_ocorrencias': False
        }

    def get_estatisticas_by_user(self, user):
        stats = {
            'total_pessoas': 0,
            'registros_hoje': 0,
            'avisos_ativos': 0,
            'porteiros_ativos': 0
        }
        try:
            if user['tipo'] == 'master':
                result = self.fetch_one("SELECT COUNT(*) as total FROM pessoas")
                stats['total_pessoas'] = result['total'] if result else 0
                result = self.fetch_one(
                    "SELECT COUNT(*) as total FROM registros WHERE DATE(data_entrada) = DATE('now')")
                stats['registros_hoje'] = result['total'] if result else 0
            else:
                result = self.fetch_one("SELECT COUNT(*) as total FROM pessoas WHERE condominio_id = ?",
                                        (user['condominio_id'],))
                stats['total_pessoas'] = result['total'] if result else 0
                result = self.fetch_one("""
                    SELECT COUNT(*) as total FROM registros r
                    JOIN pessoas p ON r.pessoa_id = p.id
                    WHERE DATE(r.data_entrada) = DATE('now') AND p.condominio_id = ?
                """, (user['condominio_id'],))
                stats['registros_hoje'] = result['total'] if result else 0
            result = self.fetch_one("SELECT COUNT(*) as total FROM avisos WHERE ativo = 1")
            stats['avisos_ativos'] = result['total'] if result else 0
            result = self.fetch_one("SELECT COUNT(*) as total FROM usuarios WHERE tipo = 'porteiro' AND ativo = 1")
            stats['porteiros_ativos'] = result['total'] if result else 0
            return stats
        except:
            return stats

    def get_statistics(self):
        return self.get_estatisticas_by_user({'tipo': 'master'})