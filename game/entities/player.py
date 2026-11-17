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
    TiroEspecialDreadnought,
    TiroEspecialHellion,
    TiroEspecialHyperion,
    TiroEspecialLaser,
    TiroEspecialNova,
    TiroEspecialTitan,
)
from game.display import multiplicador_tamanho_em_jogo
from game.ship_art import ARQUIVOS_IMAGEM_NAVE, criar_imagem_nave


class Nave(pygame.sprite.Sprite):
    def __init__(self, x, y, imagem_path, niveis_melhorias=None):
        super().__init__()
        modelo_imagem = os.path.splitext(os.path.basename(imagem_path))[0].lower()
        self.modelo = {
            "titan hellion core": "titan",
        }.get(modelo_imagem, modelo_imagem)
        self.habilidade_especial = (
            "hellion" if modelo_imagem == "titan hellion core" else self.modelo
        )
        self.tamanho = round(84 * multiplicador_tamanho_em_jogo())
        arquivo_imagem = ARQUIVOS_IMAGEM_NAVE.get(modelo_imagem, imagem_path)
        caminho_imagem = resolver_caminho_arquivo(arquivo_imagem)
        try:
            self.image_original = pygame.image.load(caminho_imagem).convert_alpha()
            self.image_original = pygame.transform.scale(
                self.image_original,
                (self.tamanho, self.tamanho),
            )
        except Exception as e:
            print(f"Erro ao carregar {imagem_path}: {e}. Usando placeholder.")
            if self.modelo in {
                "tempest", "nova", "wraith",
                "dreadnought", "vortex", "seraph",
            }:
                self.image_original = criar_imagem_nave(self.modelo)
                self.image_original = pygame.transform.scale(
                    self.image_original,
                    (self.tamanho, self.tamanho),
                )
            else:
                self.image_original = pygame.Surface((self.tamanho, self.tamanho))
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
            1.5
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
        self.duracao_invulneravel = 1500
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

        limite = self.tamanho // 2
        if self.x < limite:
            self.x = limite
            self.vx = 0
        elif self.x > config.LARGURA - limite:
            self.x = config.LARGURA - limite
            self.vx = 0
        if self.y < limite:
            self.y = limite
            self.vy = 0
        elif self.y > config.ALTURA - limite:
            self.y = config.ALTURA - limite
            self.vy = 0

        self.rect.center = (int(self.x), int(self.y))
        self.image = pygame.transform.rotate(self.image_original, self.angulo - 90)
        self.rect = self.image.get_rect(center=self.rect.center)

        if self.invulneravel:
            if pygame.time.get_ticks() - self.tempo_invulneravel > self.duracao_invulneravel:
                self.invulneravel = False
                self.duracao_invulneravel = 1500

        if self.modelo == "wraith" and self.invulneravel:
            self.image.set_alpha(120)

    def perder_vida(self, dano=20):
        if not self.invulneravel:
            self.vida = max(0, self.vida - dano)
            self.dano_sofrido = True
            self.invulneravel = True
            self.tempo_invulneravel = pygame.time.get_ticks()
            self.duracao_invulneravel = 1500
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
            elif self.modelo == "wraith":
                self.invulneravel = True
                self.tempo_invulneravel = pygame.time.get_ticks()
                self.duracao_invulneravel = 3000
            elif self.modelo == "seraph":
                self.recuperar_vida(40)
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
        elif self.modelo == "tempest":
            tiros = [
                Tiro(
                    x, y, self.angulo + deslocamento,
                    dano=1, velocidade=17, largura=5, comprimento=17,
                    cor=(90, 225, 255),
                )
                for deslocamento in (-12, 0, 12)
            ]
        elif self.modelo == "nova":
            tiros = [
                Tiro(
                    x, y, self.angulo,
                    velocidade=10, dano=3, largura=12, comprimento=25,
                    cor=(255, 155, 65),
                )
            ]
        elif self.modelo == "wraith":
            tiros = [
                Tiro(
                    x, y, self.angulo,
                    velocidade=21, largura=4, comprimento=19,
                    cor=(190, 130, 255),
                )
            ]
        elif self.modelo == "dreadnought":
            tiros = [
                Tiro(
                    x, y, self.angulo,
                    velocidade=10, dano=4, largura=14, comprimento=26,
                    cor=(255, 130, 65),
                )
            ]
        elif self.modelo == "vortex":
            rad = math.radians(self.angulo)
            deslocamento_x = math.sin(rad) * 7
            deslocamento_y = math.cos(rad) * 7
            tiros = [
                Tiro(
                    x + sinal * deslocamento_x,
                    y + sinal * deslocamento_y,
                    self.angulo,
                    dano=1,
                    velocidade=23,
                    largura=4,
                    comprimento=18,
                    cor=(100, 255, 205),
                )
                for sinal in (-1, 1)
            ]
        elif self.modelo == "seraph":
            tiros = [
                Tiro(
                    x + sinal * 9, y, self.angulo,
                    velocidade=18, largura=6, comprimento=20,
                    cor=(255, 230, 130),
                )
                for sinal in (-1, 1)
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

        elif self.modelo == "hyperion":
            tiros = [
                Tiro(
                    x, y, self.angulo,
                    velocidade=11, dano=5,
                    largura=12, comprimento=28,
                    cor=(100, 210, 255),
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

        if self.modelo == "hyperion":
            return [
                TiroEspecialHyperion(
                    x,
                    y,
                    nivel=self.niveis["especial"],
                )
            ]
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
        if self.modelo == "tempest":
            tiros = [
                TiroEspecial(
                    x, y, self.angulo + deslocamento,
                    tipo="tempest", cor=(80, 225, 255), velocidade=18,
                )
                for deslocamento in (-30, -15, 0, 15, 30)
            ]
            for tiro in tiros:
                tiro.dano_inimigo = 1
                tiro.limite_alvos = 1
            return tiros
        if self.modelo == "nova":
            return [
                TiroEspecialNova(
                    x, y, self.angulo, nivel=self.niveis["especial"],
                )
            ]
        if self.modelo == "wraith":
            return []
        if self.modelo == "dreadnought":
            return [
                TiroEspecialDreadnought(
                    x,
                    y,
                    self.angulo,
                    nivel=self.niveis["especial"],
                )
            ]
        if self.modelo == "vortex":
            tiros = [
                TiroEspecial(
                    x, y, self.angulo + deslocamento,
                    tipo="vortex", cor=(90, 255, 220), velocidade=22,
                )
                for deslocamento in (-36, -24, -12, 0, 12, 24, 36)
            ]
            for tiro in tiros:
                tiro.dano_inimigo = 2
                tiro.limite_alvos = 2
            return tiros
        if self.modelo == "seraph":
            tiros = [
                TiroEspecial(
                    x, y, self.angulo + deslocamento,
                    tipo="seraph", cor=(255, 230, 140), velocidade=17,
                )
                for deslocamento in (-22, -11, 0, 11, 22)
            ]
            for tiro in tiros:
                tiro.dano_inimigo = 3
                tiro.limite_alvos = 2
            return tiros
        if self.habilidade_especial == "hellion":
            duracao = 60 + max(0, self.niveis["especial"] - 1) * 12
            return [
                TiroEspecialHellion(
                    x,
                    y,
                    duracao=duracao,
                    nivel=self.niveis["especial"],
                )
            ]
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
