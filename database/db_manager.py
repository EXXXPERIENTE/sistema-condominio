import pymysql
import hashlib
from datetime import datetime, timedelta
import os
import subprocess


class DatabaseManager:
    def __init__(self, host='localhost', user='root', password='', database='condominio_db', port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True
            )
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False

    def close(self):
        if self.connection:
            self.connection.close()

    def dict_fetch(self, cursor):
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def dict_fetch_one(self, cursor):
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        if row:
            return dict(zip(columns, row))
        return None

    def create_database(self):
        try:
            conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                autocommit=True
            )
            cursor = conn.cursor()

            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            cursor.execute(f"USE {self.database}")

            # Tabela condominios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS condominios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    endereco VARCHAR(200),
                    telefone VARCHAR(20)
                )
            """)

            # Tabela usuarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    login VARCHAR(50) UNIQUE NOT NULL,
                    senha VARCHAR(255) NOT NULL,
                    tipo ENUM('master', 'porteiro') NOT NULL,
                    condominio_id INT,
                    ativo BOOLEAN DEFAULT TRUE
                )
            """)

            # Tabela pessoas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pessoas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    tipo ENUM('morador', 'visitante', 'entregador', 'tecnico') NOT NULL,
                    documento VARCHAR(20),
                    telefone VARCHAR(20),
                    veiculo_placa VARCHAR(10),
                    veiculo_modelo VARCHAR(50),
                    morador_permanente BOOLEAN DEFAULT FALSE,
                    condominio_id INT,
                    apartamento VARCHAR(20),
                    bloqueado BOOLEAN DEFAULT FALSE,
                    motivo_bloqueio TEXT
                )
            """)

            # Tabela registros
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS registros (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    pessoa_id INT,
                    data_entrada DATETIME DEFAULT CURRENT_TIMESTAMP,
                    usuario_registro INT,
                    observacao TEXT,
                    recebido_por VARCHAR(100)
                )
            """)

            # Tabela permissoes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS permissoes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario_id INT,
                    pode_apagar_banco BOOLEAN DEFAULT FALSE,
                    pode_editar_cadastros BOOLEAN DEFAULT TRUE,
                    pode_deletar_registros BOOLEAN DEFAULT FALSE,
                    pode_gerenciar_porteiros BOOLEAN DEFAULT FALSE,
                    pode_criar_avisos BOOLEAN DEFAULT FALSE,
                    pode_gerenciar_ocorrencias BOOLEAN DEFAULT FALSE
                )
            """)

            # Tabela avisos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS avisos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    titulo VARCHAR(100) NOT NULL,
                    mensagem TEXT NOT NULL,
                    tipo ENUM('info', 'alerta', 'urgente', 'sucesso') DEFAULT 'info',
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_expiracao DATETIME,
                    ativo BOOLEAN DEFAULT TRUE,
                    criado_por INT,
                    condominio_id INT
                )
            """)

            # Tabela ocorrencias (NOVA)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ocorrencias (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    titulo VARCHAR(100) NOT NULL,
                    descricao TEXT NOT NULL,
                    tipo ENUM('reclamacao', 'manutencao', 'sugestao', 'informe') DEFAULT 'reclamacao',
                    status ENUM('aberto', 'andamento', 'concluido', 'cancelado') DEFAULT 'aberto',
                    prioridade ENUM('baixa', 'media', 'alta', 'urgente') DEFAULT 'media',
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_conclusao DATETIME,
                    criado_por INT,
                    condominio_id INT,
                    responsavel VARCHAR(100)
                )
            """)

            # Tabela fotos (NOVA)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fotos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    pessoa_id INT UNIQUE,
                    caminho_foto VARCHAR(255),
                    data_upload DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabela logs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario_id INT,
                    acao VARCHAR(100),
                    descricao TEXT,
                    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ip VARCHAR(45)
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
                    "INSERT INTO usuarios (id, nome, login, senha, tipo) VALUES (1, 'Administrador Master', 'master', %s, 'master')",
                    (senha_hash,))

                # Permissões master
                cursor.execute("""
                    INSERT INTO permissoes (usuario_id, pode_apagar_banco, pode_editar_cadastros, 
                        pode_deletar_registros, pode_gerenciar_porteiros, pode_criar_avisos, pode_gerenciar_ocorrencias)
                    VALUES (1, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE)
                """)

                # Porteiros
                senha_porteiro = hashlib.sha256('123456'.encode()).hexdigest()
                cursor.execute(
                    "INSERT INTO usuarios (nome, login, senha, tipo, condominio_id) VALUES ('João Porteiro', 'joao', %s, 'porteiro', 1)",
                    (senha_porteiro,))
                cursor.execute("INSERT INTO permissoes (usuario_id, pode_editar_cadastros) VALUES (2, TRUE)")

                cursor.execute(
                    "INSERT INTO usuarios (nome, login, senha, tipo, condominio_id) VALUES ('Maria Porteira', 'maria', %s, 'porteiro', 2)",
                    (senha_porteiro,))
                cursor.execute("INSERT INTO permissoes (usuario_id, pode_editar_cadastros) VALUES (3, TRUE)")

                # Pessoas exemplo
                cursor.execute(
                    "INSERT INTO pessoas (nome, tipo, apartamento, telefone, condominio_id) VALUES ('Ana Silva', 'morador', '101', '(11) 99999-1111', 1)")
                cursor.execute(
                    "INSERT INTO pessoas (nome, tipo, apartamento, telefone, condominio_id) VALUES ('Carlos Souza', 'morador', '202', '(11) 99999-2222', 1)")
                cursor.execute(
                    "INSERT INTO pessoas (nome, tipo, apartamento, telefone, condominio_id) VALUES ('Entregador Express', 'entregador', NULL, '(11) 3333-7777', 1)")
                cursor.execute(
                    "INSERT INTO pessoas (nome, tipo, apartamento, telefone, condominio_id) VALUES ('Mariana Oliveira', 'morador', '303', '(11) 99999-3333', 2)")
                cursor.execute(
                    "INSERT INTO pessoas (nome, tipo, apartamento, telefone, condominio_id) VALUES ('Pedro Santos', 'morador', '404', '(11) 99999-4444', 2)")

                # Registros exemplo
                data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute("INSERT INTO registros (pessoa_id, data_entrada, usuario_registro) VALUES (1, %s, 1)",
                               (data_atual,))
                cursor.execute("INSERT INTO registros (pessoa_id, data_entrada, usuario_registro) VALUES (3, %s, 1)",
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
            cursor.execute("SELECT * FROM permissoes WHERE usuario_id = %s", (user_id,))
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
                conn = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    autocommit=True
                )
                cursor = conn.cursor()
                cursor.execute(f"DROP DATABASE IF EXISTS {self.database}")
                cursor.close()
                conn.close()
                return True
            except:
                return False
        return False

    def authenticate_user(self, login, senha):
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE login = %s AND senha = %s AND ativo = TRUE",
                           (login, senha_hash))
            result = self.dict_fetch_one(cursor)
            cursor.close()
            return result
        except:
            return None

    def log_action(self, usuario_id, acao, descricao, ip='localhost'):
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO logs (usuario_id, acao, descricao, ip) VALUES (%s, %s, %s, %s)",
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
        except:
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

                result = self.fetch_one("SELECT COUNT(*) as total FROM registros WHERE DATE(data_entrada) = CURDATE()")
                stats['registros_hoje'] = result['total'] if result else 0
            else:
                result = self.fetch_one("SELECT COUNT(*) as total FROM pessoas WHERE condominio_id = %s",
                                        (user['condominio_id'],))
                stats['total_pessoas'] = result['total'] if result else 0

                result = self.fetch_one("""
                    SELECT COUNT(*) as total FROM registros r
                    JOIN pessoas p ON r.pessoa_id = p.id
                    WHERE DATE(r.data_entrada) = CURDATE() AND p.condominio_id = %s
                """, (user['condominio_id'],))
                stats['registros_hoje'] = result['total'] if result else 0

            result = self.fetch_one("SELECT COUNT(*) as total FROM avisos WHERE ativo = TRUE")
            stats['avisos_ativos'] = result['total'] if result else 0

            result = self.fetch_one("SELECT COUNT(*) as total FROM usuarios WHERE tipo = 'porteiro' AND ativo = TRUE")
            stats['porteiros_ativos'] = result['total'] if result else 0

            return stats
        except:
            return stats

    def get_statistics(self):
        return self.get_estatisticas_by_user({'tipo': 'master'})

    # ==================== NOVOS MÉTODOS PARA RELATÓRIOS ====================
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
                # Pessoas por tipo
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

                # Registros
                result = self.fetch_one("SELECT COUNT(*) as total FROM registros")
                stats['total_registros'] = result['total'] if result else 0

                result = self.fetch_one("SELECT COUNT(*) as total FROM registros WHERE DATE(data_entrada) = CURDATE()")
                stats['registros_hoje'] = result['total'] if result else 0

                result = self.fetch_one(
                    "SELECT COUNT(*) as total FROM registros WHERE data_entrada >= CURDATE() - INTERVAL 7 DAY")
                stats['registros_semana'] = result['total'] if result else 0

                result = self.fetch_one(
                    "SELECT COUNT(*) as total FROM registros WHERE data_entrada >= CURDATE() - INTERVAL 30 DAY")
                stats['registros_mes'] = result['total'] if result else 0

                # Ocorrências
                result = self.fetch_one("SELECT COUNT(*) as total FROM ocorrencias")
                stats['total_ocorrencias'] = result['total'] if result else 0

                result = self.fetch_one(
                    "SELECT COUNT(*) as total FROM ocorrencias WHERE status = 'aberto' OR status = 'andamento'")
                stats['ocorrencias_abertas'] = result['total'] if result else 0

                result = self.fetch_one("SELECT COUNT(*) as total FROM ocorrencias WHERE status = 'concluido'")
                stats['ocorrencias_concluidas'] = result['total'] if result else 0

                # Avisos
                result = self.fetch_one("SELECT COUNT(*) as total FROM avisos")
                stats['total_avisos'] = result['total'] if result else 0

                result = self.fetch_one("SELECT COUNT(*) as total FROM avisos WHERE ativo = TRUE")
                stats['avisos_ativos'] = result['total'] if result else 0

            else:
                # Para porteiro, filtrar por condomínio
                result = self.fetch_one("SELECT COUNT(*) as total FROM pessoas WHERE condominio_id = %s",
                                        (user['condominio_id'],))
                stats['total_pessoas'] = result['total'] if result else 0

                result = self.fetch_one("SELECT COUNT(*) as total FROM registros WHERE DATE(data_entrada) = CURDATE()")
                stats['registros_hoje'] = result['total'] if result else 0

                result = self.fetch_one("SELECT COUNT(*) as total FROM ocorrencias WHERE condominio_id = %s",
                                        (user['condominio_id'],))
                stats['total_ocorrencias'] = result['total'] if result else 0

                result = self.fetch_one("SELECT COUNT(*) as total FROM avisos WHERE ativo = TRUE")
                stats['avisos_ativos'] = result['total'] if result else 0

            return stats
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return stats

    def get_registros_para_relatorio(self, user, data_inicio=None, data_fim=None):
        """Retorna registros para exportação"""
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
                WHERE DATE(r.data_entrada) BETWEEN %s AND %s
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
                WHERE p.condominio_id = %s AND DATE(r.data_entrada) BETWEEN %s AND %s
                ORDER BY r.data_entrada DESC
            """
            return self.fetch_all(query, (user['condominio_id'], data_inicio, data_fim))

    def get_ocorrencias_para_relatorio(self, user, status=None):
        """Retorna ocorrências para exportação"""
        if user['tipo'] == 'master':
            if status:
                query = "SELECT * FROM ocorrencias WHERE status = %s ORDER BY data_criacao DESC"
                return self.fetch_all(query, (status,))
            else:
                return self.fetch_all("SELECT * FROM ocorrencias ORDER BY data_criacao DESC")
        else:
            if status:
                query = "SELECT * FROM ocorrencias WHERE condominio_id = %s AND status = %s ORDER BY data_criacao DESC"
                return self.fetch_all(query, (user['condominio_id'], status))
            else:
                return self.fetch_all("SELECT * FROM ocorrencias WHERE condominio_id = %s ORDER BY data_criacao DESC",
                                      (user['condominio_id'],))

    def criar_backup(self):
        """Cria backup do banco de dados usando Python (não precisa do mysqldump)"""
        import os
        from datetime import datetime

        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"backup_condominio_{timestamp}.sql")

        try:
            # Buscar todas as tabelas
            cursor = self.connection.cursor()
            cursor.execute("SHOW TABLES")
            tabelas = cursor.fetchall()

            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(f"-- ===================================================\n")
                f.write(f"-- BACKUP DO SISTEMA DE CONDOMÍNIOS\n")
                f.write(f"-- Banco: {self.database}\n")
                f.write(f"-- Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"-- ===================================================\n\n")
                f.write(f"SET FOREIGN_KEY_CHECKS=0;\n\n")

                for tabela in tabelas:
                    nome_tabela = tabela[0]

                    f.write(f"-- -----------------------------------------------------\n")
                    f.write(f"-- Tabela: {nome_tabela}\n")
                    f.write(f"-- -----------------------------------------------------\n\n")

                    # Estrutura da tabela
                    cursor.execute(f"SHOW CREATE TABLE {nome_tabela}")
                    row = cursor.fetchone()
                    if row:
                        create_sql = row[1]
                        f.write(f"{create_sql};\n\n")

                    # Dados da tabela
                    cursor.execute(f"SELECT * FROM {nome_tabela}")
                    dados = cursor.fetchall()

                    if dados:
                        # Pegar nomes das colunas
                        cursor.execute(f"DESCRIBE {nome_tabela}")
                        colunas_info = cursor.fetchall()
                        colunas = [col[0] for col in colunas_info]
                        colunas_str = ", ".join([f"`{c}`" for c in colunas])

                        f.write(f"-- Inserindo dados\n")
                        for linha in dados:
                            valores = []
                            for val in linha:
                                if val is None:
                                    valores.append("NULL")
                                elif isinstance(val, (int, float)):
                                    valores.append(str(val))
                                else:
                                    val_str = str(val).replace("'", "''")
                                    valores.append(f"'{val_str}'")

                            f.write(f"INSERT INTO `{nome_tabela}` ({colunas_str}) VALUES ({', '.join(valores)});\n")
                        f.write("\n")

                f.write(f"\nSET FOREIGN_KEY_CHECKS=1;\n")
                f.write(f"\n-- ===================================================\n")
                f.write(f"-- FIM DO BACKUP\n")
                f.write(f"-- ===================================================\n")

            cursor.close()

            if os.path.exists(backup_file) and os.path.getsize(backup_file) > 0:
                print(f"✅ Backup criado: {backup_file} ({os.path.getsize(backup_file)} bytes)")
                return backup_file
            else:
                print("❌ Backup falhou - arquivo vazio")
                return None

        except Exception as e:
            print(f"Erro no backup: {e}")
            return None

        def restaurar_backup(self, arquivo_backup):
            """Restaura um backup a partir de um arquivo SQL"""
            try:
                cursor = self.connection.cursor()

                with open(arquivo_backup, 'r', encoding='utf-8') as f:
                    conteudo = f.read()

                # Executar cada comando separadamente
                for comando in conteudo.split(';'):
                    comando = comando.strip()
                    if comando and not comando.startswith('--'):
                        try:
                            cursor.execute(comando)
                        except Exception as e:
                            print(f"Erro ao executar comando: {e}")
                            continue

                self.connection.commit()
                cursor.close()
                return True

            except Exception as e:
                print(f"Erro ao restaurar backup: {e}")
                return False


    def salvar_foto(self, pessoa_id, caminho_foto):
        """Salva o caminho da foto de uma pessoa"""
        return self.execute_query("""
            INSERT INTO fotos (pessoa_id, caminho_foto) 
            VALUES (%s, %s) 
            ON DUPLICATE KEY UPDATE caminho_foto = %s, data_upload = CURRENT_TIMESTAMP
        """, (pessoa_id, caminho_foto, caminho_foto))

    def get_foto(self, pessoa_id):
        """Recupera o caminho da foto de uma pessoa"""
        result = self.fetch_one("SELECT caminho_foto FROM fotos WHERE pessoa_id = %s", (pessoa_id,))
        return result['caminho_foto'] if result else None