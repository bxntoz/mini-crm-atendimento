"""Popula o banco com dados fictícios para testar e tirar prints.

Execute com:  python -m src.demo
"""
from datetime import date, timedelta

from src import atendimentos, banco, clientes, negociacoes


def popular(conn):
    hoje = date.today()
    ana = clientes.criar(conn, "Ana Souza", "(11) 91234-5678", "ana@exemplo.com")
    bruno = clientes.criar(conn, "Bruno Lima", "(11) 98765-4321", "bruno@exemplo.com")
    clientes.criar(conn, "Carla Dias", "(11) 95555-0000", "carla@exemplo.com")

    atendimentos.registrar(conn, ana, "whatsapp", "Dúvida sobre proposta", "em_negociacao")
    atendimentos.registrar(conn, bruno, "telefone", "Renovação de contrato", "fechado",
                           data=(hoje - timedelta(days=45)).isoformat())

    n1 = negociacoes.abrir(conn, ana, "Plano anual", 2400.00)
    negociacoes.avancar_etapa(conn, n1)
    n2 = negociacoes.abrir(conn, bruno, "Renovação de contrato", 1800.00)
    negociacoes.encerrar(conn, n2, ganha=True)


if __name__ == "__main__":
    conexao = banco.conectar()
    popular(conexao)
    print("Dados de exemplo criados em crm.db. Rode: python -m src.main")
