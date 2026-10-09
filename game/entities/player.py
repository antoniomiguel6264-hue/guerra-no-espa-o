import math
import os
import random

import config
import pygame
from config import AZUL_NEON
from game.balance import calcular_vida_maxima, calcular_taxa_recarga_especial
from game.entities.common import resolver_caminho_arquivo
from game.entities.projectiles import (
    Tiro,
    TiroEspecial,
    TiroEspecialAegis,
    TiroEspecialLaser,
    TiroEspecialTitan,
)


class Nave(pygame.sprite.Sprite):
    def __init__(self, x, y, imagem_path, niveis_melhorias=None):
        super().__init__()
        self.modelo = os.path.splitext(os.path.basename(imagem_path))[0].lower()
        caminho_imagem = resolver_caminho_arquivo(imagem_path)
        try:
            self.image_original = pygame.image.load(caminho_imagem).convert_alpha()
            self.image_original = pygame.transform.scale(self.image_original, (68, 68))
        except Exception as e:
            print(f"Erro ao carregar {imagem_path}: {e}. Usando placeholder.")
            self.image_original = pygame.Surface((68, 68))
            self.image_original.fill(AZUL_NEON)
            
        self.image = self.image_original
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        if niveis_melhorias is None:
            niveis_melhorias = {
                "velocidade": 1,
                "cadencia": 1,
                "especial": 1,
                "dano": 1,
                "defesa": 1,
                "vida": 1,
                "manobrabilidade": 1,
                "recarga": 1,
                "recompensa": 1,
            }
            
        self.niveis = niveis_melhorias
        
        self.x = float(x)
        self.y = float(y)
        self.angulo = 90
        nivel_manobrabilidade = max(1, int(self.niveis.get("manobrabilidade", 1)))
        self.velocidade_giro = (
            2.2
            + (self.niveis["velocidade"] - 1) * 0.25
            + (nivel_manobrabilidade - 1) * 0.3
        )
        self.aceleracao = (
            0.2
            + (self.niveis["velocidade"] - 1) * 0.05
            + (nivel_manobrabilidade - 1) * 0.025
        )
        self.velocidade_maxima = 6 + (self.niveis["velocidade"] - 1) * 0.8
        self.vx = 0
        self.vy = 0
        
        self.vida_maxima = calcular_vida_maxima(self.niveis.get("vida", 1))
        self.vida = self.vida_maxima
        self.dano_sofrido = False
        self.invulneravel = False
        self.tempo_invulneravel = 0
        self.aegis_ativo = False
        self.pontos_para_cura = 0
        
        self.energia_especial = 0
        self.energia_maxima = 100
        self.progresso_energia_especial = 0
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
            self.dano_sofrido = True
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
        taxa_recarga = calcular_taxa_recarga_especial(
            self.niveis.get("recarga", 1)
        )
        quantidade = round(quantidade * taxa_recarga / 50)
        self.energia_especial += quantidade
        if self.energia_especial > self.energia_maxima:
            self.energia_especial = self.energia_maxima

    def adicionar_energia_por_dano(self, dano):
        if self.energia_especial >= self.energia_maxima:
            self.progresso_energia_especial = 0
            return

        taxa_recarga = calcular_taxa_recarga_especial(
            self.niveis.get("recarga", 1)
        )
        self.progresso_energia_especial += max(0, int(dano)) * taxa_recarga
        energia_ganha = self.progresso_energia_especial // 100
        self.progresso_energia_especial %= 100
        self.energia_especial = min(
            self.energia_maxima,
            self.energia_especial + energia_ganha,
        )
        if self.energia_especial >= self.energia_maxima:
            self.progresso_energia_especial = 0

    def disparar_especial(self):
        if self.energia_especial >= self.energia_maxima:
            self.energia_especial = 0
            if self.modelo == "aegis":
                self.aegis_ativo = True
            return True 
        return False

    def criar_tiros_basicos(self):
        x = self.rect.centerx
        y = self.rect.centery
        tiros = None

        if self.modelo == "scout":
            tiros = [
                Tiro(
                    x, y, self.angulo,
                    velocidade=22, largura=4, comprimento=22,
                    cor=(90, 235, 255),
                )
            ]
        elif self.modelo == "titan":
            tiros = [
                Tiro(
                    x, y, self.angulo,
                    velocidade=12, largura=10, comprimento=21,
                    cor=(255, 145, 65),
                )
            ]
        elif self.modelo == "phantom":
            rad = math.radians(self.angulo)
            deslocamento_x = math.sin(rad) * 8
            deslocamento_y = math.cos(rad) * 8
            tiros = [
                Tiro(
                    x + sinal * deslocamento_x,
                    y + sinal * deslocamento_y,
                    self.angulo,
                    dano=1,
                    largura=5,
                    comprimento=14,
                    cor=(235, 115, 255),
                )
                for sinal in (-1, 1)
            ]
        elif self.modelo == "aegis":
            tiros = [
                Tiro(
                    x, y, self.angulo,
                    velocidade=15, largura=10, comprimento=18,
                    cor=(100, 255, 205),
                )
            ]

        if tiros is None:
            tiros = [Tiro(x, y, self.angulo)]

        bonus_dano = max(0, int(self.niveis.get("dano", 1)) - 1)
        for indice in range(bonus_dano):
            tiros[indice % len(tiros)].dano_inimigo += 1
        return tiros

    def criar_tiro_especial(self):
        x = self.rect.centerx
        y = self.rect.centery

        if self.modelo == "vanguard":
            tiros = [
                TiroEspecial(x, y, self.angulo - 12, tipo="vanguard", cor=(120, 220, 255)),
                TiroEspecial(x, y, self.angulo, tipo="vanguard", cor=(160, 245, 255)),
                TiroEspecial(x, y, self.angulo + 12, tipo="vanguard", cor=(120, 220, 255)),
            ]
            for tiro in tiros:
                tiro.dano_inimigo = 2
                tiro.limite_alvos = 3
            return tiros
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
