import pygame
import sys

from config import AMARELO, AZUL_NEON, BRANCO, CINZA, VERMELHO
from game.screens_common import _centralizar, _desenhar_fundo, texto_com_borda



def tela_selecao_nave(
    dados_jogador,
    tela,
    relogio,
    fontes,
    fundo,
    atualizar_tamanho_tela,
    resolver_caminho_arquivo,
    validar_dados_jogador,
    salvar_dados,
):
    fonte_titulo, fonte_texto, fonte_hud = fontes
    dados_jogador = validar_dados_jogador(dados_jogador)
    naves_disponiveis = [
        {"nome": "Vanguard", "arquivo": "Vanguard.png", "preco": 0, "descricao": "Padrão de patrulha (Gratuita)"},
        {"nome": "Scout", "arquivo": "Scout.png", "preco": 50, "descricao": "Alta velocidade de locomoção."},
        {"nome": "Titan", "arquivo": "Titan.png", "preco": 100, "descricao": "Blindagem pesada e dano alto."},
        {"nome": "Phantom", "arquivo": "Phantom.png", "preco": 150, "descricao": "Disparadores de plasma velozes."},
        {"nome": "Aegis", "arquivo": "Aegis.png", "preco": 250, "descricao": "Escudo supremo e laser total."},
    ]
    imagens_naves = {}
    for nave in naves_disponiveis:
        try:
            imagem = pygame.image.load(resolver_caminho_arquivo(nave["arquivo"])).convert_alpha()
        except pygame.error:
            imagem = pygame.Surface((200, 200), pygame.SRCALPHA)
            pygame.draw.rect(imagem, AZUL_NEON, (0, 0, 200, 200), border_radius=20)
        imagens_naves[nave["arquivo"]] = imagem

    indice_selecionado = 0
    while True:
        relogio.tick(60)
        _desenhar_fundo(tela, fundo)
        _centralizar(tela, texto_com_borda(fonte_titulo, "HANGAR - SELEÇÃO DE NAVES", AZUL_NEON), 30)
        _centralizar(
            tela,
            texto_com_borda(fonte_hud, f"Suas Moedas: {dados_jogador['moedas']} 🪙", AMARELO),
            80,
        )

        centro_x = tela.get_width() // 2
        base_y = 210
        for offset in (-2, -1, 0, 1, 2):
            indice = (indice_selecionado + offset) % len(naves_disponiveis)
            nave = naves_disponiveis[indice]
            if offset == 0:
                tamanho, alpha, cor_borda, y, texto_cor = (190, 190), 255, AMARELO, base_y, AMARELO
            elif abs(offset) == 1:
                tamanho, alpha, cor_borda, y, texto_cor = (110, 110), 210, AZUL_NEON, base_y + 30, BRANCO
            else:
                tamanho, alpha, cor_borda, y, texto_cor = (78, 78), 150, CINZA, base_y + 55, CINZA

            x = centro_x + offset * 150
            imagem = pygame.transform.smoothscale(imagens_naves[nave["arquivo"]], tamanho)
            imagem.set_alpha(alpha)
            rect_imagem = pygame.Rect(x - tamanho[0] // 2, y, *tamanho)
            pygame.draw.rect(tela, cor_borda, rect_imagem, 3 if offset == 0 else 1, border_radius=18)
            tela.blit(imagem, rect_imagem.topleft)
            nome = texto_com_borda(fonte_texto, nave["nome"], texto_cor)
            tela.blit(nome, (x - nome.get_width() // 2, rect_imagem.bottom + 10))

            if offset == 0:
                desbloqueada = (
                    nave["arquivo"] in dados_jogador["naves_desbloqueadas"]
                    or nave["preco"] == 0
                )
                status = "LIBERADA" if desbloqueada else f"PREÇO: {nave['preco']} 🪙"
                descricao = texto_com_borda(fonte_texto, nave["descricao"], BRANCO)
                status_texto = texto_com_borda(
                    fonte_hud, f"Status: {status}", AMARELO if desbloqueada else VERMELHO,
                )
                _centralizar(tela, descricao, rect_imagem.bottom + 40)
                _centralizar(tela, status_texto, rect_imagem.bottom + 70)

        _centralizar(
            tela,
            texto_com_borda(
                fonte_hud,
                "Use [← / →] ou [SETAS] para navegar | [ENTER] para Selecionar/Comprar",
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
                if evento.key in (pygame.K_LEFT, pygame.K_a, pygame.K_UP):
                    indice_selecionado = (indice_selecionado - 1) % len(naves_disponiveis)
                elif evento.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN):
                    indice_selecionado = (indice_selecionado + 1) % len(naves_disponiveis)
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    nave_atual = naves_disponiveis[indice_selecionado]
                    ja_tem = (
                        nave_atual["arquivo"] in dados_jogador["naves_desbloqueadas"]
                        or nave_atual["preco"] == 0
                    )
                    if ja_tem:
                        return nave_atual["arquivo"]
                    if dados_jogador["moedas"] >= nave_atual["preco"]:
                        dados_jogador["moedas"] -= nave_atual["preco"]
                        dados_jogador["naves_desbloqueadas"].append(nave_atual["arquivo"])
                        salvar_dados(dados_jogador)
                        return nave_atual["arquivo"]

def tela_melhorias(
    dados_jogador,
    tela,
    relogio,
    fontes,
    fundo,
    atualizar_tamanho_tela,
    validar_dados_jogador,
    salvar_dados,
    calcular_duracao_especial_titan,
):
    fonte_titulo, fonte_texto, fonte_hud = fontes
    dados_jogador = validar_dados_jogador(dados_jogador)
    opcoes = ["velocidade", "cadencia", "especial"]
    custos = {"velocidade": 30, "cadencia": 40, "especial": 35}
    nomes = {"velocidade": "Velocidade", "cadencia": "Cadência", "especial": "Especial"}
    indice_selecionado = 0
    rodando = True

    while rodando:
        relogio.tick(60)
        _desenhar_fundo(tela, fundo)
        _centralizar(tela, texto_com_borda(fonte_titulo, "LABORATÓRIO DE MELHORIAS", AZUL_NEON), 30)
        _centralizar(
            tela,
            texto_com_borda(fonte_hud, f"Suas Moedas: {dados_jogador['moedas']} 🪙", AMARELO),
            80,
        )

        centro_x = tela.get_width() // 2
        base_y = 190
        for offset in (-1, 0, 1):
            indice = (indice_selecionado + offset) % len(opcoes)
            chave = opcoes[indice]
            nivel_atual = dados_jogador["niveis_melhorias"][chave]
            custo_atual = custos[chave] * nivel_atual
            if offset == 0:
                largura, altura, alpha, borda, texto_cor, y = 220, 140, 255, AMARELO, BRANCO, base_y
            else:
                largura, altura, alpha, borda, texto_cor, y = 130, 90, 180, AZUL_NEON, BRANCO, base_y + 20

            x = centro_x + offset * 170
            card = pygame.Surface((largura, altura), pygame.SRCALPHA)
            pygame.draw.rect(card, (20, 24, 35, 180), card.get_rect(), border_radius=16)
            pygame.draw.rect(card, borda, card.get_rect(), 2, border_radius=16)
            card.set_alpha(alpha)
            tela.blit(card, (x - largura // 2, y))

            textos = [
                (nomes[chave], fonte_hud, texto_cor, y + 18),
                (f"Nível: {nivel_atual}", fonte_texto, BRANCO, y + 48),
                (f"Custo: {custo_atual} 🪙", fonte_texto, AMARELO, y + 72),
            ]
            for texto, fonte, cor, texto_y in textos:
                renderizado = texto_com_borda(fonte, texto, cor)
                tela.blit(renderizado, (x - renderizado.get_width() // 2, texto_y))

            if chave == "especial":
                duracao = calcular_duracao_especial_titan(nivel_atual)
                texto_duracao = texto_com_borda(fonte_texto, f"Duração: {duracao:.1f}s", AZUL_NEON)
                tela.blit(texto_duracao, (x - texto_duracao.get_width() // 2, y + 96))

        _centralizar(
            tela,
            texto_com_borda(
                fonte_hud,
                "[SETAS] Mudar | [ENTER] Comprar | [ESPAÇO] Ir para Missão",
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
                if evento.key in (pygame.K_LEFT, pygame.K_UP):
                    indice_selecionado = (indice_selecionado - 1) % len(opcoes)
                elif evento.key in (pygame.K_RIGHT, pygame.K_DOWN):
                    indice_selecionado = (indice_selecionado + 1) % len(opcoes)
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    chave = opcoes[indice_selecionado]
                    nivel = dados_jogador["niveis_melhorias"][chave]
                    custo = custos[chave] * nivel
                    if dados_jogador["moedas"] >= custo:
                        dados_jogador["moedas"] -= custo
                        dados_jogador["niveis_melhorias"][chave] += 1
                        salvar_dados(dados_jogador)
                elif evento.key == pygame.K_SPACE:
                    rodando = False
