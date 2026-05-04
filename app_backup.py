from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from database.init_db import init_db, get_db, get_db_connection, hash_senha, verificar_senha
from functools import wraps
import pandas as pd
import io
import json
from datetime import datetime
import os
import shutil

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui_mude_para_producao'


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def master_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('perfil') != 'MASTER':
            return jsonify({'error': 'Acesso negado'}), 403
        return f(*args, **kwargs)

    return decorated_function


def verificar_senha_master(senha):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT senha FROM usuarios WHERE perfil = 'MASTER' AND id = ?", (session['usuario_id'],))
    senha_hash = cursor.fetchone()
    db.close()
    if senha_hash and verificar_senha(senha, senha_hash[0]):
        return True
    return False


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()
        db.close()

        if usuario and verificar_senha(senha, usuario[3]):
            session['usuario_id'] = usuario[0]
            session['usuario_nome'] = usuario[1]
            session['perfil'] = usuario[4]
            session['condominio_id'] = usuario[5]

            if usuario[4] == 'MASTER':
                return redirect(url_for('master_dashboard'))
            else:
                return redirect(url_for('porteiro_dashboard_rapido'))

        return render_template('login.html', erro="Email ou senha inválidos")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ==================== MASTER DASHBOARD ====================
@app.route('/master')
@login_required
@master_required
def master_dashboard():
    backup_msg = session.pop('backup_msg', None)
    return render_template('master_dashboard.html', backup_msg=backup_msg)


# API para condomínios
@app.route('/api/condominios', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
@master_required
def api_condominios():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT id, nome, endereco, cor, created_at FROM condominios ORDER BY nome")
        condominios = cursor.fetchall()
        db.close()
        return jsonify([{
            'id': c[0],
            'nome': c[1],
            'endereco': c[2],
            'cor': c[3],
            'created_at': c[4]
        } for c in condominios])

    elif request.method == 'POST':
        data = request.json
        cursor.execute("INSERT INTO condominios (nome, endereco, cor) VALUES (?, ?, ?)",
                       (data['nome'], data.get('endereco', ''), data.get('cor', '#3498db')))
        db.commit()
        novo_id = cursor.lastrowid
        db.close()
        return jsonify({'success': True, 'id': novo_id})

    elif request.method == 'PUT':
        data = request.json
        cursor.execute("UPDATE condominios SET nome=?, endereco=?, cor=? WHERE id=?",
                       (data['nome'], data.get('endereco', ''), data.get('cor', '#3498db'), data['id']))
        db.commit()
        db.close()
        return jsonify({'success': True})

    elif request.method == 'DELETE':
        condominio_id = request.args.get('id', type=int)
        cursor.execute("SELECT COUNT(*) FROM pessoas WHERE condominio_id=?", (condominio_id,))
        count = cursor.fetchone()[0]
        if count > 0:
            db.close()
            return jsonify(
                {'error': f'Existem {count} registros vinculados. Exclua primeiro as pessoas e registros.'}), 400
        cursor.execute("DELETE FROM condominios WHERE id=?", (condominio_id,))
        db.commit()
        db.close()
        return jsonify({'success': True})


# API para porteiros
@app.route('/api/porteiros', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
@master_required
def api_porteiros():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'GET':
        condominio_id = request.args.get('condominio_id', type=int)
        if condominio_id:
            cursor.execute(
                "SELECT id, nome, email, condominio_id, ativo FROM usuarios WHERE perfil='PORTEIRO' AND condominio_id=? ORDER BY nome",
                (condominio_id,))
        else:
            cursor.execute(
                "SELECT id, nome, email, condominio_id, ativo FROM usuarios WHERE perfil='PORTEIRO' ORDER BY nome")
        porteiros = cursor.fetchall()
        db.close()
        return jsonify([{
            'id': p[0],
            'nome': p[1],
            'email': p[2],
            'condominio_id': p[3],
            'ativo': p[4]
        } for p in porteiros])

    elif request.method == 'POST':
        data = request.json
        senha_hash = hash_senha(data['senha'])
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, perfil, condominio_id, ativo) VALUES (?, ?, ?, 'PORTEIRO', ?, 1)",
            (data['nome'], data['email'], senha_hash, data['condominio_id']))
        db.commit()
        novo_id = cursor.lastrowid
        db.close()
        return jsonify({'success': True, 'id': novo_id})

    elif request.method == 'PUT':
        data = request.json
        if 'senha' in data and data['senha']:
            senha_hash = hash_senha(data['senha'])
            cursor.execute(
                "UPDATE usuarios SET nome=?, email=?, senha=?, condominio_id=?, ativo=? WHERE id=? AND perfil='PORTEIRO'",
                (data['nome'], data['email'], senha_hash, data['condominio_id'], data.get('ativo', 1), data['id']))
        else:
            cursor.execute(
                "UPDATE usuarios SET nome=?, email=?, condominio_id=?, ativo=? WHERE id=? AND perfil='PORTEIRO'",
                (data['nome'], data['email'], data['condominio_id'], data.get('ativo', 1), data['id']))
        db.commit()
        db.close()
        return jsonify({'success': True})

    elif request.method == 'DELETE':
        porteiro_id = request.args.get('id', type=int)
        cursor.execute("UPDATE usuarios SET ativo=0 WHERE id=? AND perfil='PORTEIRO'", (porteiro_id,))
        db.commit()
        db.close()
        return jsonify({'success': True})


