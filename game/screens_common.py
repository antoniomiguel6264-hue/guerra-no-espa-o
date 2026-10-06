import pygame

from game.ui import desenhar_fundo, texto_com_borda


def _desenhar_fundo(tela, fundo):
    desenhar_fundo(tela, fundo)


def _centralizar(tela, superficie, y):
    tela.blit(superficie, (tela.get_width() // 2 - superficie.get_width() // 2, y))
