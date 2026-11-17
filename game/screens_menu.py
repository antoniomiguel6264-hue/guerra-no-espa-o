import pygame
import sys

from config import AMARELO, AZUL_NEON, BRANCO, CINZA, VERMELHO
from game.habitats import obter_habitat
from game.screens_common import (
    _centralizar,
    _desenhar_fundo,
    animar_transicao,
    texto_com_borda,
)
from game.rewards import MAX_FASES_CAMPANHA, RECOMPENSAS_POR_MARCO



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
    animar_entrada = True
    while rodando:
        relogio.tick(60)
        tela.fill((5, 12, 30))

        mensagens = (
            (fonte_titulo, "SOLDADO CÓSMICO", AZUL_NEON, 160),
            (fonte_texto, "Olá, soldado cósmico. A Terra está sendo ameaçada", (175, 207, 238), 230),
            (fonte_texto, "por asteroides, precisamos impedir que isso aconteça!", (175, 207, 238), 260),
            (fonte_hud, "[ENTER] - Iniciar Missão", (105, 190, 255), 350),
            (fonte_hud, "[C] - Ver Comandos / Teclas", (145, 185, 225), 390),
            (fonte_hud, "[R] - Ver Ranking", AZUL_NEON, 430),
            (fonte_hud, "[F11] - Alternar tela cheia", (145, 185, 225), 470),
            (fonte_hud, "[A] - Ver Conquistas", (105, 190, 255), 510),
        )
        for fonte, texto, cor, y in mensagens:
            _centralizar(tela, texto_com_borda(fonte, texto, cor), y)

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
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    animar_transicao(tela, relogio, entrada=False)
                    rodando = False
                elif evento.key == pygame.K_c:
                    animar_transicao(tela, relogio, entrada=False)
                    abrir_comandos()
                    animar_entrada = True
                elif evento.key == pygame.K_r:
                    animar_transicao(tela, relogio, entrada=False)
                    abrir_ranking()
                    animar_entrada = True
                elif evento.key == pygame.K_a:
                    animar_transicao(tela, relogio, entrada=False)
                    abrir_conquistas()
                    animar_entrada = True

def tela_ranking(tela, relogio, fontes, fundo, atualizar_tamanho_tela, listar_ranking):
    fonte_titulo, _, fonte_hud = fontes
    rodando = True
    animar_entrada = True
    while rodando:
        relogio.tick(60)
        _desenhar_fundo(tela, fundo)

        _centralizar(tela, texto_com_borda(fonte_titulo, "RECORDES POR MODO E NAVE", AMARELO), 60)
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
            if evento.type == pygame.KEYDOWN and evento.key in (
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
                pygame.K_ESCAPE,
            ):
                animar_transicao(tela, relogio, entrada=False)
                rodando = False

def tela_comandos(tela, relogio, fontes, fundo, atualizar_tamanho_tela):
    fonte_titulo, fonte_texto, fonte_hud = fontes
    rodando = True
    animar_entrada = True
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
            if evento.type == pygame.KEYDOWN and evento.key in (
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
                pygame.K_ESCAPE,
            ):
                animar_transicao(tela, relogio, entrada=False)
                rodando = False

def tela_selecao_modo(tela, relogio, fontes, fundo, atualizar_tamanho_tela):
    fonte_titulo, fonte_texto, fonte_hud = fontes
    opcoes = [
        {"nome": "ASTEROIDES", "valor": "asteroides", "descricao": "Fases e chefes"},
        {"nome": "FROTA INIMIGA", "valor": "frota_inimiga", "descricao": "Batalha contra naves"},
        {"nome": "INFINITO", "valor": "infinito", "descricao": "Sobreviva e pontue"},
    ]
    indice = 0
    animar_entrada = True
    while True:
        relogio.tick(60)
        _desenhar_fundo(tela, fundo)

        _centralizar(tela, texto_com_borda(fonte_titulo, "ESCOLHA O MODO", AZUL_NEON), 70)
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
                "← → / A D   •   ENTER escolher",
                BRANCO,
            ),
            500,
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
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_LEFT, pygame.K_a):
                    indice = (indice - 1) % len(opcoes)
                elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                    indice = (indice + 1) % len(opcoes)
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    animar_transicao(tela, relogio, entrada=False)
                    return opcoes[indice]["valor"]


