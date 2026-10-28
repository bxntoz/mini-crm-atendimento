"""Relatórios e exportação para CSV."""
import csv
from datetime import date, timedelta

TABELAS_EXPORTAVEIS = ("clientes", "atendimentos", "negociacoes")


def atendimentos_por_status(conn):
    """Retorna {'aberto': n, 'em_negociacao': n, 'fechado': n}."""
    resultado = {"aberto": 0, "em_negociacao": 0, "fechado": 0}
    for linha in conn.execute("SELECT status, COUNT(*) AS total FROM atendimentos GROUP BY status"):
        resultado[linha["status"]] = linha["total"]
    return resultado


def total_negociado_mes(conn, ano, mes):
    """Soma o valor das negociações ganhas e fechadas no mês."""
    prefixo = f"{ano:04d}-{mes:02d}"
    linha = conn.execute(
        "SELECT COALESCE(SUM(valor), 0) AS total FROM negociacoes "
        "WHERE resultado = 'ganha' AND substr(fechado_em, 1, 7) = ?",
        (prefixo,),
    ).fetchone()
    return linha["total"]


def clientes_sem_contato(conn, dias=30, hoje=None):
    """Clientes sem atendimento há mais de `dias` dias (ou que nunca tiveram)."""
    limite = ((hoje or date.today()) - timedelta(days=dias)).isoformat()
    return conn.execute(
        "SELECT c.id, c.nome, MAX(a.data) AS ultimo_contato "
        "FROM clientes c LEFT JOIN atendimentos a ON a.cliente_id = c.id "
        "GROUP BY c.id HAVING ultimo_contato IS NULL OR ultimo_contato < ? "
        "ORDER BY c.nome",
        (limite,),
    ).fetchall()


def exportar_csv(conn, tabela, caminho):
    """Exporta uma tabela para CSV (abre direto no Excel). Retorna o nº de linhas."""
    if tabela not in TABELAS_EXPORTAVEIS:
        raise ValueError(f"Tabela inválida. Use: {', '.join(TABELAS_EXPORTAVEIS)}.")
    cur = conn.execute(f"SELECT * FROM {tabela}")
    linhas = cur.fetchall()
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.writer(f, delimiter=";")
        escritor.writerow([d[0] for d in cur.description])
        escritor.writerows([tuple(l) for l in linhas])
    return len(linhas)
