from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database.init_db import get_db, hash_senha, verificar_senha, is_postgresql, execute_query
import os
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'chave-secreta-padrao-para-desenvolvimento')


# Decorator para login obrigatório
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Faça login para acessar esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


# Decorator para admin/master
def master_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('usuario_perfil') != 'MASTER':
            flash('Acesso restrito a administradores', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        conn = get_db()
        cursor = conn.cursor()

        execute_query(cursor, "SELECT * FROM usuarios WHERE email = %s", (email,))

        usuario = cursor.fetchone()
        cursor.close()
        conn.close()

        if usuario and verificar_senha(senha, usuario['senha']):
            session['usuario_id'] = usuario['id']
            session['usuario_nome'] = usuario['nome']
            session['usuario_perfil'] = usuario['perfil']
            session['condominio_id'] = usuario['condominio_id']
            flash(f'Bem-vindo, {usuario["nome"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha inválidos', 'danger')

    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()

    condominio_id = session.get('condominio_id')

    if condominio_id:
        execute_query(cursor, "SELECT nome, cor FROM condominios WHERE id = %s", (condominio_id,))
        condominio = cursor.fetchone()
    else:
        condominio = None

    cursor.close()
    conn.close()

    return render_template(
        'master_dashboard.html' if session.get('usuario_perfil') == 'MASTER' else 'porteiro_dashboard.html',
        nome=session.get('usuario_nome'),
        perfil=session.get('usuario_perfil'),
        condominio=condominio)


@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso', 'info')
    return redirect(url_for('login'))


# ==================== CONDOMÍNIOS ====================

@app.route('/condominios')
@login_required
@master_required
def listar_condominios():
    conn = get_db()
    cursor = conn.cursor()

    execute_query(cursor, "SELECT id, nome, endereco, cor, created_at FROM condominios ORDER BY nome")

    condominios = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('condominios.html', condominios=condominios)


@app.route('/condominios/novo', methods=['GET', 'POST'])
@login_required
@master_required
def novo_condominio():
    if request.method == 'POST':
        nome = request.form.get('nome')
        endereco = request.form.get('endereco')
        cor = request.form.get('cor', '#007bff')

        conn = get_db()
        cursor = conn.cursor()

        execute_query(cursor, "INSERT INTO condominios (nome, endereco, cor) VALUES (%s, %s, %s)",
                      (nome, endereco, cor))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Condomínio criado com sucesso!', 'success')
        return redirect(url_for('listar_condominios'))

    return render_template('novo_condominio.html')


@app.route('/condominios/editar/<int:condominio_id>', methods=['GET', 'POST'])
@login_required
@master_required
def editar_condominio(condominio_id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form.get('nome')
        endereco = request.form.get('endereco')
        cor = request.form.get('cor')

        execute_query(cursor, "UPDATE condominios SET nome=%s, endereco=%s, cor=%s WHERE id=%s",
                      (nome, endereco, cor, condominio_id))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Condomínio atualizado com sucesso!', 'success')
        return redirect(url_for('listar_condominios'))

    execute_query(cursor, "SELECT * FROM condominios WHERE id = %s", (condominio_id,))
    condominio = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('editar_condominio.html', condominio=condominio)


@app.route('/condominios/deletar/<int:condominio_id>')
@login_required
@master_required
def deletar_condominio(condominio_id):
    conn = get_db()
    cursor = conn.cursor()

    # Verificar se há pessoas vinculadas
    execute_query(cursor, "SELECT COUNT(*) FROM pessoas WHERE condominio_id=%s", (condominio_id,))
    count = cursor.fetchone()[0]

    if count > 0:
        flash(f'Não é possível deletar o condomínio pois existem {count} pessoas vinculadas.', 'danger')
    else:
        execute_query(cursor, "DELETE FROM condominios WHERE id=%s", (condominio_id,))
        conn.commit()
        flash('Condomínio deletado com sucesso!', 'success')

    cursor.close()
    conn.close()

    return redirect(url_for('listar_condominios'))


# ==================== PORTEIROS ====================

@app.route('/porteiros')
@login_required
@master_required
def listar_porteiros():
    conn = get_db()
    cursor = conn.cursor()

    execute_query(cursor, """
        SELECT u.id, u.nome, u.email, u.condominio_id, c.nome as condominio_nome
        FROM usuarios u
        LEFT JOIN condominios c ON u.condominio_id = c.id
        WHERE u.perfil = 'PORTEIRO' AND u.ativo = 1
        ORDER BY u.nome
    """)

    porteiros = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('porteiros.html', porteiros=porteiros)


@app.route('/porteiros/novo', methods=['GET', 'POST'])
@login_required
@master_required
def novo_porteiro():
    conn = get_db()
    cursor = conn.cursor()

    execute_query(cursor, "SELECT id, nome FROM condominios ORDER BY nome")
    condominios = cursor.fetchall()

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        condominio_id = request.form.get('condominio_id')

        senha_hash = hash_senha(senha)

        execute_query(cursor,
                      "INSERT INTO usuarios (nome, email, senha, perfil, condominio_id) VALUES (%s, %s, %s, 'PORTEIRO', %s)",
                      (nome, email, senha_hash, condominio_id))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Porteiro criado com sucesso!', 'success')
        return redirect(url_for('listar_porteiros'))

    cursor.close()
    conn.close()

    return render_template('novo_porteiro.html', condominios=condominios)


@app.route('/porteiros/editar/<int:porteiro_id>', methods=['GET', 'POST'])
@login_required
@master_required
def editar_porteiro(porteiro_id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')

        execute_query(cursor,
                      "UPDATE usuarios SET nome=%s, email=%s WHERE id=%s AND perfil='PORTEIRO'",
                      (nome, email, porteiro_id))
        conn.commit()

        flash('Porteiro atualizado com sucesso!', 'success')
        return redirect(url_for('listar_porteiros'))

    execute_query(cursor, "SELECT id, nome, email FROM usuarios WHERE id=%s AND perfil='PORTEIRO'", (porteiro_id,))
    porteiro = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('editar_porteiro.html', porteiro=porteiro)


@app.route('/porteiros/deletar/<int:porteiro_id>')
@login_required
@master_required
def deletar_porteiro(porteiro_id):
    conn = get_db()
    cursor = conn.cursor()

    execute_query(cursor, "UPDATE usuarios SET ativo=0 WHERE id=%s AND perfil='PORTEIRO'", (porteiro_id,))
    conn.commit()

    cursor.close()
    conn.close()

    flash('Porteiro desativado com sucesso!', 'success')
    return redirect(url_for('listar_porteiros'))


# ==================== AUTENTICAÇÃO ====================

@app.route('/verificar_login')
def verificar_login():
    if 'usuario_id' in session:
        return jsonify({'logado': True, 'nome': session['usuario_nome'], 'perfil': session['usuario_perfil']})
    return jsonify({'logado': False})


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    conn = get_db()
    cursor = conn.cursor()

    execute_query(cursor, "SELECT id, nome, senha, perfil, condominio_id FROM usuarios WHERE email = %s", (email,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()

    if usuario and verificar_senha(senha, usuario['senha']):
        session['usuario_id'] = usuario['id']
        session['usuario_nome'] = usuario['nome']
        session['usuario_perfil'] = usuario['perfil']
        session['condominio_id'] = usuario['condominio_id']
        return jsonify({'success': True, 'perfil': usuario['perfil']})

    return jsonify({'success': False, 'message': 'Email ou senha inválidos'})


# ==================== PESSOAS (MORADORES/VISITANTES) ====================

@app.route('/pessoas')
@login_required
def listar_pessoas():
    condominio_id = session.get('condominio_id')

    if not condominio_id and session.get('usuario_perfil') == 'MASTER':
        # Master vê todos
        conn = get_db()
        cursor = conn.cursor()
        execute_query(cursor, """
            SELECT p.*, c.nome as condominio_nome, c.cor 
            FROM pessoas p 
            JOIN condominios c ON p.condominio_id = c.id 
            ORDER BY p.nome
        """)
    else:
        conn = get_db()
        cursor = conn.cursor()
        execute_query(cursor, """
            SELECT p.*, c.nome as condominio_nome, c.cor 
            FROM pessoas p 
            JOIN condominios c ON p.condominio_id = c.id 
            WHERE p.condominio_id = %s 
            ORDER BY p.nome
        """, (condominio_id,))

    pessoas = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('pessoas.html', pessoas=pessoas)


@app.route('/pessoas/nova', methods=['GET', 'POST'])
@login_required
def nova_pessoa():
    condominio_id = session.get('condominio_id')

    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form.get('nome')
        bloco = request.form.get('bloco')
        numero = request.form.get('numero')
        documento = request.form.get('documento')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        observacoes = request.form.get('observacoes')

        execute_query(cursor, """
            INSERT INTO pessoas (condominio_id, nome, bloco, numero, documento, telefone, email, observacoes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (condominio_id, nome, bloco, numero, documento, telefone, email, observacoes))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Pessoa cadastrada com sucesso!', 'success')
        return redirect(url_for('listar_pessoas'))

    cursor.close()
    conn.close()

    return render_template('nova_pessoa.html')


@app.route('/pessoas/editar/<int:pessoa_id>', methods=['GET', 'POST'])
@login_required
def editar_pessoa(pessoa_id):
    condominio_id = session.get('condominio_id')
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form.get('nome')
        bloco = request.form.get('bloco')
        numero = request.form.get('numero')
        documento = request.form.get('documento')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        observacoes = request.form.get('observacoes')

        execute_query(cursor, """
            UPDATE pessoas 
            SET nome=%s, bloco=%s, numero=%s, documento=%s, telefone=%s, email=%s, observacoes=%s
            WHERE id=%s AND condominio_id=%s
        """, (nome, bloco, numero, documento, telefone, email, observacoes, pessoa_id, condominio_id))
        conn.commit()

        flash('Pessoa atualizada com sucesso!', 'success')
        return redirect(url_for('listar_pessoas'))

    execute_query(cursor, """
        SELECT p.id, p.nome, p.bloco, p.numero, p.documento, p.telefone, p.email, p.observacoes,
               c.nome as condominio_nome, c.cor
        FROM pessoas p
        JOIN condominios c ON p.condominio_id = c.id
        WHERE p.id = %s
    """, (pessoa_id,))

    pessoa = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('editar_pessoa.html', pessoa=pessoa)


@app.route('/pessoas/deletar/<int:pessoa_id>')
@login_required
def deletar_pessoa(pessoa_id):
    condominio_id = session.get('condominio_id')
    conn = get_db()
    cursor = conn.cursor()

    execute_query(cursor, "DELETE FROM pessoas WHERE id=%s AND condominio_id=%s", (pessoa_id, condominio_id))
    conn.commit()

    cursor.close()
    conn.close()

    flash('Pessoa removida com sucesso!', 'success')
    return redirect(url_for('listar_pessoas'))


# ==================== REGISTROS ====================

@app.route('/registros')
@login_required
def listar_registros():
    condominio_id = session.get('condominio_id')
    conn = get_db()
    cursor = conn.cursor()

    if session.get('usuario_perfil') == 'MASTER':
        execute_query(cursor, """
            SELECT r.*, p.nome as pessoa_nome, p.bloco, p.numero, c.nome as condominio_nome
            FROM registros r
            JOIN pessoas p ON r.pessoa_id = p.id
            JOIN condominios c ON r.condominio_id = c.id
            ORDER BY r.data_criacao DESC
            LIMIT 100
        """)
    else:
        execute_query(cursor, """
            SELECT r.*, p.nome as pessoa_nome, p.bloco, p.numero 
            FROM registros r
            JOIN pessoas p ON r.pessoa_id = p.id
            WHERE r.condominio_id = %s
            ORDER BY r.data_criacao DESC
            LIMIT 100
        """, (condominio_id,))

    registros = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('registros.html', registros=registros)


@app.route('/registros/novo', methods=['POST'])
@login_required
def novo_registro():
    data = request.get_json()

    pessoa_id = data.get('pessoa_id')
    tipo = data.get('tipo')
    descricao = data.get('descricao')
    condominio_id = session.get('condominio_id')
    usuario_nome = session.get('usuario_nome')

    conn = get_db()
    cursor = conn.cursor()

    execute_query(cursor, """
        INSERT INTO registros (condominio_id, pessoa_id, tipo, descricao, usuario_nome)
        VALUES (%s, %s, %s, %s, %s)
    """, (condominio_id, pessoa_id, tipo, descricao, usuario_nome))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/buscar_pessoas')
@login_required
def buscar_pessoas():
    condominio_id = session.get('condominio_id')
    search = request.args.get('q', '')

    conn = get_db()
    cursor = conn.cursor()

    if session.get('usuario_perfil') == 'MASTER':
        execute_query(cursor, """
            SELECT p.id, p.nome, p.bloco, p.numero, c.nome as condominio_nome
            FROM pessoas p
            JOIN condominios c ON p.condominio_id = c.id
            WHERE p.nome LIKE %s
            ORDER BY p.nome
            LIMIT 20
        """, (f'%{search}%',))
    else:
        execute_query(cursor, """
            SELECT p.id, p.nome, p.bloco, p.numero
            FROM pessoas p
            WHERE p.condominio_id = %s AND p.nome LIKE %s
            ORDER BY p.nome
            LIMIT 20
        """, (condominio_id, f'%{search}%'))

    pessoas = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify([dict(pessoa) for pessoa in pessoas])


# ==================== PORTEIRO RÁPIDO ====================

@app.route('/porteiro_rapido')
@login_required
def porteiro_rapido():
    condominio_id = session.get('condominio_id')

    conn = get_db()
    cursor = conn.cursor()

    execute_query(cursor, "SELECT nome, cor FROM condominios WHERE id = %s", (condominio_id,))
    condominio = cursor.fetchone()

    execute_query(cursor, """
        SELECT id, nome, bloco, numero 
        FROM pessoas 
        WHERE condominio_id = %s 
        ORDER BY bloco, numero
    """, (condominio_id,))

    pessoas = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('porteiro_rapido.html', condominio=condominio, pessoas=pessoas)


# ==================== RELATÓRIOS ====================

@app.route('/relatorios')
@login_required
def relatorios():
    condominio_id = session.get('condominio_id')
    conn = get_db()
    cursor = conn.cursor()

    # Totais
    execute_query(cursor, "SELECT COUNT(*) FROM pessoas WHERE condominio_id = %s", (condominio_id,))
    total_pessoas = cursor.fetchone()[0]

    execute_query(cursor, "SELECT COUNT(*) FROM registros WHERE condominio_id = %s", (condominio_id,))
    total_registros = cursor.fetchone()[0]

    # Registros por tipo
    execute_query(cursor, """
        SELECT tipo, COUNT(*) as total 
        FROM registros 
        WHERE condominio_id = %s 
        GROUP BY tipo
    """, (condominio_id,))
    registros_por_tipo = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('relatorios.html',
                           total_pessoas=total_pessoas,
                           total_registros=total_registros,
                           registros_por_tipo=registros_por_tipo)


# ==================== INICIALIZAÇÃO ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))  # Mudado de 5000 para 8080 (padrão Railway)
    app.run(host='0.0.0.0', port=port, debug=False)