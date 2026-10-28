"""CRUD de clientes."""
CAMPOS_EDITAVEIS = {"nome", "telefone", "email"}


def criar(conn, nome, telefone="", email=""):
    nome = nome.strip()
    if not nome:
        raise ValueError("O nome do cliente é obrigatório.")
    cur = conn.execute(
        "INSERT INTO clientes (nome, telefone, email) VALUES (?, ?, ?)",
        (nome, telefone.strip(), email.strip()),
    )
    conn.commit()
    return cur.lastrowid


def obter(conn, cliente_id):
    return conn.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,)).fetchone()


def listar(conn):
    return conn.execute("SELECT * FROM clientes ORDER BY nome").fetchall()


def buscar(conn, termo):
    """Procura por parte do nome, e-mail ou telefone."""
    like = f"%{termo.strip()}%"
    return conn.execute(
        "SELECT * FROM clientes WHERE nome LIKE ? OR email LIKE ? OR telefone LIKE ? ORDER BY nome",
        (like, like, like),
    ).fetchall()


def editar(conn, cliente_id, **campos):
    invalidos = set(campos) - CAMPOS_EDITAVEIS
    if invalidos or not campos:
        raise ValueError(f"Campos inválidos: {sorted(invalidos) or 'nenhum informado'}")
    if "nome" in campos and not campos["nome"].strip():
        raise ValueError("O nome do cliente é obrigatório.")
    colunas = ", ".join(f"{c} = ?" for c in campos)
    cur = conn.execute(
        f"UPDATE clientes SET {colunas} WHERE id = ?", (*campos.values(), cliente_id)
    )
    conn.commit()
    return cur.rowcount > 0


def excluir(conn, cliente_id):
    """Remove o cliente e, em cascata, seus atendimentos e negociações."""
    cur = conn.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    conn.commit()
    return cur.rowcount > 0
