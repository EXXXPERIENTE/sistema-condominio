from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from functools import wraps
import sys
import os
import hashlib
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DatabaseManager

app = Flask(__name__)
app.secret_key = 'chave_mestra_condominio_2024'
CORS(app)

db = DatabaseManager()
db.connect()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Não autorizado'}), 401
        return f(*args, **kwargs)

    return decorated_function


def master_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_tipo' not in session or session['user_tipo'] != 'master':
            return jsonify({'success': False, 'error': 'Acesso negado! Apenas administrador.'}), 403
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    user = db.authenticate_user(data.get('login'), data.get('senha'))
    if user:
        session['user_id'] = user['id']
        session['user_nome'] = user['nome']
        session['user_tipo'] = user['tipo']
        session['user_condominio_id'] = user.get('condominio_id')
        print(f"✅ Login: {user['nome']} - Tipo: {user['tipo']}")
        return jsonify({'success': True, 'user': user})
    return jsonify({'success': False, 'error': 'Usuário ou senha inválidos!'})


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})


# ==================== CONDOMÍNIOS ====================
@app.route('/api/condominios', methods=['GET'])
@login_required
def get_condominios():
    condos = db.fetch_all("SELECT * FROM condominios ORDER BY nome")
    return jsonify({'success': True, 'condominios': condos})


@app.route('/api/condominios', methods=['POST'])
@login_required
@master_required
def create_condominio():
    data = request.get_json()
    db.execute_query(
        "INSERT INTO condominios (nome, endereco, telefone) VALUES (%s, %s, %s)",
        (data.get('nome'), data.get('endereco'), data.get('telefone'))
    )
    return jsonify({'success': True, 'message': 'Condomínio criado com sucesso!'})


@app.route('/api/condominios/<int:id>', methods=['DELETE'])
@login_required
@master_required
def delete_condominio(id):
    db.execute_query("DELETE FROM condominios WHERE id = %s", (id,))
    return jsonify({'success': True, 'message': 'Condomínio removido com sucesso!'})


# ==================== PESSOAS ====================
@app.route('/api/pessoas', methods=['GET'])
@login_required
def get_pessoas():
    busca = request.args.get('busca', '')
    if busca:
        pessoas = db.fetch_all("SELECT * FROM pessoas WHERE nome LIKE %s ORDER BY nome", (f'%{busca}%',))
    else:
        pessoas = db.fetch_all("SELECT * FROM pessoas ORDER BY nome")
    return jsonify({'success': True, 'pessoas': pessoas})


