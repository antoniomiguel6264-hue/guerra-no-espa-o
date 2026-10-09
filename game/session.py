import math
import random
import sys
from dataclasses import dataclass
from typing import Callable

import pygame

import config
from config import FPS
from game.entities.effects import Explosao, Impacto
from game.entities.enemies import (
    Asteroide,
    ChefeFrota,
    calcular_meta_frota,
    gerar_frota_inimiga,
)
from game.entities.player import Nave
from game.entities.projectiles import TiroEspecialAegis
from game.achievements import (
    CONQUISTAS_POR_ID,
    TEMPO_SOBREVIVENTE_MS,
    acumular_tempo_sobrevivencia,
    desbloquear_conquista,
)
from game.balance import (
    calcular_bonus_moedas_inimigo,
    calcular_cura_inimigo_derrotado,
    calcular_dano_recebido_frota,
)
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


def _calcular_dano_colisao(
    modo_jogo,
    colidiu_com_asteroide,
    dano_asteroide,
    nivel_defesa=1,
):
    if colidiu_com_asteroide:
        return dano_asteroide
    if modo_jogo == "frota_inimiga":
        return calcular_dano_recebido_frota(nivel_defesa)
    return 20


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
    botao_abandonar = pygame.Rect(largura // 2 - 130, altura // 2 + 70, 260, 44)
    abandonada = False
    tempo_inicio_infinito = pygame.time.get_ticks() if modo_infinito else 0
    tempo_sobrevivido_ms = 0
    notificacao_conquista = None
    notificacao_ate = 0
    chefe = None
    chefe_derrotado = False

    def aplicar_dano_inimigo(inimigo, dano):
        vida_anterior = max(0, inimigo.vida)
        dano_efetivo = min(vida_anterior, max(0, dano))
        inimigo.vida = vida_anterior - dano_efetivo
        if modo_frota:
            jogador.adicionar_energia_por_dano(dano_efetivo)

    def tentar_desbloquear(conquista_id):
        nonlocal notificacao_conquista, notificacao_ate
        if dados_jogador is not None and desbloquear_conquista(dados_jogador, conquista_id):
            services.save_player(dados_jogador)
            notificacao_conquista = CONQUISTAS_POR_ID[conquista_id]["nome"]
            notificacao_ate = pygame.time.get_ticks() + 4000

    def registrar_derrota_inimigo(inimigo, pontos_base, cura=False):
        nonlocal pontos, moedas, chefe_derrotado
        inimigo.kill()
        bonus_moedas = calcular_bonus_moedas_inimigo(
            niveis_melhorias.get("recompensa", 1)
        )

        if getattr(inimigo, "eh_chefe", False):
            chefe_derrotado = True
            pontos += 100 + fase_atual * 50
            moedas += 10 + bonus_moedas
            jogador.recuperar_vida(calcular_cura_inimigo_derrotado(fase_atual))
            jogador.adicionar_energia(30)
            services.play_sound([180, 260, 520, 780], duracao=0.35, volume=0.4)
            return

        pontos += pontos_base
        moedas += 2 + bonus_moedas
        if cura:
            jogador.recuperar_vida(calcular_cura_inimigo_derrotado(fase_atual))
        jogador.adicionar_energia(12)
        services.play_sound([260, 200], duracao=0.12, volume=0.25)
    
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
                botao_abandonar = pygame.Rect(
                    largura // 2 - 130,
                    altura // 2 + 70,
                    260,
                    44,
                )

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if botao_pausa.collidepoint(evento.pos):
                    pausado = not pausado
                elif pausado and botao_abandonar.collidepoint(evento.pos):
                    abandonada = True
                    rodando = False

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

        if abandonada:
            break

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
                    "botao_abandonar": botao_abandonar,
                    "chefe_vida": chefe.vida if chefe is not None and chefe.alive() else None,
                    "chefe_vida_maxima": (
                        chefe.vida_maxima if chefe is not None and chefe.alive() else None
                    ),
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
                novos_tiros = jogador.criar_tiros_basicos()
                todos_sprites.add(novos_tiros)
                tiros.add(novos_tiros)
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
            impacto = Impacto(ast.rect.centerx, ast.rect.centery, "asteroide")
            todos_sprites.add(impacto)
            explosoes.add(impacto)
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
                        aplicar_dano_inimigo(nave_inimiga, dano_nave)
                        explosao = Explosao(nave_inimiga.rect.centerx, nave_inimiga.rect.centery, cor=(255, 55, 55), raio_inicial=12)
                        todos_sprites.add(explosao)
                        explosoes.add(explosao)
                        if nave_inimiga.vida <= 0:
                            pontos_base = (
                                100 + fase_atual * 50
                                if getattr(nave_inimiga, "eh_chefe", False)
                                else 18 + fase_atual * 4 + dano_nave
                            )
                            registrar_derrota_inimigo(nave_inimiga, pontos_base)
                            jogador.aplicar_pontos_para_cura(18 + fase_atual * 4 + dano_nave)

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

                        aplicar_dano_inimigo(nave_inimiga, especial.dano_inimigo)
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
                            pontos_base = (
                                100 + fase_atual * 50
                                if getattr(nave_inimiga, "eh_chefe", False)
                                else 25 + fase_atual * 5
                            )
                            registrar_derrota_inimigo(
                                nave_inimiga,
                                pontos_base,
                                cura=True,
                            )
                            jogador.aplicar_pontos_para_cura(25 + fase_atual * 5)

            else:
                for nave_inimiga in list(inimigos_frota):
                    if (
                        not especial.alive()
                        or not nave_inimiga.alive()
                        or not especial.rect.colliderect(nave_inimiga.rect)
                        or not especial.registrar_impacto_inimigo(nave_inimiga)
                    ):
                        continue

                    aplicar_dano_inimigo(nave_inimiga, especial.dano_inimigo)
                    explosao = Explosao(
                        nave_inimiga.rect.centerx,
                        nave_inimiga.rect.centery,
                        cor=especial.cor,
                        raio_inicial=12,
                    )
                    todos_sprites.add(explosao)
                    explosoes.add(explosao)
                    if nave_inimiga.vida <= 0:
                        pontos_base = (
                            100 + fase_atual * 50
                            if getattr(nave_inimiga, "eh_chefe", False)
                            else 25 + fase_atual * 5
                        )
                        registrar_derrota_inimigo(
                            nave_inimiga,
                            pontos_base,
                            cura=True,
                        )
                        jogador.aplicar_pontos_para_cura(25 + fase_atual * 5)

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
                    if getattr(nave_inimiga, "eh_chefe", False):
                        novos_tiros = nave_inimiga.criar_tiros(jogador)
                    else:
                        tiro_inimigo = nave_inimiga.criar_tiro(jogador)
                        novos_tiros = [tiro_inimigo] if tiro_inimigo is not None else []
                    todos_sprites.add(novos_tiros)
                    tiros_inimigos.add(novos_tiros)

            colisoes_frota = pygame.sprite.groupcollide(inimigos_frota, tiros, False, True)
            for nave_inimiga, tiros_que_atingiram in colisoes_frota.items():
                aplicar_dano_inimigo(
                    nave_inimiga,
                    sum(tiro.dano_inimigo for tiro in tiros_que_atingiram),
                )
                for tiro in tiros_que_atingiram:
                    impacto = Impacto(tiro.rect.centerx, tiro.rect.centery, "nave")
                    todos_sprites.add(impacto)
                    explosoes.add(impacto)
                if nave_inimiga.vida <= 0:
                    explosao = Explosao(
                        nave_inimiga.rect.centerx,
                        nave_inimiga.rect.centery,
                        cor=(255, 90, 90),
                        raio_inicial=42 if getattr(nave_inimiga, "eh_chefe", False) else 16,
                    )
                    todos_sprites.add(explosao)
                    explosoes.add(explosao)
                    pontos_base = (
                        100 + fase_atual * 50
                        if getattr(nave_inimiga, "eh_chefe", False)
                        else 25 + fase_atual * 5
                    )
                    registrar_derrota_inimigo(
                        nave_inimiga,
                        pontos_base,
                        cura=True,
                    )
                    jogador.aplicar_pontos_para_cura(25 + fase_atual * 5)
                else:
                    services.play_sound([760, 580], duracao=0.09, volume=0.18)

            if len(inimigos_frota) == 0 and pontos < meta_pontos:
                nova_frota = gerar_frota_inimiga(fase_atual)
                for nave_inimiga in nova_frota:
                    todos_sprites.add(nave_inimiga)
                    inimigos_frota.add(nave_inimiga)

        if modo_frota and pontos >= meta_pontos and chefe is None:
            chefe = ChefeFrota(largura // 2, 90, fase_atual)
            todos_sprites.add(chefe)
            inimigos_frota.add(chefe)
            services.play_sound([150, 220, 180], duracao=0.45, volume=0.4)

        if jogador.modelo == "aegis" and not teclas[pygame.K_k] and jogador.aegis_ativo:
            jogador.aegis_ativo = False

        if (
            not modo_infinito
            and pontos >= meta_pontos
            and (not modo_frota or chefe_derrotado)
        ):
            venceu = True
            rodando = False

        tiros_jogador_colidindo = pygame.sprite.spritecollide(jogador, tiros_inimigos, True)
        colidiu_com_asteroide = pygame.sprite.spritecollideany(jogador, asteroides)
        dano_asteroide = services.asteroid_damage(modo_jogo)

        if colidiu_com_asteroide or (modo_frota and pygame.sprite.spritecollideany(jogador, inimigos_frota)) or tiros_jogador_colidindo:
            services.play_sound([100, 70], duracao=0.18, volume=0.28)
            dano_aplicado = _calcular_dano_colisao(
                modo_jogo,
                colidiu_com_asteroide,
                dano_asteroide,
                niveis_melhorias.get("defesa", 1),
            )
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
                "chefe_vida": chefe.vida if chefe is not None and chefe.alive() else None,
                "chefe_vida_maxima": (
                    chefe.vida_maxima if chefe is not None and chefe.alive() else None
                ),
                "notificacao_conquista": (
                    notificacao_conquista
                    if pygame.time.get_ticks() < notificacao_ate
                    else None
                ),
            },
        )

    if venceu and not jogador.dano_sofrido:
        tentar_desbloquear("intocavel")

    return pontos, moedas, venceu, abandonada
