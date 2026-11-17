import random
import math
import os

import pygame
import sys
import config
from audio import tocar_som
from config import FPS, PRETO, BRANCO, AZUL_NEON, AMARELO, VERMELHO, CINZA
from entidades import Nave, NaveInimiga, Tiro, TiroEspecial, TiroEspecialAegis, Asteroide, Explosao, gerar_frota_inimiga, gerar_frota_infinita, calcular_meta_frota
from game.balance import calcular_cura_inimigo_derrotado
from game.habitats import fundos_para_habitat, obter_habitat
from game.rewards import (
    MAX_FASES_CAMPANHA,
    RECOMPENSAS_POR_ID,
    registrar_fase_concluida,
    resgatar_recompensa,
)
from game.achievements import (
    CONQUISTAS_POR_ID,
    TEMPO_SOBREVIVENTE_MS,
    acumular_tempo_sobrevivencia,
    desbloquear_conquista,
    listar_conquistas,
)
from game.resources import criar_recursos_jogo
from game.session import SessionServices, run_game_session
from game.ui import desenhar_botao_pausa as _desenhar_botao_pausa
from game.ui import desenhar_tela_jogo, texto_com_borda
from game.screens import (
    tela_boas_vindas as _tela_boas_vindas,
    tela_comandos as _tela_comandos,
    tela_ranking as _tela_ranking,
    tela_conquistas as _tela_conquistas,
    tela_selecao_modo as _tela_selecao_modo,
    tela_intro_fase as _tela_intro_fase,
    tela_vitoria as _tela_vitoria,
    tela_game_over as _tela_game_over,
    tela_pos_fase as _tela_pos_fase,
    tela_selecao_nave as _tela_selecao_nave,
    tela_melhorias as _tela_melhorias,
    tela_selecao_fase as _tela_selecao_fase,
)
from salvamento import carregar_dados, normalizar_dados_jogador, salvar_dados, salvar_pontuacao, listar_ranking

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def resolver_caminho_arquivo(nome_arquivo):
    if not nome_arquivo:
        return nome_arquivo
    if os.path.isabs(nome_arquivo):
        return nome_arquivo
    return os.path.join(BASE_DIR, nome_arquivo)


def validar_dados_jogador(dados_jogador):
    return normalizar_dados_jogador(dados_jogador)


LARGURA = config.LARGURA
ALTURA = config.ALTURA
recursos_jogo = None
tela = None
modo_tela = None
relogio = None
fonte_titulo = None
fonte_texto = None
fonte_hud = None
fundo_img = None
fundo_infinito = None
fundo_fase_1 = None
fundo_fase_2 = None
fundo_fase_3 = None
fundo_fase_4 = None
fundos_fases = ()
fundos_habitat = {}
fundo_caminhos = None
fundo_selecao = None
fundo_fim = None


def inicializar_app():
    global ALTURA, LARGURA, fundo_fase_1, fundo_fase_2, fundo_fase_3
    global fundo_caminhos, fundo_fase_4, fundo_fim, fundo_img, fundo_infinito
    global fundo_selecao, fundos_habitat, fundos_fases
    global fonte_hud, fonte_texto, fonte_titulo, modo_tela, recursos_jogo
    global relogio, tela

    if recursos_jogo is None:
        recursos_jogo = criar_recursos_jogo(resolver_caminho_arquivo)

    tela = recursos_jogo.tela
    modo_tela = recursos_jogo.modo_tela
    relogio = recursos_jogo.relogio
    fonte_titulo, fonte_texto, fonte_hud = recursos_jogo.fontes
    fundo_img = recursos_jogo.fundo_img
    fundo_infinito = recursos_jogo.fundo_infinito
    fundos_fases = recursos_jogo.fundos_fase
    fundo_fase_1, fundo_fase_2, fundo_fase_3, fundo_fase_4 = fundos_fases[:4]
    fundos_habitat = recursos_jogo.fundos_habitat
    fundo_caminhos = recursos_jogo.fundo_caminhos
    fundo_selecao = recursos_jogo.fundo_selecao
    fundo_fim = recursos_jogo.fundo_fim
    LARGURA, ALTURA = tela.get_size()
    config.LARGURA, config.ALTURA = LARGURA, ALTURA
    return recursos_jogo


def atualizar_tamanho_tela(evento=None):
    global LARGURA, ALTURA
    global tela
    if evento is not None:
        if modo_tela is None:
            raise RuntimeError("Chame inicializar_app() antes de processar eventos da tela.")
        tela = modo_tela.handle_event(evento)
        LARGURA, ALTURA = tela.get_size()
        config.LARGURA, config.ALTURA = LARGURA, ALTURA
    return LARGURA, ALTURA

def desenhar_botao_pausa(tela_surface, rect, texto, ativo=False):
    _desenhar_botao_pausa(tela_surface, rect, texto, fonte_hud, ativo)


