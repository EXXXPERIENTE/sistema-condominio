import sqlite3
import hashlib
from datetime import datetime, timedelta
import os


class DatabaseManager:
    def __init__(self, database='condominio.db'):
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.database)
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
                    ativo INTEGER DEFAULT 1,
                    whatsapp TEXT,
                    FOREIGN KEY (condominio_id) REFERENCES condominios(id)
                )
            """)

            # Tabela pessoas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pessoas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    tipo TEXT CHECK(tipo IN ('morador', 'visitante', 'entregador', 'tecnico')) NOT NULL,
                    documento TEXT,
                    telefone TEXT,
                    veiculo_placa TEXT,
                    veiculo_modelo TEXT,
                    morador_permanente INTEGER DEFAULT 0,
                    condominio_id INTEGER,
                    apartamento TEXT,
                    bloqueado INTEGER DEFAULT 0,
                    motivo_bloqueio TEXT,
                    status TEXT DEFAULT 'ATIVO',
                    FOREIGN KEY (condominio_id) REFERENCES condominios(id)
                )
            """)

            # Tabela registros
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS registros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pessoa_id INTEGER,
                    data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usuario_registro INTEGER,
                    observacao TEXT,
                    recebido_por TEXT,
                    FOREIGN KEY (pessoa_id) REFERENCES pessoas(id),
                    FOREIGN KEY (usuario_registro) REFERENCES usuarios(id)
                )
            """)

            # Tabela permissoes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS permissoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER UNIQUE,
                    pode_apagar_banco INTEGER DEFAULT 0,
                    pode_editar_cadastros INTEGER DEFAULT 1,
                    pode_deletar_registros INTEGER DEFAULT 0,
                    pode_gerenciar_porteiros INTEGER DEFAULT 0,
                    pode_criar_avisos INTEGER DEFAULT 0,
                    pode_gerenciar_ocorrencias INTEGER DEFAULT 0,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """)

            # Tabela avisos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS avisos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    mensagem TEXT NOT NULL,
                    tipo TEXT CHECK(tipo IN ('info', 'alerta', 'urgente', 'sucesso')) DEFAULT 'info',
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_expiracao TIMESTAMP,
                    ativo INTEGER DEFAULT 1,
                    criado_por INTEGER,
                    condominio_id INTEGER,
                    FOREIGN KEY (criado_por) REFERENCES usuarios(id),
                    FOREIGN KEY (condominio_id) REFERENCES condominios(id)
                )
            """)

            # Tabela ocorrencias
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ocorrencias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    tipo TEXT CHECK(tipo IN ('reclamacao', 'manutencao', 'sugestao', 'informe')) DEFAULT 'reclamacao',
                    status TEXT CHECK(status IN ('aberto', 'andamento', 'concluido', 'cancelado')) DEFAULT 'aberto',
                    prioridade TEXT CHECK(prioridade IN ('baixa', 'media', 'alta', 'urgente')) DEFAULT 'media',
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_conclusao TIMESTAMP,
                    criado_por INTEGER,
                    condominio_id INTEGER,
                    responsavel TEXT,
                    FOREIGN KEY (criado_por) REFERENCES usuarios(id),
                    FOREIGN KEY (condominio_id) REFERENCES condominios(id)
                )
            """)

            # Tabela fotos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fotos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pessoa_id INTEGER UNIQUE,
                    caminho_foto TEXT,
                    data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pessoa_id) REFERENCES pessoas(id)
                )
            """)

            # Tabela logs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER,
                    acao TEXT,
                    descricao TEXT,
                    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip TEXT,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
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
                cursor.execute("""
                    INSERT INTO permissoes (usuario_id, pode_apagar_banco, pode_editar_cadastros, 
                        pode_deletar_registros, pode_gerenciar_porteiros, pode_criar_avisos, pode_gerenciar_ocorrencias)
                    VALUES (1, 1, 1, 1, 1, 1, 1)
                """)

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
                    "INSERT INTO pessoas (nome, tipo, apartamento, telefone, condominio_id, status) VALUES ('Entregador Express', 'entregador', NULL, '(11) 3333-7777', 1, 'ATIVO')")
                cursor.execute(
                    "INSERT INTO pessoas (nome, tipo, apartamento, telefone, condominio_id, status) VALUES ('Mariana Oliveira', 'morador', '303', '(11) 99999-3333', 2, 'ATIVO')")
                cursor.execute(
                    "INSERT INTO pessoas (nome, tipo, apartamento, telefone, condominio_id, status) VALUES ('Pedro Santos', 'morador', '404', '(11) 99999-4444', 2, 'ATIVO')")

                # Registros exemplo
                data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute("INSERT INTO registros (pessoa_id, data_entrada, usuario_registro) VALUES (1, ?, 1)",
                               (data_atual,))
                cursor.execute("INSERT INTO registros (pessoa_id, data_entrada, usuario_registro) VALUES (3, ?, 1)",
                               (data_atual,))

            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao criar banco: {e}")
            return False

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

    def delete_database(self, password):
        if password == "admin123":
            try:
                if os.path.exists(self.database):
                    os.remove(self.database)
                return True
            except:
                return False
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

    def log_action(self, usuario_id, acao, descricao, ip='localhost'):
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO logs (usuario_id, acao, descricao, ip) VALUES (?, ?, ?, ?)",
                           (usuario_id, acao, descricao, ip))
            cursor.close()
            return True
        except:
            return False

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

                result = self.fetch_one("SELECT COUNT(*) as total FROM registros WHERE DATE(data_entrada) = DATE('now')")
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
        except Exception as e:
            print(f"Erro: {e}")
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
        backup_file = os.path.join(backup_dir, f"backup_condominio_{timestamp}.sql")

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
            INSERT INTO fotos (pessoa_id, caminho_foto) 
            VALUES (?, ?) 
            ON CONFLICT(pessoa_id) DO UPDATE SET caminho_foto = ?, data_upload = CURRENT_TIMESTAMP
        """, (pessoa_id, caminho_foto, caminho_foto))

    def get_foto(self, pessoa_id):
        result = self.fetch_one("SELECT caminho_foto FROM fotos WHERE pessoa_id = ?", (pessoa_id,))
        return result['caminho_foto'] if result else None