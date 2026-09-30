import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import random
import math
import config
from config import BRANCO, AMARELO, AZUL_NEON, VERMELHO

class Nave(pygame.sprite.Sprite):
    def __init__(self, x, y, imagem_path, niveis_melhorias=None):
        super().__init__()
        self.modelo = os.path.splitext(os.path.basename(imagem_path))[0].lower()
        try:
            self.image_original = pygame.image.load(imagem_path).convert_alpha()
            self.image_original = pygame.transform.scale(self.image_original, (68, 68))
        except Exception as e:
            print(f"Erro ao carregar {imagem_path}: {e}. Usando placeholder.")
            self.image_original = pygame.Surface((68, 68))
            self.image_original.fill(AZUL_NEON)
            
        self.image = self.image_original
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        if niveis_melhorias is None:
            niveis_melhorias = {"velocidade": 1, "cadencia": 1, "especial": 1}
            
        self.niveis = niveis_melhorias
        
        self.x = float(x)
        self.y = float(y)
        self.angulo = 90
        self.velocidade_giro = 2.2 + (self.niveis["velocidade"] - 1) * 0.25
        self.aceleracao = 0.2 + (self.niveis["velocidade"] - 1) * 0.05
        self.velocidade_maxima = 6 + (self.niveis["velocidade"] - 1) * 0.8
        self.vx = 0
        self.vy = 0
        
        self.vida_maxima = 100
        self.vida = self.vida_maxima
        self.invulneravel = False
        self.tempo_invulneravel = 0
        self.aegis_ativo = False
        self.pontos_para_cura = 0
        
        self.energia_especial = 0
        self.energia_maxima = 100
        self.bonus_energia = 20 + (self.niveis["especial"] - 1) * 5
        self.duracao_especial = 36 + max(0, self.niveis["especial"] - 1) * 12

    def update(self, teclas=None):
        if teclas is None:
            teclas = pygame.key.get_pressed()

        if teclas[pygame.K_q]:
            self.angulo += self.velocidade_giro
        if teclas[pygame.K_e]:
            self.angulo -= self.velocidade_giro

        is_moving = False
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            rad = math.radians(self.angulo)
            self.vx += math.cos(rad) * self.aceleracao
            self.vy -= math.sin(rad) * self.aceleracao
            is_moving = True

        velocidade_atual = math.hypot(self.vx, self.vy)
        if velocidade_atual > self.velocidade_maxima:
            self.vx = (self.vx / velocidade_atual) * self.velocidade_maxima
            self.vy = (self.vy / velocidade_atual) * self.velocidade_maxima

        if not is_moving:
            self.vx *= 0.95
            self.vy *= 0.95

        self.x += self.vx
        self.y += self.vy

        if self.x < 25:
            self.x = 25
            self.vx = 0
        elif self.x > config.LARGURA - 25:
            self.x = config.LARGURA - 25
            self.vx = 0
        if self.y < 25:
            self.y = 25
            self.vy = 0
        elif self.y > config.ALTURA - 25:
            self.y = config.ALTURA - 25
            self.vy = 0

        self.rect.center = (int(self.x), int(self.y))
        self.image = pygame.transform.rotate(self.image_original, self.angulo - 90)
        self.rect = self.image.get_rect(center=self.rect.center)

        if self.invulneravel:
            if pygame.time.get_ticks() - self.tempo_invulneravel > 1500:
                self.invulneravel = False

    def perder_vida(self, dano=20):
        if not self.invulneravel:
            self.vida = max(0, self.vida - dano)
            self.invulneravel = True
            self.tempo_invulneravel = pygame.time.get_ticks()
            return self.vida <= 0
        return False

    def recuperar_vida(self, quantidade=35):
        if quantidade <= 0:
            return self.vida

        if self.vida < self.vida_maxima * 0.5:
            quantidade = int(quantidade * 1.5)

        self.vida = min(self.vida_maxima, self.vida + quantidade)
        return self.vida

    def aplicar_pontos_para_cura(self, pontos_ganhos=0):
        if pontos_ganhos <= 0:
            return self.vida

        self.pontos_para_cura += pontos_ganhos
        recuperacoes = self.pontos_para_cura // 200
        if recuperacoes > 0:
            self.pontos_para_cura -= recuperacoes * 200
            cura = recuperacoes * max(1, int(self.vida_maxima * 0.05))
            self.recuperar_vida(cura)
        return self.vida

    def adicionar_energia(self, quantidade):
        if quantidade is None:
            quantidade = 0
        quantidade = max(0, int(quantidade))
        self.energia_especial += quantidade
        if self.energia_especial > self.energia_maxima:
            self.energia_especial = self.energia_maxima

    def disparar_especial(self):
        if self.energia_especial >= self.energia_maxima:
            self.energia_especial = 0
            if self.modelo == "aegis":
                self.aegis_ativo = True
            return True 
        return False

    def criar_tiro_especial(self):
        x = self.rect.centerx
        y = self.rect.centery

        if self.modelo == "vanguard":
            return [
                TiroEspecial(x, y, self.angulo - 12, tipo="vanguard", cor=(120, 220, 255)),
                TiroEspecial(x, y, self.angulo, tipo="vanguard", cor=(160, 245, 255)),
                TiroEspecial(x, y, self.angulo + 12, tipo="vanguard", cor=(120, 220, 255)),
            ]
        if self.modelo == "scout":
            return [TiroEspecialLaser(x, y, self.angulo)]
        if self.modelo == "titan":
            duracao = 36 + max(0, self.niveis["especial"] - 1) * 12
            return [TiroEspecialTitan(x, y, duracao=duracao, nivel=self.niveis["especial"])]
        if self.modelo == "phantom":
            tiros = []
            for i in range(7):
                angulo = self.angulo + random.randint(-28, 28) + (i - 3) * 10
                tiros.append(TiroEspecial(x, y, angulo, tipo="phantom", cor=(255, 120, 255), velocidade=14 + i))
            return tiros
        if self.modelo == "aegis":
            return [TiroEspecialAegis(x, y, self.angulo, nave=self)]

        return [TiroEspecial(x, y, self.angulo)]


