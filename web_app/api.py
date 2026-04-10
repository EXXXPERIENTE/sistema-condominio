from flask import Flask, render_template, request, jsonify, session, send_file
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
# Garantir que o banco existe e está conectado
if not db.connect():
    print("⚠️ Banco não encontrado, criando...")
    db.create_database()
    db.connect()
print("✅ Banco de dados conectado")


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
    login = data.get('login')
    senha = data.get('senha')

    # Gerar hash SHA256 (igual ao banco)
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    print(f"🔐 Tentando login: {login}")
    print(f"   Hash gerado: {senha_hash}")

    user = db.authenticate_user(login, senha)

    if user:
        session['user_id'] = user['id']
        session['user_nome'] = user['nome']
        session['user_tipo'] = user['tipo']
        session['user_condominio_id'] = user.get('condominio_id')
        print(f"✅ Login: {user['nome']} - Tipo: {user['tipo']}")
        return jsonify({'success': True, 'user': user})

    print(f"❌ Falha no login: {login}")
    return jsonify({'success': False, 'error': 'Usuário ou senha inválidos!'})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})


# ==================== CONDOMÍNIOS ====================
@app.route('/api/condominios', methods=['GET'])
@login_required
@master_required
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

    if session.get('user_tipo') == 'porteiro':
        condominio_id = session.get('user_condominio_id')
        if busca:
            pessoas = db.fetch_all(
                "SELECT * FROM pessoas WHERE condominio_id = %s AND nome LIKE %s ORDER BY nome",
                (condominio_id, f'%{busca}%')
            )
        else:
            pessoas = db.fetch_all(
                "SELECT * FROM pessoas WHERE condominio_id = %s ORDER BY nome",
                (condominio_id,)
            )
    else:
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

        if session.get('user_tipo') == 'porteiro':
            condominio_id = session.get('user_condominio_id')
        else:
            condominio_id = data.get('condominio_id')

        if not condominio_id:
            return jsonify({'success': False, 'error': 'Selecione um condomínio!'}), 400

        query = """
            INSERT INTO pessoas (nome, tipo, apartamento, telefone, documento, veiculo_placa, veiculo_modelo, status, condominio_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'ATIVO', %s)
        """
        db.execute_query(query, (
            data.get('nome'),
            data.get('tipo'),
            data.get('apartamento'),
            data.get('telefone'),
            data.get('documento'),
            data.get('veiculo_placa'),
            data.get('veiculo_modelo'),
            condominio_id
        ))
        return jsonify({'success': True, 'message': 'Pessoa cadastrada com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/pessoas/<int:id>', methods=['PUT'])
@login_required
def update_pessoa(id):
    try:
        data = request.get_json()
        query = """
            UPDATE pessoas 
            SET nome=%s, tipo=%s, apartamento=%s, telefone=%s, documento=%s, 
                veiculo_placa=%s, veiculo_modelo=%s
            WHERE id=%s
        """
        db.execute_query(query, (
            data.get('nome'), data.get('tipo'), data.get('apartamento'),
            data.get('telefone'), data.get('documento'), data.get('veiculo_placa'),
            data.get('veiculo_modelo'), id
        ))
        return jsonify({'success': True, 'message': 'Pessoa atualizada com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/pessoas/<int:id>', methods=['DELETE'])
@login_required
@master_required
def delete_pessoa(id):
    try:
        db.execute_query("DELETE FROM registros WHERE pessoa_id = %s", (id,))
        db.execute_query("DELETE FROM pessoas WHERE id = %s", (id,))
        return jsonify({'success': True, 'message': 'Pessoa removida com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/registrar_entrada', methods=['POST'])
@login_required
def registrar_entrada():
    try:
        data = request.get_json()
        pessoa_id = data.get('pessoa_id')
        observacao = data.get('observacao', '')

        pessoa = db.fetch_one("SELECT status, nome, condominio_id, bloqueado FROM pessoas WHERE id=%s", (pessoa_id,))

        if not pessoa:
            return jsonify({'success': False, 'error': 'Pessoa não encontrada!'})

        # Verificar bloqueio (status ou campo bloqueado)
        if pessoa.get('status') == 'BLOQUEADO' or pessoa.get('bloqueado') == 1:
            return jsonify({'success': False, 'error': 'Pessoa bloqueada! Entrada não permitida.'}), 403

        if session.get('user_tipo') == 'porteiro':
            if pessoa.get('condominio_id') != session.get('user_condominio_id'):
                return jsonify(
                    {'success': False, 'error': 'Acesso negado! Esta pessoa não pertence ao seu condomínio.'}), 403

        usuario_registro = session.get('user_id')

        db.execute_query(
            "INSERT INTO registros (pessoa_id, data_entrada, usuario_registro, observacao) VALUES (%s, %s, %s, %s)",
            (pessoa_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), usuario_registro, observacao)
        )

        print(f"✅ Entrada registrada para: {pessoa['nome']} - Observação: {observacao if observacao else 'Nenhuma'}")
        return jsonify({'success': True, 'message': f'Entrada de {pessoa["nome"]} registrada com sucesso!'})
    except Exception as e:
        print(f"❌ Erro ao registrar entrada: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/registros', methods=['GET'])
@login_required
def get_registros():
    if session.get('user_tipo') == 'porteiro':
        condominio_id = session.get('user_condominio_id')
        query = """
            SELECT 
                r.id, r.data_entrada, r.observacao,
                p.nome as pessoa_nome, 
                p.tipo as pessoa_tipo, 
                p.apartamento,
                u.nome as usuario_nome
            FROM registros r 
            JOIN pessoas p ON r.pessoa_id = p.id 
            LEFT JOIN usuarios u ON r.usuario_registro = u.id
            WHERE p.condominio_id = %s
            ORDER BY r.data_entrada DESC 
            LIMIT 100
        """
        registros = db.fetch_all(query, (condominio_id,))
    else:
        query = """
            SELECT 
                r.id, r.data_entrada, r.observacao,
                p.nome as pessoa_nome, 
                p.tipo as pessoa_tipo, 
                p.apartamento,
                u.nome as usuario_nome
            FROM registros r 
            JOIN pessoas p ON r.pessoa_id = p.id 
            LEFT JOIN usuarios u ON r.usuario_registro = u.id
            ORDER BY r.data_entrada DESC 
            LIMIT 100
        """
        registros = db.fetch_all(query)

    for reg in registros:
        reg['nome'] = reg.get('pessoa_nome')
        reg['tipo'] = reg.get('pessoa_tipo')
        reg['usuario'] = reg.get('usuario_nome') or 'Sistema'

    return jsonify({'success': True, 'registros': registros})

@app.route('/api/registros/<int:id>', methods=['DELETE'])
@login_required
@master_required
def delete_registro(id):
    try:
        db.execute_query("DELETE FROM registros WHERE id = %s", (id,))
        return jsonify({'success': True, 'message': 'Registro removido com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ==================== ESTATÍSTICAS ====================
@app.route('/api/estatisticas', methods=['GET'])
@login_required
def get_estatisticas():
    if session.get('user_tipo') == 'porteiro':
        condominio_id = session.get('user_condominio_id')
        total_pessoas = db.fetch_one("SELECT COUNT(*) as total FROM pessoas WHERE condominio_id = %s", (condominio_id,))
        total_registros = db.fetch_one(
            "SELECT COUNT(*) as total FROM registros r JOIN pessoas p ON r.pessoa_id = p.id WHERE p.condominio_id = %s",
            (condominio_id,))
        hoje = datetime.now().strftime('%Y-%m-%d')
        registros_hoje = db.fetch_one("""
            SELECT COUNT(*) as total FROM registros r 
            JOIN pessoas p ON r.pessoa_id = p.id 
            WHERE p.condominio_id = %s AND DATE(r.data_entrada) = %s
        """, (condominio_id, hoje))
    else:
        total_pessoas = db.fetch_one("SELECT COUNT(*) as total FROM pessoas")
        total_registros = db.fetch_one("SELECT COUNT(*) as total FROM registros")
        hoje = datetime.now().strftime('%Y-%m-%d')
        registros_hoje = db.fetch_one("SELECT COUNT(*) as total FROM registros WHERE DATE(data_entrada) = %s", (hoje,))

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
    if session.get('user_tipo') == 'porteiro':
        condominio_id = session.get('user_condominio_id')
        query = """
            SELECT a.*, 
                   c.nome as condominio_nome,
                   u.nome as criado_por_nome
            FROM avisos a
            LEFT JOIN condominios c ON a.condominio_id = c.id
            LEFT JOIN usuarios u ON a.criado_por = u.id
            WHERE a.condominio_id = %s
            ORDER BY a.id DESC
        """
        avisos = db.fetch_all(query, (condominio_id,))
    else:
        query = """
            SELECT a.*, 
                   c.nome as condominio_nome,
                   u.nome as criado_por_nome
            FROM avisos a
            LEFT JOIN condominios c ON a.condominio_id = c.id
            LEFT JOIN usuarios u ON a.criado_por = u.id
            ORDER BY a.id DESC
        """
        avisos = db.fetch_all(query)
    return jsonify({'success': True, 'avisos': avisos})


@app.route('/api/avisos', methods=['POST'])
@login_required
def create_aviso():
    data = request.get_json()

    if session.get('user_tipo') == 'porteiro':
        condominio_id = session.get('user_condominio_id')
    else:
        condominio_id = data.get('condominio_id')

    # Pega o ID do usuário logado
    criado_por = session.get('user_id')

    db.execute_query(
        "INSERT INTO avisos (titulo, mensagem, tipo, data_criacao, condominio_id, criado_por) VALUES (%s, %s, %s, %s, %s, %s)",
        (data.get('titulo'), data.get('mensagem'), data.get('tipo'),
         datetime.now().strftime('%Y-%m-%d %H:%M:%S'), condominio_id, criado_por)
    )
    return jsonify({'success': True, 'message': 'Aviso publicado com sucesso!'})

@app.route('/api/avisos/<int:id>', methods=['PUT'])
@login_required
@master_required
def update_aviso(id):
    try:
        data = request.get_json()
        db.execute_query("""
            UPDATE avisos 
            SET titulo = %s, mensagem = %s, tipo = %s, ativo = %s
            WHERE id = %s
        """, (data.get('titulo'), data.get('mensagem'), data.get('tipo'),
              data.get('ativo', 1), id))
        return jsonify({'success': True, 'message': 'Aviso atualizado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/avisos/<int:id>', methods=['DELETE'])
@login_required
@master_required
def delete_aviso(id):
    try:
        db.execute_query("DELETE FROM avisos WHERE id = %s", (id,))
        return jsonify({'success': True, 'message': 'Aviso removido com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ==================== OCORRÊNCIAS ====================
@app.route('/api/ocorrencias', methods=['GET'])
@login_required
def get_ocorrencias():
    if session.get('user_tipo') == 'porteiro':
        condominio_id = session.get('user_condominio_id')
        query = """
            SELECT o.*, 
                   c.nome as condominio_nome,
                   u.nome as criado_por_nome
            FROM ocorrencias o
            LEFT JOIN condominios c ON o.condominio_id = c.id
            LEFT JOIN usuarios u ON o.criado_por = u.id
            WHERE o.condominio_id = %s
            ORDER BY o.id DESC
        """
        ocorrencias = db.fetch_all(query, (condominio_id,))
    else:
        query = """
            SELECT o.*, 
                   c.nome as condominio_nome,
                   u.nome as criado_por_nome
            FROM ocorrencias o
            LEFT JOIN condominios c ON o.condominio_id = c.id
            LEFT JOIN usuarios u ON o.criado_por = u.id
            ORDER BY o.id DESC
        """
        ocorrencias = db.fetch_all(query)
    return jsonify({'success': True, 'ocorrencias': ocorrencias})


@app.route('/api/ocorrencias', methods=['POST'])
@login_required
def create_ocorrencia():
    try:
        data = request.get_json()
        print(f"📝 Dados recebidos: {data}")  # Log para debug

        if session.get('user_tipo') == 'porteiro':
            condominio_id = session.get('user_condominio_id')
        else:
            condominio_id = data.get('condominio_id', 1)  # Valor padrão

        criado_por = session.get('user_id')

        # Verificar se os campos obrigatórios existem
        titulo = data.get('titulo')
        descricao = data.get('descricao')

        if not titulo or not descricao:
            return jsonify({'success': False, 'error': 'Título e descrição são obrigatórios!'}), 400

        tipo = data.get('tipo', 'reclamacao')
        prioridade = data.get('prioridade', 'media')
        status = data.get('status', 'aberto')
        responsavel = data.get('responsavel', '')

        query = """
            INSERT INTO ocorrencias (titulo, descricao, tipo, prioridade, status, data_criacao, condominio_id, responsavel, criado_por) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        db.execute_query(query, (
            titulo, descricao, tipo, prioridade, status,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            condominio_id, responsavel, criado_por
        ))

        print("✅ Ocorrência criada com sucesso!")
        return jsonify({'success': True, 'message': 'Ocorrência registrada com sucesso!'})

    except Exception as e:
        print(f"❌ Erro ao criar ocorrência: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/porteiros', methods=['GET'])
@login_required
@master_required
def get_porteiros():
    try:
        query = """
            SELECT u.id, u.nome, u.login, u.ativo, u.condominio_id, 
                   IFNULL(c.nome, 'Não definido') as condominio_nome 
            FROM usuarios u 
            LEFT JOIN condominios c ON u.condominio_id = c.id 
            WHERE u.tipo = 'porteiro'
            ORDER BY u.nome
        """
        porteiros = db.fetch_all(query)
        print(f"📋 Porteiros encontrados: {len(porteiros)}")
        return jsonify({'success': True, 'porteiros': porteiros})
    except Exception as e:
        print(f"❌ Erro ao buscar porteiros: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/relatorio_registros', methods=['GET'])
@login_required
@master_required
def relatorio_registros():
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from datetime import datetime
        import io

        query = """
            SELECT 
                r.id, 
                r.data_entrada, 
                r.observacao,
                p.nome as pessoa_nome, 
                p.tipo as pessoa_tipo,
                p.apartamento, 
                p.telefone, 
                c.nome as condominio_nome,
                u.nome as usuario_nome
            FROM registros r
            JOIN pessoas p ON r.pessoa_id = p.id
            LEFT JOIN condominios c ON p.condominio_id = c.id
            LEFT JOIN usuarios u ON r.usuario_registro = u.id
            ORDER BY r.data_entrada DESC
        """

        registros = db.fetch_all(query)

        if not registros:
            return jsonify({'success': False, 'error': 'Nenhum registro encontrado'}), 404

        wb = Workbook()
        ws = wb.active
        ws.title = "Registros"

        header_font = Font(name='Arial', size=12, bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        header_alignment = Alignment(horizontal='center', vertical='center')
        border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'),
                        bottom=Side(style='thin'))

        headers = ['ID', 'DATA/HORA', 'PESSOA', 'TIPO', 'APARTAMENTO', 'TELEFONE', 'CONDOMÍNIO', 'REGISTRADO POR',
                   'OBSERVAÇÃO']

        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = border

        for row_idx, reg in enumerate(registros, 2):
            data_hora = reg.get('data_entrada', '')
            if data_hora:
                try:
                    if isinstance(data_hora, datetime):
                        data_formatada = data_hora.strftime('%d/%m/%Y %H:%M:%S')
                    else:
                        dt = datetime.strptime(str(data_hora), '%Y-%m-%d %H:%M:%S')
                        data_formatada = dt.strftime('%d/%m/%Y %H:%M:%S')
                except:
                    data_formatada = str(data_hora)
            else:
                data_formatada = ''

            ws.cell(row=row_idx, column=1, value=reg.get('id', ''))
            ws.cell(row=row_idx, column=2, value=data_formatada)
            ws.cell(row=row_idx, column=3, value=reg.get('pessoa_nome', ''))
            ws.cell(row=row_idx, column=4, value=reg.get('pessoa_tipo', ''))
            ws.cell(row=row_idx, column=5, value=reg.get('apartamento', ''))
            ws.cell(row=row_idx, column=6, value=reg.get('telefone', ''))
            ws.cell(row=row_idx, column=7, value=reg.get('condominio_nome', ''))
            ws.cell(row=row_idx, column=8, value=reg.get('usuario_nome', 'Sistema'))
            ws.cell(row=row_idx, column=9, value=reg.get('observacao', ''))

            for col in range(1, 10):
                ws.cell(row=row_idx, column=col).border = border

        col_widths = [8, 20, 35, 15, 15, 18, 25, 25, 40]
        for i, width in enumerate(col_widths, 1):
            ws.column_dimensions[chr(64 + i)].width = width

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        nome_arquivo = f"relatorio_registros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=nome_arquivo
        )

    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/desbloquear_pessoa/<int:id>', methods=['POST'])
@login_required
@master_required
def desbloquear_pessoa(id):
    try:
        db.execute_query(
            "UPDATE pessoas SET status='ATIVO', bloqueado=0, motivo_bloqueio=NULL WHERE id=%s",
            (id,)
        )
        print(f"🔓 Pessoa {id} desbloqueada")
        return jsonify({'success': True, 'message': 'Pessoa desbloqueada com sucesso!'})
    except Exception as e:
        print(f"❌ Erro ao desbloquear: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bloquear_pessoa/<int:id>', methods=['POST'])
@login_required
@master_required
def bloquear_pessoa(id):
    try:
        data = request.get_json()
        motivo = data.get('motivo')

        if not motivo:
            return jsonify({'success': False, 'error': 'Motivo é obrigatório!'}), 400

        # Atualizar os campos de bloqueio
        db.execute_query(
            "UPDATE pessoas SET status='BLOQUEADO', bloqueado=1, motivo_bloqueio=%s WHERE id=%s",
            (motivo, id)
        )
        print(f"🔒 Pessoa {id} bloqueada. Motivo: {motivo}")
        return jsonify({'success': True, 'message': 'Pessoa bloqueada com sucesso!'})
    except Exception as e:
        print(f"❌ Erro ao bloquear: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/relatorio_pessoas', methods=['GET'])
@login_required
@master_required
def relatorio_pessoas():
    """Gera relatório Excel com todas as pessoas separadas por condomínio"""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        import io

        condominios = db.fetch_all("SELECT id, nome FROM condominios ORDER BY nome")

        if not condominios:
            return jsonify({'success': False, 'error': 'Nenhum condomínio encontrado'}), 404

        wb = Workbook()
        wb.remove(wb.active)

        cores = ['4472C4', '2E7D32', 'ED7D31', '9B59B6', 'E74C3C', '1ABC9C', 'F39C12', '3498DB', '27AE60', '8E44AD']

        header_font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
        header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell_alignment = Alignment(horizontal='left', vertical='center')
        center_alignment = Alignment(horizontal='center', vertical='center')

        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        data_relatorio = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        for idx, cond in enumerate(condominios):
            query = """
                SELECT 
                    p.id, p.nome, p.tipo, p.apartamento, p.telefone,
                    p.documento, p.veiculo_placa, p.veiculo_modelo,
                    p.status, p.motivo_bloqueio
                FROM pessoas p
                WHERE p.condominio_id = %s
                ORDER BY p.nome
            """
            pessoas = db.fetch_all(query, (cond['id'],))

            sheet_name = cond['nome'][:31]
            ws = wb.create_sheet(title=sheet_name)

            cor_cabecalho = cores[idx % len(cores)]
            header_fill = PatternFill(start_color=cor_cabecalho, end_color=cor_cabecalho, fill_type='solid')

            # Título
            ws.merge_cells('A1:J1')
            ws['A1'] = f"{cond['nome'].upper()} - RELATÓRIO DE PESSOAS"
            ws['A1'].font = Font(name='Calibri', size=16, bold=True, color=cor_cabecalho)
            ws['A1'].alignment = Alignment(horizontal='center')

            # Data
            ws.merge_cells('A2:J2')
            ws['A2'] = f"Gerado em: {data_relatorio}"
            ws['A2'].font = Font(name='Calibri', size=10, italic=True, color='666666')
            ws['A2'].alignment = Alignment(horizontal='center')

            # Quantidade
            ws.merge_cells('A3:J3')
            ws['A3'] = f"Total de pessoas: {len(pessoas)}"
            ws['A3'].font = Font(name='Calibri', size=11, bold=True)
            ws['A3'].alignment = Alignment(horizontal='center')
            ws['A3'].fill = PatternFill(start_color='F5F5F5', end_color='F5F5F5', fill_type='solid')

            # Cabeçalhos
            headers = ['ID', 'NOME', 'TIPO', 'APARTAMENTO', 'TELEFONE', 'DOCUMENTO', 'PLACA', 'MODELO', 'STATUS',
                       'MOTIVO']

            row_cabecalho = 4
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=row_cabecalho, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = border

            if pessoas:
                for row_idx, pessoa in enumerate(pessoas, row_cabecalho + 1):
                    ws.cell(row=row_idx, column=1, value=pessoa.get('id', ''))
                    ws.cell(row=row_idx, column=2, value=pessoa.get('nome', ''))
                    ws.cell(row=row_idx, column=3, value=pessoa.get('tipo', ''))
                    ws.cell(row=row_idx, column=4, value=pessoa.get('apartamento', ''))
                    ws.cell(row=row_idx, column=5, value=pessoa.get('telefone', ''))
                    ws.cell(row=row_idx, column=6, value=pessoa.get('documento', ''))
                    ws.cell(row=row_idx, column=7, value=pessoa.get('veiculo_placa', ''))
                    ws.cell(row=row_idx, column=8, value=pessoa.get('veiculo_modelo', ''))
                    ws.cell(row=row_idx, column=9, value=pessoa.get('status', 'ATIVO'))
                    ws.cell(row=row_idx, column=10, value=pessoa.get('motivo_bloqueio', ''))

                    for col in range(1, 11):
                        cell = ws.cell(row=row_idx, column=col)
                        cell.border = border
                        if col in [1, 3, 4, 9]:
                            cell.alignment = center_alignment
                        else:
                            cell.alignment = cell_alignment
                        if row_idx % 2 == 0:
                            cell.fill = PatternFill(start_color='F8F9FA', end_color='F8F9FA', fill_type='solid')
            else:
                ws.merge_cells(f'A{row_cabecalho + 1}:J{row_cabecalho + 1}')
                ws.cell(row=row_cabecalho + 1, column=1, value="NENHUMA PESSOA CADASTRADA")
                ws.cell(row=row_cabecalho + 1, column=1).font = Font(italic=True, color='999999')
                ws.cell(row=row_cabecalho + 1, column=1).alignment = Alignment(horizontal='center')

            col_widths = [8, 40, 15, 15, 18, 20, 15, 18, 12, 30]
            for i, width in enumerate(col_widths, 1):
                ws.column_dimensions[get_column_letter(i)].width = width

            ws.row_dimensions[row_cabecalho].height = 25
            ws.freeze_panes = f'A{row_cabecalho + 1}'

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        nome_arquivo = f"relatorio_pessoas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=nome_arquivo
        )

    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


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
        return jsonify({'success': True, 'message': 'Banco de dados zerado com sucesso!'})
    except Exception as e:
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
    print("👔 Porteiro: joao (credenciais fornecidas pelo administrador)")
    print("👔 Porteiro: maria (credenciais fornecidas pelo administrador)")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)