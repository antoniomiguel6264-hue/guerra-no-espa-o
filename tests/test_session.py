import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import main
from game.session import _selecionar_fundo_sessao


def test_modo_infinito_usa_fundo_infinito_sem_mudar_fundos_de_fase():
    fundos_fase = ("fase 1", "fase 2", "fase 3", "fase 4")
    fundo_infinito = "infinito"

    assert _selecionar_fundo_sessao(
        "infinito", 1, fundos_fase, fundo_infinito
    ) == fundo_infinito
    assert _selecionar_fundo_sessao(
        "asteroides", 1, fundos_fase, fundo_infinito
    ) == fundos_fase[0]
    assert _selecionar_fundo_sessao(
        "frota_inimiga", 4, fundos_fase, fundo_infinito
    ) == fundos_fase[3]


def test_jogo_principal_delega_sessao_com_servicos_explicitos(monkeypatch):
    main.inicializar_app()
    chamada = {}

    def executar_sessao(*args, services):
        chamada["args"] = args
        chamada["services"] = services
        return 120, 3, True

    monkeypatch.setattr(main, "run_game_session", executar_sessao)

    resultado = main.jogo_principal(
        "Vanguard.png",
        {"cadencia": 1},
        fase_atual=2,
        modo_jogo="frota_inimiga",
        dados_jogador={"moedas": 0},
    )

    assert resultado == (120, 3, True)
    assert chamada["args"] == (
        "Vanguard.png",
        {"cadencia": 1},
        2,
        "frota_inimiga",
        {"moedas": 0},
    )
    assert chamada["services"].clock is main.relogio
    assert chamada["services"].resize_display is main.atualizar_tamanho_tela
    assert chamada["services"].asteroid_damage is main.calcular_dano_asteroide
    assert chamada["services"].infinite_background is main.fundo_infinito
