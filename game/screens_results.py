import pygame
import sys

from config import AMARELO, AZUL_NEON, BRANCO, VERMELHO
from game.screens_common import _centralizar, _desenhar_fundo, texto_com_borda



def _tela_resultado(
    titulo,
    cor_titulo,
    frase,
    rotulo_pontuacao,
    y_titulo,
    y_frase,
    y_pontuacao,
    y_moedas,
    y_ranking,
    y_linhas,
    y_continuar,
    fundo,
    pontos,
    moedas,
    relogio,
    tela,
    fontes,
    atualizar_tamanho_tela,
    listar_ranking,
):
    fonte_titulo, fonte_texto, fonte_hud = fontes
    ranking = listar_ranking(5)
    rodando = True
    while rodando:
        relogio.tick(60)
        _desenhar_fundo(tela, fundo)
        _centralizar(tela, texto_com_borda(fonte_titulo, titulo, cor_titulo), y_titulo)
        _centralizar(tela, texto_com_borda(fonte_texto, frase, BRANCO), y_frase)
        _centralizar(tela, texto_com_borda(fonte_texto, f"{rotulo_pontuacao}: {pontos}", BRANCO), y_pontuacao)
        _centralizar(tela, texto_com_borda(fonte_texto, f"Moedas Coletadas: {moedas} 🪙", AMARELO), y_moedas)
        _centralizar(tela, texto_com_borda(fonte_hud, "TOP 5", AMARELO), y_ranking)
        for idx, item in enumerate(ranking[:5], start=1):
            linha = texto_com_borda(
                fonte_texto,
                f"{idx}. {item['pontuacao']} - {item['modo']} - {item['nave']}",
                BRANCO,
            )
            _centralizar(tela, linha, y_linhas + (idx - 1) * 22)
        _centralizar(
            tela,
            texto_com_borda(fonte_hud, "Pressione [ENTER] para voltar ao Hangar", AZUL_NEON),
            y_continuar,
        )
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.VIDEORESIZE or (
                evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11
            ):
                atualizar_tamanho_tela(evento)
            if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                rodando = False

def tela_vitoria(
    pontos,
    moedas,
    modo_jogo,
    nave_escolhida,
    tela,
    relogio,
    fontes,
    fundo,
    atualizar_tamanho_tela,
    salvar_pontuacao,
    listar_ranking,
):
    salvar_pontuacao(pontos, modo_jogo, nave_escolhida)
    _tela_resultado(
        "FASE CONCLUÍDA!", AMARELO,
        "Parabéns, soldado! Você limpou o setor de asteroides.",
        "Pontuação", 140, 210, 290, 325, 360, 390, 520,
        fundo, pontos, moedas, relogio, tela, fontes,
        atualizar_tamanho_tela, listar_ranking,
    )

def tela_game_over(
    pontos,
    moedas,
    modo_jogo,
    nave_escolhida,
    tela,
    relogio,
    fontes,
    fundo,
    atualizar_tamanho_tela,
    salvar_pontuacao,
    listar_ranking,
):
    salvar_pontuacao(pontos, modo_jogo, nave_escolhida)
    _tela_resultado(
        "FIM DE JOGO", VERMELHO,
        '"A frota caiu, mas a lenda do Soldado Cósmico nunca morre!"',
        "Pontuação Final", 110, 180, 250, 285, 330, 360, 500,
        fundo, pontos, moedas, relogio, tela, fontes,
        atualizar_tamanho_tela, listar_ranking,
    )
