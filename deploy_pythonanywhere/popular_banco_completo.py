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

    print("=" * 70)
    print("     POPULANDO BANCO COM 30 REGISTROS POR CAMPO")
    print("=" * 70)

    # ==================== CONDOMÍNIOS ====================
    condominios = [
        ('AMERICA 3', 'Rua das Flores, 123, Jardim America', '#3498db'),
        ('FENIX', 'Av. Brasil, 456, Centro', '#e74c3c'),
        ('GRAN PARADISO', 'Rua dos Ipês, 789, Jardins', '#2ecc71'),
        ('M. RIBAAS', 'Av. Paulista, 1000, Bela Vista', '#f39c12'),
        ('VILLAGE AMAZON', 'Rua Amazonas, 50, Parque 10', '#9b59b6'),
        ('PASSAROS II', 'Av. das Aves, 200, Cidade Nova', '#1abc9c'),
        ('GRALHA AZUL', 'Rua Azul, 300, Alto da Serra', '#e67e22'),
        ('MORAR BEN', 'Rua da Paz, 400, Boa Vista', '#34495e'),
        ('MONTEBELO', 'Av. Monte Belo, 500, Alto Padrão', '#16a085'),
        ('PARQUE DAS FLORES', 'Rua das Orquídeas, 600, Jardim Flora', '#27ae60'),
    ]

    for cond in condominios:
        cursor.execute("INSERT OR IGNORE INTO condominios (nome, endereco, cor) VALUES (?, ?, ?)", cond)

    cursor.execute("SELECT id FROM condominios")
    condominios_ids = [row[0] for row in cursor.fetchall()]
    print(f"✅ {len(condominios_ids)} condomínios inseridos")

    # ==================== USUÁRIOS ====================
    # Master
    cursor.execute("""
        INSERT OR IGNORE INTO usuarios (nome, email, senha, perfil, condominio_id, ativo)
        VALUES (?, ?, ?, 'MASTER', NULL, 1)
    """, ('Administrador Master', 'master@condominio.com', hash_senha('123456')))

    # Porteiros (10)
    nomes_porteiros = [
        'Carlos Silva', 'Maria Santos', 'José Oliveira', 'Ana Souza', 'Pedro Lima',
        'Lucia Ferreira', 'Rafael Costa', 'Fernanda Rocha', 'Paulo Almeida', 'Juliana Martins'
    ]

    for i, cond_id in enumerate(condominios_ids[:10]):
        if i < len(nomes_porteiros):
            nome = nomes_porteiros[i]
            email = f"{nome.lower().replace(' ', '.')}@condominio.com"
            cursor.execute("""
                INSERT OR IGNORE INTO usuarios (nome, email, senha, perfil, condominio_id, ativo)
                VALUES (?, ?, ?, 'PORTEIRO', ?, 1)
            """, (nome, email, hash_senha('123456'), cond_id))

    print(f"✅ 10 porteiros inseridos")

    # ==================== PESSOAS ====================
    nomes_moradores = [
        'João Silva', 'Maria Oliveira', 'Pedro Santos', 'Ana Costa', 'Lucas Lima',
        'Fernanda Souza', 'Rafael Almeida', 'Patricia Rocha', 'Marcelo Gomes', 'Juliana Dias'
    ]

    nomes_visitantes = [
        'Entregador Amazon', 'Técnico Internet', 'Parente Silva', 'Amigo João', 'Prestador Serviço',
        'Entregador Magazine', 'Técnico TV', 'Parente Oliveira', 'Amigo Pedro', 'Prestador Limpeza'
    ]

    documentos = [
        '123.456.789-00', '987.654.321-00', '456.789.123-00', '321.654.987-00', '789.123.456-00',
        '147.258.369-00', '258.369.147-00', '369.147.258-00', '159.357.486-00', '753.951.852-00'
    ]

    placas = [
        'ABC-1234', 'DEF-5678', 'GHI-9012', 'JKL-3456', 'MNO-7890',
        'PQR-1234', 'STU-5678', 'VWX-9012', 'YZA-3456', 'BCD-7890'
    ]

    telefones = [
        '(11) 91234-5678', '(21) 98765-4321', '(31) 99876-5432', '(41) 98765-1234', '(51) 91234-8765',
        '(61) 99877-6655', '(71) 98766-5544', '(81) 91235-6789', '(91) 98765-4321', '(11) 99888-7777'
    ]

    casas = ['101', '202', '303', '404', '505', '606', '707', '808', '909', '1001', '1102', '1203', '1304', '1405',
             '1506']

    # MORADORES (30)
    for i in range(30):
        cond_id = random.choice(condominios_ids)
        nome = random.choice(nomes_moradores) + f" {random.randint(1, 99)}"
        documento = random.choice(documentos) if random.random() > 0.3 else ''
        placa = random.choice(placas) if random.random() > 0.5 else ''
        telefone = random.choice(telefones) if random.random() > 0.3 else ''
        casa = random.choice(casas)
        observacao = f"Morador desde {random.randint(2020, 2025)} - {random.choice(['Proprietário', 'Inquilino'])}"

        cursor.execute("""
            INSERT INTO pessoas (condominio_id, tipo, nome, documento, placa, telefone, casa, observacao)
            VALUES (?, 'MORADOR', ?, ?, ?, ?, ?, ?)
        """, (cond_id, nome, documento, placa, telefone, casa, observacao))

    # VISITANTES (30)
    for i in range(30):
        cond_id = random.choice(condominios_ids)
        nome = random.choice(nomes_visitantes) + f" {random.randint(1, 50)}"
        documento = random.choice(documentos) if random.random() > 0.4 else ''
        placa = random.choice(placas) if random.random() > 0.6 else ''
        telefone = random.choice(telefones) if random.random() > 0.4 else ''
        casa = random.choice(casas)
        observacao = f"Motivo: {random.choice(['Entrega', 'Manutenção', 'Visita', 'Serviço'])}"

        cursor.execute("""
            INSERT INTO pessoas (condominio_id, tipo, nome, documento, placa, telefone, casa, observacao)
            VALUES (?, 'VISITANTE', ?, ?, ?, ?, ?, ?)
        """, (cond_id, nome, documento, placa, telefone, casa, observacao))

    print(f"✅ 30 moradores e 30 visitantes inseridos")

    # Commit para garantir que as pessoas estão salvas
    conn.commit()

    # Buscar IDs das pessoas
    cursor.execute("SELECT id, nome, condominio_id FROM pessoas")
    pessoas_list = cursor.fetchall()

    # Buscar nomes dos porteiros
    cursor.execute("SELECT nome FROM usuarios WHERE perfil = 'PORTEIRO'")
    porteiros_nomes = [row[0] for row in cursor.fetchall()]
    if not porteiros_nomes:
        porteiros_nomes = ['Carlos Silva', 'Maria Santos', 'José Oliveira']

    agora = datetime.now()
    data_inicio = agora - timedelta(days=180)

    def data_aleatoria():
        return data_inicio + timedelta(days=random.randint(0, 180), hours=random.randint(0, 23),
                                       minutes=random.randint(0, 59))

    # ==================== ENCOMENDAS (30) ====================
    empresas = ['Amazon', 'Magazine Luiza', 'Shopee', 'Mercado Livre', 'Shein']
    for i in range(30):
        cond_id = random.choice(condominios_ids)
        destinatario = random.choice([p for p in pessoas_list if p[2] == cond_id]) if pessoas_list else None
        destinatario_nome = destinatario[1] if destinatario else 'Morador'
        entregador = f"Entregador {random.choice(['José', 'Carlos', 'Marcos', 'Paulo', 'Rafael'])}"
        status = random.choice(['AGUARDANDO', 'RECEBIDO', 'RETIRADO'])
        empresa = random.choice(empresas)
        registrado_por = random.choice(porteiros_nomes)
        data_registro = data_aleatoria()

        cursor.execute("""
            INSERT INTO registros (condominio_id, tipo, titulo, descricao, status, cor, entregador, destinatario, registrado_por, data_hora)
            VALUES (?, 'ENCOMENDA', ?, ?, ?, '#2ecc71', ?, ?, ?, ?)
        """, (cond_id, f"{empresa} - Produto {i + 1}",
              f"Pacote {random.choice(['pequeno', 'médio', 'grande'])} - Código: {random.randint(10000, 99999)}",
              status, entregador, destinatario_nome, registrado_por, data_registro.strftime("%Y-%m-%d %H:%M:%S")))

    # ==================== AVISOS (30) ====================
    titulos_avisos = [
        'Manutenção programada', 'Assembleia Geral', 'Festa do condomínio', 'Limpeza caixa dágua', 'Poda de árvores',
        'Pintura do prédio', 'Troca de interfone', 'Reforma da área comum', 'Campanha de vacinação', 'Bazar beneficente'
    ]
    for i in range(30):
        cond_id = random.choice(condominios_ids)
        titulo = random.choice(titulos_avisos)
        descricao = f"Aviso: {titulo} será realizada no dia {random.randint(1, 30)}/{random.randint(1, 12)} às {random.randint(8, 20)}h."
        registrado_por = random.choice(porteiros_nomes)
        data_aviso = data_aleatoria()

        cursor.execute("""
            INSERT INTO registros (condominio_id, tipo, titulo, descricao, status, cor, registrado_por, data_hora)
            VALUES (?, 'AVISO', ?, ?, 'ATIVO', '#f39c12', ?, ?)
        """, (cond_id, titulo, descricao, registrado_por, data_aviso.strftime("%Y-%m-%d %H:%M:%S")))

    # ==================== ENTRADAS/SAÍDAS (30) ====================
    for i in range(30):
        cond_id = random.choice(condominios_ids)

        # Buscar visitante do mesmo condomínio
        visitantes_cond = [p for p in pessoas_list if
                           p[2] == cond_id and ('Visitante' in p[1] or 'Entregador' in p[1] or 'Técnico' in p[1])]

        if visitantes_cond:
            visitante = random.choice(visitantes_cond)
            visitante_id = visitante[0]
            visitante_nome = visitante[1]
        else:
            visitante_id = None
            visitante_nome = f"Visitante {random.randint(1, 100)}"

        casa_visitada = random.choice(casas)
        hora_entrada = data_aleatoria()
        hora_saida = hora_entrada + timedelta(hours=random.randint(1, 6)) if random.random() > 0.3 else None
        status = 'FINALIZADO' if hora_saida else 'DENTRO'
        registrado_por = random.choice(porteiros_nomes)
        motivo = random.choice(['Visita', 'Entrega', 'Manutenção', 'Serviço', 'Obra'])

        cursor.execute("""
            INSERT INTO registros (condominio_id, tipo, titulo, pessoa_id, visitando, hora_entrada, hora_saida, status, cor, registrado_por, data_hora)
            VALUES (?, 'ENTRADA', ?, ?, ?, ?, ?, ?, '#3498db', ?, ?)
        """, (cond_id, f"{motivo} - {visitante_nome}", visitante_id,
              casa_visitada, hora_entrada.strftime("%Y-%m-%d %H:%M:%S"),
              hora_saida.strftime("%Y-%m-%d %H:%M:%S") if hora_saida else None,
              status, registrado_por, hora_entrada.strftime("%Y-%m-%d %H:%M:%S")))

    # ==================== OCORRÊNCIAS (30) ====================
    titulos_ocorrencias = [
        'Barulho excessivo', 'Vaga ocupada', 'Lixo fora do local', 'Animal solto', 'Festa não autorizada',
        'Dano à propriedade', 'Discussão entre moradores', 'Furto de encomenda', 'Vazamento de água',
        'Elevador quebrado'
    ]
    for i in range(30):
        cond_id = random.choice(condominios_ids)
        titulo = random.choice(titulos_ocorrencias)
        descricao = f"Ocorrência: {titulo} no local {random.choice(['apto', 'área comum', 'garagem', 'portaria'])}. Status: {random.choice(['Resolvido', 'Em andamento', 'Arquivado'])}"
        registrado_por = random.choice(porteiros_nomes)
        data_ocorrencia = data_aleatoria()

        cursor.execute("""
            INSERT INTO registros (condominio_id, tipo, titulo, descricao, status, cor, registrado_por, data_hora)
            VALUES (?, 'OCORRENCIA', ?, ?, 'EM_ANDAMENTO', '#e67e22', ?, ?)
        """, (cond_id, titulo, descricao, registrado_por, data_ocorrencia.strftime("%Y-%m-%d %H:%M:%S")))

    # ==================== RECLAMAÇÕES (30) ====================
    reclamacoes = [
        'Barulho do vizinho', 'Lixo na área comum', 'Animais sem coleira', 'Festa até tarde', 'Uso da garagem',
        'Som alto', 'Obra sem autorização', 'Pichação', 'Estacionamento irregular', 'Crianças soltas'
    ]
    for i in range(30):
        cond_id = random.choice(condominios_ids)
        titulo = random.choice(reclamacoes)
        descricao = f"Reclamação: {titulo} - {random.choice(['Morador', 'Visitante', 'Síndico', 'Porteiro'])} reportou o problema."
        registrado_por = random.choice(porteiros_nomes)
        data_reclamacao = data_aleatoria()

        cursor.execute("""
            INSERT INTO registros (condominio_id, tipo, titulo, descricao, status, cor, registrado_por, data_hora)
            VALUES (?, 'RECLAMACAO', ?, ?, 'PENDENTE', '#95a5a6', ?, ?)
        """, (cond_id, titulo, descricao, registrado_por, data_reclamacao.strftime("%Y-%m-%d %H:%M:%S")))

    print(f"✅ 30 encomendas, 30 avisos, 30 entradas, 30 ocorrências e 30 reclamações inseridos")

    # ==================== ESTATÍSTICAS FINAIS ====================
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM condominios")
    total_cond = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE perfil = 'PORTEIRO'")
    total_porteiros = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pessoas WHERE tipo = 'MORADOR'")
    total_moradores = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pessoas WHERE tipo = 'VISITANTE'")
    total_visitantes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM registros WHERE tipo = 'ENCOMENDA'")
    total_encomendas = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM registros WHERE tipo = 'AVISO'")
    total_avisos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM registros WHERE tipo = 'ENTRADA'")
    total_entradas = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM registros WHERE tipo = 'OCORRENCIA'")
    total_ocorrencias = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM registros WHERE tipo = 'RECLAMACAO'")
    total_reclamacoes = cursor.fetchone()[0]

    conn.close()

    print("\n" + "=" * 70)
    print("  ✅ BANCO POPULADO COM SUCESSO!")
    print("=" * 70)
    print(f"\n📊 ESTATÍSTICAS FINAIS:")
    print(f"   🏘️ Condomínios: {total_cond}")
    print(f"   👮 Porteiros: {total_porteiros}")
    print(f"   👥 Moradores: {total_moradores}")
    print(f"   🚶 Visitantes: {total_visitantes}")
    print(f"   📦 Encomendas: {total_encomendas}")
    print(f"   📢 Avisos: {total_avisos}")
    print(f"   🚪 Entradas/Saídas: {total_entradas}")
    print(f"   ⚠️ Ocorrências: {total_ocorrencias}")
    print(f"   💬 Reclamações: {total_reclamacoes}")
    print("\n🔑 CREDENCIAIS DE ACESSO:")
    print("   Master: master@condominio.com / 123456")
    print("   Porteiro: carlos.silva@condominio.com / 123456")
    print("=" * 70)


if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        resposta = input("⚠️ Banco já existe. Deseja recriá-lo? (s/N): ")
        if resposta.lower() == 's':
            os.remove(DB_PATH)
            print("✅ Banco antigo removido!")
            from database.init_db import init_db

            init_db()
            popular_banco()
        else:
            print("❌ Operação cancelada.")
    else:
        from database.init_db import init_db

        init_db()
        popular_banco()
