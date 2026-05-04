@'


"""
Script para popular o banco PostgreSQL com dados de teste
"""
import psycopg2
import bcrypt
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração do PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'database': 'condominio_db',
    'user': 'condominio_user',
    'password': 'Condominio@2024',
    'port': 5432
}


def hash_senha(senha):
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def popular_banco():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    print("=" * 70)
    print("     POPULANDO BANCO POSTGRESQL COM DADOS DE TESTE")
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
        cursor.execute(
            "INSERT INTO condominios (nome, endereco, cor) VALUES (%s, %s, %s) ON CONFLICT (nome) DO NOTHING", cond)

    conn.commit()
    print(f"✅ {len(condominios)} condomínios inseridos")

    # ==================== USUÁRIOS ====================
    # Master
    cursor.execute("""
        INSERT INTO usuarios (nome, email, senha, perfil, condominio_id, ativo)
        VALUES (%s, %s, %s, 'MASTER', NULL, 1) ON CONFLICT (email) DO NOTHING
    """, ('Administrador Master', 'master@condominio.com', hash_senha('123456')))

    # Porteiros
    nomes_porteiros = [
        'Carlos Silva', 'Maria Santos', 'José Oliveira', 'Ana Souza', 'Pedro Lima',
        'Lucia Ferreira', 'Rafael Costa', 'Fernanda Rocha', 'Paulo Almeida', 'Juliana Martins'
    ]

    cursor.execute("SELECT id FROM condominios")
    condominios_ids = [row[0] for row in cursor.fetchall()]

    for i, cond_id in enumerate(condominios_ids[:10]):
        if i < len(nomes_porteiros):
            nome = nomes_porteiros[i]
            email = f"{nome.lower().replace(' ', '.')}@condominio.com"
            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha, perfil, condominio_id, ativo)
                VALUES (%s, %s, %s, 'PORTEIRO', %s, 1) ON CONFLICT (email) DO NOTHING
            """, (nome, email, hash_senha('123456'), cond_id))

    conn.commit()
    print(f"✅ {len(nomes_porteiros)} porteiros inseridos")

    # ==================== PESSOAS ====================
    nomes = [
        'João Silva', 'Maria Oliveira', 'Pedro Santos', 'Ana Costa', 'Lucas Lima',
        'Fernanda Souza', 'Rafael Almeida', 'Patricia Rocha', 'Marcelo Gomes', 'Juliana Dias'
    ]

    documentos = [
        '123.456.789-00', '987.654.321-00', '456.789.123-00', '321.654.987-00', '789.123.456-00'
    ]

    placas = [
        'ABC-1234', 'DEF-5678', 'GHI-9012', 'JKL-3456', 'MNO-7890'
    ]

    telefones = [
        '(11) 91234-5678', '(21) 98765-4321', '(31) 99876-5432', '(41) 98765-1234', '(51) 91234-8765'
    ]

    casas = ['101', '202', '303', '404', '505', '606', '707', '808', '909', '1001']

    # MORADORES (30)
    for i in range(30):
        cond_id = random.choice(condominios_ids)
        nome = random.choice(nomes) + f" {random.randint(1, 99)}"
        documento = random.choice(documentos) if random.random() > 0.3 else ''
        placa = random.choice(placas) if random.random() > 0.5 else ''
        telefone = random.choice(telefones) if random.random() > 0.3 else ''
        casa = random.choice(casas)
        observacao = f"Morador desde {random.randint(2020, 2025)}"

        cursor.execute("""
            INSERT INTO pessoas (condominio_id, tipo, nome, documento, placa, telefone, casa, observacao)
            VALUES (%s, 'MORADOR', %s, %s, %s, %s, %s, %s)
        """, (cond_id, nome, documento, placa, telefone, casa, observacao))

    # VISITANTES (30)
    for i in range(30):
        cond_id = random.choice(condominios_ids)
        nome = f"Visitante {random.choice(['Amazon', 'Magazine', 'Shopee', 'Técnico', 'Parente'])} {random.randint(1, 50)}"
        documento = random.choice(documentos) if random.random() > 0.4 else ''
        placa = random.choice(placas) if random.random() > 0.6 else ''
        telefone = random.choice(telefones) if random.random() > 0.4 else ''
        casa = random.choice(casas)
        observacao = f"Motivo: {random.choice(['Entrega', 'Manutenção', 'Visita', 'Serviço'])}"

        cursor.execute("""
            INSERT INTO pessoas (condominio_id, tipo, nome, documento, placa, telefone, casa, observacao)
            VALUES (%s, 'VISITANTE', %s, %s, %s, %s, %s, %s)
        """, (cond_id, nome, documento, placa, telefone, casa, observacao))

    conn.commit()
    print(f"✅ 30 moradores e 30 visitantes inseridos")

    # ==================== REGISTROS ====================
    agora = datetime.now()
    data_inicio = agora - timedelta(days=180)

    def data_aleatoria():
        return data_inicio + timedelta(days=random.randint(0, 180), hours=random.randint(0, 23),
                                       minutes=random.randint(0, 59))

    # ENCOMENDAS (30)
    empresas = ['Amazon', 'Magazine Luiza', 'Shopee', 'Mercado Livre', 'Shein']
    for i in range(30):
        cond_id = random.choice(condominios_ids)
        destinatario = random.choice(nomes)
        entregador = f"Entregador {random.choice(['José', 'Carlos', 'Marcos'])}"
        status = random.choice(['AGUARDANDO', 'RECEBIDO', 'RETIRADO'])
        empresa = random.choice(empresas)

        cursor.execute("""
            INSERT INTO registros (condominio_id, tipo, titulo, descricao, status, cor, entregador, destinatario, data_hora)
            VALUES (%s, 'ENCOMENDA', %s, %s, %s, '#2ecc71', %s, %s, %s)
        """, (cond_id, f"{empresa} - Produto {i + 1}", f"Pacote {random.choice(['pequeno', 'médio', 'grande'])}",
              status, entregador, destinatario, data_aleatoria()))

    # AVISOS (30)
    titulos_avisos = [
        'Manutenção programada', 'Assembleia Geral', 'Festa do condomínio', 'Limpeza caixa dágua', 'Poda de árvores'
    ]
    for i in range(30):
        cond_id = random.choice(condominios_ids)
        titulo = random.choice(titulos_avisos)
        descricao = f"Aviso: {titulo} será realizada no dia {random.randint(1, 30)}/{random.randint(1, 12)}"

        cursor.execute("""
            INSERT INTO registros (condominio_id, tipo, titulo, descricao, status, cor, data_hora)
            VALUES (%s, 'AVISO', %s, %s, 'ATIVO', '#f39c12', %s)
        """, (cond_id, titulo, descricao, data_aleatoria()))

    # ENTRADAS/SAÍDAS (30)
    for i in range(30):
        cond_id = random.choice(condominios_ids)
        visitante_nome = f"Visitante {random.randint(1, 100)}"
        casa_visitada = random.choice(casas)
        hora_entrada = data_aleatoria()
        hora_saida = hora_entrada + timedelta(hours=random.randint(1, 4)) if random.random() > 0.3 else None
        status = 'FINALIZADO' if hora_saida else 'DENTRO'

        cursor.execute("""
            INSERT INTO registros (condominio_id, tipo, titulo, visitando, hora_entrada, hora_saida, status, cor, data_hora)
            VALUES (%s, 'ENTRADA', %s, %s, %s, %s, %s, '#3498db', %s)
        """, (cond_id, f"Visita de {visitante_nome}", casa_visitada,
              hora_entrada, hora_saida, status, hora_entrada))

    conn.commit()

    print(f"✅ 30 encomendas, 30 avisos, 30 entradas inseridos")

    # ==================== ESTATÍSTICAS ====================
    cursor.execute("SELECT COUNT(*) FROM condominios")
    total_cond = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE perfil = 'PORTEIRO'")
    total_porteiros = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pessoas WHERE tipo = 'MORADOR'")
    total_moradores = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pessoas WHERE tipo = 'VISITANTE'")
    total_visitantes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM registros")
    total_registros = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    print("\n" + "=" * 70)
    print("  ✅ BANCO POSTGRESQL POPULADO COM SUCESSO!")
    print("=" * 70)
    print(f"\n📊 ESTATÍSTICAS FINAIS:")
    print(f"   🏘️ Condomínios: {total_cond}")
    print(f"   👮 Porteiros: {total_porteiros}")
    print(f"   👥 Moradores: {total_moradores}")
    print(f"   🚶 Visitantes: {total_visitantes}")
    print(f"   📋 Registros: {total_registros}")
    print("\n🔑 CREDENCIAIS:")
    print("   Master: master@condominio.com / 123456")
    print("   Porteiro: carlos.silva@condominio.com / 123456")
    print("=" * 70)


if __name__ == "__main__":
    popular_banco()
'@ | Out-File -FilePath popular_postgres.py -Encoding UTF8