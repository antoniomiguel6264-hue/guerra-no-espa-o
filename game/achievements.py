CONQUISTAS = (
    {
        "id": "sobrevivente",
        "nome": "Sobrevivente",
        "descricao": "Sobreviva por 5 minutos no modo infinito.",
    },
    {
        "id": "intocavel",
        "nome": "Intocável",
        "descricao": "Conclua uma fase sem receber dano.",
    },
)

CONQUISTAS_POR_ID = {conquista["id"]: conquista for conquista in CONQUISTAS}
TEMPO_SOBREVIVENTE_MS = 5 * 60 * 1000


def acumular_tempo_sobrevivencia(tempo_atual_ms, delta_ms, modo_infinito, pausado):
    if not modo_infinito or pausado:
        return tempo_atual_ms
    return tempo_atual_ms + max(0, int(delta_ms))


def normalizar_conquistas(conquistas):
    if not isinstance(conquistas, (list, tuple, set)):
        return []
    return list(dict.fromkeys(
        conquista_id
        for conquista_id in conquistas
        if isinstance(conquista_id, str) and conquista_id in CONQUISTAS_POR_ID
    ))


def desbloquear_conquista(dados_jogador, conquista_id):
    if conquista_id not in CONQUISTAS_POR_ID:
        raise ValueError(f"Conquista desconhecida: {conquista_id}")

    desbloqueadas = normalizar_conquistas(dados_jogador.get("conquistas_desbloqueadas"))
    if conquista_id in desbloqueadas:
        dados_jogador["conquistas_desbloqueadas"] = desbloqueadas
        return False

    desbloqueadas.append(conquista_id)
    dados_jogador["conquistas_desbloqueadas"] = desbloqueadas
    return True


def listar_conquistas(dados_jogador):
    desbloqueadas = set(normalizar_conquistas(dados_jogador.get("conquistas_desbloqueadas")))
    return [
        {**conquista, "desbloqueada": conquista["id"] in desbloqueadas}
        for conquista in CONQUISTAS
    ]
