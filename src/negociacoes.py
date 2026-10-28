"""Funil simples de negociações: proposta -> negociacao -> fechamento."""
from datetime import date

ETAPAS = ("proposta", "negociacao", "fechamento")


def abrir(conn, cliente_id, descricao, valor, data=None):
    if not descricao.strip():
        raise ValueError("A descrição é obrigatória.")
    if valor <= 0:
        raise ValueError("O valor deve ser maior que zero.")
    cur = conn.execute(
        "INSERT INTO negociacoes (cliente_id, descricao, valor, criado_em) VALUES (?, ?, ?, ?)",
        (cliente_id, descricao.strip(), valor, data or date.today().isoformat()),
    )
    conn.commit()
    return cur.lastrowid


def listar(conn, resultado=None):
    sql = (
        "SELECT n.*, c.nome AS cliente FROM negociacoes n "
        "JOIN clientes c ON c.id = n.cliente_id"
    )
    params = []
    if resultado:
        sql += " WHERE n.resultado = ?"
        params.append(resultado)
    return conn.execute(sql + " ORDER BY n.id DESC", params).fetchall()


def avancar_etapa(conn, negociacao_id):
    """Move para a próxima etapa do funil. Retorna a nova etapa."""
    neg = conn.execute("SELECT * FROM negociacoes WHERE id = ?", (negociacao_id,)).fetchone()
    if neg is None:
        raise ValueError("Negociação não encontrada.")
    if neg["resultado"] != "em_andamento":
        raise ValueError("Esta negociação já foi encerrada.")
    pos = ETAPAS.index(neg["etapa"])
    if pos == len(ETAPAS) - 1:
        raise ValueError("Já está na última etapa. Encerre como ganha ou perdida.")
    nova = ETAPAS[pos + 1]
    conn.execute("UPDATE negociacoes SET etapa = ? WHERE id = ?", (nova, negociacao_id))
    conn.commit()
    return nova


def encerrar(conn, negociacao_id, ganha, data=None):
    resultado = "ganha" if ganha else "perdida"
    cur = conn.execute(
        "UPDATE negociacoes SET resultado = ?, fechado_em = ? "
        "WHERE id = ? AND resultado = 'em_andamento'",
        (resultado, data or date.today().isoformat(), negociacao_id),
    )
    conn.commit()
    if cur.rowcount == 0:
        raise ValueError("Negociação não encontrada ou já encerrada.")
    return resultado
