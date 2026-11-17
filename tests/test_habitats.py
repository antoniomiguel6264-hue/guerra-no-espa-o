import pygame

from game.habitats import (
    HABITATS_POR_NAVE,
    aplicar_habitat,
    fundos_para_habitat,
    obter_habitat,
)


def test_cada_nave_tem_habitat_com_nome_e_cor_proprios():
    assert len({habitat["nome"] for habitat in HABITATS_POR_NAVE.values()}) == len(
        HABITATS_POR_NAVE
    )
    assert len({habitat["cor"] for habitat in HABITATS_POR_NAVE.values()}) == len(
        HABITATS_POR_NAVE
    )


def test_aplicar_habitat_tonaliza_o_fundo_sem_alterar_a_origem():
    fundo = pygame.Surface((4, 4))
    fundo.fill((80, 80, 80))

    fundo_titan = aplicar_habitat(fundo, "Titan.png")
    fundo_aegis = aplicar_habitat(fundo, "Aegis.png")

    assert fundo.get_at((0, 0))[:3] == (80, 80, 80)
    assert fundo_titan.get_at((0, 0)) != fundo_aegis.get_at((0, 0))
    assert aplicar_habitat(None, "Titan.png") is None
    assert obter_habitat("nave_desconhecida.png") is HABITATS_POR_NAVE["Vanguard.png"]


def test_cada_fase_mantem_seu_fundo_com_a_tonalidade_do_habitat():
    fundos_base = tuple(pygame.Surface((2, 2)) for _ in range(4))
    for indice, fundo in enumerate(fundos_base):
        fundo.fill((indice * 30, 80, 100))

    fundos = fundos_para_habitat("Titan.png", fundos_base)

    assert len({fundo.get_at((0, 0))[:3] for fundo in fundos}) == 4
    assert all(
        fundo.get_at((0, 0))[:3] != fundo_base.get_at((0, 0))[:3]
        for fundo, fundo_base in zip(fundos, fundos_base)
    )