import pygame

from config import AMARELO, AZUL_NEON, BRANCO, CINZA, PRETO, VERMELHO

_fundos_redimensionados = {}


def desenhar_fundo(tela_surface, fundo):
    if fundo is None:
        tela_surface.fill(PRETO)
        return

    tamanho = tela_surface.get_size()
    if fundo.get_size() != tamanho:
        chave = (id(fundo), tamanho)
        entrada_cache = _fundos_redimensionados.get(chave)
        if entrada_cache is None or entrada_cache[0] is not fundo:
            fundo_redimensionado = pygame.transform.scale(fundo, tamanho)
            _fundos_redimensionados[chave] = (fundo, fundo_redimensionado)
        else:
            fundo_redimensionado = entrada_cache[1]
        fundo = fundo_redimensionado
    tela_surface.blit(fundo, (0, 0))


def texto_com_borda(fonte, texto, cor, borda_cor=PRETO, tamanho_borda=1, fundo=None):
    if texto is None or texto == "":
        return fonte.render("", True, cor, fundo)

    superficie = fonte.render(texto, True, cor, fundo)
    if tamanho_borda <= 0:
        return superficie

    contorno = pygame.Surface(
        (superficie.get_width() + tamanho_borda * 2, superficie.get_height() + tamanho_borda * 2),
        pygame.SRCALPHA,
    )
    texto_borda = fonte.render(texto, True, borda_cor, fundo)

    for dx in range(-tamanho_borda, tamanho_borda + 1):
        for dy in range(-tamanho_borda, tamanho_borda + 1):
            if dx == 0 and dy == 0:
                continue
            contorno.blit(texto_borda, (dx + tamanho_borda, dy + tamanho_borda))

    contorno.blit(superficie, (tamanho_borda, tamanho_borda))
    return contorno


def desenhar_botao_pausa(tela_surface, rect, texto, fonte, ativo=False):
    cor_fundo = (30, 30, 40) if not ativo else (70, 110, 170)
    cor_borda = AZUL_NEON if not ativo else AMARELO
    pygame.draw.rect(tela_surface, cor_fundo, rect, border_radius=8)
    pygame.draw.rect(tela_surface, cor_borda, rect, 2, border_radius=8)
    texto_renderizado = texto_com_borda(fonte, texto, BRANCO if not ativo else AMARELO)
    tela_surface.blit(
        texto_renderizado,
        (
            rect.centerx - texto_renderizado.get_width() // 2,
            rect.centery - texto_renderizado.get_height() // 2,
        ),
    )


def desenhar_hud_jogo(
    tela_surface,
    fonte,
    pontos,
    meta_pontos,
    fase_atual,
    moedas,
    vida,
    vida_maxima,
    energia_especial,
    inimigos_restantes,
    modo_jogo,
    modelo_nave,
    botao_pausa,
    pausado=False,
    titan_restante=None,
    chefe_vida=None,
    chefe_vida_maxima=None,
):
    modo_infinito = modo_jogo == "infinito"
    modo_frota = modo_jogo == "frota_inimiga"

    texto_pontos = f"Pontos: {pontos}" if modo_infinito else f"Pontos: {pontos} / {meta_pontos}"
    texto_fase = "INFINITO" if modo_infinito else f"Fase: {fase_atual}"
    tela_surface.blit(texto_com_borda(fonte, texto_pontos, BRANCO), (20, 20))
    tela_surface.blit(texto_com_borda(fonte, texto_fase, AZUL_NEON), (20, 45))
    tela_surface.blit(texto_com_borda(fonte, f"Moedas: {moedas} 🪙", AMARELO), (20, 70))
    tela_surface.blit(texto_com_borda(fonte, "Vida", BRANCO), (20, 95))

    proporcao_vida = vida / vida_maxima if vida_maxima > 0 else 0
    largura_vida = int(180 * proporcao_vida)
    pygame.draw.rect(tela_surface, (50, 50, 50), (20, 118, 180, 14))
    pygame.draw.rect(tela_surface, (60, 220, 120), (20, 118, largura_vida, 14))
    pygame.draw.rect(tela_surface, BRANCO, (20, 118, 180, 14), 1)

    if chefe_vida is not None and chefe_vida_maxima:
        largura_barra_chefe = 360
        barra_chefe = pygame.Rect(
            tela_surface.get_width() // 2 - largura_barra_chefe // 2,
            24,
            largura_barra_chefe,
            20,
        )
        pygame.draw.rect(tela_surface, (45, 20, 30), barra_chefe, border_radius=6)
        largura_vida_chefe = round(
            largura_barra_chefe
            * max(0, min(1, chefe_vida / chefe_vida_maxima))
        )
        if largura_vida_chefe:
            pygame.draw.rect(
                tela_surface,
                (235, 55, 95),
                (barra_chefe.x, barra_chefe.y, largura_vida_chefe, barra_chefe.height),
                border_radius=6,
            )
        pygame.draw.rect(tela_surface, BRANCO, barra_chefe, 2, border_radius=6)
        texto_chefe = texto_com_borda(fonte, "CHEFE", VERMELHO)
        tela_surface.blit(
            texto_chefe,
            (
                barra_chefe.centerx - texto_chefe.get_width() // 2,
                barra_chefe.bottom + 3,
            ),
        )

    texto_botao = "Continuar" if pausado else "Pausar"
    desenhar_botao_pausa(tela_surface, botao_pausa, texto_botao, fonte, ativo=pausado)

    if pausado:
        return

    texto_frota = "Frota: 0" if modo_infinito else f"Frota: {inimigos_restantes}"
    texto_modo = (
        "MODO: INFINITO"
        if modo_infinito
        else ("MODO: FROTA INIMIGA" if modo_frota else "MODO: ASTEROIDES")
    )
    cor_modo = AMARELO if modo_infinito or modo_frota else AZUL_NEON
    tela_surface.blit(texto_com_borda(fonte, texto_frota, VERMELHO), (20, 145))
    tela_surface.blit(texto_com_borda(fonte, texto_modo, cor_modo), (20, 170))

    pygame.draw.rect(tela_surface, (50, 50, 50), (20, 175, 150, 15))
    largura_barra = int(1.5 * energia_especial)
    cor_barra = AZUL_NEON if energia_especial >= 100 else (0, 150, 200)
    pygame.draw.rect(tela_surface, cor_barra, (20, 175, largura_barra, 15))
    pygame.draw.rect(tela_surface, BRANCO, (20, 175, 150, 15), 1)

    texto_especial = "ESPECIAL [K]"
    cor_especial = BRANCO if energia_especial >= 100 else CINZA
    tela_surface.blit(texto_com_borda(fonte, texto_especial, cor_especial), (180, 173))

    if titan_restante is not None:
        texto_duracao = f"Titan: {titan_restante:.1f}s"
        tela_surface.blit(texto_com_borda(fonte, texto_duracao, AMARELO), (20, 205))
    elif modelo_nave == "titan":
        tela_surface.blit(texto_com_borda(fonte, "Titan: pronto", AZUL_NEON), (20, 205))


