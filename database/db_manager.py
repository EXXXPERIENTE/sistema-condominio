import sqlite3
import hashlib
from datetime import datetime, timedelta
import os
import threading


class DatabaseManager:
    _local = threading.local()

    def __init__(self, database='condominio.db'):
        self.database = database

    def get_connection(self):
        """Retorna uma conexão para a thread atual"""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(self.database, check_same_thread=False)
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection

    def connect(self):
        try:
            self.get_connection()
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False

    def close(self):
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            delattr(self._local, 'connection')

    def dict_fetch(self, cursor):
        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def dict_fetch_one(self, cursor):
        columns = [col[0] for col in cursor.description] if cursor.description else []
        row = cursor.fetchone()
        if row:
            return dict(zip(columns, row))
        return None

    def execute_query(self, query, params=None):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Erro na query: {e}")
            return False

    def fetch_all(self, query, params=None):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
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
            conn = self.get_connection()
            cursor = conn.cursor()
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

    def authenticate_user(self, login, senha):
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE login = ? AND senha = ? AND ativo = 1",
                           (login, senha_hash))
            result = self.dict_fetch_one(cursor)
            cursor.close()
            return result
        except Exception as e:
            print(f"Erro na autenticação: {e}")
            return None

    def create_database(self):
        try:
            conn = sqlite3.connect(self.database)
            cursor = conn.cursor()

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
                    tipo TEXT CHECK(tipo IN ('master', 'porteiro')) NOT NULL,
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
                    condominio_id INTEGER
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
                    responsavel TEXT
                )
            """)

            # Verificar se já existem dados
            cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            count = cursor.fetchone()[0]

            if count == 0:
                # Inserir condomínios
                cursor.execute(
                    "INSERT INTO condominios (nome) VALUES ('Condomínio Vila Verde'), ('Condomínio Parque das Árvores')")

                # Usuário master
                senha_hash = hashlib.sha256('admin123'.encode()).hexdigest()
                cursor.execute(
                    "INSERT INTO usuarios (id, nome, login, senha, tipo) VALUES (1, 'Administrador Master', 'master', ?, 'master')",
                    (senha_hash,))

                # Permissões master
                cursor.execute(
                    "INSERT INTO permissoes (usuario_id, pode_apagar_banco, pode_editar_cadastros, pode_deletar_registros, pode_gerenciar_porteiros, pode_criar_avisos, pode_gerenciar_ocorrencias) VALUES (1, 1, 1, 1, 1, 1, 1)")

                # Porteiros
                senha_porteiro = hashlib.sha256('123456'.encode()).hexdigest()
                cursor.execute(
                    "INSERT INTO usuarios (nome, login, senha, tipo, condominio_id) VALUES ('João Porteiro', 'joao', ?, 'porteiro', 1)",
                    (senha_porteiro,))
                cursor.execute("INSERT INTO permissoes (usuario_id, pode_editar_cadastros) VALUES (2, 1)")
                cursor.execute(
                    "INSERT INTO usuarios (nome, login, senha, tipo, condominio_id) VALUES ('Maria Porteira', 'maria', ?, 'porteiro', 2)",
                    (senha_porteiro,))
                cursor.execute("INSERT INTO permissoes (usuario_id, pode_editar_cadastros) VALUES (3, 1)")

                # Pessoas exemplo
                cursor.execute(
                    "INSERT INTO pessoas (nome, tipo, apartamento, telefone, condominio_id, status) VALUES ('Ana Silva', 'morador', '101', '(11) 99999-1111', 1, 'ATIVO')")
                cursor.execute(
                    "INSERT INTO pessoas (nome, tipo, apartamento, telefone, condominio_id, status) VALUES ('Carlos Souza', 'morador', '202', '(11) 99999-2222', 1, 'ATIVO')")
                cursor.execute(
                    "INSERT INTO pessoas (nome, tipo, apartamento, telefone, condominio_id, status) VALUES ('Mariana Oliveira', 'morador', '303', '(11) 99999-3333', 2, 'ATIVO')")

            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao criar banco: {e}")
            return False

    def get_user_permissions(self, user_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
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

    def get_estatisticas_completas(self, user):
        """Retorna estatísticas completas para relatórios"""
        stats = {
            'total_pessoas': 0,
            'total_moradores': 0,
            'total_visitantes': 0,
            'total_entregadores': 0,
            'total_tecnicos': 0,
            'total_registros': 0,
            'registros_hoje': 0,
            'registros_semana': 0,
            'registros_mes': 0,
            'total_ocorrencias': 0,
            'ocorrencias_abertas': 0,
            'ocorrencias_concluidas': 0,
            'total_avisos': 0,
            'avisos_ativos': 0
        }

        try:
            if user['tipo'] == 'master':
                tipos = self.fetch_all("SELECT tipo, COUNT(*) as total FROM pessoas GROUP BY tipo")
                for t in tipos:
                    if t['tipo'] == 'morador':
                        stats['total_moradores'] = t['total']
                    elif t['tipo'] == 'visitante':
                        stats['total_visitantes'] = t['total']
                    elif t['tipo'] == 'entregador':
                        stats['total_entregadores'] = t['total']
                    elif t['tipo'] == 'tecnico':
                        stats['total_tecnicos'] = t['total']

                stats['total_pessoas'] = sum([stats['total_moradores'], stats['total_visitantes'],
                                              stats['total_entregadores'], stats['total_tecnicos']])

                result = self.fetch_one("SELECT COUNT(*) as total FROM registros")
                stats['total_registros'] = result['total'] if result else 0

                result = self.fetch_one("SELECT COUNT(*) as total FROM registros WHERE DATE(data_entrada) = DATE('now')")
                stats['registros_hoje'] = result['total'] if result else 0

                result = self.fetch_one(
                    "SELECT COUNT(*) as total FROM registros WHERE data_entrada >= DATE('now', '-7 days')")
                stats['registros_semana'] = result['total'] if result else 0

                result = self.fetch_one(
                    "SELECT COUNT(*) as total FROM registros WHERE data_entrada >= DATE('now', '-30 days')")
                stats['registros_mes'] = result['total'] if result else 0

                result = self.fetch_one("SELECT COUNT(*) as total FROM ocorrencias")
                stats['total_ocorrencias'] = result['total'] if result else 0

                result = self.fetch_one(
                    "SELECT COUNT(*) as total FROM ocorrencias WHERE status = 'aberto' OR status = 'andamento'")
                stats['ocorrencias_abertas'] = result['total'] if result else 0

                result = self.fetch_one("SELECT COUNT(*) as total FROM ocorrencias WHERE status = 'concluido'")
                stats['ocorrencias_concluidas'] = result['total'] if result else 0

                result = self.fetch_one("SELECT COUNT(*) as total FROM avisos")
                stats['total_avisos'] = result['total'] if result else 0

                result = self.fetch_one("SELECT COUNT(*) as total FROM avisos WHERE ativo = 1")
                stats['avisos_ativos'] = result['total'] if result else 0

            else:
                result = self.fetch_one("SELECT COUNT(*) as total FROM pessoas WHERE condominio_id = ?",
                                        (user['condominio_id'],))
                stats['total_pessoas'] = result['total'] if result else 0

                result = self.fetch_one("SELECT COUNT(*) as total FROM registros WHERE DATE(data_entrada) = DATE('now')")
                stats['registros_hoje'] = result['total'] if result else 0

                result = self.fetch_one("SELECT COUNT(*) as total FROM ocorrencias WHERE condominio_id = ?",
                                        (user['condominio_id'],))
                stats['total_ocorrencias'] = result['total'] if result else 0

                result = self.fetch_one("SELECT COUNT(*) as total FROM avisos WHERE ativo = 1")
                stats['avisos_ativos'] = result['total'] if result else 0

            return stats
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return stats

    def get_registros_para_relatorio(self, user, data_inicio=None, data_fim=None):
        if not data_inicio:
            data_inicio = "1900-01-01"
        if not data_fim:
            data_fim = datetime.now().strftime("%Y-%m-%d")

        if user['tipo'] == 'master':
            query = """
                SELECT r.data_entrada, p.nome, p.tipo, p.apartamento, u.nome as usuario_registro,
                       r.observacao, r.recebido_por, c.nome as condominio
                FROM registros r
                JOIN pessoas p ON r.pessoa_id = p.id
                LEFT JOIN usuarios u ON r.usuario_registro = u.id
                LEFT JOIN condominios c ON p.condominio_id = c.id
                WHERE DATE(r.data_entrada) BETWEEN ? AND ?
                ORDER BY r.data_entrada DESC
            """
            return self.fetch_all(query, (data_inicio, data_fim))
        else:
            query = """
                SELECT r.data_entrada, p.nome, p.tipo, p.apartamento, u.nome as usuario_registro,
                       r.observacao, r.recebido_por
                FROM registros r
                JOIN pessoas p ON r.pessoa_id = p.id
                LEFT JOIN usuarios u ON r.usuario_registro = u.id
                WHERE p.condominio_id = ? AND DATE(r.data_entrada) BETWEEN ? AND ?
                ORDER BY r.data_entrada DESC
            """
            return self.fetch_all(query, (user['condominio_id'], data_inicio, data_fim))

    def get_ocorrencias_para_relatorio(self, user, status=None):
        if user['tipo'] == 'master':
            if status:
                query = "SELECT * FROM ocorrencias WHERE status = ? ORDER BY data_criacao DESC"
                return self.fetch_all(query, (status,))
            else:
                return self.fetch_all("SELECT * FROM ocorrencias ORDER BY data_criacao DESC")
        else:
            if status:
                query = "SELECT * FROM ocorrencias WHERE condominio_id = ? AND status = ? ORDER BY data_criacao DESC"
                return self.fetch_all(query, (user['condominio_id'], status))
            else:
                return self.fetch_all("SELECT * FROM ocorrencias WHERE condominio_id = ? ORDER BY data_criacao DESC",
                                      (user['condominio_id'],))

    def criar_backup(self):
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"backup_condominio_{timestamp}.db")

        try:
            import shutil
            shutil.copy2(self.database, backup_file)
            print(f"✅ Backup criado: {backup_file}")
            return backup_file
        except Exception as e:
            print(f"Erro no backup: {e}")
            return None

    def restaurar_backup(self, arquivo_backup):
        try:
            import shutil
            shutil.copy2(arquivo_backup, self.database)
            return True
        except Exception as e:
            print(f"Erro ao restaurar backup: {e}")
            return False

    def salvar_foto(self, pessoa_id, caminho_foto):
        return self.execute_query("""
            INSERT OR REPLACE INTO fotos (pessoa_id, caminho_foto, data_upload) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (pessoa_id, caminho_foto))

    def get_foto(self, pessoa_id):
        result = self.fetch_one("SELECT caminho_foto FROM fotos WHERE pessoa_id = ?", (pessoa_id,))
        return result['caminho_foto'] if result else None