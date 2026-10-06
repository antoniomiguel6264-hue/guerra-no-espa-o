import pygame
import sys

from config import AMARELO, AZUL_NEON, BRANCO
from game.screens_common import _centralizar, _desenhar_fundo, texto_com_borda



def tela_conquistas(
    dados_jogador,
    tela,
    relogio,
    fontes,
    fundo,
    atualizar_tamanho_tela,
    listar_conquistas,
):
    fonte_titulo, fonte_texto, fonte_hud = fontes
    rodando = True
    while rodando:
        relogio.tick(60)
        _desenhar_fundo(tela, fundo)
        _centralizar(tela, texto_com_borda(fonte_titulo, "CONQUISTAS", AMARELO), 65)

        conquistas = listar_conquistas(dados_jogador)
        for indice, conquista in enumerate(conquistas):
            y = 170 + indice * 125
            cor = AZUL_NEON if conquista["desbloqueada"] else BRANCO
            status = "DESBLOQUEADA" if conquista["desbloqueada"] else "BLOQUEADA"
            painel = pygame.Rect(tela.get_width() // 2 - 300, y, 600, 90)
            pygame.draw.rect(tela, (18, 22, 30), painel, border_radius=12)
            pygame.draw.rect(tela, cor, painel, 2, border_radius=12)
            tela.blit(
                texto_com_borda(fonte_hud, f"{conquista['nome']} - {status}", cor),
                (painel.x + 20, painel.y + 15),
            )
            tela.blit(
                texto_com_borda(fonte_texto, conquista["descricao"], BRANCO),
                (painel.x + 20, painel.y + 52),
            )

        _centralizar(
            tela,
            texto_com_borda(fonte_hud, "Pressione [ESC] ou [ENTER] para voltar", AZUL_NEON),
            tela.get_height() - 65,
        )
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.VIDEORESIZE or (
                evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11
            ):
                atualizar_tamanho_tela(evento)
            if evento.type == pygame.KEYDOWN and evento.key in (
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
                pygame.K_ESCAPE,
            ):
                rodando = False
