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

    def create_database(self):
        # Este método já está no init_db.py, mantemos vazio
        return True

    # Métodos adicionais necessários para o sistema
    def get_user_permissions(self, user_id):
        return {'pode_apagar_banco': False, 'pode_editar_cadastros': True, 'pode_deletar_registros': False, 'pode_gerenciar_porteiros': False, 'pode_criar_avisos': False, 'pode_gerenciar_ocorrencias': False}

    def get_estatisticas_by_user(self, user):
        return {'total_pessoas': 0, 'registros_hoje': 0, 'avisos_ativos': 0, 'porteiros_ativos': 0}

    def get_statistics(self):
        return self.get_estatisticas_by_user({'tipo': 'master'})