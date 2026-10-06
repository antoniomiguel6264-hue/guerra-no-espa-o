def calcular_cura_inimigo_derrotado(fase_atual=1):
    return 15 + max(0, fase_atual - 1) * 3
