from game.rewards import registrar_fase_concluida, resgatar_recompensa
from salvamento import normalizar_dados_jogador


def test_progresso_da_campanha_e_compartilhado_entre_modos():
    dados = normalizar_dados_jogador({})

    registrar_fase_concluida(dados, "asteroides", 1)
    assert dados["fases_desbloqueadas"] == {
        "asteroides": 2,
        "frota_inimiga": 2,
    }

    registrar_fase_concluida(dados, "frota_inimiga", 2)
    assert dados["fases_desbloqueadas"] == {
        "asteroides": 3,
        "frota_inimiga": 3,
    }
    assert dados["fases_concluidas_por_modo"] == {
        "asteroides": 1,
        "frota_inimiga": 2,
    }


def test_recompensa_da_fase_cinco_precisa_ser_resgatada_uma_vez():
    dados = normalizar_dados_jogador({})
    dados["fases_concluidas_por_modo"]["asteroides"] = 4

    registrar_fase_concluida(dados, "asteroides", 5)

    assert dados["recompensas_pendentes"] == ["hyperion"]
    assert resgatar_recompensa(dados, "hyperion")
    assert "Hyperion.png" in dados["naves_desbloqueadas"]
    assert dados["recompensas_resgatadas"] == ["hyperion"]
    dados["recompensas_pendentes"].append("hyperion")
    assert not resgatar_recompensa(dados, "hyperion")


def test_recompensa_da_fase_dez_libera_a_skin_titan():
    dados = normalizar_dados_jogador({})
    dados["fases_concluidas_por_modo"]["frota_inimiga"] = 9

    registrar_fase_concluida(dados, "frota_inimiga", 10)

    assert dados["recompensas_pendentes"] == ["hyperion", "titan_hellion_core"]
    assert resgatar_recompensa(dados, "titan_hellion_core")
    assert "titan_hellion_core" in dados["skins_desbloqueadas"]


def test_save_legado_migra_progresso_e_recompensa_da_fase_cinco():
    dados = normalizar_dados_jogador(
        {"fases_desbloqueadas": {"asteroides": 6, "frota_inimiga": 1}}
    )

    assert dados["fases_desbloqueadas"] == {
        "asteroides": 6,
        "frota_inimiga": 6,
    }
    assert dados["recompensas_pendentes"] == ["hyperion"]
