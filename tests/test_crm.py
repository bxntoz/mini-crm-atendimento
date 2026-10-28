import pytest

from src import atendimentos, banco, clientes, negociacoes, relatorios
from datetime import date


@pytest.fixture
def conn():
    c = banco.conectar(":memory:")
    yield c
    c.close()


@pytest.fixture
def ana(conn):
    return clientes.criar(conn, "Ana Souza", "11 91234-5678", "ana@exemplo.com")


def test_criar_e_buscar_cliente(conn, ana):
    assert clientes.obter(conn, ana)["nome"] == "Ana Souza"
    assert len(clientes.buscar(conn, "souza")) == 1
    assert clientes.buscar(conn, "inexistente") == []


def test_nome_vazio_e_rejeitado(conn):
    with pytest.raises(ValueError):
        clientes.criar(conn, "   ")


def test_editar_cliente(conn, ana):
    assert clientes.editar(conn, ana, telefone="11 90000-0000")
    assert clientes.obter(conn, ana)["telefone"] == "11 90000-0000"
    with pytest.raises(ValueError):
        clientes.editar(conn, ana, id=99)


def test_atendimento_valida_canal_e_status(conn, ana):
    with pytest.raises(ValueError):
        atendimentos.registrar(conn, ana, "pombo-correio", "Teste")
    with pytest.raises(ValueError):
        atendimentos.registrar(conn, ana, "email", "Teste", status="perdido")
    atendimentos.registrar(conn, ana, "email", "Dúvida")
    assert len(atendimentos.listar(conn, cliente_id=ana)) == 1


def test_excluir_cliente_remove_historico(conn, ana):
    atendimentos.registrar(conn, ana, "telefone", "Contato")
    negociacoes.abrir(conn, ana, "Plano", 100)
    assert clientes.excluir(conn, ana)
    assert atendimentos.listar(conn) == []
    assert negociacoes.listar(conn) == []


def test_funil_de_negociacao(conn, ana):
    nid = negociacoes.abrir(conn, ana, "Plano anual", 1000)
    assert negociacoes.avancar_etapa(conn, nid) == "negociacao"
    assert negociacoes.avancar_etapa(conn, nid) == "fechamento"
    with pytest.raises(ValueError):
        negociacoes.avancar_etapa(conn, nid)
    assert negociacoes.encerrar(conn, nid, ganha=True) == "ganha"
    with pytest.raises(ValueError):
        negociacoes.encerrar(conn, nid, ganha=False)


def test_valor_invalido(conn, ana):
    with pytest.raises(ValueError):
        negociacoes.abrir(conn, ana, "Plano", 0)


def test_total_negociado_considera_so_ganhas_do_mes(conn, ana):
    a = negociacoes.abrir(conn, ana, "A", 1000)
    b = negociacoes.abrir(conn, ana, "B", 500)
    c = negociacoes.abrir(conn, ana, "C", 700)
    negociacoes.encerrar(conn, a, True, data="2026-10-05")
    negociacoes.encerrar(conn, b, False, data="2026-10-06")
    negociacoes.encerrar(conn, c, True, data="2026-09-30")
    assert relatorios.total_negociado_mes(conn, 2026, 10) == 1000
    assert relatorios.total_negociado_mes(conn, 2026, 9) == 700


def test_atendimentos_por_status(conn, ana):
    atendimentos.registrar(conn, ana, "email", "A")
    atendimentos.registrar(conn, ana, "email", "B", status="fechado")
    assert relatorios.atendimentos_por_status(conn) == {
        "aberto": 1, "em_negociacao": 0, "fechado": 1,
    }


def test_clientes_sem_contato(conn, ana):
    bruno = clientes.criar(conn, "Bruno Lima")
    clientes.criar(conn, "Carla Dias")  # nunca teve atendimento
    atendimentos.registrar(conn, ana, "email", "Recente", data="2026-10-20")
    atendimentos.registrar(conn, bruno, "email", "Antigo", data="2026-08-01")
    nomes = [c["nome"] for c in relatorios.clientes_sem_contato(conn, 30, hoje=date(2026, 10, 28))]
    assert nomes == ["Bruno Lima", "Carla Dias"]


def test_exportar_csv(conn, ana, tmp_path):
    arquivo = tmp_path / "clientes.csv"
    assert relatorios.exportar_csv(conn, "clientes", arquivo) == 1
    assert "Ana Souza" in arquivo.read_text(encoding="utf-8-sig")
    with pytest.raises(ValueError):
        relatorios.exportar_csv(conn, "sqlite_master", arquivo)
