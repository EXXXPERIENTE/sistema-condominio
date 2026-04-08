#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para popular o banco de dados MySQL com dados de teste
Uso: python popular_mysql.py
"""

import mysql.connector
import random
from datetime import datetime, timedelta
import hashlib

# Configurações do banco MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'condominio_db'
}


def conectar():
    """Conecta ao banco MySQL"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        print("\nVerifique suas credenciais no arquivo")
        return None


def limpar_dados(cursor, conn):
    """Remove dados existentes"""
    resposta = input("\nDeseja limpar os dados existentes antes de popular? (s/N): ")
    if resposta.lower() == 's':
        cursor.execute("DELETE FROM registros")
        cursor.execute("DELETE FROM pessoas")
        cursor.execute("DELETE FROM avisos")
        cursor.execute("DELETE FROM ocorrencias")
        cursor.execute("DELETE FROM usuarios WHERE tipo = 'porteiro'")
        cursor.execute("DELETE FROM condominios WHERE id > 0")
        conn.commit()
        print("✅ Dados antigos removidos!")
        return True
    return False


def gerar_nome():
    """Gera nome aleatório"""
    nomes = ['João Silva', 'Maria Santos', 'José Oliveira', 'Ana Paula', 'Carlos Eduardo',
             'Fernanda Lima', 'Ricardo Alves', 'Patrícia Souza', 'Roberto Carlos', 'Juliana Costa',
             'André Luiz', 'Camila Rocha', 'Marcelo Vieira', 'Tatiana Mendes', 'Rafaela Dias',
             'Gustavo Lima', 'Beatriz Nunes', 'Thiago Martins', 'Larissa Faria', 'Diego Araújo']
    return random.choice(nomes)


def gerar_telefone():
    """Gera telefone aleatório"""
    return f"({random.randint(11, 99)}) {random.randint(90000, 99999)}-{random.randint(1000, 9999)}"


def gerar_apartamento():
    """Gera apartamento aleatório"""
    blocos = ['', 'A', 'B', 'C', 'D']
    return f"{random.randint(1, 200)}{random.choice(blocos)}"


def gerar_placa():
    """Gera placa de veículo"""
    letras = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return f"{random.choice(letras)}{random.choice(letras)}{random.choice(letras)}-{random.randint(1000, 9999)}"


def criar_condominios(cursor, conn, quantidade=5):
    """Cria condomínios fictícios"""
    print(f"\n🏢 Criando {quantidade} condomínios...")
    condominios = []
    nomes_cond = [
        'Residencial Solar', 'Parque das Flores', 'Village Garden', 'Plaza Center',
        'Torres Ipanema', 'Condomínio Belvedere', 'Jardim Europa', 'Parque Imperial',
        'Village Premium', 'Residencial Vista Alegre', 'Condomínio Monte Carlo',
        'Parque Residencial', 'Village das Águas', 'Residencial Barcelona'
    ]

    for i in range(quantidade):
        nome = random.choice(nomes_cond) + (f" {i + 1}" if i >= len(nomes_cond) else "")
        endereco = f"Rua {random.choice(['A', 'B', 'C', 'D', 'E'])} {random.randint(100, 999)}, {random.randint(1, 1000)}"
        telefone = gerar_telefone()

        cursor.execute("""
            INSERT INTO condominios (nome, endereco, telefone)
            VALUES (%s, %s, %s)
        """, (nome, endereco, telefone))

        condominio_id = cursor.lastrowid
        condominios.append({
            'id': condominio_id,
            'nome': nome
        })
        print(f"  ✅ Criado: {nome}")

    conn.commit()
    return condominios