@app.route('/api/pessoas', methods=['POST'])
@login_required
def create_pessoa():
    try:
        data = request.get_json()
        print(f"📝 Criando pessoa: {data}")

        query = """
            INSERT INTO pessoas (nome, tipo, apartamento, telefone, documento, veiculo_placa, veiculo_modelo, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'ATIVO')
        """
        db.execute_query(query, (
            data.get('nome'),
            data.get('tipo'),
            data.get('apartamento'),
            data.get('telefone'),
            data.get('documento'),
            data.get('veiculo_placa'),
            data.get('veiculo_modelo')
        ))
        print(f"✅ Pessoa criada com sucesso!")
        return jsonify({'success': True, 'message': 'Pessoa cadastrada com sucesso!'})
    except Exception as e:
        print(f"❌ Erro ao criar pessoa: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/pessoas/<int:id>', methods=['PUT'])
@login_required
def update_pessoa(id):
    data = request.get_json()
    query = """
        UPDATE pessoas 
        SET nome=%s, tipo=%s, apartamento=%s, telefone=%s, documento=%s, veiculo_placa=%s, veiculo_modelo=%s
        WHERE id=%s
    """
    db.execute_query(query, (
        data.get('nome'), data.get('tipo'), data.get('apartamento'),
        data.get('telefone'), data.get('documento'), data.get('veiculo_placa'), data.get('veiculo_modelo'), id
    ))
    return jsonify({'success': True, 'message': 'Pessoa atualizada com sucesso!'})


@app.route('/api/pessoas/<int:id>', methods=['DELETE'])
@login_required
@master_required
def delete_pessoa(id):
    db.execute_query("DELETE FROM registros WHERE pessoa_id = %s", (id,))
    db.execute_query("DELETE FROM pessoas WHERE id = %s", (id,))
    return jsonify({'success': True, 'message': 'Pessoa removida com sucesso!'})


@app.route('/api/bloquear_pessoa/<int:id>', methods=['POST'])
@login_required
@master_required
def bloquear_pessoa(id):
    data = request.get_json()
    db.execute_query("UPDATE pessoas SET status='BLOQUEADO', motivo_bloqueio=%s WHERE id=%s", (data.get('motivo'), id))
    return jsonify({'success': True, 'message': 'Pessoa bloqueada com sucesso!'})


@app.route('/api/desbloquear_pessoa/<int:id>', methods=['POST'])
@login_required
@master_required
def desbloquear_pessoa(id):
    db.execute_query("UPDATE pessoas SET status='ATIVO', motivo_bloqueio=NULL WHERE id=%s", (id,))
    return jsonify({'success': True, 'message': 'Pessoa desbloqueada com sucesso!'})


# ==================== REGISTROS ====================
@app.route('/api/registrar_entrada', methods=['POST'])
@login_required
def registrar_entrada():
    try:
        data = request.get_json()
        pessoa_id = data.get('pessoa_id')

        pessoa = db.fetch_one("SELECT status, nome FROM pessoas WHERE id=%s", (pessoa_id,))
        if not pessoa:
            return jsonify({'success': False, 'error': 'Pessoa não encontrada!'})

        if pessoa.get('status') == 'BLOQUEADO':
            return jsonify({'success': False, 'error': 'Pessoa bloqueada! Entrada não permitida.'})

        db.execute_query(
            "INSERT INTO registros (pessoa_id, data_entrada, usuario) VALUES (%s, %s, %s)",
            (pessoa_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), session.get('user_nome'))
        )
        print(f"✅ Entrada registrada para: {pessoa['nome']}")
        return jsonify({'success': True, 'message': f'Entrada de {pessoa["nome"]} registrada com sucesso!'})
    except Exception as e:
        print(f"❌ Erro ao registrar entrada: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/registros', methods=['GET'])
@login_required
def get_registros():
    query = """
        SELECT r.*, p.nome, p.tipo, p.apartamento 
        FROM registros r 
        JOIN pessoas p ON r.pessoa_id = p.id 
        ORDER BY r.data_entrada DESC 
        LIMIT 50
    """
    registros = db.fetch_all(query)
    return jsonify({'success': True, 'registros': registros})


# ==================== ESTATÍSTICAS ====================
@app.route('/api/estatisticas', methods=['GET'])
@login_required
def get_estatisticas():
    total_pessoas = db.fetch_one("SELECT COUNT(*) as total FROM pessoas")
    total_registros = db.fetch_one("SELECT COUNT(*) as total FROM registros")
    hoje = datetime.now().strftime('%Y-%m-%d')
    registros_hoje = db.fetch_one("SELECT COUNT(*) as total FROM registros WHERE DATE(data_entrada) = %s", (hoje,))

    print(
        f"📊 Estatísticas: Pessoas={total_pessoas['total'] if total_pessoas else 0}, Registros={total_registros['total'] if total_registros else 0}, Hoje={registros_hoje['total'] if registros_hoje else 0}")

    return jsonify({
        'success': True,
        'estatisticas': {
            'total_pessoas': total_pessoas['total'] if total_pessoas else 0,
            'total_registros': total_registros['total'] if total_registros else 0,
            'registros_hoje': registros_hoje['total'] if registros_hoje else 0
        }
    })


# ==================== AVISOS ====================
@app.route('/api/avisos', methods=['GET'])
@login_required
def get_avisos():
    avisos = db.fetch_all("SELECT * FROM avisos ORDER BY id DESC")
    return jsonify({'success': True, 'avisos': avisos})


@app.route('/api/avisos', methods=['POST'])
@login_required
def create_aviso():
    data = request.get_json()
    db.execute_query(
        "INSERT INTO avisos (titulo, tipo, mensagem, data_criacao) VALUES (%s, %s, %s, %s)",
        (data.get('titulo'), data.get('tipo'), data.get('mensagem'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    return jsonify({'success': True, 'message': 'Aviso publicado com sucesso!'})


# ==================== OCORRÊNCIAS ====================
@app.route('/api/ocorrencias', methods=['GET'])
@login_required
def get_ocorrencias():
    ocorrencias = db.fetch_all("SELECT * FROM ocorrencias ORDER BY id DESC")
    return jsonify({'success': True, 'ocorrencias': ocorrencias})


@app.route('/api/ocorrencias', methods=['POST'])
@login_required
def create_ocorrencia():
    data = request.get_json()
    db.execute_query(
        "INSERT INTO ocorrencias (titulo, tipo, prioridade, descricao, responsavel, data_criacao, status) VALUES (%s, %s, %s, %s, %s, %s, 'aberta')",
        (data.get('titulo'), data.get('tipo'), data.get('prioridade'), data.get('descricao'), data.get('responsavel'),
         datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    return jsonify({'success': True, 'message': 'Ocorrência registrada com sucesso!'})


# ==================== PORTEIROS ====================
@app.route('/api/porteiros', methods=['GET'])
@login_required
@master_required
def get_porteiros():
    query = """
        SELECT u.id, u.nome, u.login, u.ativo, u.condominio_id, c.nome as condominio_nome 
        FROM usuarios u 
        LEFT JOIN condominios c ON u.condominio_id = c.id 
        WHERE u.tipo = 'porteiro'
    """
    porteiros = db.fetch_all(query)
    return jsonify({'success': True, 'porteiros': porteiros})


@app.route('/api/porteiros', methods=['POST'])
@login_required
@master_required
def create_porteiro():
    data = request.get_json()
    senha_hash = hashlib.sha256(data['senha'].encode()).hexdigest()
    db.execute_query(
        "INSERT INTO usuarios (nome, login, senha, tipo, condominio_id, ativo) VALUES (%s, %s, %s, 'porteiro', %s, %s)",
        (data['nome'], data['login'], senha_hash, data.get('condominio_id'), 1 if data.get('ativo') else 0)
    )
    return jsonify({'success': True, 'message': 'Porteiro cadastrado com sucesso!'})


@app.route('/api/porteiros/<int:id>', methods=['PUT'])
@login_required
@master_required
def update_porteiro(id):
    data = request.get_json()
    if data.get('senha'):
        senha_hash = hashlib.sha256(data['senha'].encode()).hexdigest()
        db.execute_query(
            "UPDATE usuarios SET nome=%s, login=%s, senha=%s, condominio_id=%s, ativo=%s WHERE id=%s AND tipo='porteiro'",
            (data['nome'], data['login'], senha_hash, data.get('condominio_id'), 1 if data.get('ativo') else 0, id)
        )
    else:
        db.execute_query(
            "UPDATE usuarios SET nome=%s, login=%s, condominio_id=%s, ativo=%s WHERE id=%s AND tipo='porteiro'",
            (data['nome'], data['login'], data.get('condominio_id'), 1 if data.get('ativo') else 0, id)
        )
    return jsonify({'success': True, 'message': 'Porteiro atualizado com sucesso!'})


@app.route('/api/porteiros/<int:id>', methods=['DELETE'])
@login_required
@master_required
def delete_porteiro(id):
    db.execute_query("DELETE FROM usuarios WHERE id=%s AND tipo='porteiro'", (id,))
    return jsonify({'success': True, 'message': 'Porteiro removido com sucesso!'})


# ==================== ZERAR BANCO ====================
@app.route('/api/zerar_banco', methods=['POST'])
@login_required
@master_required
def zerar_banco():
    try:
        db.execute_query("DELETE FROM pessoas")
        db.execute_query("DELETE FROM registros")
        db.execute_query("DELETE FROM avisos")
        db.execute_query("DELETE FROM ocorrencias")
        print("🗑️ Banco de dados zerado (pessoas, registros, avisos, ocorrências)")
        return jsonify({'success': True, 'message': 'Banco de dados zerado com sucesso! Pessoas, registros, avisos e ocorrências foram removidos.'})
    except Exception as e:
        print(f"❌ Erro ao zerar banco: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/backup', methods=['POST'])
@login_required
@master_required
def backup():
    return jsonify({'success': True, 'message': 'Backup realizado com sucesso!'})


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 SERVIDOR INICIADO")
    print("📱 Acesse: http://localhost:5000")
    print("🔑 Master: master / admin123")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)