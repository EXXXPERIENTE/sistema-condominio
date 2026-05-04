import sqlite3
import bcrypt
from datetime import datetime, timedelta
import random
import os

DB_PATH = 'condominio.db'


def hash_senha(senha):
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def popular_banco():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ... resto do seu código continua igual ...