import math

import config
import pygame

from config import AMARELO, AZUL_NEON


class Tiro(pygame.sprite.Sprite):
    def __init__(
        self,
        x,
        y,
        angulo,
        velocidade=16,
        dano=2,
        largura=6,
        comprimento=16,
        cor=AMARELO,
    ):
        super().__init__()
        self.image_original = pygame.Surface((largura, comprimento), pygame.SRCALPHA)
        self.image_original.fill(cor)
        
        self.angulo = angulo
        self.image = pygame.transform.rotate(self.image_original, self.angulo - 90)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = float(x)
        self.y = float(y)
        
        rad = math.radians(self.angulo)
        self.velocidade = velocidade
        self.dano_inimigo = dano
        self.vx = math.cos(rad) * self.velocidade
        self.vy = -math.sin(rad) * self.velocidade

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (round(self.x), round(self.y))
        
        if self.rect.right < 0 or self.rect.left > config.LARGURA or self.rect.bottom < 0 or self.rect.top > config.ALTURA:
            self.kill()


class TiroEspecial(pygame.sprite.Sprite):
    def __init__(self, x, y, angulo, tipo="normal", cor=AZUL_NEON, velocidade=14):
        super().__init__()
        self.tipo = tipo
        self.cor = cor
        self.image_original = pygame.Surface((14, 28), pygame.SRCALPHA)
        pygame.draw.rect(self.image_original, cor, (5, 0, 4, 28))
        self.angulo = angulo
        self.image = pygame.transform.rotate(self.image_original, self.angulo - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        rad = math.radians(self.angulo)
        self.velocidade = velocidade
        self.vx = math.cos(rad) * self.velocidade
        self.vy = -math.sin(rad) * self.velocidade
        self.dano_inimigo = 1
        self.limite_alvos = 1
        self.alvos_atingidos = set()

    def registrar_impacto_inimigo(self, inimigo):
        if inimigo in self.alvos_atingidos:
            return False

        self.alvos_atingidos.add(inimigo)
        if self.limite_alvos is not None and len(self.alvos_atingidos) >= self.limite_alvos:
            self.kill()
        return True

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.right < 0 or self.rect.left > config.LARGURA or self.rect.bottom < 0 or self.rect.top > config.ALTURA:
            self.kill()


class TiroInimigo(pygame.sprite.Sprite):
    def __init__(self, x, y, angulo, dano=1, velocidade=6):
        super().__init__()
        self.dano = dano
        self.image_original = pygame.Surface((6, 16), pygame.SRCALPHA)
        pygame.draw.rect(self.image_original, (255, 120, 120), (2, 0, 2, 16))
        self.angulo = angulo
        self.image = pygame.transform.rotate(self.image_original, self.angulo - 90)
        self.rect = self.image.get_rect(center=(x, y))

        rad = math.radians(self.angulo)
        self.velocidade = velocidade
        self.vx = math.cos(rad) * self.velocidade
        self.vy = -math.sin(rad) * self.velocidade

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

        if self.rect.right < 0 or self.rect.left > config.LARGURA or self.rect.bottom < 0 or self.rect.top > config.ALTURA:
            self.kill()


class TiroEspecialLaser(TiroEspecial):
    def __init__(self, x, y, angulo):
        super().__init__(x, y, angulo, tipo="laser", cor=(110, 240, 255), velocidade=30)
        self.image_original = pygame.Surface((10, 900), pygame.SRCALPHA)
        pygame.draw.rect(self.image_original, (110, 240, 255), (2, 0, 6, 900))
        self.image = pygame.transform.rotate(self.image_original, self.angulo - 90)
        self.rect = self.image.get_rect(center=(x, y))
        self.vida = 18
        self.dano_inimigo = 5
        self.limite_alvos = None

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.vida -= 1
        if self.vida <= 0 or self.rect.right < 0 or self.rect.left > config.LARGURA or self.rect.bottom < 0 or self.rect.top > config.ALTURA:
            self.kill()


class TiroEspecialTitan(TiroEspecial):
    def __init__(self, x, y, duracao=36, nivel=1):
        super().__init__(x, y, 0, tipo="titan", cor=(255, 55, 55), velocidade=0)
        self.nivel = max(1, nivel)
        self.raio = math.ceil(min(80, 55 + (self.nivel - 1) * 10) * 1.5)
        self.dano = 2 + max(0, self.nivel - 1) * 2
        self.dano_central = 5 + max(0, self.nivel - 1) * 3
        self.pulso = 0.0
        self.tempo_total = float(max(1, duracao))
        self.vida = duracao
        self.efeito_fim = 0.0
        self.atualizar_visual()

    def atualizar_visual(self):
        tamanho = self.raio * 2 + 4
        imagem = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
        centro = (tamanho // 2, tamanho // 2)
        brilho = 0.5 + 0.5 * math.sin(self.pulso)
        fim = min(1.0, self.efeito_fim)

        for indice, r in enumerate(range(self.raio - 8, max(16, self.raio // 2), -12)):
            alpha = min(255, int(40 + (1 - indice / 8) * 120 + brilho * 90 + fim * 70))
            raio = min(
                self.raio,
                r + int(10 * math.sin(self.pulso * 2 + indice)) + int(fim * 8),
            )
            pygame.draw.circle(imagem, (255, 35 + indice * 8, 35, alpha), centro, raio, 2)

        ring_externo = min(
            self.raio,
            int(self.raio * (0.94 + brilho * 0.04)),
        )
        pygame.draw.circle(imagem, (255, 45, 45, 130 + int(60 * brilho)), centro, ring_externo)
        pygame.draw.circle(imagem, (255, 90, 90, 200), centro, int(self.raio * (0.72 + brilho * 0.18 + fim * 0.08)))
        pygame.draw.circle(imagem, (255, 170, 170, 200), centro, max(14, self.raio // 2 + int(6 * math.sin(self.pulso)) + int(fim * 8)))
        pygame.draw.circle(imagem, (190, 30, 45, 180), centro, max(18, self.raio // 2 + 12), 7)
        pygame.draw.circle(imagem, (255, 25, 25, 200), centro, max(5, self.raio // 5), 3)

        for angulo in range(0, 360, 45):
            rad = math.radians(angulo + self.pulso * 40)
            x = int(centro[0] + math.cos(rad) * (self.raio - 8))
            y = int(centro[1] + math.sin(rad) * (self.raio - 8))
            pygame.draw.circle(imagem, (255, 155, 155, 135), (x, y), 5 + int(2 * math.sin(self.pulso + angulo)))

        if fim > 0:
            onda = int(self.raio * (0.5 + fim * 0.45))
            pygame.draw.circle(imagem, (255, 110, 110, int(80 * (1.0 - fim))), centro, onda, 4)

        self.image = imagem
        self.rect = self.image.get_rect(center=(self.rect.centerx, self.rect.centery)) if hasattr(self, 'rect') else self.image.get_rect()

    def update(self):
        self.pulso += 0.35
        if self.vida <= 8:
            self.efeito_fim = min(1.0, self.efeito_fim + 0.14)
        self.atualizar_visual()
        self.vida -= 1
        if self.vida <= 0:
            self.kill()


class TiroEspecialAegis(TiroEspecial):
    def __init__(self, x, y, angulo, nave=None):
        super().__init__(x, y, angulo, tipo="aegis", cor=(100, 255, 180), velocidade=0)
        self.nave = nave
        self.largura = 520
        self.altura = 34
        self.max_vida = 180
        self.vida = self.max_vida
        self.pulso = 0
        self.ativo = True
        self.dano_inimigo = 3
        self.intervalo_dano = 20
        self.cooldowns_inimigos = {}
        self.atualizar_visual()

    def atualizar_visual(self):
        alpha = 210 if self.ativo else 80
        brilho = 180 + int(55 * math.sin(self.pulso))
        if not self.ativo:
            brilho = max(80, brilho // 2)

        self.image_original = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        pygame.draw.rect(self.image_original, (80, 255, 180, alpha), (0, 0, self.largura, self.altura), border_radius=16)
        pygame.draw.rect(self.image_original, (180, 255, 220, min(255, alpha + 30)), (18, 8, self.largura - 36, 18), border_radius=10)
        pygame.draw.rect(self.image_original, (255, 255, 255, brilho), (0, 0, self.largura, 6), border_radius=16)
        self.image = pygame.transform.rotate(self.image_original, self.angulo - 90)
        self.rect = self.image.get_rect(center=(self.rect.centerx, self.rect.centery)) if self.rect else self.image.get_rect(center=(self.nave.rect.centerx if self.nave else 0, self.nave.rect.centery if self.nave else 0))

    def update(self):
        if self.nave is not None:
            self.ativo = bool(self.nave.aegis_ativo)
            if self.ativo:
                self.pulso += 0.5
                self.vida -= 1
            else:
                self.pulso += 0.2
                self.vida -= 2

            rad = math.radians(self.nave.angulo)
            distancia = 155
            centro_x = int(self.nave.rect.centerx + math.cos(rad) * distancia)
            centro_y = int(self.nave.rect.centery - math.sin(rad) * distancia)
            self.angulo = self.nave.angulo
            self.atualizar_visual()
            self.rect = self.image.get_rect(center=(centro_x, centro_y))
        else:
            self.pulso += 0.3
            self.vida -= 1

        if self.vida <= 0:
            if self.nave is not None:
                self.nave.aegis_ativo = False
            self.kill()