# API para dados do condomínio
@app.route('/api/condominio/<int:condominio_id>/dados')
@login_required
def get_condominio_dados(condominio_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT id, tipo, nome, documento, placa, telefone, casa, observacao, created_at FROM pessoas WHERE condominio_id = ? ORDER BY nome",
        (condominio_id,))
    pessoas = cursor.fetchall()

    cursor.execute("""
        SELECT r.*, p.nome as pessoa_nome 
        FROM registros r 
        LEFT JOIN pessoas p ON r.pessoa_id = p.id 
        WHERE r.condominio_id = ? 
        ORDER BY r.data_hora DESC
    """, (condominio_id,))
    registros = cursor.fetchall()

    db.close()

    return jsonify({
        'pessoas': [{
            'id': p[0],
            'tipo': p[1],
            'nome': p[2],
            'documento': p[3],
            'placa': p[4],
            'telefone': p[5],
            'casa': p[6],
            'observacao': p[7],
            'created_at': p[8]
        } for p in pessoas],
        'registros': [{
            'id': r[0],
            'tipo': r[3],
            'titulo': r[4],
            'descricao': r[5],
            'data_hora': r[6],
            'status': r[7],
            'cor': r[8] if len(r) > 8 else '#3498db',
            'acao': r[9] if len(r) > 9 else 'LIBERADO',
            'hora_entrada': r[10] if len(r) > 10 else None,
            'hora_saida': r[11] if len(r) > 11 else None,
            'visitando': r[12] if len(r) > 12 else None,
            'entregador': r[13] if len(r) > 13 else None,
            'destinatario': r[14] if len(r) > 14 else None,
            'quem_recebeu': r[15] if len(r) > 15 else None,
            'data_retirada': r[16] if len(r) > 16 else None,
            'quem_retirou': r[17] if len(r) > 17 else None,
            'quem_liberou': r[18] if len(r) > 18 else None,
            'registrado_por': r[19] if len(r) > 19 else None,
            'pessoa_nome': r[20] if len(r) > 20 else None,
            'pessoa_id': r[2]
        } for r in registros]
    })


