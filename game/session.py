import math
import random
import sys
from dataclasses import dataclass
from typing import Callable

import pygame

import config
from config import FPS
from game.entities.effects import Explosao
from game.entities.enemies import (
    Asteroide,
    calcular_meta_frota,
    gerar_frota_inimiga,
)
from game.entities.player import Nave
from game.entities.projectiles import Tiro, TiroEspecialAegis
from game.achievements import (
    CONQUISTAS_POR_ID,
    TEMPO_SOBREVIVENTE_MS,
    acumular_tempo_sobrevivencia,
    desbloquear_conquista,
)
from game.balance import calcular_cura_inimigo_derrotado
from game.ui import desenhar_tela_jogo


@dataclass(frozen=True)
class SessionServices:
    get_screen: Callable[[], pygame.Surface]
    clock: pygame.time.Clock
    fonts: tuple
    backgrounds: tuple
    infinite_background: pygame.Surface | None
    resize_display: Callable[[pygame.event.Event], tuple[int, int]]
    create_initial_asteroids: Callable
    create_infinite_asteroids: Callable
    asteroid_damage: Callable
    save_player: Callable
    play_sound: Callable


def _selecionar_fundo_sessao(modo_jogo, fase_atual, backgrounds, infinite_background):
    if modo_jogo == "infinito":
        return infinite_background
    if fase_atual == 1:
        return backgrounds[0]
    if fase_atual == 2:
        return backgrounds[1]
    if fase_atual == 3:
        return backgrounds[2]
    return backgrounds[3]


