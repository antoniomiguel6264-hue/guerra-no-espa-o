
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

# Inicialização do Pygame e Fontes
pygame.init()
pygame.font.init()

# Dimensões da Tela
LARGURA = 800
ALTURA = 600

# Cores Padrão (RGB)
PRETO = (10, 10, 20)
BRANCO = (255, 255, 255)
AZUL_NEON = (0, 229, 255)
ROXO_NEON = (180, 0, 255)
VERMELHO = (255, 50, 50)
AMARELO = (255, 230, 0)
CINZA = (100, 100, 100)

# Configurações de Jogo
FPS = 60