def gerar_som_inicio_fase(fase_atual):
    frequencias_por_fase = {
        1: [220, 330],
        2: [330, 440],
        3: [440, 660],
    }
    notas = frequencias_por_fase.get(fase_atual, [300, 450])
    tocar_som(notas, duracao=0.7, volume=0.25)


def criar_asteroides_iniciais(fase_atual=1, modo_frota=False):
    asteroides = pygame.sprite.Group()
    if modo_frota:
        return asteroides

    qtd_asteroides = 4 + fase_atual
    for _ in range(qtd_asteroides):
        ast = Asteroide(fase_atual)
        ast.velocidadey = max(1, ast.velocidadey - 2 + fase_atual)
        asteroides.add(ast)

    return asteroides


def criar_asteroides_infinito(pontos=0, fase_atual=1, quantidade_minima=8):
    quantidade = max(quantidade_minima, 8 + min(18, pontos // 90) + fase_atual)
    asteroides = pygame.sprite.Group()

    for _ in range(quantidade):
        ast = Asteroide(fase_atual)
        ast.velocidadey = max(2, ast.velocidadey + min(6, pontos // 180))
        ast.velocidadex = random.randint(-2, 2)
        ast.rect.x = random.randint(0, config.LARGURA - ast.tamanho)
        ast.rect.y = random.randint(-120, -30)
        asteroides.add(ast)

    return asteroides


def calcular_dano_asteroide(modo_jogo="asteroides"):
    if modo_jogo == "infinito":
        return 10
    return 20


def calcular_duracao_especial_titan(nivel=1):
    frames = 36 + max(0, nivel - 1) * 12
    return frames / FPS

def tela_boas_vindas():
    _tela_boas_vindas(
        tela, relogio, (fonte_titulo, fonte_texto, fonte_hud), fundo_img,
        atualizar_tamanho_tela, tela_comandos, tela_ranking,
        lambda: tela_conquistas(dados_jogador),
    )


def tela_ranking():
    _tela_ranking(
        tela, relogio, (fonte_titulo, fonte_texto, fonte_hud), fundo_img,
        atualizar_tamanho_tela, listar_ranking,
    )


def tela_conquistas(dados_jogador):
    _tela_conquistas(
        dados_jogador, tela, relogio, (fonte_titulo, fonte_texto, fonte_hud),
        fundo_img, atualizar_tamanho_tela, listar_conquistas,
    )


def tela_comandos():
    _tela_comandos(
        tela, relogio, (fonte_titulo, fonte_texto, fonte_hud), fundo_img,
        atualizar_tamanho_tela,
    )

def tela_selecao_modo():
    return _tela_selecao_modo(
        tela, relogio, (fonte_titulo, fonte_texto, fonte_hud), fundo_selecao,
        atualizar_tamanho_tela,
    )


def tela_selecao_fase(modo_jogo, dados_jogador, arquivo_nave="Vanguard.png"):
    return _tela_selecao_fase(
        modo_jogo, dados_jogador["fases_desbloqueadas"], tela, relogio,
        (fonte_titulo, fonte_texto, fonte_hud), _fundos_da_nave(arquivo_nave),
        atualizar_tamanho_tela, arquivo_nave,
        dados_jogador["recompensas_pendentes"],
        dados_jogador["recompensas_resgatadas"],
    )


def tela_selecao_nave(dados_jogador):
    return _tela_selecao_nave(
        dados_jogador, tela, relogio, (fonte_titulo, fonte_texto, fonte_hud),
        fundo_selecao, atualizar_tamanho_tela, resolver_caminho_arquivo,
        validar_dados_jogador, salvar_dados,
    )

def tela_melhorias(dados_jogador):
    _tela_melhorias(
        dados_jogador, tela, relogio, (fonte_titulo, fonte_texto, fonte_hud),
        fundo_selecao, atualizar_tamanho_tela, validar_dados_jogador,
        salvar_dados, calcular_duracao_especial_titan,
    )


def _fundos_da_nave(arquivo_nave):
    fundo_habitat = fundos_habitat.get(obter_habitat(arquivo_nave)["fundo"])
    return fundos_para_habitat(arquivo_nave, fundos_fases, fundo_habitat)


def jogo_principal(
    arquivo_nave,
    niveis_melhorias,
    fase_atual=1,
    modo_jogo="asteroides",
    dados_jogador=None,
):
    fundos_fase = _fundos_da_nave(arquivo_nave)
    services = SessionServices(
        get_screen=pygame.display.get_surface,
        clock=relogio,
        fonts=(fonte_titulo, fonte_texto, fonte_hud),
        backgrounds=fundos_fase,
        infinite_background=fundo_infinito,
        resize_display=atualizar_tamanho_tela,
        create_initial_asteroids=criar_asteroides_iniciais,
        create_infinite_asteroids=criar_asteroides_infinito,
        asteroid_damage=calcular_dano_asteroide,
        save_player=salvar_dados,
        play_sound=tocar_som,
    )
    return run_game_session(
        arquivo_nave,
        niveis_melhorias,
        fase_atual,
        modo_jogo,
        dados_jogador,
        services=services,
    )


def tela_intro_fase(fase_atual, arquivo_nave="Vanguard.png"):
    habitat = obter_habitat(arquivo_nave)
    _tela_intro_fase(
        fase_atual, tela, relogio, (fonte_titulo, fonte_texto, fonte_hud),
        _fundos_da_nave(arquivo_nave),
        atualizar_tamanho_tela, gerar_som_inicio_fase, habitat["nome"],
    )


def tela_vitoria(pontos, moedas, modo_jogo="asteroides", nave_escolhida="Vanguard.png"):
    _tela_vitoria(
        pontos, moedas, modo_jogo, nave_escolhida, tela, relogio,
        (fonte_titulo, fonte_texto, fonte_hud), fundo_img,
        atualizar_tamanho_tela, salvar_pontuacao, listar_ranking,
    )


def tela_pos_fase(fase_atual, pontos, moedas, recompensa_pendente=None):
    return _tela_pos_fase(
        fase_atual, pontos, moedas, recompensa_pendente,
        tela, relogio, (fonte_titulo, fonte_texto, fonte_hud), fundo_img,
        atualizar_tamanho_tela,
    )


def tela_game_over(pontos, moedas, modo_jogo="asteroides", nave_escolhida="Vanguard.png"):
    _tela_game_over(
        pontos, moedas, modo_jogo, nave_escolhida, tela, relogio,
        (fonte_titulo, fonte_texto, fonte_hud), fundo_fim,
        atualizar_tamanho_tela, salvar_pontuacao, listar_ranking,
    )


def tela_conquistas(dados_jogador):
    _tela_conquistas(
        dados_jogador, tela, relogio, (fonte_titulo, fonte_texto, fonte_hud),
        fundo_img, atualizar_tamanho_tela, listar_conquistas,
    )


if __name__ == "__main__":
    inicializar_app()
    dados_jogador = validar_dados_jogador(carregar_dados())
    
    while True:
        tela_boas_vindas()
        while True:
            modo_jogo = tela_selecao_modo()
            nave_escolhida = tela_selecao_nave(dados_jogador)
            if modo_jogo == "infinito":
                fase_escolhida = 1
                break
            fase_escolhida = tela_selecao_fase(
                modo_jogo, dados_jogador, nave_escolhida,
            )
            if fase_escolhida is not None:
                break
        tela_melhorias(dados_jogador)

        pontos_totais = 0
        moedas_totais = 0
        fase_atual = fase_escolhida
        venceu = False

        if modo_jogo == "infinito":
            pontos_partida, moedas_partida, venceu, abandonada = jogo_principal(
                nave_escolhida,
                dados_jogador["niveis_melhorias"],
                fase_atual,
                modo_jogo,
                dados_jogador,
            )
            pontos_totais += pontos_partida
            moedas_totais += moedas_partida
            dados_jogador["moedas"] += moedas_partida
            salvar_dados(dados_jogador)
            if not abandonada:
                tela_game_over(pontos_totais, moedas_totais, modo_jogo, nave_escolhida)
            continue

        sair_campanha = False
        while fase_atual <= MAX_FASES_CAMPANHA:
            tela_intro_fase(fase_atual, nave_escolhida)
            pontos_partida, moedas_partida, venceu, abandonada = jogo_principal(
                nave_escolhida,
                dados_jogador["niveis_melhorias"],
                fase_atual,
                modo_jogo,
                dados_jogador,
            )

            pontos_totais += pontos_partida
            moedas_totais += moedas_partida

            dados_jogador["moedas"] += moedas_partida

            if abandonada:
                salvar_dados(dados_jogador)
                break

            if not venceu:
                salvar_dados(dados_jogador)
                tela_game_over(pontos_totais, moedas_totais, modo_jogo, nave_escolhida)
                break

            registrar_fase_concluida(dados_jogador, modo_jogo, fase_atual)
            salvar_dados(dados_jogador)

            while True:
                recompensa_pendente = next(
                    (
                        recompensa_id
                        for recompensa_id in dados_jogador["recompensas_pendentes"]
                        if recompensa_id in RECOMPENSAS_POR_ID
                    ),
                    None,
                )
                acao = tela_pos_fase(
                    fase_atual,
                    pontos_totais,
                    moedas_totais,
                    recompensa_pendente,
                )
                if acao == "resgatar":
                    if recompensa_pendente is None or not resgatar_recompensa(
                        dados_jogador, recompensa_pendente,
                    ):
                        raise RuntimeError("A recompensa selecionada não está disponível.")
                    salvar_dados(dados_jogador)
                    continue
                if acao == "avancar" and fase_atual < MAX_FASES_CAMPANHA:
                    fase_atual += 1
                    break
                salvar_pontuacao(pontos_totais, modo_jogo, nave_escolhida)
                sair_campanha = True
                break
            if sair_campanha:
                break