def run_game_session(
    arquivo_nave,
    niveis_melhorias,
    fase_atual=1,
    modo_jogo="asteroides",
    dados_jogador=None,
    *,
    services: SessionServices,
):
    fonte_titulo, fonte_texto, fonte_hud = services.fonts
    fundo_fase_1, fundo_fase_2, fundo_fase_3, fundo_fase_4 = services.backgrounds
    largura, altura = services.get_screen().get_size()
    todos_sprites = pygame.sprite.Group()
    tiros = pygame.sprite.Group()
    asteroides = pygame.sprite.Group()
    inimigos_frota = pygame.sprite.Group()
    tiros_inimigos = pygame.sprite.Group()
    especiais = pygame.sprite.Group()
    explosoes = pygame.sprite.Group()
    modo_frota = modo_jogo == "frota_inimiga"
    modo_infinito = modo_jogo == "infinito"

    fundo_fase = _selecionar_fundo_sessao(
        modo_jogo,
        fase_atual,
        services.backgrounds,
        services.infinite_background,
    )

    jogador = Nave(largura // 2, altura - 80, arquivo_nave, niveis_melhorias)
    todos_sprites.add(jogador)

    if modo_infinito:
        asteroides = services.create_infinite_asteroids(pontos=0, fase_atual=fase_atual, quantidade_minima=10)
    else:
        asteroides = services.create_initial_asteroids(fase_atual, modo_frota)
    for ast in asteroides:
        todos_sprites.add(ast)

    frota_inicial = []
    if modo_frota:
        frota_inicial = gerar_frota_inimiga(fase_atual)
        for nave_inimiga in frota_inicial:
            todos_sprites.add(nave_inimiga)
            inimigos_frota.add(nave_inimiga)

    moedas = 0
    pontos = 0
    meta_pontos = 0 if modo_infinito else (calcular_meta_frota(fase_atual, frota_inicial) if modo_frota else 240 + fase_atual * 120)

    rodando = True
    pausado = False
    cooldown_tiro = 0
    cadencia_base = max(4, 12 - (niveis_melhorias["cadencia"] - 1) * 2)
    venceu = False
    botao_pausa = pygame.Rect(largura - 120, 20, 100, 35)
    tempo_inicio_infinito = pygame.time.get_ticks() if modo_infinito else 0
    tempo_sobrevivido_ms = 0
    notificacao_conquista = None
    notificacao_ate = 0

    def tentar_desbloquear(conquista_id):
        nonlocal notificacao_conquista, notificacao_ate
        if dados_jogador is not None and desbloquear_conquista(dados_jogador, conquista_id):
            services.save_player(dados_jogador)
            notificacao_conquista = CONQUISTAS_POR_ID[conquista_id]["nome"]
            notificacao_ate = pygame.time.get_ticks() + 4000
    
    while rodando:
        delta_ms = services.clock.tick(FPS)
        pausado_no_inicio = pausado
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.VIDEORESIZE or (
                evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11
            ):
                largura, altura = services.resize_display(evento)
                botao_pausa = pygame.Rect(largura - 120, 20, 100, 35)

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if botao_pausa.collidepoint(evento.pos):
                    pausado = not pausado

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_p:
                    pausado = not pausado
                elif evento.key == pygame.K_k:
                    if jogador.disparar_especial():
                        services.play_sound([620, 820], duracao=0.18, volume=0.3)
                        if jogador.modelo != "aegis":
                            for especial in jogador.criar_tiro_especial():
                                todos_sprites.add(especial)
                                especiais.add(especial)
                        else:
                            especial = TiroEspecialAegis(jogador.rect.centerx, jogador.rect.centery, jogador.angulo, nave=jogador)
                            todos_sprites.add(especial)
                            especiais.add(especial)
            elif evento.type == pygame.KEYUP and evento.key == pygame.K_k and jogador.modelo == "aegis":
                jogador.aegis_ativo = False

        if pausado:
            desenhar_tela_jogo(
                pygame.display.get_surface(),
                fundo_fase,
                todos_sprites,
                (fonte_titulo, fonte_texto, fonte_hud),
                {
                    "pontos": pontos,
                    "meta_pontos": meta_pontos,
                    "fase_atual": fase_atual,
                    "moedas": moedas,
                    "vida": jogador.vida,
                    "vida_maxima": jogador.vida_maxima,
                    "energia_especial": jogador.energia_especial,
                    "inimigos_restantes": len(inimigos_frota),
                    "modo_jogo": modo_jogo,
                    "modelo_nave": jogador.modelo,
                    "botao_pausa": botao_pausa,
                    "notificacao_conquista": (
                        notificacao_conquista
                        if pygame.time.get_ticks() < notificacao_ate
                        else None
                    ),
                },
                pausado=True,
            )
            continue

        tempo_sobrevivido_ms = acumular_tempo_sobrevivencia(
            tempo_sobrevivido_ms,
            delta_ms,
            modo_infinito,
            pausado_no_inicio,
        )

        teclas = pygame.key.get_pressed()
        
        if teclas[pygame.K_j]:
            if cooldown_tiro <= 0:
                tiro = Tiro(jogador.rect.centerx, jogador.rect.centery, jogador.angulo)
                todos_sprites.add(tiro)
                tiros.add(tiro)
                services.play_sound([420], duracao=0.08, volume=0.18)
                cooldown_tiro = cadencia_base
                
        if cooldown_tiro > 0:
            cooldown_tiro -= 1

        jogador.update(teclas)

        if modo_infinito:
            tempo_jogo_ms = pygame.time.get_ticks() - tempo_inicio_infinito
            dificuldade_infinita = 1 + tempo_jogo_ms // 10000
            limite_asteroides = min(26, 10 + dificuldade_infinita + pontos // 250)

            if len(asteroides) < limite_asteroides:
                faltam = limite_asteroides - len(asteroides)
                for _ in range(faltam):
                    ast = Asteroide(fase_atual)
                    ast.velocidadey = max(2, 2 + dificuldade_infinita * 0.5 + min(4, pontos / 500))
                    ast.velocidadex = random.randint(-2, 2)
                    ast.rect.x = random.randint(0, config.LARGURA - ast.tamanho)
                    ast.rect.y = random.randint(-120, -30)
                    todos_sprites.add(ast)
                    asteroides.add(ast)

        todos_sprites.update()

        colisoes_tiro = pygame.sprite.groupcollide(asteroides, tiros, True, True)
        for ast in colisoes_tiro:
            cor_explosao = (255, 190, 80)
            if jogador.modelo == "titan":
                cor_explosao = (255, 150, 60)
            explosao = Explosao(ast.rect.centerx, ast.rect.centery, cor=cor_explosao, raio_inicial=16)
            todos_sprites.add(explosao)
            explosoes.add(explosao)
            pontos += 10
            jogador.aplicar_pontos_para_cura(10)
            moedas += 1
            jogador.adicionar_energia(20)
            services.play_sound([180, 120], duracao=0.15, volume=0.25)
            
            if pontos < meta_pontos:
                novo_ast = Asteroide(fase_atual)
                novo_ast.velocidadey = max(1, novo_ast.velocidadey - 2)
                todos_sprites.add(novo_ast)
                asteroides.add(novo_ast)

        for especial in list(especiais):
            if getattr(especial, "tipo", None) == "titan":
                for ast in list(asteroides):
                    distancia = math.hypot(ast.rect.centerx - especial.rect.centerx, ast.rect.centery - especial.rect.centery)
                    if distancia <= especial.raio:
                        dano_ast = especial.dano_central if distancia <= especial.raio * 0.5 else especial.dano
                        cor_explosao = (255, 55, 55)
                        explosao = Explosao(ast.rect.centerx, ast.rect.centery, cor=cor_explosao, raio_inicial=16)
                        todos_sprites.add(explosao)
                        explosoes.add(explosao)
                        ast.kill()
                        pontos += 8 + int(dano_ast)
                        jogador.aplicar_pontos_para_cura(8 + int(dano_ast))
                        moedas += 1
                        services.play_sound([520, 700, 820], duracao=0.2, volume=0.3)
                        if pontos < meta_pontos:
                            novo_ast = Asteroide(fase_atual)
                            novo_ast.velocidadey = max(1, novo_ast.velocidadey - 2)
                            todos_sprites.add(novo_ast)
                            asteroides.add(novo_ast)

                for nave_inimiga in list(inimigos_frota):
                    distancia = math.hypot(nave_inimiga.rect.centerx - especial.rect.centerx, nave_inimiga.rect.centery - especial.rect.centery)
                    if distancia <= especial.raio:
                        dano_nave = especial.dano_central if distancia <= especial.raio * 0.5 else especial.dano
                        nave_inimiga.vida -= dano_nave
                        explosao = Explosao(nave_inimiga.rect.centerx, nave_inimiga.rect.centery, cor=(255, 55, 55), raio_inicial=12)
                        todos_sprites.add(explosao)
                        explosoes.add(explosao)
                        if nave_inimiga.vida <= 0:
                            nave_inimiga.kill()
                            pontos += 18 + fase_atual * 4 + dano_nave
                            jogador.aplicar_pontos_para_cura(18 + fase_atual * 4 + dano_nave)
                            moedas += 2
                            jogador.adicionar_energia(12)
                            services.play_sound([260, 200], duracao=0.12, volume=0.25)

            elif getattr(especial, "tipo", None) == "aegis":
                for nave_inimiga in list(especial.cooldowns_inimigos):
                    if not nave_inimiga.alive():
                        del especial.cooldowns_inimigos[nave_inimiga]
                    else:
                        especial.cooldowns_inimigos[nave_inimiga] = max(
                            0,
                            especial.cooldowns_inimigos[nave_inimiga] - 1,
                        )

                if especial.ativo:
                    pygame.sprite.spritecollide(especial, tiros_inimigos, True)
                    for nave_inimiga in list(inimigos_frota):
                        if (
                            not nave_inimiga.alive()
                            or not especial.rect.colliderect(nave_inimiga.rect)
                            or especial.cooldowns_inimigos.get(nave_inimiga, 0) > 0
                        ):
                            continue

                        nave_inimiga.vida -= especial.dano_inimigo
                        especial.cooldowns_inimigos[nave_inimiga] = especial.intervalo_dano
                        explosao = Explosao(
                            nave_inimiga.rect.centerx,
                            nave_inimiga.rect.centery,
                            cor=(100, 255, 180),
                            raio_inicial=12,
                        )
                        todos_sprites.add(explosao)
                        explosoes.add(explosao)
                        if nave_inimiga.vida <= 0:
                            nave_inimiga.kill()
                            pontos += 25 + fase_atual * 5
                            jogador.aplicar_pontos_para_cura(25 + fase_atual * 5)
                            moedas += 2
                            jogador.recuperar_vida(calcular_cura_inimigo_derrotado(fase_atual))
                            jogador.adicionar_energia(12)
                            services.play_sound([260, 200], duracao=0.12, volume=0.25)

            else:
                for nave_inimiga in list(inimigos_frota):
                    if (
                        not especial.alive()
                        or not nave_inimiga.alive()
                        or not especial.rect.colliderect(nave_inimiga.rect)
                        or not especial.registrar_impacto_inimigo(nave_inimiga)
                    ):
                        continue

                    nave_inimiga.vida -= especial.dano_inimigo
                    explosao = Explosao(
                        nave_inimiga.rect.centerx,
                        nave_inimiga.rect.centery,
                        cor=especial.cor,
                        raio_inicial=12,
                    )
                    todos_sprites.add(explosao)
                    explosoes.add(explosao)
                    if nave_inimiga.vida <= 0:
                        nave_inimiga.kill()
                        pontos += 25 + fase_atual * 5
                        jogador.aplicar_pontos_para_cura(25 + fase_atual * 5)
                        moedas += 2
                        jogador.recuperar_vida(calcular_cura_inimigo_derrotado(fase_atual))
                        jogador.adicionar_energia(12)
                        services.play_sound([260, 200], duracao=0.12, volume=0.25)

        ataques_asteroides = [
            especial
            for especial in especiais
            if especial.tipo != "titan" and (especial.tipo != "aegis" or especial.ativo)
        ]
        colisoes_especial = pygame.sprite.groupcollide(asteroides, ataques_asteroides, True, False)
        for ast in colisoes_especial:
            cor_explosao = (255, 110, 255)
            if jogador.modelo == "titan":
                cor_explosao = (255, 55, 55)
            explosao = Explosao(ast.rect.centerx, ast.rect.centery, cor=cor_explosao, raio_inicial=18)
            todos_sprites.add(explosao)
            explosoes.add(explosao)
            pontos += 15
            jogador.aplicar_pontos_para_cura(15)
            moedas += 2
            services.play_sound([520, 700, 820], duracao=0.2, volume=0.3)
            if pontos < meta_pontos:
                novo_ast = Asteroide(fase_atual)
                novo_ast.velocidadey = max(1, novo_ast.velocidadey - 2)
                todos_sprites.add(novo_ast)
                asteroides.add(novo_ast)

        if modo_frota:
            for nave_inimiga in list(inimigos_frota):
                if nave_inimiga.cooldown_tiro <= 0:
                    tiro_inimigo = nave_inimiga.criar_tiro(jogador)
                    if tiro_inimigo is not None:
                        todos_sprites.add(tiro_inimigo)
                        tiros_inimigos.add(tiro_inimigo)

            colisoes_frota = pygame.sprite.groupcollide(inimigos_frota, tiros, False, True)
            for nave_inimiga in colisoes_frota:
                nave_inimiga.vida -= 1
                explosao = Explosao(nave_inimiga.rect.centerx, nave_inimiga.rect.centery, cor=(255, 90, 90), raio_inicial=12)
                todos_sprites.add(explosao)
                explosoes.add(explosao)
                if nave_inimiga.vida <= 0:
                    nave_inimiga.kill()
                    pontos += 25 + fase_atual * 5
                    jogador.aplicar_pontos_para_cura(25 + fase_atual * 5)
                    moedas += 2
                    jogador.recuperar_vida(calcular_cura_inimigo_derrotado(fase_atual))
                    jogador.adicionar_energia(12)
                    services.play_sound([260, 200], duracao=0.12, volume=0.25)

            if len(inimigos_frota) == 0 and pontos < meta_pontos:
                nova_frota = gerar_frota_inimiga(fase_atual)
                for nave_inimiga in nova_frota:
                    todos_sprites.add(nave_inimiga)
                    inimigos_frota.add(nave_inimiga)

        if jogador.modelo == "aegis" and not teclas[pygame.K_k] and jogador.aegis_ativo:
            jogador.aegis_ativo = False

        if not modo_infinito and pontos >= meta_pontos:
            venceu = True
            rodando = False

        tiros_jogador_colidindo = pygame.sprite.spritecollide(jogador, tiros_inimigos, True)
        colidiu_com_asteroide = pygame.sprite.spritecollideany(jogador, asteroides)
        dano_asteroide = services.asteroid_damage(modo_jogo)

        if colidiu_com_asteroide or (modo_frota and pygame.sprite.spritecollideany(jogador, inimigos_frota)) or tiros_jogador_colidindo:
            services.play_sound([100, 70], duracao=0.18, volume=0.28)
            dano_aplicado = dano_asteroide if colidiu_com_asteroide else 20
            if jogador.perder_vida(dano_aplicado):
                pygame.time.delay(500)
                rodando = False

        if (
            rodando
            and modo_infinito
            and tempo_sobrevivido_ms >= TEMPO_SOBREVIVENTE_MS
        ):
            tentar_desbloquear("sobrevivente")

        titan_restante = None
        if jogador.modelo == "titan":
            especial_ativa = next((especial for especial in especiais if getattr(especial, "tipo", None) == "titan"), None)
            if especial_ativa is not None:
                titan_restante = max(0, especial_ativa.vida / FPS)

        desenhar_tela_jogo(
            pygame.display.get_surface(),
            fundo_fase,
            todos_sprites,
            (fonte_titulo, fonte_texto, fonte_hud),
            {
                "pontos": pontos,
                "meta_pontos": meta_pontos,
                "fase_atual": fase_atual,
                "moedas": moedas,
                "vida": jogador.vida,
                "vida_maxima": jogador.vida_maxima,
                "energia_especial": jogador.energia_especial,
                "inimigos_restantes": len(inimigos_frota),
                "modo_jogo": modo_jogo,
                "modelo_nave": jogador.modelo,
                "botao_pausa": botao_pausa,
                "titan_restante": titan_restante,
                "notificacao_conquista": (
                    notificacao_conquista
                    if pygame.time.get_ticks() < notificacao_ate
                    else None
                ),
            },
        )

    if venceu and not jogador.dano_sofrido:
        tentar_desbloquear("intocavel")

    return pontos, moedas, venceu
