"""Interface de linha de comando do Mini CRM de Atendimento.

Execute com:  python -m src.main
"""
import sqlite3
from datetime import date

from src import atendimentos, banco, clientes, negociacoes, relatorios

MENU = """
=== Mini CRM de Atendimento ===
1. Cadastrar cliente
2. Listar / buscar clientes
3. Registrar atendimento
4. Listar atendimentos
5. Abrir negociação
6. Avançar ou encerrar negociação
7. Relatórios
8. Exportar para CSV
0. Sair
"""


def ler(msg, padrao=""):
    return input(f"{msg}: ").strip() or padrao


def ler_int(msg):
    while True:
        try:
            return int(input(f"{msg}: "))
        except ValueError:
            print("Digite um número inteiro.")


def ler_valor(msg):
    while True:
        try:
            return float(input(f"{msg}: ").replace(",", "."))
        except ValueError:
            print("Digite um valor numérico, por exemplo 1500,50.")


def mostrar_clientes(lista):
    if not lista:
        print("Nenhum cliente encontrado.")
    for c in lista:
        print(f"[{c['id']}] {c['nome']} | {c['telefone']} | {c['email']}")


def cadastrar_cliente(conn):
    novo_id = clientes.criar(conn, ler("Nome"), ler("Telefone"), ler("E-mail"))
    print(f"Cliente cadastrado com o id {novo_id}.")


def listar_clientes(conn):
    termo = ler("Buscar por nome, e-mail ou telefone (Enter lista todos)")
    mostrar_clientes(clientes.buscar(conn, termo) if termo else clientes.listar(conn))


def registrar_atendimento(conn):
    cid = ler_int("Id do cliente")
    canal = ler(f"Canal ({'/'.join(atendimentos.CANAIS)})")
    assunto = ler("Assunto")
    status = ler(f"Status ({'/'.join(atendimentos.STATUS)}) [aberto]", "aberto")
    atendimentos.registrar(conn, cid, canal, assunto, status)
    print("Atendimento registrado.")


def listar_atendimentos(conn):
    status = ler("Filtrar por status (Enter para todos)") or None
    lista = atendimentos.listar(conn, status=status)
    if not lista:
        print("Nenhum atendimento encontrado.")
    for a in lista:
        print(f"[{a['id']}] {a['data']} | {a['cliente']} | {a['canal']} | {a['assunto']} | {a['status']}")


def abrir_negociacao(conn):
    cid = ler_int("Id do cliente")
    nid = negociacoes.abrir(conn, cid, ler("Descrição"), ler_valor("Valor (R$)"))
    print(f"Negociação aberta com o id {nid}.")


def gerenciar_negociacao(conn):
    for n in negociacoes.listar(conn, "em_andamento"):
        print(f"[{n['id']}] {n['cliente']} | {n['descricao']} | R$ {n['valor']:.2f} | {n['etapa']}")
    nid = ler_int("Id da negociação")
    acao = ler("A = avançar etapa, G = encerrar como ganha, P = encerrar como perdida").upper()
    if acao == "A":
        print(f"Nova etapa: {negociacoes.avancar_etapa(conn, nid)}")
    elif acao in ("G", "P"):
        print(f"Negociação encerrada como {negociacoes.encerrar(conn, nid, acao == 'G')}.")
    else:
        print("Opção inválida.")


def mostrar_relatorios(conn):
    print("\nAtendimentos por status:")
    for status, total in relatorios.atendimentos_por_status(conn).items():
        print(f"  {status}: {total}")
    hoje = date.today()
    total = relatorios.total_negociado_mes(conn, hoje.year, hoje.month)
    print(f"\nTotal negociado (ganhas) em {hoje.month:02d}/{hoje.year}: R$ {total:,.2f}")
    print("\nClientes sem contato há mais de 30 dias:")
    sem_contato = relatorios.clientes_sem_contato(conn, 30)
    for c in sem_contato:
        print(f"  [{c['id']}] {c['nome']} (último contato: {c['ultimo_contato'] or 'nunca'})")
    if not sem_contato:
        print("  Nenhum.")


def exportar(conn):
    tabela = ler(f"Tabela ({'/'.join(relatorios.TABELAS_EXPORTAVEIS)})")
    caminho = ler("Nome do arquivo [exportacao.csv]", "exportacao.csv")
    print(f"{relatorios.exportar_csv(conn, tabela, caminho)} linhas exportadas para {caminho}.")


ACOES = {
    "1": cadastrar_cliente,
    "2": listar_clientes,
    "3": registrar_atendimento,
    "4": listar_atendimentos,
    "5": abrir_negociacao,
    "6": gerenciar_negociacao,
    "7": mostrar_relatorios,
    "8": exportar,
}


def main():
    conn = banco.conectar()
    while True:
        print(MENU)
        opcao = ler("Escolha uma opção")
        if opcao == "0":
            print("Até logo!")
            break
        acao = ACOES.get(opcao)
        if acao is None:
            print("Opção inválida.")
            continue
        try:
            acao(conn)
        except (ValueError, sqlite3.IntegrityError) as erro:
            print(f"Não foi possível concluir: {erro}")
    conn.close()


if __name__ == "__main__":
    main()