# ==================== EXPORTAR PARA EXCEL ====================
@app.route('/exportar/excel/<int:condominio_id>')
@login_required
def exportar_excel(condominio_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT nome FROM condominios WHERE id=?", (condominio_id,))
    condominio = cursor.fetchone()

    cursor.execute("SELECT * FROM pessoas WHERE condominio_id = ? ORDER BY nome", (condominio_id,))
    pessoas = cursor.fetchall()

    cursor.execute("""
        SELECT r.*, p.nome as pessoa_nome 
        FROM registros r 
        LEFT JOIN pessoas p ON r.pessoa_id = p.id 
        WHERE r.condominio_id = ? 
        ORDER BY r.data_hora DESC
    """, (condominio_id,))
    registros = cursor.fetchall()

    db.close()

    df_pessoas = pd.DataFrame([{
        'Nome': p[3],
        'Tipo': p[2],
        'Documento': p[4] or '',
        'Placa': p[5] or '',
        'Telefone': p[6] or '',
        'Casa': p[7] or '',
        'Observacao': p[8] or '',
        'Data Cadastro': p[9]
    } for p in pessoas])

    df_registros = pd.DataFrame([{
        'Data/Hora': r[6],
        'Tipo': r[3],
        'Título': r[4],
        'Descrição': r[5] or '',
        'Pessoa': r[20] if len(r) > 20 else '',
        'Status': r[7]
    } for r in registros])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if not df_pessoas.empty:
            df_pessoas.to_excel(writer, sheet_name='Pessoas', index=False)
        else:
            pd.DataFrame({'Mensagem': ['Nenhuma pessoa cadastrada']}).to_excel(writer, sheet_name='Pessoas',
                                                                               index=False)

        if not df_registros.empty:
            df_registros.to_excel(writer, sheet_name='Registros', index=False)
        else:
            pd.DataFrame({'Mensagem': ['Nenhum registro cadastrado']}).to_excel(writer, sheet_name='Registros',
                                                                                index=False)

    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'{condominio[0]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )


# ==================== BACKUP ====================
@app.route('/backup/banco')
@login_required
@master_required
def backup_banco():
    try:
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_backup = f'backup_condominio_{timestamp}.db'
        caminho_backup = os.path.join(backup_dir, nome_backup)

        shutil.copy2(DB_PATH, caminho_backup)

        tamanho = os.path.getsize(caminho_backup) / 1024
        session['backup_msg'] = f'✅ Backup criado com sucesso! Local: {caminho_backup} Tamanho: {tamanho:.2f} KB'

        return send_file(
            DB_PATH,
            mimetype='application/x-sqlite3',
            as_attachment=True,
            download_name=nome_backup
        )
    except Exception as e:
        session['backup_msg'] = f'❌ Erro ao criar backup: {str(e)}'
        return redirect(url_for('master_dashboard'))


@app.route('/backup/listar')
@login_required
@master_required
def listar_backups():
    backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
    backups = []

    if os.path.exists(backup_dir):
        for arquivo in os.listdir(backup_dir):
            if arquivo.endswith('.db'):
                caminho = os.path.join(backup_dir, arquivo)
                backups.append({
                    'nome': arquivo,
                    'data': datetime.fromtimestamp(os.path.getctime(caminho)).strftime("%d/%m/%Y %H:%M:%S"),
                    'tamanho': f'{os.path.getsize(caminho) / 1024:.2f} KB'
                })

    backups.sort(key=lambda x: x['data'], reverse=True)
    return jsonify(backups)


@app.route('/backup/restaurar/<nome_arquivo>', methods=['POST'])
@login_required
@master_required
def restaurar_backup(nome_arquivo):
    try:
        data = request.json
        senha = data.get('senha')

        if not verificar_senha_master(senha):
            return jsonify({'error': 'Senha do administrador incorreta!'}), 403

        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
        caminho_backup = os.path.join(backup_dir, nome_arquivo)

        if not os.path.exists(caminho_backup):
            return jsonify({'error': 'Arquivo de backup não encontrado!'}), 404

        shutil.copy2(caminho_backup, DB_PATH)

        return jsonify({'success': True, 'message': f'✅ Backup restaurado com sucesso! Arquivo: {nome_arquivo}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ZERAR DADOS ====================
@app.route('/api/zerar-dados/<int:condominio_id>', methods=['POST'])
@login_required
@master_required
def zerar_dados_condominio(condominio_id):
    try:
        data = request.json
        senha = data.get('senha')

        if not verificar_senha_master(senha):
            return jsonify({'error': 'Senha do administrador incorreta!'}), 403

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT COUNT(*) FROM pessoas WHERE condominio_id = ?", (condominio_id,))
        total_pessoas = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM registros WHERE condominio_id = ?", (condominio_id,))
        total_registros = cursor.fetchone()[0]

        cursor.execute("DELETE FROM registros WHERE condominio_id = ?", (condominio_id,))
        cursor.execute("DELETE FROM pessoas WHERE condominio_id = ?", (condominio_id,))

        db.commit()
        db.close()

        return jsonify({
            'success': True,
            'message': f'✅ Dados zerados! Removidas {total_pessoas} pessoas e {total_registros} registros.'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/zerar-tudo', methods=['POST'])
@login_required
@master_required
def zerar_tudo():
    try:
        data = request.json
        senha = data.get('senha')

        if not verificar_senha_master(senha):
            return jsonify({'error': 'Senha do administrador incorreta!'}), 403

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT COUNT(*) FROM pessoas")
        total_pessoas = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM registros")
        total_registros = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE perfil = 'PORTEIRO'")
        total_porteiros = cursor.fetchone()[0]

        cursor.execute("DELETE FROM registros")
        cursor.execute("DELETE FROM pessoas")
        cursor.execute("DELETE FROM usuarios WHERE perfil = 'PORTEIRO'")

        db.commit()
        db.close()

        return jsonify({
            'success': True,
            'message': f'✅ Banco zerado! Removidas {total_pessoas} pessoas, {total_registros} registros e {total_porteiros} porteiros.'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== PORTEIRO RÁPIDO ====================
@app.route('/porteiro/rapido')
@login_required
def porteiro_dashboard_rapido():
    if session.get('perfil') == 'MASTER':
        return redirect(url_for('master_dashboard'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT nome, cor, id FROM condominios WHERE id = ?", (session['condominio_id'],))
    condominio = cursor.fetchone()
    db.close()

    return render_template('porteiro_rapido.html',
                           condominio_nome=condominio[0] if condominio else 'Desconhecido',
                           condominio_cor=condominio[1] if condominio else '#3498db',
                           condominio_id=condominio[2] if condominio else None)


@app.route('/api/porteiro/buscar', methods=['POST'])
@login_required
def porteiro_buscar():
    data = request.json
    termo = data.get('termo', '').lower()
    condominio_id = session.get('condominio_id')

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT id, nome, tipo, documento, placa, telefone, casa, observacao
        FROM pessoas 
        WHERE condominio_id = ? AND (nome LIKE ? OR documento LIKE ? OR placa LIKE ?)
        LIMIT 10
    """, (condominio_id, f'%{termo}%', f'%{termo}%', f'%{termo}%'))
    pessoas = cursor.fetchall()

    cursor.execute("""
        SELECT r.*, p.nome as pessoa_nome
        FROM registros r
        LEFT JOIN pessoas p ON r.pessoa_id = p.id
        WHERE r.condominio_id = ? AND (r.titulo LIKE ? OR r.descricao LIKE ?)
        ORDER BY r.data_hora DESC
        LIMIT 10
    """, (condominio_id, f'%{termo}%', f'%{termo}%'))
    registros = cursor.fetchall()

    db.close()

    return jsonify({
        'pessoas': [{
            'id': p[0],
            'nome': p[1],
            'tipo': p[2],
            'documento': p[3] or '-',
            'placa': p[4] or '-',
            'telefone': p[5] or '-',
            'casa': p[6] or '-',
            'observacao': p[7] or '-'
        } for p in pessoas],
        'registros': [{
            'id': r[0],
            'titulo': r[4],
            'descricao': r[5],
            'data_hora': r[6],
            'status': r[7],
            'pessoa_nome': r[20] if len(r) > 20 else '-'
        } for r in registros]
    })


@app.route('/api/porteiro/entrada', methods=['POST'])
@login_required
def registrar_entrada():
    try:
        data = request.json
        condominio_id = session.get('condominio_id')

        db = get_db()
        cursor = db.cursor()

        pessoa_id = None
        if data.get('pessoa_id'):
            pessoa_id = data['pessoa_id']
        elif data.get('documento'):
            cursor.execute("SELECT id FROM pessoas WHERE condominio_id = ? AND documento = ?",
                           (condominio_id, data['documento']))
            pessoa = cursor.fetchone()
            if pessoa:
                pessoa_id = pessoa[0]

        if not pessoa_id and data.get('nome'):
            cursor.execute("""
                INSERT INTO pessoas (condominio_id, tipo, nome, documento, placa, telefone, casa, observacao)
                VALUES (?, 'VISITANTE', ?, ?, ?, ?, ?, ?)
            """, (condominio_id, data['nome'], data.get('documento', ''),
                  data.get('placa', ''), data.get('telefone', ''), data.get('casa', ''),
                  data.get('observacao', '')))
            db.commit()
            pessoa_id = cursor.lastrowid

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO registros (condominio_id, pessoa_id, tipo, titulo, descricao, status, cor, acao, hora_entrada, visitando, registrado_por)
            VALUES (?, ?, 'ENTRADA', ?, ?, 'DENTRO', '#2ecc71', 'LIBERADO', ?, ?, ?)
        """, (condominio_id, pessoa_id, f"Entrada de {data['nome']}",
              data.get('observacao', ''), agora, data.get('visitando', ''), session.get('usuario_nome', 'Porteiro')))
        db.commit()
        db.close()

        return jsonify({'success': True, 'message': f'✅ Entrada registrada às {agora}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/porteiro/saida/<int:registro_id>', methods=['PUT'])
@login_required
def registrar_saida(registro_id):
    try:
        db = get_db()
        cursor = db.cursor()

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("SELECT hora_entrada FROM registros WHERE id = ?", (registro_id,))
        registro = cursor.fetchone()

        if not registro:
            return jsonify({'error': 'Registro não encontrado'}), 404

        hora_entrada = registro[0]

        from datetime import datetime as dt
        entrada_dt = dt.strptime(hora_entrada, "%Y-%m-%d %H:%M:%S")
        saida_dt = dt.strptime(agora, "%Y-%m-%d %H:%M:%S")
        tempo = saida_dt - entrada_dt
        horas = tempo.seconds // 3600
        minutos = (tempo.seconds % 3600) // 60

        tempo_texto = f"{horas}h {minutos}min" if horas > 0 else f"{minutos}min"

        cursor.execute("""
            UPDATE registros 
            SET hora_saida = ?, status = ?, descricao = COALESCE(descricao, '') || ' | Saída: ' || ? || ' | Tempo: ' || ?
            WHERE id = ?
        """, (agora, 'FINALIZADO', agora, tempo_texto, registro_id))
        db.commit()
        db.close()

        return jsonify({'success': True, 'message': f'✅ Saída registrada às {agora}', 'tempo': tempo_texto})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/porteiro/visitantes-ativos')
@login_required
def visitantes_ativos():
    try:
        condominio_id = session.get('condominio_id')
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT r.id, p.nome, p.documento, p.placa, p.casa, r.hora_entrada, r.visitando
            FROM registros r
            JOIN pessoas p ON r.pessoa_id = p.id
            WHERE r.condominio_id = ? AND r.tipo = 'ENTRADA' AND r.status = 'DENTRO'
            ORDER BY r.hora_entrada DESC
        """, (condominio_id,))

        visitantes = cursor.fetchall()
        db.close()

        return jsonify([{
            'id': v[0],
            'nome': v[1],
            'documento': v[2] or '-',
            'placa': v[3] or '-',
            'casa': v[4] or '-',
            'hora_entrada': v[5],
            'visitando': v[6] or '-'
        } for v in visitantes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/porteiro/registrar', methods=['POST'])
@login_required
def porteiro_registrar():
    try:
        data = request.json
        condominio_id = session.get('condominio_id')

        db = get_db()
        cursor = db.cursor()

        pessoa_id = None
        if data.get('pessoa_id'):
            pessoa_id = data['pessoa_id']
        elif data.get('documento'):
            cursor.execute("SELECT id FROM pessoas WHERE condominio_id = ? AND documento = ?",
                           (condominio_id, data['documento']))
            pessoa = cursor.fetchone()
            if pessoa:
                pessoa_id = pessoa[0]

        if not pessoa_id and data.get('nome') and data['nome'] != 'SISTEMA':
            cursor.execute("""
                INSERT INTO pessoas (condominio_id, tipo, nome, documento, placa, telefone, casa, observacao)
                VALUES (?, 'VISITANTE', ?, ?, ?, ?, ?, ?)
            """, (condominio_id, data['nome'], data.get('documento', ''),
                  data.get('placa', ''), data.get('telefone', ''), data.get('casa', ''),
                  data.get('observacao', '')))
            db.commit()
            pessoa_id = cursor.lastrowid

        cores_padrao = {
            'ENCOMENDA': '#2ecc71',
            'VISITANTE': '#9b59b6',
            'MORADOR': '#1abc9c',
            'EMERGENCIA': '#e74c3c',
            'OCORRENCIA': '#e67e22',
            'AVISO': '#f39c12',
            'RECLAMACAO': '#95a5a6'
        }
        cor = data.get('cor', cores_padrao.get(data.get('tipo', 'AVISO'), '#3498db'))

        cursor.execute("""
            INSERT INTO registros (condominio_id, pessoa_id, tipo, titulo, descricao, status, cor, acao, visitando, registrado_por)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (condominio_id, pessoa_id, data['tipo'], data.get('motivo', data.get('titulo', 'Registro')),
              data.get('observacao', ''), data.get('status', 'AGUARDANDO'), cor, data.get('acao', 'REGISTRADO'),
              data.get('visitando', ''), session.get('usuario_nome', 'Sistema')))
        db.commit()
        db.close()

        return jsonify({'success': True, 'id': cursor.lastrowid})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== PORTEIRO DASHBOARD NORMAL ====================
@app.route('/porteiro')
@login_required
def porteiro_dashboard():
    if session.get('perfil') == 'MASTER':
        return redirect(url_for('master_dashboard'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT nome, cor FROM condominios WHERE id = ?", (session['condominio_id'],))
    condominio = cursor.fetchone()
    db.close()
    return render_template('porteiro_dashboard.html',
                           condominio_nome=condominio[0] if condominio else 'Desconhecido',
                           condominio_cor=condominio[1] if condominio else '#3498db')


# ==================== CRUD PESSOAS ====================
@app.route('/api/pessoas', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def crud_pessoas():
    if session.get('perfil') == 'MASTER':
        condominio_id = request.args.get('condominio_id', type=int)
        if not condominio_id:
            return jsonify({'error': 'condominio_id é obrigatório'}), 400
    else:
        condominio_id = session.get('condominio_id')

    db = get_db()
    cursor = db.cursor()

    if request.method == 'GET':
        cursor.execute(
            "SELECT id, tipo, nome, documento, placa, telefone, casa, observacao, created_at FROM pessoas WHERE condominio_id = ? ORDER BY nome",
            (condominio_id,))
        pessoas = cursor.fetchall()
        db.close()
        return jsonify([{
            'id': p[0], 'tipo': p[1], 'nome': p[2], 'documento': p[3],
            'placa': p[4], 'telefone': p[5], 'casa': p[6], 'observacao': p[7], 'created_at': p[8]
        } for p in pessoas])

    elif request.method == 'POST':
        data = request.json
        cursor.execute("""
            INSERT INTO pessoas (condominio_id, tipo, nome, documento, placa, telefone, casa, observacao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (condominio_id, data['tipo'], data['nome'], data.get('documento', ''),
              data.get('placa', ''), data.get('telefone', ''), data.get('casa', ''),
              data.get('observacao', '')))
        db.commit()
        db.close()
        return jsonify({'success': True, 'id': cursor.lastrowid})

    elif request.method == 'PUT':
        data = request.json
        cursor.execute("""
            UPDATE pessoas SET tipo=?, nome=?, documento=?, placa=?, telefone=?, casa=?, observacao=?
            WHERE id=? AND condominio_id=?
        """, (data['tipo'], data['nome'], data.get('documento', ''), data.get('placa', ''),
              data.get('telefone', ''), data.get('casa', ''), data.get('observacao', ''),
              data['id'], condominio_id))
        db.commit()
        db.close()
        return jsonify({'success': True})

    elif request.method == 'DELETE':
        pessoa_id = request.args.get('id', type=int)
        cursor.execute("DELETE FROM pessoas WHERE id=? AND condominio_id=?", (pessoa_id, condominio_id))
        db.commit()
        db.close()
        return jsonify({'success': True})


# ==================== CRUD REGISTROS ====================
@app.route('/api/registros', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def crud_registros():
    if session.get('perfil') == 'MASTER':
        condominio_id = request.args.get('condominio_id', type=int)
        if not condominio_id:
            return jsonify({'error': 'condominio_id é obrigatório'}), 400
    else:
        condominio_id = session.get('condominio_id')

    db = get_db()
    cursor = db.cursor()

    if request.method == 'GET':
        cursor.execute("""
            SELECT r.*, p.nome as pessoa_nome 
            FROM registros r 
            LEFT JOIN pessoas p ON r.pessoa_id = p.id 
            WHERE r.condominio_id = ? 
            ORDER BY r.data_hora DESC
        """, (condominio_id,))
        registros = cursor.fetchall()
        db.close()
        return jsonify([{
            'id': r[0], 'tipo': r[3], 'titulo': r[4], 'descricao': r[5],
            'data_hora': r[6], 'status': r[7], 'cor': r[8] if len(r) > 8 else '#3498db',
            'acao': r[9] if len(r) > 9 else 'LIBERADO',
            'pessoa_nome': r[20] if len(r) > 20 else None,
            'pessoa_id': r[2]
        } for r in registros])

    elif request.method == 'POST':
        data = request.json
        cursor.execute("""
            INSERT INTO registros (condominio_id, pessoa_id, tipo, titulo, descricao, status, cor, acao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (condominio_id, data.get('pessoa_id'), data['tipo'], data['titulo'],
              data.get('descricao', ''), data.get('status', 'AGUARDANDO'),
              data.get('cor', '#3498db'), data.get('acao', 'LIBERADO')))
        db.commit()
        db.close()
        return jsonify({'success': True, 'id': cursor.lastrowid})

    elif request.method == 'PUT':
        data = request.json
        cursor.execute("""
            UPDATE registros SET tipo=?, titulo=?, descricao=?, status=?, pessoa_id=?, cor=?, acao=?
            WHERE id=? AND condominio_id=?
        """, (data['tipo'], data['titulo'], data.get('descricao', ''), data['status'],
              data.get('pessoa_id'), data.get('cor', '#3498db'), data.get('acao', 'LIBERADO'),
              data['id'], condominio_id))
        db.commit()
        db.close()
        return jsonify({'success': True})

    elif request.method == 'DELETE':
        registro_id = request.args.get('id', type=int)
        cursor.execute("DELETE FROM registros WHERE id=? AND condominio_id=?", (registro_id, condominio_id))
        db.commit()
        db.close()
        return jsonify({'success': True})


# ==================== RELATÓRIO CONSOLIDADO ====================
@app.route('/api/relatorio-consolidado/<int:condominio_id>')
@login_required
def relatorio_consolidado(condominio_id):
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT 
                r.id,
                r.data_hora,
                CASE 
                    WHEN r.pessoa_id IS NULL THEN r.titulo
                    ELSE COALESCE(p.nome, r.titulo)
                END as nome,
                COALESCE(p.documento, '') as documento,
                COALESCE(p.placa, '') as placa,
                COALESCE(p.casa, '') as casa,
                r.tipo,
                r.titulo as motivo,
                COALESCE(r.descricao, '') as observacao,
                r.status,
                r.cor,
                r.acao,
                r.hora_entrada,
                r.hora_saida,
                COALESCE(r.visitando, '') as visitando,
                COALESCE(r.entregador, '') as entregador,
                COALESCE(r.destinatario, '') as destinatario,
                COALESCE(r.quem_recebeu, '') as quem_recebeu,
                r.data_retirada,
                COALESCE(r.quem_retirou, '') as quem_retirou,
                COALESCE(r.quem_liberou, '') as quem_liberou,
                COALESCE(r.registrado_por, 'Sistema') as registrado_por,
                COALESCE(p.telefone, '') as telefone
            FROM registros r
            LEFT JOIN pessoas p ON r.pessoa_id = p.id
            WHERE r.condominio_id = ?
            ORDER BY r.data_hora DESC
        """, (condominio_id,))

        registros = cursor.fetchall()
        db.close()

        resultado = []
        for r in registros:
            resultado.append({
                'id': r[0],
                'data_hora': r[1],
                'nome': r[2] if r[2] else '-',
                'documento': r[3] if r[3] else '-',
                'placa': r[4] if r[4] else '-',
                'casa': r[5] if r[5] else '-',
                'tipo': r[6] if r[6] else '-',
                'motivo': r[7] if r[7] else '-',
                'observacao': r[8] if r[8] else '-',
                'status': r[9] if r[9] else '-',
                'cor': r[10] if r[10] else '#3498db',
                'acao': r[11] if r[11] else '-',
                'hora_entrada': r[12] if r[12] else '-',
                'hora_saida': r[13] if r[13] else '-',
                'visitando': r[14] if r[14] else '-',
                'entregador': r[15] if r[15] else '-',
                'destinatario': r[16] if r[16] else '-',
                'quem_recebeu': r[17] if r[17] else '-',
                'data_retirada': r[18] if r[18] else '-',
                'quem_retirou': r[19] if r[19] else '-',
                'quem_liberou': r[20] if r[20] else '-',
                'registrado_por': r[21] if r[21] else 'Sistema',
                'telefone': r[22] if r[22] else '-'
            })

        return jsonify({
            'registros': resultado,
            'total': len(resultado)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== VISUALIZAÇÃO CONSOLIDADA ====================
@app.route('/consolidado/<int:condominio_id>')
@login_required
def visualizacao_consolidada(condominio_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT nome, cor FROM condominios WHERE id = ?", (condominio_id,))
    condominio = cursor.fetchone()
    db.close()

    return render_template('registros_consolidado.html',
                           condominio_nome=condominio[0] if condominio else 'Desconhecido',
                           condominio_cor=condominio[1] if condominio else '#3498db',
                           condominio_id=condominio_id)


# ==================== GERENCIAR BACKUPS ====================
@app.route('/gerenciar-backups')
@login_required
@master_required
def gerenciar_backups():
    return render_template('gerenciar_backups.html')


@app.route('/backup/baixar/<nome_arquivo>')
@login_required
@master_required
def baixar_backup(nome_arquivo):
    try:
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
        caminho_backup = os.path.join(backup_dir, nome_arquivo)

        if not os.path.exists(caminho_backup):
            return jsonify({'error': 'Arquivo não encontrado'}), 404

        return send_file(
            caminho_backup,
            mimetype='application/x-sqlite3',
            as_attachment=True,
            download_name=nome_arquivo
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/backup/excluir/<nome_arquivo>', methods=['DELETE'])
@login_required
@master_required
def excluir_backup(nome_arquivo):
    try:
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
        caminho_backup = os.path.join(backup_dir, nome_arquivo)

        if not os.path.exists(caminho_backup):
            return jsonify({'error': 'Arquivo não encontrado'}), 404

        os.remove(caminho_backup)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='localhost', port=5000)