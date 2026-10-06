import pytest

from entidades import Nave
from game.achievements import (
    TEMPO_SOBREVIVENTE_MS,
    acumular_tempo_sobrevivencia,
    listar_conquistas,
    normalizar_conquistas,
    desbloquear_conquista,
)
from salvamento import normalizar_dados_jogador


def test_normalizar_conquistas_filtra_ids_invalidos_e_remove_duplicatas():
    assert normalizar_conquistas(
        ["sobrevivente", "desconhecida", "sobrevivente", None, "intocavel"]
    ) == ["sobrevivente", "intocavel"]


def test_desbloquear_conquista_e_idempotente():
    dados = {"conquistas_desbloqueadas": []}

    assert desbloquear_conquista(dados, "sobrevivente")
    assert not desbloquear_conquista(dados, "sobrevivente")
    assert dados["conquistas_desbloqueadas"] == ["sobrevivente"]


def test_id_desconhecido_nao_e_aceito():
    with pytest.raises(ValueError, match="Conquista desconhecida"):
        desbloquear_conquista({}, "medalha_inventada")


def test_lista_informa_conquistas_bloqueadas_e_desbloqueadas():
    conquistas = listar_conquistas({"conquistas_desbloqueadas": ["intocavel"]})

    assert [item["id"] for item in conquistas] == ["sobrevivente", "intocavel"]
    assert [item["desbloqueada"] for item in conquistas] == [False, True]


def test_save_antigo_recebe_lista_vazia_de_conquistas():
    dados = normalizar_dados_jogador(
        {"moedas": 5, "naves_desbloqueadas": ["Vanguard.png"], "niveis_melhorias": {}}
    )

    assert dados["conquistas_desbloqueadas"] == []


def test_dominio_filtra_ids_de_conquista_desconhecidos():
    assert normalizar_conquistas(
        ["sobrevivente", "conquista_futura", "sobrevivente"]
    ) == ["sobrevivente"]


def test_sobrevivencia_so_acumula_no_modo_infinito_e_sem_pausa():
    decorrido = acumular_tempo_sobrevivencia(1000, 500, True, False)
    assert decorrido == 1500
    assert acumular_tempo_sobrevivencia(decorrido, 20_000, True, True) == decorrido
    assert acumular_tempo_sobrevivencia(decorrido, 20_000, False, False) == decorrido


def test_tempo_de_sobrevivencia_configurado_em_cinco_minutos():
    assert TEMPO_SOBREVIVENTE_MS == 300_000


def test_dano_sofrido_sinaliza_apenas_dano_efetivamente_recebido():
    nave = Nave(100, 100, "Vanguard.png")

    assert not nave.dano_sofrido
    nave.perder_vida()
    assert nave.dano_sofrido

    nave.dano_sofrido = False
    nave.perder_vida()
    assert not nave.dano_sofrido
