import pygame
import sys

from config import AMARELO, AZUL_NEON, BRANCO, VERMELHO
from game.screens_common import _centralizar, _desenhar_fundo, texto_com_borda



def tela_boas_vindas(
    tela,
    relogio,
    fontes,
    fundo,
    atualizar_tamanho_tela,
    abrir_comandos,
    abrir_ranking,
    abrir_conquistas,
):
    fonte_titulo, fonte_texto, fonte_hud = fontes
    rodando = True
    while rodando:
        relogio.tick(60)
        _desenhar_fundo(tela, fundo)

        mensagens = (
            (fonte_titulo, "SOLDADO CÓSMICO", AZUL_NEON, 160),
            (fonte_texto, "Olá, soldado cósmico. A Terra está sendo ameaçada", BRANCO, 230),
            (fonte_texto, "por asteroides, precisamos impedir que isso aconteça!", BRANCO, 260),
            (fonte_hud, "[ENTER] - Iniciar Missão", AMARELO, 350),
            (fonte_hud, "[C] - Ver Comandos / Teclas", BRANCO, 390),
            (fonte_hud, "[R] - Ver Ranking", AZUL_NEON, 430),
            (fonte_hud, "[F11] - Alternar tela cheia", BRANCO, 470),
            (fonte_hud, "[A] - Ver Conquistas", AMARELO, 510),
        )
        for fonte, texto, cor, y in mensagens:
            _centralizar(tela, texto_com_borda(fonte, texto, cor), y)

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.VIDEORESIZE or (
                evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11
            ):
                atualizar_tamanho_tela(evento)
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    rodando = False
                elif evento.key == pygame.K_c:
                    abrir_comandos()
                elif evento.key == pygame.K_r:
                    abrir_ranking()
                elif evento.key == pygame.K_a:
                    abrir_conquistas()