def desenhar_tela_jogo(
    tela_surface,
    fundo,
    sprites,
    fontes,
    estado_hud,
    pausado=False,
):
    fonte_titulo, _, fonte_hud = fontes
    desenhar_fundo(tela_surface, fundo)

    sprites.draw(tela_surface)
    desenhar_hud_jogo(
        tela_surface,
        fonte_hud,
        estado_hud["pontos"],
        estado_hud["meta_pontos"],
        estado_hud["fase_atual"],
        estado_hud["moedas"],
        estado_hud["vida"],
        estado_hud["vida_maxima"],
        estado_hud["energia_especial"],
        estado_hud["inimigos_restantes"],
        estado_hud["modo_jogo"],
        estado_hud["modelo_nave"],
        estado_hud["botao_pausa"],
        pausado=pausado,
        titan_restante=estado_hud.get("titan_restante"),
        chefe_vida=estado_hud.get("chefe_vida"),
        chefe_vida_maxima=estado_hud.get("chefe_vida_maxima"),
    )

    if pausado:
        overlay = pygame.Surface(tela_surface.get_size(), pygame.SRCALPHA)
        overlay.fill((10, 12, 20, 170))
        tela_surface.blit(overlay, (0, 0))

        texto_pausa = texto_com_borda(fonte_titulo, "PAUSADO", AMARELO)
        texto_instrucao = texto_com_borda(
            fonte_hud,
            "Pressione [P] ou clique no botão para continuar",
            BRANCO,
        )
        largura, altura = tela_surface.get_size()
        botao_abandonar = estado_hud["botao_abandonar"]
        pygame.draw.rect(
            tela_surface,
            (55, 25, 30),
            botao_abandonar,
            border_radius=8,
        )
        pygame.draw.rect(
            tela_surface,
            VERMELHO,
            botao_abandonar,
            2,
            border_radius=8,
        )
        texto_abandonar = texto_com_borda(fonte_hud, "Abandonar partida", BRANCO)
        tela_surface.blit(
            texto_pausa,
            (largura // 2 - texto_pausa.get_width() // 2, altura // 2 - 40),
        )
        tela_surface.blit(
            texto_instrucao,
            (
                largura // 2 - texto_instrucao.get_width() // 2,
                altura // 2 + 30,
            ),
        )
        tela_surface.blit(
            texto_abandonar,
            (
                botao_abandonar.centerx - texto_abandonar.get_width() // 2,
                botao_abandonar.centery - texto_abandonar.get_height() // 2,
            ),
        )

    notificacao = estado_hud.get("notificacao_conquista")
    if notificacao:
        largura, _ = tela_surface.get_size()
        painel = pygame.Rect(largura // 2 - 190, 235, 380, 64)
        pygame.draw.rect(tela_surface, (18, 22, 30), painel, border_radius=12)
        pygame.draw.rect(tela_surface, AMARELO, painel, 2, border_radius=12)
        texto_conquista = texto_com_borda(fonte_hud, f"Conquista: {notificacao}", AMARELO)
        tela_surface.blit(
            texto_conquista,
            (
                painel.centerx - texto_conquista.get_width() // 2,
                painel.centery - texto_conquista.get_height() // 2,
            ),
        )

    pygame.display.flip()
