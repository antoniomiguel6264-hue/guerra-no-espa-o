import pytest

from entidades import Nave
from game.balance import calcular_cura_inimigo_derrotado


@pytest.mark.parametrize(
    ("fase", "cura_base"),
    [(1, 15), (2, 18), (3, 21), (4, 24), (5, 27)],
)
def test_cura_por_inimigo_derrotado_aumenta_gradualmente(fase, cura_base):
    assert calcular_cura_inimigo_derrotado(fase) == cura_base


def test_cura_reduzida_mantem_bonus_de_recuperacao_em_vida_baixa():
    jogador = Nave(100, 100, "Vanguard.png")
    jogador.vida = 30

    jogador.recuperar_vida(calcular_cura_inimigo_derrotado(1))

    assert jogador.vida == 52
