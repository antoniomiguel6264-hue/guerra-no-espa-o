import math
import random

import config
import pygame

from game.entities.common import resolver_caminho_arquivo
from game.entities.projectiles import TiroInimigo


class NaveInimiga(pygame.sprite.Sprite):
    def __init__(self, x, y, fase_atual=1):
        super().__init__()
        self.fase = fase_atual
        self.vida = 3 + fase_atual
        self.tamanho = 42 + fase_atual * 4
        self.cooldown_tiro = random.randint(70, 120)

        self.image_original = None
        for nome_arquivo in ("inimigo.png", "inimigo.jpg", "flanejante.png", "flanejante.jpg"):
            try:
                imagem = pygame.image.load(resolver_caminho_arquivo(nome_arquivo)).convert_alpha()
                self.image_original = pygame.transform.scale(imagem, (self.tamanho, self.tamanho))
                break
            except Exception:
                continue

        if self.image_original is None:
            self.image_original = pygame.Surface((self.tamanho, self.tamanho), pygame.SRCALPHA)
            pygame.draw.polygon(
                self.image_original,
                (255, 90, 90),
                [(self.tamanho // 2, 0), (self.tamanho, self.tamanho), (self.tamanho // 2, self.tamanho - 6), (0, self.tamanho)],
            )
            pygame.draw.circle(self.image_original, (255, 220, 120), (self.tamanho // 2, self.tamanho // 2), max(7, self.tamanho // 6))

        self.image = self.image_original
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidadey = 1 + fase_atual
        self.velocidadex = random.randint(-1, 1)
        self.tempo_bob = random.randint(0, 100)

    def update(self):
        self.tempo_bob += 1
        self.cooldown_tiro = max(0, self.cooldown_tiro - 1)
        self.rect.y += self.velocidadey
        self.rect.x += self.velocidadex + math.sin(self.tempo_bob / 18) * 0.8

        if self.rect.top > config.ALTURA + 20:
            self.kill()

        if self.rect.left < 0 or self.rect.right > config.LARGURA:
            self.velocidadex *= -1

    def criar_tiro(self, alvo):
        if alvo is None:
            return None

        dx = alvo.rect.centerx - self.rect.centerx
        dy = alvo.rect.centery - self.rect.centery
        if dx == 0 and dy == 0:
            return None

        angulo = math.degrees(math.atan2(-dy, dx))
        self.cooldown_tiro = random.randint(70, 120)
        return TiroInimigo(self.rect.centerx, self.rect.centery, angulo, dano=1, velocidade=6)


def gerar_frota_inimiga(fase_atual=1):
    quantidade = min(12, 3 + fase_atual * 2)
    frota = []
    espaco_horizontal = max(70, 120 - fase_atual * 5)

    for indice in range(quantidade):
        linha = indice // 4
        coluna = indice % 4
        x = 90 + coluna * espaco_horizontal + random.randint(-18, 18)
        y = -30 - linha * 70
        nave = NaveInimiga(x, y, fase_atual=fase_atual)
        frota.append(nave)

    return frota


def gerar_frota_infinita(pontos=0):
    # O modo infinito foi ajustado para sobreviver apenas com asteroides.
    # Nenhuma frota inimiga deve ser gerada nesse modo.
    return []


def calcular_meta_frota(fase_atual=1, frota=None):
    if frota is None:
        frota = gerar_frota_inimiga(fase_atual)
    return max(120, len(frota) * (25 + fase_atual * 5))


class Asteroide(pygame.sprite.Sprite):
    def __init__(self, fase_atual=1):
        super().__init__()
        self.tamanho = random.randint(40, 70)
        self.fase_atual = fase_atual

        try:
            self.image_original = pygame.image.load(resolver_caminho_arquivo("asteroide.png")).convert_alpha()
            self.image_original = pygame.transform.scale(self.image_original, (self.tamanho, self.tamanho))
        except Exception as e:
            print(f"Erro ao carregar imagem de asteroide: {e}. Usando placeholder.")
            self.image_original = pygame.Surface((self.tamanho, self.tamanho), pygame.SRCALPHA)
            pygame.draw.circle(self.image_original, (120, 120, 120), (self.tamanho // 2, self.tamanho // 2), self.tamanho // 2)

        self.image = self.image_original
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, config.LARGURA - self.tamanho)
        self.rect.y = random.randint(-150, -50)
        self.velocidadey = random.randint(1, 4)
        self.velocidadex = random.randint(-1, 1)

    def update(self):
        self.rect.y += self.velocidadey
        self.rect.x += self.velocidadex
        
        if self.rect.top > config.ALTURA + 10:
            self.rect.x = random.randint(0, config.LARGURA - self.tamanho)
            self.rect.y = random.randint(-100, -40)
            self.velocidadey = random.randint(1, 4)
