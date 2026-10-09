import pygame

from game.ui import desenhar_fundo, texto_com_borda


def _desenhar_fundo(tela, fundo):
    desenhar_fundo(tela, fundo)


def _centralizar(tela, superficie, y):
    tela.blit(superficie, (tela.get_width() // 2 - superficie.get_width() // 2, y))


def animar_transicao(tela, relogio, entrada=True, duracao_ms=180):
    quadros = max(1, round(duracao_ms * 60 / 1000))
    quadro_original = tela.copy()
    overlay = pygame.Surface(tela.get_size(), pygame.SRCALPHA)

    for quadro in range(quadros + 1):
        progresso = quadro / quadros
        alfa = round(255 * (1 - progresso if entrada else progresso))
        tela.blit(quadro_original, (0, 0))
        overlay.fill((0, 0, 0, alfa))
        tela.blit(overlay, (0, 0))
        pygame.display.flip()
        relogio.tick(60)
