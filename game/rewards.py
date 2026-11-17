MAX_FASES_CAMPANHA = 10

RECOMPENSAS_POR_MARCO = {
    5: {
        "id": "hyperion",
        "tipo": "nave",
        "nome": "Hyperion",
        "arquivo": "Hyperion.png",
    },
    10: {
        "id": "titan_hellion_core",
        "tipo": "skin",
        "nome": "Titan Hellion Core",
        "arquivo": "titan Hellion Core.png",
    },
}
RECOMPENSAS_POR_ID = {
    recompensa["id"]: recompensa
    for recompensa in RECOMPENSAS_POR_MARCO.values()
}


def registrar_fase_concluida(dados_jogador, modo_jogo, fase):
    fases_concluidas = dados_jogador["fases_concluidas_por_modo"]
    fases_concluidas[modo_jogo] = max(fases_concluidas[modo_jogo], fase)
    total_concluido = max(fases_concluidas.values())
    fase_seguinte = min(MAX_FASES_CAMPANHA, total_concluido + 1)
    for modo in dados_jogador["fases_desbloqueadas"]:
        dados_jogador["fases_desbloqueadas"][modo] = max(
            dados_jogador["fases_desbloqueadas"][modo],
            fase_seguinte,
        )
    pendentes = dados_jogador["recompensas_pendentes"]
    resgatadas = dados_jogador["recompensas_resgatadas"]
    for marco, recompensa in RECOMPENSAS_POR_MARCO.items():
        recompensa_id = recompensa["id"]
        if (
            total_concluido >= marco
            and recompensa_id not in pendentes
            and recompensa_id not in resgatadas
        ):
            pendentes.append(recompensa_id)


def resgatar_recompensa(dados_jogador, recompensa_id):
    if (
        recompensa_id not in dados_jogador["recompensas_pendentes"]
        or recompensa_id in dados_jogador["recompensas_resgatadas"]
    ):
        return False

    recompensa = RECOMPENSAS_POR_ID.get(recompensa_id)
    if recompensa is None:
        return False

    if recompensa["tipo"] == "nave":
        desbloqueados = dados_jogador["naves_desbloqueadas"]
        item_desbloqueado = recompensa["arquivo"]
    else:
        desbloqueados = dados_jogador["skins_desbloqueadas"]
        item_desbloqueado = recompensa["id"]
    if item_desbloqueado not in desbloqueados:
        desbloqueados.append(item_desbloqueado)

    dados_jogador["recompensas_pendentes"].remove(recompensa_id)
    dados_jogador["recompensas_resgatadas"].append(recompensa_id)
    return True