def tela_ranking(tela, relogio, fontes, fundo, atualizar_tamanho_tela, listar_ranking):
    fonte_titulo, _, fonte_hud = fontes
    rodando = True
    while rodando:
        relogio.tick(60)
        _desenhar_fundo(tela, fundo)

        _centralizar(tela, texto_com_borda(fonte_titulo, "RANKING FINAL", AMARELO), 60)
        ranking = listar_ranking(10)
        painel = pygame.Surface((700, 420), pygame.SRCALPHA)
        painel.fill((15, 18, 28, 180))
        tela.blit(painel, (tela.get_width() // 2 - 350, 110))

        if not ranking:
            _centralizar(
                tela,
                texto_com_borda(fonte_hud, "Nenhuma pontuação registrada ainda.", BRANCO),
                260,
            )
        else:
            for idx, item in enumerate(ranking, start=1):
                texto_linha = texto_com_borda(
                    fonte_hud,
                    f"{idx}. {item['pontuacao']} pts  |  {item['modo']}  |  {item['nave']}  |  {item['data']}",
                    BRANCO if idx % 2 == 1 else AMARELO,
                )
                _centralizar(tela, texto_linha, 150 + (idx - 1) * 32)

        _centralizar(
            tela,
            texto_com_borda(fonte_hud, "Pressione [ESC] ou [ENTER] para voltar", AZUL_NEON),
            520,
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
            if evento.type == pygame.KEYDOWN and evento.key in (
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
                pygame.K_ESCAPE,
            ):
                rodando = False

def tela_comandos(tela, relogio, fontes, fundo, atualizar_tamanho_tela):
    fonte_titulo, fonte_texto, fonte_hud = fontes
    rodando = True
    while rodando:
        relogio.tick(60)
        _desenhar_fundo(tela, fundo)

        _centralizar(tela, texto_com_borda(fonte_titulo, "PAINEL DE COMANDOS", AZUL_NEON), 70)
        comandos = (
            ("• [Q / E] : Gira a nave para a esquerda e para a direita", BRANCO),
            ("• [CIMA] ou [W] : Acelera a nave para frente", BRANCO),
            ("• [J] (Segurar) : Dispara tiros normais contínuos", AMARELO),
            ("• [K] : Dispara o Tiro Especial (quando a barra encher)", AZUL_NEON),
            ("• [R] : Abre o ranking final", AMARELO),
            ("• [ESC] / Fechar : Sai do jogo", VERMELHO),
            ("• [F11] : Alterna entre janela e tela cheia", AZUL_NEON),
        )
        for indice, (texto, cor) in enumerate(comandos):
            tela.blit(texto_com_borda(fonte_texto, texto, cor), (40, 160 + indice * 50))

        _centralizar(
            tela,
            texto_com_borda(fonte_hud, "Pressione [ESC] ou [ENTER] para voltar", AMARELO),
            500,
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
            if evento.type == pygame.KEYDOWN and evento.key in (
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
                pygame.K_ESCAPE,
            ):
                rodando = False

def tela_selecao_modo(tela, relogio, fontes, fundo, atualizar_tamanho_tela):
    fonte_titulo, fonte_texto, fonte_hud = fontes
    opcoes = [
        {"nome": "ASTEROIDES", "valor": "asteroides", "descricao": "Missão clássica contra meteoros e obstáculos."},
        {"nome": "FROTA INIMIGA", "valor": "frota_inimiga", "descricao": "Modo de combate direto contra naves inimigas."},
        {"nome": "INFINITO", "valor": "infinito", "descricao": "Sobreviva o máximo de tempo e marque a maior pontuação possível."},
    ]
    indice = 0
    while True:
        relogio.tick(60)
        _desenhar_fundo(tela, fundo)

        _centralizar(tela, texto_com_borda(fonte_titulo, "SELEÇÃO DE MODO", AZUL_NEON), 50)
        for idx, opcao in enumerate(opcoes):
            offset = idx - (len(opcoes) - 1) / 2
            x = tela.get_width() // 2 + offset * 240
            y, largura, altura = 240, 200, 180
            selecionado = idx == indice
            cor = AMARELO if selecionado else AZUL_NEON
            rect = pygame.Rect(x - largura // 2, y, largura, altura)
            pygame.draw.rect(tela, (18, 22, 30), rect, border_radius=18)
            pygame.draw.rect(tela, cor, rect, 3 if selecionado else 1, border_radius=18)

            nome = texto_com_borda(fonte_hud, opcao["nome"], AMARELO if selecionado else BRANCO)
            descricao = texto_com_borda(fonte_texto, opcao["descricao"], BRANCO)
            tela.blit(nome, (x - nome.get_width() // 2, y + 40))
            tela.blit(descricao, (x - descricao.get_width() // 2, y + 90))

        _centralizar(
            tela,
            texto_com_borda(
                fonte_hud,
                "Use [← / →] ou [A / D] para escolher | [ENTER] para confirmar",
                BRANCO,
            ),
            500,
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
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_LEFT, pygame.K_a):
                    indice = (indice - 1) % len(opcoes)
                elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                    indice = (indice + 1) % len(opcoes)
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return opcoes[indice]["valor"]

def tela_intro_fase(
    fase_atual,
    tela,
    relogio,
    fontes,
    fundos_fase,
    atualizar_tamanho_tela,
    gerar_som_inicio_fase,
):
    fonte_titulo, fonte_texto, fonte_hud = fontes
    gerar_som_inicio_fase(fase_atual)
    inicio = pygame.time.get_ticks()
    duracao_intro = 5000
    mensagens = {
        1: "A borda do setor está infestada. Prepare-se para romper as linhas inimigas.",
        2: "O campo foi reforçado. Asteroides maiores e mais agressivos surgem do vazio.",
        3: "Último bastião da rota. A frota inimiga se concentra em um ataque final.",
        4: "A névoa de fogo do setor final está ativa. O último empurrão será decisivo.",
    }
    cores_fase = {
        1: AZUL_NEON,
        2: AMARELO,
        3: VERMELHO,
        4: (255, 120, 40),
    }

    while True:
        tempo_decorrido = pygame.time.get_ticks() - inicio
        if tempo_decorrido >= duracao_intro:
            return

        relogio.tick(60)
        indice_fundo = fase_atual - 1 if fase_atual in (1, 2, 3) else 3
        fundo = fundos_fase[indice_fundo]
        _desenhar_fundo(tela, fundo)

        transicao = min(255, max(0, int((tempo_decorrido / 1200) * 255)))
        fade_saida = min(255, max(0, int(((duracao_intro - tempo_decorrido) / 1200) * 255)))
        overlay = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        overlay.fill((8, 12, 20, min(transicao, fade_saida)))
        tela.blit(overlay, (0, 0))

        painel = pygame.Surface((620, 230), pygame.SRCALPHA)
        painel.fill((15, 18, 28, 180))
        tela.blit(painel, (tela.get_width() // 2 - 310, 110))

        titulo = texto_com_borda(fonte_titulo, f"FASE {fase_atual}", cores_fase.get(fase_atual, AZUL_NEON))
        mensagem = texto_com_borda(
            fonte_texto,
            mensagens.get(fase_atual, "Atenção: novos inimigos se aproximam."),
            BRANCO,
        )
        segundos = max(1, int((duracao_intro - tempo_decorrido) / 1000) + 1)
        contador = texto_com_borda(fonte_hud, f"Início em {segundos}s", AMARELO)
        _centralizar(tela, titulo, 150)
        _centralizar(tela, mensagem, 240)
        _centralizar(tela, contador, 305)
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.VIDEORESIZE or (
                evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11
            ):
                atualizar_tamanho_tela(evento)
