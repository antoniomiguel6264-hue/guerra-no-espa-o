def calcular_cura_inimigo_derrotado(fase_atual=1):
    return 15 + max(0, fase_atual - 1) * 3


def calcular_dano_recebido_frota(nivel_defesa=1):
    nivel_defesa = max(1, int(nivel_defesa))
    return max(2, 12 - nivel_defesa * 2)


def calcular_vida_maxima(nivel_vida=1):
    return 100 + max(0, int(nivel_vida) - 1) * 20


def calcular_taxa_recarga_especial(nivel_recarga=1):
    return min(100, 50 + max(0, int(nivel_recarga) - 1) * 10)


def calcular_bonus_moedas_inimigo(nivel_recompensa=1):
    return max(0, int(nivel_recompensa) - 1)
