from .init_db import get_db, get_db_connection, hash_senha, verificar_senha, is_postgresql, execute_query

# Isto permite que no app.py você use:
# from database import get_db
# Em vez de:
# from database.init_db import get_db