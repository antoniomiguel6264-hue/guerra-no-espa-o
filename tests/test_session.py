import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import main


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