def criar_pessoas(cursor, conn, condominios, quantidade=100):
    """Cria pessoas fictícias"""
    print(f"\n👥 Criando {quantidade} pessoas...")
    tipos = ['morador', 'visitante', 'entregador', 'tecnico']
    status_opcoes = ['ATIVO', 'ATIVO', 'ATIVO', 'ATIVO', 'BLOQUEADO']

    for i in range(quantidade):
        condominio = random.choice(condominios)
        nome = gerar_nome()
        tipo = random.choice(tipos)
        apartamento = gerar_apartamento() if tipo == 'morador' else ''
        telefone = gerar_telefone() if random.choice([True, False]) else ''
        documento = f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}" if random.choice(
            [True, False]) else ''
        veiculo = gerar_placa() if random.choice([True, False]) else ''
        status = random.choice(status_opcoes)

        cursor.execute("""
            INSERT INTO pessoas (nome, tipo, apartamento, telefone, documento, veiculo_placa, veiculo_modelo, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (nome, tipo, apartamento, telefone, documento, veiculo, veiculo, status))

        if (i + 1) % 20 == 0:
            print(f"  📊 {i + 1}/{quantidade} pessoas criadas...")

    print(f"  ✅ {quantidade} pessoas criadas!")
    conn.commit()


def criar_registros(cursor, conn, quantidade=200):
    """Cria registros de entrada fictícios"""
    print(f"\n📝 Criando {quantidade} registros de entrada...")

    # Busca todas as pessoas
    cursor.execute("SELECT id, nome FROM pessoas")
    pessoas = cursor.fetchall()

    if not pessoas:
        print("  ⚠️ Nenhuma pessoa encontrada para criar registros!")
        return

    for i in range(quantidade):
        pessoa = random.choice(pessoas)
        pessoa_id = pessoa[0]

        # Data aleatória nos últimos 30 dias
        dias_atras = random.randint(0, 30)
        horas = random.randint(8, 22)
        minutos = random.randint(0, 59)
        data_entrada = datetime.now() - timedelta(days=dias_atras, hours=horas, minutes=minutos)
        data_str = data_entrada.strftime('%Y-%m-%d %H:%M:%S')

        usuario = random.choice(['master', 'joao', 'porteiro_sistema'])

        cursor.execute("""
            INSERT INTO registros (pessoa_id, data_entrada, usuario)
            VALUES (%s, %s, %s)
        """, (pessoa_id, data_str, usuario))

        if (i + 1) % 50 == 0:
            print(f"  📊 {i + 1}/{quantidade} registros criados...")

    print(f"  ✅ {quantidade} registros criados!")
    conn.commit()


def criar_avisos(cursor, conn, quantidade=30):
    """Cria avisos fictícios"""
    print(f"\n📢 Criando {quantidade} avisos...")

    titulos = [
        'Manutenção programada', 'Feriado na portaria', 'Assembleia geral',
        'Taxa de condomínio', 'Obras no elevador', 'Vistoria de incêndio',
        'Evento de confraternização', 'Coleta seletiva', 'Vagas de visitantes',
        'Novo regulamento', 'Alerta de segurança', 'Campanha de vacinação'
    ]

    tipos = ['info', 'alerta', 'urgente', 'sucesso']
    mensagens = [
        'Informamos que...', 'Atenção moradores...', 'Comunicamos que...',
        'Favor verificar...', 'Importante saber...', 'Fique atento...'
    ]

    for i in range(quantidade):
        titulo = random.choice(titulos) + f" - {random.randint(1, 100)}"
        tipo = random.choice(tipos)
        mensagem = random.choice(mensagens) + " " + " ".join(random.choice(['A', 'B', 'C', 'D']) for _ in range(10))
        data_criacao = (datetime.now() - timedelta(days=random.randint(0, 15))).strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("""
            INSERT INTO avisos (titulo, tipo, mensagem, data_criacao)
            VALUES (%s, %s, %s, %s)
        """, (titulo, tipo, mensagem, data_criacao))

        if (i + 1) % 10 == 0:
            print(f"  📊 {i + 1}/{quantidade} avisos criados...")

    print(f"  ✅ {quantidade} avisos criados!")
    conn.commit()


def criar_ocorrencias(cursor, conn, quantidade=50):
    """Cria ocorrências fictícias"""
    print(f"\n⚠️ Criando {quantidade} ocorrências...")

    titulos = [
        'Barulho noturno', 'Vaga ocupada', 'Animal solto', 'Entregador não autorizado',
        'Portão quebrado', 'Iluminação defeituosa', 'Vazamento de água',
        'Som alto', 'Festa sem autorização', 'Descarte irregular'
    ]

    tipos = ['reclamacao', 'manutencao', 'sugestao', 'informe']
    prioridades = ['baixa', 'media', 'alta', 'urgente']

    for i in range(quantidade):
        titulo = random.choice(titulos)
        tipo = random.choice(tipos)
        prioridade = random.choice(prioridades)
        descricao = f"Ocorrência registrada: {titulo}. Detalhes adicionais sobre o problema."
        responsavel = random.choice(['João Porteiro', 'Maria Adm', 'Carlos Zelador', 'Não atribuído'])
        data_criacao = (datetime.now() - timedelta(days=random.randint(0, 20))).strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("""
            INSERT INTO ocorrencias (titulo, tipo, prioridade, descricao, responsavel, data_criacao, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'aberta')
        """, (titulo, tipo, prioridade, descricao, responsavel, data_criacao))

        if (i + 1) % 10 == 0:
            print(f"  📊 {i + 1}/{quantidade} ocorrências criadas...")

    print(f"  ✅ {quantidade} ocorrências criadas!")
    conn.commit()


def criar_porteiros(cursor, conn, condominios):
    """Cria porteiros adicionais para teste"""
    print(f"\n👮 Criando porteiros adicionais...")

    porteiros_existentes = [
        ('Carlos Porteiro', 'carlos', 'carlos123'),
        ('Marina Silva', 'marina', 'marina123'),
        ('Roberto Santos', 'roberto', 'roberto123'),
        ('Patrícia Lima', 'patricia', 'patricia123')
    ]

    for nome, login, senha in porteiros_existentes:
        # Verifica se já existe
        cursor.execute("SELECT id FROM usuarios WHERE login = %s", (login,))
        if not cursor.fetchone():
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            condominio_id = random.choice(condominios)['id'] if condominios else None

            cursor.execute("""
                INSERT INTO usuarios (nome, login, senha, tipo, condominio_id, ativo)
                VALUES (%s, %s, %s, 'porteiro', %s, 1)
            """, (nome, login, senha_hash, condominio_id))
            print(f"  ✅ Porteiro: {nome} (login: {login}, senha: {senha})")

    conn.commit()


def mostrar_estatisticas(cursor):
    """Mostra estatísticas do banco"""
    print("\n" + "=" * 60)
    print("📊 ESTATÍSTICAS DO BANCO DE DADOS (MySQL)")
    print("=" * 60)

    cursor.execute("SELECT COUNT(*) FROM condominios")
    condominios = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pessoas")
    pessoas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pessoas WHERE status = 'BLOQUEADO'")
    bloqueados = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM registros")
    registros = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM avisos")
    avisos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ocorrencias")
    ocorrencias = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo = 'porteiro'")
    porteiros = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo = 'master'")
    masters = cursor.fetchone()[0]

    print(f"🏢 Condomínios: {condominios}")
    print(f"👥 Pessoas: {pessoas}")
    print(f"  ├─ 🚫 Bloqueados: {bloqueados}")
    print(f"  └─ ✅ Ativos: {pessoas - bloqueados}")
    print(f"📝 Registros de entrada: {registros}")
    print(f"📢 Avisos: {avisos}")
    print(f"⚠️ Ocorrências: {ocorrencias}")
    print(f"👮 Porteiros: {porteiros}")
    print(f"👑 Administradores (master): {masters}")
    print("=" * 60)


def main():
    print("\n" + "=" * 60)
    print("🌱 POPULANDO BANCO DE DADOS MYSQL")
    print("=" * 60)

    conn = conectar()
    if not conn:
        return

    cursor = conn.cursor()

    # Limpar dados existentes (opcional)
    limpar_dados(cursor, conn)

    # Criar dados de teste
    condominios = criar_condominios(cursor, conn, quantidade=5)
    criar_pessoas(cursor, conn, condominios, quantidade=100)
    criar_registros(cursor, conn, quantidade=200)
    criar_avisos(cursor, conn, quantidade=30)
    criar_ocorrencias(cursor, conn, quantidade=50)
    criar_porteiros(cursor, conn, condominios)

    # Mostrar estatísticas
    mostrar_estatisticas(cursor)

    print("\n🔑 CREDENCIAIS DE ACESSO:")
    print("-" * 60)
    print(f"  👑 Master: login: master / senha: admin123")
    print(f"  👔 Porteiros: login: joao / senha: 123456")
    print(f"  👔 Porteiros adicionais: carlos, marina, roberto, patricia (senha: nome+123)")

    print("\n" + "=" * 60)
    print("✅ POPULAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print("\n💡 Acesse o sistema: http://localhost:5000")
    print("=" * 60 + "\n")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    # Verifica se o pacote mysql-connector está instalado
    try:
        import mysql.connector
    except ImportError:
        print("❌ Pacote 'mysql-connector-python' não encontrado!")
        print("\n📦 Instale com: pip install mysql-connector-python")
        exit(1)

    main()