def tela_selecao_fase(
    modo_jogo,
    fases_desbloqueadas,
    tela,
    relogio,
    fontes,
    fundo,
    atualizar_tamanho_tela,
    arquivo_nave="Vanguard.png",
    recompensas_pendentes=(),
    recompensas_resgatadas=(),
):
    fonte_titulo, fonte_texto, fonte_hud = fontes
    habitat = obter_habitat(arquivo_nave)
    fase_maxima = min(
        MAX_FASES_CAMPANHA,
        max(1, int(fases_desbloqueadas.get(modo_jogo, 1))),
    )
    fase_selecionada = 1
    inicio_lista = 0
    fases_visiveis = 5
    quantidade_fases = MAX_FASES_CAMPANHA
    animar_entrada = True
    nomes_modo = {
        "asteroides": "ASTEROIDES",
        "frota_inimiga": "FROTA INIMIGA",
    }

    while True:
        relogio.tick(60)
        fundo_atual = fundo[fase_selecionada - 1] if isinstance(fundo, (tuple, list)) else fundo
        _desenhar_fundo(tela, fundo_atual)
        largura, altura = tela.get_size()
        centro_x = largura // 2
        amplitude = min(170, largura * 0.22)
        topo = 160
        passo_y = min(84, max(58, (altura - 260) / (fases_visiveis - 1)))
        fases_na_tela = range(
            inicio_lista + 1,
            min(quantidade_fases, inicio_lista + fases_visiveis) + 1,
        )
        posicoes = {
            fase: (
                round(centro_x + (amplitude if fase % 2 == 0 else -amplitude)),
                round(topo + (fase - inicio_lista - 1) * passo_y),
            )
            for fase in fases_na_tela
        }

        _centralizar(
            tela,
            texto_com_borda(fonte_titulo, "TRILHA DE FASES", AZUL_NEON),
            35,
        )
        _centralizar(
            tela,
            texto_com_borda(fonte_hud, nomes_modo.get(modo_jogo, modo_jogo.upper()), AMARELO),
            85,
        )
        _centralizar(
            tela,
            texto_com_borda(fonte_texto, f"HABITAT: {habitat['nome']}", BRANCO),
            112,
        )

        for fase in fases_na_tela:
            if fase + 1 not in posicoes:
                continue
            cor_trilha = AZUL_NEON if fase + 1 <= fase_maxima else (55, 65, 78)
            pygame.draw.line(tela, cor_trilha, posicoes[fase], posicoes[fase + 1], 6)

        for indice, posicao in posicoes.items():
            desbloqueada = indice <= fase_maxima
            selecionada = indice == fase_selecionada
            cor = AMARELO if selecionada and desbloqueada else (
                AZUL_NEON if desbloqueada else CINZA
            )
            raio = 31 if selecionada else 27
            pygame.draw.circle(tela, (17, 23, 32), posicao, raio)
            pygame.draw.circle(tela, cor, posicao, raio, 3 if selecionada else 2)
            rotulo = f"{indice}" if desbloqueada else "X"
            texto_no = texto_com_borda(
                fonte_hud,
                rotulo,
                cor,
            )
            tela.blit(
                texto_no,
                (posicao[0] - texto_no.get_width() // 2, posicao[1] - texto_no.get_height() // 2),
            )
            recompensa_marco = RECOMPENSAS_POR_MARCO.get(indice)
            if recompensa_marco is not None and recompensa_marco["id"] in recompensas_pendentes:
                texto_status = "RECOMPENSA PENDENTE"
            elif recompensa_marco is not None and recompensa_marco["id"] in recompensas_resgatadas:
                texto_status = "RECOMPENSA RESGATADA"
            elif desbloqueada:
                texto_status = "DISPONÍVEL"
            else:
                texto_status = "BLOQUEADA"
            texto_fase = texto_com_borda(
                fonte_texto,
                f"FASE {indice}  ·  {texto_status}",
                AMARELO if texto_status == "RECOMPENSA PENDENTE" else (
                    BRANCO if desbloqueada else CINZA
                ),
            )
            tela.blit(
                texto_fase,
                (posicao[0] - texto_fase.get_width() // 2, posicao[1] + 38),
            )

        _centralizar(
            tela,
            texto_com_borda(
                fonte_hud,
                "↑ / ↓ ou roda do mouse   ·   ENTER iniciar   ·   ESC voltar",
                BRANCO,
            ),
            altura - 48,
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
            if evento.type == pygame.MOUSEMOTION:
                for indice, posicao in posicoes.items():
                    if pygame.Vector2(evento.pos).distance_to(posicao) <= 34:
                        fase_selecionada = indice
                        break
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for indice, posicao in posicoes.items():
                    if pygame.Vector2(evento.pos).distance_to(posicao) <= 34:
                        fase_selecionada = indice
                        if indice <= fase_maxima:
                            animar_transicao(tela, relogio, entrada=False)
                            return indice
                        break
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_UP, pygame.K_w):
                    fase_selecionada = max(1, fase_selecionada - 1)
                elif evento.key in (pygame.K_DOWN, pygame.K_s):
                    fase_selecionada = min(quantidade_fases, fase_selecionada + 1)
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if fase_selecionada <= fase_maxima:
                        animar_transicao(tela, relogio, entrada=False)
                        return fase_selecionada
                elif evento.key == pygame.K_ESCAPE:
                    animar_transicao(tela, relogio, entrada=False)
                    return None
            if evento.type == pygame.MOUSEWHEEL:
                inicio_lista = max(
                    0,
                    min(
                        quantidade_fases - fases_visiveis,
                        inicio_lista - evento.y,
                    ),
                )
            if evento.type == pygame.KEYDOWN:
                if fase_selecionada <= inicio_lista:
                    inicio_lista = fase_selecionada - 1
                elif fase_selecionada > inicio_lista + fases_visiveis:
                    inicio_lista = fase_selecionada - fases_visiveis

def tela_intro_fase(
    fase_atual,
    tela,
    relogio,
    fontes,
    fundos_fase,
    atualizar_tamanho_tela,
    gerar_som_inicio_fase,
    nome_habitat=None,
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
        5: "O último setor se abriu. Prepare-se para o confronto definitivo.",
    }
    cores_fase = {
        1: AZUL_NEON,
        2: AMARELO,
        3: VERMELHO,
        4: (255, 120, 40),
        5: (190, 100, 255),
    }

    animar_entrada = True
    while True:
        tempo_decorrido = pygame.time.get_ticks() - inicio
        if tempo_decorrido >= duracao_intro:
            animar_transicao(tela, relogio, entrada=False, duracao_ms=300)
            return

        relogio.tick(60)
        indice_fundo = min(max(fase_atual - 1, 0), len(fundos_fase) - 1)
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
        habitat = (
            texto_com_borda(fonte_hud, f"HABITAT: {nome_habitat}", AZUL_NEON)
            if nome_habitat
            else None
        )
        mensagem = texto_com_borda(
            fonte_texto,
            mensagens.get(fase_atual, "Atenção: novos inimigos se aproximam."),
            BRANCO,
        )
        segundos = max(1, int((duracao_intro - tempo_decorrido) / 1000) + 1)
        contador = texto_com_borda(fonte_hud, f"Início em {segundos}s", AMARELO)
        _centralizar(tela, titulo, 150)
        if habitat is not None:
            _centralizar(tela, habitat, 198)
        _centralizar(tela, mensagem, 240)
        _centralizar(tela, contador, 305)
        if animar_entrada:
            animar_transicao(tela, relogio, duracao_ms=300)
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