class Tiro(pygame.sprite.Sprite):
    def __init__(self, x, y, angulo):
        super().__init__()
        self.image_original = pygame.Surface((6, 16), pygame.SRCALPHA)
        self.image_original.fill(AMARELO)
        
        self.angulo = angulo
        self.image = pygame.transform.rotate(self.image_original, self.angulo - 90)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        rad = math.radians(self.angulo)
        self.velocidade = 12
        self.vx = math.cos(rad) * self.velocidade
        self.vy = -math.sin(rad) * self.velocidade

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        if self.rect.right < 0 or self.rect.left > config.LARGURA or self.rect.bottom < 0 or self.rect.top > config.ALTURA:
            self.kill()


class TiroEspecial(pygame.sprite.Sprite):
    def __init__(self, x, y, angulo, tipo="normal", cor=AZUL_NEON, velocidade=14):
        super().__init__()
        self.tipo = tipo
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

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.vida -= 1
        if self.vida <= 0 or self.rect.right < 0 or self.rect.left > config.LARGURA or self.rect.bottom < 0 or self.rect.top > config.ALTURA:
            self.kill()


class TiroEspecialTitan(TiroEspecial):
    def __init__(self, x, y, duracao=36, nivel=1):
        super().__init__(x, y, 0, tipo="titan", cor=(255, 180, 70), velocidade=0)
        self.nivel = max(1, nivel)
        self.raio = int(55 * math.sqrt(6)) + max(0, self.nivel - 1) * 10
        self.dano = 2 + max(0, self.nivel - 1) * 2
        self.dano_central = 5 + max(0, self.nivel - 1) * 3
        self.pulso = 0.0
        self.tempo_total = float(max(1, duracao))
        self.vida = duracao
        self.efeito_fim = 0.0
        self.atualizar_visual()

    def atualizar_visual(self):
        tamanho = self.raio * 2 + 40
        imagem = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
        centro = (tamanho // 2, tamanho // 2)
        brilho = 0.5 + 0.5 * math.sin(self.pulso)
        fim = min(1.0, self.efeito_fim)

        for indice, r in enumerate(range(self.raio + 18, max(16, self.raio - 30), -12)):
            alpha = int(40 + (1 - indice / 8) * 120 + brilho * 90 + fim * 70)
            raio = r + int(10 * math.sin(self.pulso * 2 + indice)) + int(fim * 18)
            pygame.draw.circle(imagem, (255, 140 + indice * 8, 40, alpha), centro, raio, 2)

        ring_externo = int(self.raio + 18 + 10 * math.sin(self.pulso * 3) + fim * 28)
        pygame.draw.circle(imagem, (255, 175, 70, 130 + int(60 * brilho)), centro, ring_externo)
        pygame.draw.circle(imagem, (255, 220, 120, 200), centro, int(self.raio * (0.72 + brilho * 0.18) + fim * 12))
        pygame.draw.circle(imagem, (255, 255, 200, 200), centro, max(14, self.raio // 2 + int(6 * math.sin(self.pulso)) + int(fim * 8)))
        pygame.draw.circle(imagem, (70, 180, 255, 180), centro, max(18, self.raio // 2 + 12), 7)
        pygame.draw.circle(imagem, (255, 120, 30, 200), centro, max(5, self.raio // 5), 3)

        for angulo in range(0, 360, 45):
            rad = math.radians(angulo + self.pulso * 40)
            x = int(centro[0] + math.cos(rad) * (self.raio + 20 + fim * 12))
            y = int(centro[1] + math.sin(rad) * (self.raio + 20 + fim * 12))
            pygame.draw.circle(imagem, (255, 255, 200, 135), (x, y), 5 + int(2 * math.sin(self.pulso + angulo)))

        if fim > 0:
            onda = int(self.raio * (1.1 + fim * 1.5))
            pygame.draw.circle(imagem, (255, 255, 255, int(80 * (1.0 - fim))), centro, onda, 4)

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
                self.vida = min(self.max_vida, self.vida + 0.5)
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
            self.kill()


class Explosao(pygame.sprite.Sprite):
    def __init__(self, x, y, cor=(255, 180, 70), raio_inicial=18):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.cor = cor
        self.vida = 12
        self.max_vida = 12
        self.raio_inicial = raio_inicial
        self.atualizar_visual()

    def atualizar_visual(self):
        progresso = 1 - (self.vida / self.max_vida)
        raio = int(self.raio_inicial + progresso * 40)
        tamanho = raio * 2 + 18
        imagem = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
        alpha = max(20, int(255 * (self.vida / self.max_vida)))
        pygame.draw.circle(imagem, (*self.cor, alpha), (tamanho // 2, tamanho // 2), raio)
        pygame.draw.circle(imagem, (255, 255, 255, alpha), (tamanho // 2, tamanho // 2), max(3, raio // 3))
        self.image = imagem
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self):
        self.vida -= 1
        if self.vida <= 0:
            self.kill()
            return
        self.atualizar_visual()


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
                imagem = pygame.image.load(nome_arquivo).convert_alpha()
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
            self.image_original = pygame.image.load("asteroide.png").convert_alpha()
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