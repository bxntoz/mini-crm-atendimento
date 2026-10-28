"""Registro e consulta de atendimentos."""
from datetime import date

STATUS = ("aberto", "em_negociacao", "fechado")
CANAIS = ("telefone", "whatsapp", "email", "presencial")


def registrar(conn, cliente_id, canal, assunto, status="aberto", data=None):
    if canal not in CANAIS:
        raise ValueError(f"Canal inválido. Use: {', '.join(CANAIS)}.")
    if status not in STATUS:
        raise ValueError(f"Status inválido. Use: {', '.join(STATUS)}.")
    if not assunto.strip():
        raise ValueError("O assunto é obrigatório.")
    cur = conn.execute(
        "INSERT INTO atendimentos (cliente_id, data, canal, assunto, status) VALUES (?, ?, ?, ?, ?)",
        (cliente_id, data or date.today().isoformat(), canal, assunto.strip(), status),
    )
    conn.commit()
    return cur.lastrowid


def listar(conn, cliente_id=None, status=None):
    sql = (
        "SELECT a.*, c.nome AS cliente FROM atendimentos a "
        "JOIN clientes c ON c.id = a.cliente_id WHERE 1=1"
    )
    params = []
    if cliente_id is not None:
        sql += " AND a.cliente_id = ?"
        params.append(cliente_id)
    if status is not None:
        sql += " AND a.status = ?"
        params.append(status)
    return conn.execute(sql + " ORDER BY a.data DESC, a.id DESC", params).fetchall()


def atualizar_status(conn, atendimento_id, status):
    if status not in STATUS:
        raise ValueError(f"Status inválido. Use: {', '.join(STATUS)}.")
    cur = conn.execute(
        "UPDATE atendimentos SET status = ? WHERE id = ?", (status, atendimento_id)
    )
    conn.commit()
    return cur.rowcount > 0
