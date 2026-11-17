import pygame
import sys

from config import AMARELO, AZUL_NEON, BRANCO, VERMELHO
from game.rewards import RECOMPENSAS_POR_ID
from game.screens_common import (
    _centralizar,
    _desenhar_fundo,
    animar_transicao,
    texto_com_borda,
)



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
    modo_jogo,
    nave_escolhida,
):
    fonte_titulo, fonte_texto, fonte_hud = fontes
    ranking = [
        item
        for item in listar_ranking(100)
        if item["modo"] == modo_jogo and item["nave"] == nave_escolhida
    ][:5]
    rodando = True
    animar_entrada = True
    while rodando:
        relogio.tick(60)
        _desenhar_fundo(tela, fundo)
        _centralizar(tela, texto_com_borda(fonte_titulo, titulo, cor_titulo), y_titulo)
        _centralizar(tela, texto_com_borda(fonte_texto, frase, BRANCO), y_frase)
        _centralizar(tela, texto_com_borda(fonte_texto, f"{rotulo_pontuacao}: {pontos}", BRANCO), y_pontuacao)
        _centralizar(tela, texto_com_borda(fonte_texto, f"Moedas Coletadas: {moedas} 🪙", AMARELO), y_moedas)
        _centralizar(
            tela,
            texto_com_borda(fonte_hud, "RECORDE DESTE MODO E NAVE", AMARELO),
            y_ranking,
        )
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
        if animar_entrada:
            animar_transicao(tela, relogio)
            animar_entrada = False
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
                animar_transicao(tela, relogio, entrada=False)
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
        modo_jogo, nave_escolhida,
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
        modo_jogo, nave_escolhida,
    )


def tela_pos_fase(
    fase_atual,
    pontos,
    moedas,
    recompensa_pendente,
    tela,
    relogio,
    fontes,
    fundo,
    atualizar_tamanho_tela,
):
    _, fonte_texto, fonte_hud = fontes
    opcoes = [("sair", "Sair")]
    if fase_atual < 10:
        opcoes.append(("avancar", f"Avançar para a fase {fase_atual + 1}"))
    if recompensa_pendente is not None:
        recompensa = RECOMPENSAS_POR_ID[recompensa_pendente]
        opcoes.append(("resgatar", f"Resgatar recompensa: {recompensa['nome']}"))

    indice = next(
        (i for i, (acao, _) in enumerate(opcoes) if acao == "avancar"),
        0,
    )
    animar_entrada = True
    while True:
        relogio.tick(60)
        _desenhar_fundo(tela, fundo)
        _centralizar(
            tela,
            texto_com_borda(fonte_hud, f"FASE {fase_atual} CONCLUÍDA", AMARELO),
            110,
        )
        _centralizar(
            tela,
            texto_com_borda(fonte_texto, f"Pontuação da campanha: {pontos}", BRANCO),
            155,
        )
        _centralizar(
            tela,
            texto_com_borda(fonte_texto, f"Moedas coletadas: {moedas}", BRANCO),
            185,
        )
        if recompensa_pendente is not None:
            recompensa = RECOMPENSAS_POR_ID[recompensa_pendente]
            _centralizar(
                tela,
                texto_com_borda(
                    fonte_hud,
                    f"RECOMPENSA DISPONÍVEL: {recompensa['nome']}",
                    AMARELO,
                ),
                235,
            )

        botoes = []
        for posicao, (_, rotulo) in enumerate(opcoes):
            rect = pygame.Rect(tela.get_width() // 2 - 200, 300 + posicao * 58, 400, 46)
            selecionada = posicao == indice
            pygame.draw.rect(
                tela,
                (25, 45, 65) if selecionada else (18, 25, 35),
                rect,
                border_radius=10,
            )
            pygame.draw.rect(
                tela,
                AMARELO if selecionada else AZUL_NEON,
                rect,
                2,
                border_radius=10,
            )
            texto = texto_com_borda(fonte_texto, rotulo, BRANCO)
            tela.blit(
                texto,
                (rect.centerx - texto.get_width() // 2, rect.centery - texto.get_height() // 2),
            )
            botoes.append(rect)

        if animar_entrada:
            animar_transicao(tela, relogio)
            animar_entrada = False
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.VIDEORESIZE or (
                evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11
            ):
                atualizar_tamanho_tela(evento)
            if evento.type == pygame.MOUSEMOTION:
                for posicao, rect in enumerate(botoes):
                    if rect.collidepoint(evento.pos):
                        indice = posicao
                        break
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for posicao, rect in enumerate(botoes):
                    if rect.collidepoint(evento.pos):
                        animar_transicao(tela, relogio, entrada=False)
                        return opcoes[posicao][0]
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_UP, pygame.K_w):
                    indice = (indice - 1) % len(opcoes)
                elif evento.key in (pygame.K_DOWN, pygame.K_s):
                    indice = (indice + 1) % len(opcoes)
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    animar_transicao(tela, relogio, entrada=False)
                    return opcoes[indice][0]
