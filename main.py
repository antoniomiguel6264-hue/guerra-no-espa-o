import pygame
import sys
import config
from audio import iniciar_audio, tocar_som
from config import FPS, PRETO, BRANCO, AZUL_NEON, AMARELO, VERMELHO, CINZA
from entidades import Nave, Tiro, TiroEspecial, TiroEspecialAegis, Asteroide, Explosao
from salvamento import carregar_dados, salvar_dados

LARGURA = config.LARGURA
ALTURA = config.ALTURA

pygame.init()
iniciar_audio()
tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.RESIZABLE)
pygame.display.set_caption("Space Shooter - Soldado Cósmico")
relogio = pygame.time.Clock()


def atualizar_tamanho_tela(evento=None):
    global LARGURA, ALTURA
    if evento is not None and evento.type == pygame.VIDEORESIZE:
        config.LARGURA = evento.w
        config.ALTURA = evento.h
        LARGURA, ALTURA = config.LARGURA, config.ALTURA
        pygame.display.set_mode((LARGURA, ALTURA), pygame.RESIZABLE)
    return LARGURA, ALTURA

def texto_com_borda(fonte, texto, cor, borda_cor=PRETO, tamanho_borda=1, fundo=None):
    superficie = fonte.render(texto, True, cor, fundo)
    if tamanho_borda <= 0 or texto is None or texto == "":
        return superficie

    contorno = pygame.Surface(
        (superficie.get_width() + tamanho_borda * 2, superficie.get_height() + tamanho_borda * 2),
        pygame.SRCALPHA,
    )

    for dx in range(-tamanho_borda, tamanho_borda + 1):
        for dy in range(-tamanho_borda, tamanho_borda + 1):
            if dx == 0 and dy == 0:
                continue
            texto_borda = fonte.render(texto, True, borda_cor, fundo)
            contorno.blit(texto_borda, (dx + tamanho_borda, dy + tamanho_borda))

    contorno.blit(superficie, (tamanho_borda, tamanho_borda))
    return contorno


def desenhar_botao_pausa(tela_surface, rect, texto, ativo=False):
    cor_fundo = (30, 30, 40) if not ativo else (70, 110, 170)
    cor_borda = AZUL_NEON if not ativo else AMARELO
    pygame.draw.rect(tela_surface, cor_fundo, rect, border_radius=8)
    pygame.draw.rect(tela_surface, cor_borda, rect, 2, border_radius=8)
    txt = texto_com_borda(fonte_hud, texto, BRANCO if not ativo else AMARELO)
    tela_surface.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))


def gerar_som_inicio_fase(fase_atual):
    frequencias_por_fase = {
        1: [220, 330],
        2: [330, 440],
        3: [440, 660],
    }
    notas = frequencias_por_fase.get(fase_atual, [300, 450])
    tocar_som(notas, duracao=0.7, volume=0.25)


fonte_titulo = pygame.font.SysFont("Noto Sans", 32, bold=True)
fonte_texto = pygame.font.SysFont("Noto Sans", 16)
fonte_hud = pygame.font.SysFont("Noto Sans", 16, bold=True)

# Carrega a imagem de fundo da tela de boas-vindas
try:
    fundo_img = pygame.image.load("chagada.jpg").convert()
    fundo_img = pygame.transform.scale(fundo_img, (LARGURA, ALTURA))
except Exception as e:
    print(f"Erro ao carregar chagada.jpg: {e}. Usando fundo preto.")
    fundo_img = None

# Fundos das fases do jogo
fundo_fase_1 = None
try:
    fundo_fase_1 = pygame.image.load("fase1.jpg").convert()
    fundo_fase_1 = pygame.transform.scale(fundo_fase_1, (LARGURA, ALTURA))
except Exception as e:
    print(f"Erro ao carregar fase1.jpg: {e}. Usando fundo preto.")

fundo_fase_2 = None
try:
    fundo_fase_2 = pygame.image.load("fase2.jpg").convert()
    fundo_fase_2 = pygame.transform.scale(fundo_fase_2, (LARGURA, ALTURA))
except Exception as e:
    print(f"Erro ao carregar fase2.jpg: {e}. Usando fundo preto.")

fundo_fase_3 = None
try:
    fundo_fase_3 = pygame.image.load("fase3.jpg").convert()
    fundo_fase_3 = pygame.transform.scale(fundo_fase_3, (LARGURA, ALTURA))
except Exception as e:
    print(f"Erro ao carregar fase3.jpg: {e}. Usando fundo preto.")

fundo_fase_4 = None
try:
    fundo_fase_4 = pygame.image.load("fase4.jpg").convert()
    fundo_fase_4 = pygame.transform.scale(fundo_fase_4, (LARGURA, ALTURA))
except Exception as e:
    print(f"Erro ao carregar fase4.jpg: {e}. Usando fundo preto.")

# Fundo usado na tela de seleção de nave
try:
    fundo_selecao = pygame.image.load("tela preta.jpg").convert()
    fundo_selecao = pygame.transform.scale(fundo_selecao, (LARGURA, ALTURA))
except Exception as e:
    print(f"Erro ao carregar tela preta.jpg: {e}. Usando fundo preto.")
    fundo_selecao = None

# Fundo específico da tela de fim de jogo
fundo_fim = None
try:
    fundo_fim = pygame.image.load("fim.jpg").convert()
    fundo_fim = pygame.transform.scale(fundo_fim, (LARGURA, ALTURA))
except Exception as e:
    print(f"Erro ao carregar fim.jpg: {e}. Usando fundo preto.")
    fundo_fim = None

def tela_boas_vindas():
    rodando = True
    while rodando:
        relogio.tick(60)
        if fundo_img:
            tela.blit(fundo_img, (0, 0))
        else:
            tela.fill(PRETO)
        
        msg1 = texto_com_borda(fonte_titulo, "SOLDADO CÓSMICO", AZUL_NEON)
        msg2 = texto_com_borda(fonte_texto, "Olá, soldado cósmico. A Terra está sendo ameaçada", BRANCO)
        msg3 = texto_com_borda(fonte_texto, "por asteroides, precisamos impedir que isso aconteça!", BRANCO)
        
        msg_op1 = texto_com_borda(fonte_hud, "[ENTER] - Iniciar Missão", AMARELO)
        msg_op2 = texto_com_borda(fonte_hud, "[C] - Ver Comandos / Teclas", BRANCO)
        
        tela.blit(msg1, (LARGURA//2 - msg1.get_width()//2, 160))
        tela.blit(msg2, (LARGURA//2 - msg2.get_width()//2, 230))
        tela.blit(msg3, (LARGURA//2 - msg3.get_width()//2, 260))
        
        tela.blit(msg_op1, (LARGURA//2 - msg_op1.get_width()//2, 350))
        tela.blit(msg_op2, (LARGURA//2 - msg_op2.get_width()//2, 390))
        
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.VIDEORESIZE:
                atualizar_tamanho_tela(evento)
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN or evento.key == pygame.K_KP_ENTER:
                    rodando = False
                elif evento.key == pygame.K_c:
                    tela_comandos()

def tela_comandos():
    rodando = True
    while rodando:
        relogio.tick(60)
        if fundo_img:
            tela.blit(fundo_img, (0, 0))
        else:
            tela.fill(PRETO)
        
        titulo = texto_com_borda(fonte_titulo, "PAINEL DE COMANDOS", AZUL_NEON)
        
        c1 = texto_com_borda(fonte_texto, "• [Q / E] : Gira a nave para a esquerda e para a direita", BRANCO)
        c2 = texto_com_borda(fonte_texto, "• [CIMA] ou [W] : Acelera a nave para frente", BRANCO)
        c3 = texto_com_borda(fonte_texto, "• [J] (Segurar) : Dispara tiros normais contínuos", AMARELO)
        c4 = texto_com_borda(fonte_texto, "• [K] : Dispara o Tiro Especial (quando a barra encher)", AZUL_NEON)
        c5 = texto_com_borda(fonte_texto, "• [ESC] / Fechar : Sai do jogo", VERMELHO)
        
        voltar = texto_com_borda(fonte_hud, "Pressione [ESC] ou [ENTER] para voltar", AMARELO)
        
        tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 70))
        
        tela.blit(c1, (40, 160))
        tela.blit(c2, (40, 210))
        tela.blit(c3, (40, 260))
        tela.blit(c4, (40, 310))
        tela.blit(c5, (40, 360))
        
        tela.blit(voltar, (LARGURA//2 - voltar.get_width()//2, 460))
        
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.VIDEORESIZE:
                atualizar_tamanho_tela(evento)
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN or evento.key == pygame.K_KP_ENTER or evento.key == pygame.K_ESCAPE:
                    rodando = False

def tela_selecao_nave(dados_jogador):
    naves_disponiveis = [
        {"nome": "Vanguard", "arquivo": "Vanguard.png", "preco": 0, "descricao": "Padrão de patrulha (Gratuita)"},
        {"nome": "Scout", "arquivo": "Scout.png", "preco": 50, "descricao": "Alta velocidade de locomoção."},
        {"nome": "Titan", "arquivo": "Titan.png", "preco": 100, "descricao": "Blindagem pesada e dano alto."},
        {"nome": "Phantom", "arquivo": "Phantom.png", "preco": 150, "descricao": "Disparadores de plasma velozes."},
        {"nome": "Aegis", "arquivo": "Aegis.png", "preco": 250, "descricao": "Escudo supremo e laser total."}
    ]

    imagens_naves = {}
    for nave in naves_disponiveis:
        try:
            imagem = pygame.image.load(nave["arquivo"]).convert_alpha()
        except Exception:
            imagem = pygame.Surface((200, 200), pygame.SRCALPHA)
            pygame.draw.rect(imagem, AZUL_NEON, (0, 0, 200, 200), border_radius=20)
        imagens_naves[nave["arquivo"]] = imagem

    indice_selecionado = 0
    rodando = True

    while rodando:
        relogio.tick(60)
        if fundo_selecao:
            tela.blit(fundo_selecao, (0, 0))
        else:
            tela.fill(PRETO)

        titulo = texto_com_borda(fonte_titulo, "HANGAR - SELEÇÃO DE NAVES", AZUL_NEON)
        tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 30))

        txt_moedas = texto_com_borda(fonte_hud, f"Suas Moedas: {dados_jogador['moedas']} 🪙", AMARELO)
        tela.blit(txt_moedas, (LARGURA//2 - txt_moedas.get_width()//2, 80))

        centro_x = LARGURA // 2
        base_y = 210
        mapa_offsets = [-2, -1, 0, 1, 2]

        for offset in mapa_offsets:
            indice = (indice_selecionado + offset) % len(naves_disponiveis)
            nave = naves_disponiveis[indice]
            if offset == 0:
                tamanho = (190, 190)
                alpha = 255
                cor_borda = AMARELO
                y = base_y
                texto_cor = AMARELO
            elif abs(offset) == 1:
                tamanho = (110, 110)
                alpha = 210
                cor_borda = AZUL_NEON
                y = base_y + 30
                texto_cor = BRANCO
            else:
                tamanho = (78, 78)
                alpha = 150
                cor_borda = CINZA
                y = base_y + 55
                texto_cor = CINZA

            x = centro_x + offset * 150
            imagem = pygame.transform.smoothscale(imagens_naves[nave["arquivo"]], tamanho)
            imagem.set_alpha(alpha)

            rect_imagem = pygame.Rect(x - tamanho[0] // 2, y, *tamanho)
            pygame.draw.rect(tela, cor_borda, rect_imagem, 3 if offset == 0 else 1, border_radius=18)
            tela.blit(imagem, rect_imagem.topleft)

            nome_txt = texto_com_borda(fonte_texto, nave["nome"], texto_cor)
            tela.blit(nome_txt, (x - nome_txt.get_width() // 2, rect_imagem.bottom + 10))

            if offset == 0:
                desbloqueada = nave["arquivo"] in dados_jogador["naves_desbloqueadas"] or nave["preco"] == 0
                status = "LIBERADA" if desbloqueada else f"PREÇO: {nave['preco']} 🪙"
                descricao = texto_com_borda(fonte_texto, nave["descricao"], BRANCO)
                status_txt = texto_com_borda(fonte_hud, f"Status: {status}", AMARELO if desbloqueada else VERMELHO)
                tela.blit(descricao, (LARGURA // 2 - descricao.get_width() // 2, rect_imagem.bottom + 40))
                tela.blit(status_txt, (LARGURA // 2 - status_txt.get_width() // 2, rect_imagem.bottom + 70))

        txt_instrucao = texto_com_borda(fonte_hud, "Use [← / →] ou [SETAS] para navegar | [ENTER] para Selecionar/Comprar", BRANCO)
        tela.blit(txt_instrucao, (LARGURA//2 - txt_instrucao.get_width()//2, 500))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.VIDEORESIZE:
                atualizar_tamanho_tela(evento)
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_LEFT, pygame.K_a, pygame.K_UP):
                    indice_selecionado = (indice_selecionado - 1) % len(naves_disponiveis)
                elif evento.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN):
                    indice_selecionado = (indice_selecionado + 1) % len(naves_disponiveis)
                elif evento.key == pygame.K_RETURN or evento.key == pygame.K_KP_ENTER:
                    nave_atual = naves_disponiveis[indice_selecionado]
                    ja_tem = nave_atual["arquivo"] in dados_jogador["naves_desbloqueadas"] or nave_atual["preco"] == 0

                    if ja_tem:
                        return nave_atual["arquivo"]
                    elif dados_jogador["moedas"] >= nave_atual["preco"]:
                        dados_jogador["moedas"] -= nave_atual["preco"]
                        dados_jogador["naves_desbloqueadas"].append(nave_atual["arquivo"])
                        salvar_dados(dados_jogador)
                        return nave_atual["arquivo"]

def tela_melhorias(dados_jogador):
    opcoes = ["velocidade", "cadencia", "especial"]
    indice_selecionado = 0
    rodando = True

    custos = {
        "velocidade": 30,
        "cadencia": 40,
        "especial": 35
    }

    nomes = {
        "velocidade": "Velocidade",
        "cadencia": "Cadência",
        "especial": "Especial"
    }

    while rodando:
        relogio.tick(60)
        if fundo_selecao:
            tela.blit(fundo_selecao, (0, 0))
        else:
            tela.fill(PRETO)

        titulo = texto_com_borda(fonte_titulo, "LABORATÓRIO DE MELHORIAS", AZUL_NEON)
        tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 30))

        txt_moedas = texto_com_borda(fonte_hud, f"Suas Moedas: {dados_jogador['moedas']} 🪙", AMARELO)
        tela.blit(txt_moedas, (LARGURA//2 - txt_moedas.get_width()//2, 80))

        centro_x = LARGURA // 2
        base_y = 190
        pad = 170

        for offset in (-1, 0, 1):
            indice = (indice_selecionado + offset) % len(opcoes)
            chave = opcoes[indice]
            nivel_atual = dados_jogador["niveis_melhorias"][chave]
            custo_atual = custos[chave] * nivel_atual

            if offset == 0:
                largura = 200
                altura = 120
                alpha = 255
                borda = AMARELO
                texto_cor = BRANCO
                y = base_y
            elif abs(offset) == 1:
                largura = 130
                altura = 90
                alpha = 180
                borda = AZUL_NEON
                texto_cor = BRANCO
                y = base_y + 20

            x = centro_x + offset * pad
            card = pygame.Surface((largura, altura), pygame.SRCALPHA)
            pygame.draw.rect(card, (20, 24, 35, 180), card.get_rect(), border_radius=16)
            pygame.draw.rect(card, borda, card.get_rect(), 2, border_radius=16)
            card.set_alpha(alpha)
            tela.blit(card, (x - largura // 2, y))

            nome = texto_com_borda(fonte_hud, nomes[chave], texto_cor)
            nivel = texto_com_borda(fonte_texto, f"Nível: {nivel_atual}", BRANCO)
            valor = texto_com_borda(fonte_texto, f"Custo: {custo_atual} 🪙", AMARELO)

            tela.blit(nome, (x - nome.get_width() // 2, y + 18))
            tela.blit(nivel, (x - nivel.get_width() // 2, y + 48))
            tela.blit(valor, (x - valor.get_width() // 2, y + 72))

        txt_instrucao = texto_com_borda(fonte_hud, "[SETAS] Mudar | [ENTER] Comprar | [ESPAÇO] Ir para Missão", BRANCO)
        tela.blit(txt_instrucao, (LARGURA//2 - txt_instrucao.get_width()//2, 500))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.VIDEORESIZE:
                atualizar_tamanho_tela(evento)
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT or evento.key == pygame.K_UP:
                    indice_selecionado = (indice_selecionado - 1) % len(opcoes)
                elif evento.key == pygame.K_RIGHT or evento.key == pygame.K_DOWN:
                    indice_selecionado = (indice_selecionado + 1) % len(opcoes)
                elif evento.key == pygame.K_RETURN or evento.key == pygame.K_KP_ENTER:
                    chave_escolhida = opcoes[indice_selecionado]
                    nivel_atual = dados_jogador["niveis_melhorias"][chave_escolhida]
                    custo_necessario = custos[chave_escolhida] * nivel_atual

                    if dados_jogador["moedas"] >= custo_necessario:
                        dados_jogador["moedas"] -= custo_necessario
                        dados_jogador["niveis_melhorias"][chave_escolhida] += 1
                        salvar_dados(dados_jogador)
                elif evento.key == pygame.K_SPACE:
                    rodando = False

def jogo_principal(arquivo_nave, niveis_melhorias, fase_atual=1):
    todos_sprites = pygame.sprite.Group()
    tiros = pygame.sprite.Group()
    asteroides = pygame.sprite.Group()
    especiais = pygame.sprite.Group()
    explosoes = pygame.sprite.Group()

    if fase_atual == 1:
        fundo_fase = fundo_fase_1
    elif fase_atual == 2:
        fundo_fase = fundo_fase_2
    elif fase_atual == 3:
        fundo_fase = fundo_fase_3
    else:
        fundo_fase = fundo_fase_4

    jogador = Nave(LARGURA // 2, ALTURA - 80, arquivo_nave, niveis_melhorias)
    todos_sprites.add(jogador)

    qtd_asteroides = 4 + fase_atual
    for _ in range(qtd_asteroides):
        ast = Asteroide(fase_atual)
        ast.velocidadey = max(1, ast.velocidadey - 2 + fase_atual)
        todos_sprites.add(ast)
        asteroides.add(ast)

    moedas = 0
    pontos = 0
    if fase_atual == 1:
        meta_pontos = 240
    elif fase_atual == 2:
        meta_pontos = 480
    elif fase_atual == 3:
        meta_pontos = 720
    else:
        meta_pontos = 960

    rodando = True
    pausado = False
    cooldown_tiro = 0
    cadencia_base = max(4, 12 - (niveis_melhorias["cadencia"] - 1) * 2)
    venceu = False
    botao_pausa = pygame.Rect(LARGURA - 120, 20, 100, 35)
    
    while rodando:
        relogio.tick(FPS)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.VIDEORESIZE:
                atualizar_tamanho_tela(evento)
                botao_pausa = pygame.Rect(LARGURA - 120, 20, 100, 35)

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if botao_pausa.collidepoint(evento.pos):
                    pausado = not pausado

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_p:
                    pausado = not pausado
                elif evento.key == pygame.K_k:
                    if jogador.disparar_especial():
                        tocar_som([620, 820], duracao=0.18, volume=0.3)
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
            if fundo_fase:
                tela.blit(fundo_fase, (0, 0))
            else:
                tela.fill(PRETO)

            todos_sprites.draw(tela)

            txt_pontos = texto_com_borda(fonte_hud, f"Pontos: {pontos} / {meta_pontos}", BRANCO)
            txt_fase = texto_com_borda(fonte_hud, f"Fase: {fase_atual}", AZUL_NEON)
            txt_moedas = texto_com_borda(fonte_hud, f"Moedas: {moedas} 🪙", AMARELO)
            txt_vidas = texto_com_borda(fonte_hud, f"Vidas: {'❤️ ' * jogador.vidas}", VERMELHO)

            tela.blit(txt_pontos, (20, 20))
            tela.blit(txt_fase, (20, 45))
            tela.blit(txt_moedas, (20, 70))
            tela.blit(txt_vidas, (20, 95))
            desenhar_botao_pausa(tela, botao_pausa, "Continuar", ativo=True)

            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((10, 12, 20, 170))
            tela.blit(overlay, (0, 0))

            txt_pausa = texto_com_borda(fonte_titulo, "PAUSADO", AMARELO)
            txt_instrucao = texto_com_borda(fonte_hud, "Pressione [P] ou clique no botão para continuar", BRANCO)
            tela.blit(txt_pausa, (LARGURA // 2 - txt_pausa.get_width() // 2, ALTURA // 2 - 40))
            tela.blit(txt_instrucao, (LARGURA // 2 - txt_instrucao.get_width() // 2, ALTURA // 2 + 30))
            pygame.display.flip()
            continue

        teclas = pygame.key.get_pressed()
        
        if teclas[pygame.K_j]:
            if cooldown_tiro <= 0:
                tiro = Tiro(jogador.rect.centerx, jogador.rect.centery, jogador.angulo)
                todos_sprites.add(tiro)
                tiros.add(tiro)
                tocar_som([420], duracao=0.08, volume=0.18)
                cooldown_tiro = cadencia_base
                
        if cooldown_tiro > 0:
            cooldown_tiro -= 1

        jogador.update(teclas)
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
            moedas += 1
            jogador.adicionar_energia(20)
            tocar_som([180, 120], duracao=0.15, volume=0.25)
            
            if pontos < meta_pontos:
                novo_ast = Asteroide(fase_atual)
                novo_ast.velocidadey = max(1, novo_ast.velocidadey - 2)
                todos_sprites.add(novo_ast)
                asteroides.add(novo_ast)

        colisoes_especial = pygame.sprite.groupcollide(asteroides, especiais, True, False)
        for ast in colisoes_especial:
            cor_explosao = (255, 110, 255)
            if jogador.modelo == "titan":
                cor_explosao = (255, 180, 90)
            explosao = Explosao(ast.rect.centerx, ast.rect.centery, cor=cor_explosao, raio_inicial=18)
            todos_sprites.add(explosao)
            explosoes.add(explosao)
            pontos += 15
            moedas += 2
            tocar_som([520, 700, 820], duracao=0.2, volume=0.3)
            if pontos < meta_pontos:
                novo_ast = Asteroide(fase_atual)
                novo_ast.velocidadey = max(1, novo_ast.velocidadey - 2)
                todos_sprites.add(novo_ast)
                asteroides.add(novo_ast)

        if jogador.modelo == "aegis" and not teclas[pygame.K_k] and jogador.aegis_ativo:
            jogador.aegis_ativo = False

        # Condição de vitória da fase
        if pontos >= meta_pontos:
            venceu = True
            rodando = False

        if pygame.sprite.spritecollideany(jogador, asteroides):
            tocar_som([100, 70], duracao=0.18, volume=0.28)
            if jogador.perder_vida():
                if jogador.vidas <= 0:
                    pygame.time.delay(500)
                    rodando = False

        if fundo_fase:
            tela.blit(fundo_fase, (0, 0))
        else:
            tela.fill(PRETO)
            
        todos_sprites.draw(tela)

        txt_pontos = texto_com_borda(fonte_hud, f"Pontos: {pontos} / {meta_pontos}", BRANCO)
        txt_fase = texto_com_borda(fonte_hud, f"Fase: {fase_atual}", AZUL_NEON)
        txt_moedas = texto_com_borda(fonte_hud, f"Moedas: {moedas} 🪙", AMARELO)
        txt_vidas = texto_com_borda(fonte_hud, f"Vidas: {'❤️ ' * jogador.vidas}", VERMELHO)
        
        tela.blit(txt_pontos, (20, 20))
        tela.blit(txt_fase, (20, 45))
        tela.blit(txt_moedas, (20, 70))
        tela.blit(txt_vidas, (20, 95))

        pygame.draw.rect(tela, (50, 50, 50), (20, 130, 150, 15))
        largura_barra = int(1.5 * jogador.energia_especial)
        cor_barra = AZUL_NEON if jogador.energia_especial >= 100 else (0, 150, 200)
        pygame.draw.rect(tela, cor_barra, (20, 130, largura_barra, 15))
        pygame.draw.rect(tela, BRANCO, (20, 130, 150, 15), 1)
        
        txt_especial = texto_com_borda(fonte_hud, "ESPECIAL [K]", BRANCO if jogador.energia_especial >= 100 else CINZA)
        tela.blit(txt_especial, (180, 128))
        desenhar_botao_pausa(tela, botao_pausa, "Pausar", ativo=False)

        pygame.display.flip()

    return pontos, moedas, venceu

def tela_intro_fase(fase_atual):
    gerar_som_inicio_fase(fase_atual)
    inicio = pygame.time.get_ticks()
    duracao_intro = 5000
    mensagens = {
        1: "A borda do setor está infestada. Prepare-se para romper as linhas inimigas.",
        2: "O campo foi reforçado. Asteroides maiores e mais agressivos surgem do vazio.",
        3: "Último bastião da rota. A frota inimiga se concentra em um ataque final.",
        4: "A névoa de fogo do setor final está ativa. O último empurrão será decisivo."
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
            break

        relogio.tick(60)

        if fase_atual == 1:
            fundo = fundo_fase_1
        elif fase_atual == 2:
            fundo = fundo_fase_2
        elif fase_atual == 3:
            fundo = fundo_fase_3
        else:
            fundo = fundo_fase_4
        if fundo:
            tela.blit(fundo, (0, 0))
        else:
            tela.fill(PRETO)

        transicao = min(255, max(0, int((tempo_decorrido / 1200) * 255)))
        fade_saida = min(255, max(0, int(((duracao_intro - tempo_decorrido) / 1200) * 255)))
        alpha = min(transicao, fade_saida)

        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((8, 12, 20, alpha))
        tela.blit(overlay, (0, 0))

        painel = pygame.Surface((620, 230), pygame.SRCALPHA)
        painel.fill((15, 18, 28, 180))
        tela.blit(painel, (LARGURA // 2 - 310, 110))

        cor_titulo = cores_fase.get(fase_atual, AZUL_NEON)
        txt_titulo = texto_com_borda(fonte_titulo, f"FASE {fase_atual}", cor_titulo)
        txt_msg = texto_com_borda(fonte_texto, mensagens.get(fase_atual, "Atenção: novos inimigos se aproximam."), BRANCO)
        segundos_restantes = max(1, int((duracao_intro - tempo_decorrido) / 1000) + 1)
        txt_contador = texto_com_borda(fonte_hud, f"Início em {segundos_restantes}s", AMARELO)

        tela.blit(txt_titulo, (LARGURA // 2 - txt_titulo.get_width() // 2, 150))
        tela.blit(txt_msg, (LARGURA // 2 - txt_msg.get_width() // 2, 240))
        tela.blit(txt_contador, (LARGURA // 2 - txt_contador.get_width() // 2, 305))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.VIDEORESIZE:
                atualizar_tamanho_tela(evento)


def tela_vitoria(pontos, moedas):
    rodando = True
    while rodando:
        relogio.tick(60)
        if fundo_img:
            tela.blit(fundo_img, (0, 0))
        else:
            tela.fill(PRETO)
        
        txt_v = texto_com_borda(fonte_titulo, "FASE CONCLUÍDA!", AMARELO)
        txt_frase = texto_com_borda(fonte_texto, "Parabéns, soldado! Você limpou o setor de asteroides.", BRANCO)
        
        txt_resumo_p = texto_com_borda(fonte_texto, f"Pontuação: {pontos}", BRANCO)
        txt_resumo_m = texto_com_borda(fonte_texto, f"Moedas Coletadas: {moedas} 🪙", AMARELO)
        
        txt_continuar = texto_com_borda(fonte_hud, "Pressione [ENTER] para voltar ao Hangar", AZUL_NEON)
        
        tela.blit(txt_v, (LARGURA//2 - txt_v.get_width()//2, 140))
        tela.blit(txt_frase, (LARGURA//2 - txt_frase.get_width()//2, 210))
        
        tela.blit(txt_resumo_p, (LARGURA//2 - txt_resumo_p.get_width()//2, 290))
        tela.blit(txt_resumo_m, (LARGURA//2 - txt_resumo_m.get_width()//2, 325))
        
        tela.blit(txt_continuar, (LARGURA//2 - txt_continuar.get_width()//2, 420))
        
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.VIDEORESIZE:
                atualizar_tamanho_tela(evento)
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN or evento.key == pygame.K_KP_ENTER:
                    rodando = False

def tela_game_over(pontos, moedas):
    rodando = True
    while rodando:
        relogio.tick(60)
        if fundo_fim:
            tela.blit(fundo_fim, (0, 0))
        else:
            tela.fill(PRETO)
        
        txt_go = texto_com_borda(fonte_titulo, "FIM DE JOGO", VERMELHO)
        txt_frase = texto_com_borda(fonte_texto, '"A frota caiu, mas a lenda do Soldado Cósmico nunca morre!"', BRANCO)
        
        txt_resumo_p = texto_com_borda(fonte_texto, f"Pontuação Final: {pontos}", BRANCO)
        txt_resumo_m = texto_com_borda(fonte_texto, f"Moedas Coletadas: {moedas} 🪙", AMARELO)
        
        txt_continuar = texto_com_borda(fonte_hud, "Pressione [ENTER] para voltar ao Hangar", AZUL_NEON)
        
        tela.blit(txt_go, (LARGURA//2 - txt_go.get_width()//2, 140))
        tela.blit(txt_frase, (LARGURA//2 - txt_frase.get_width()//2, 210))
        
        tela.blit(txt_resumo_p, (LARGURA//2 - txt_resumo_p.get_width()//2, 290))
        tela.blit(txt_resumo_m, (LARGURA//2 - txt_resumo_m.get_width()//2, 325))
        
        tela.blit(txt_continuar, (LARGURA//2 - txt_continuar.get_width()//2, 420))
        
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.VIDEORESIZE:
                atualizar_tamanho_tela(evento)
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN or evento.key == pygame.K_KP_ENTER:
                    rodando = False

if __name__ == "__main__":
    dados_jogador = carregar_dados()
    
    while True:
        tela_boas_vindas()
        nave_escolhida = tela_selecao_nave(dados_jogador)
        tela_melhorias(dados_jogador)

        pontos_totais = 0
        moedas_totais = 0
        fase_atual = 1
        venceu = False

        while fase_atual <= 4:
            tela_intro_fase(fase_atual)
            pontos_partida, moedas_partida, venceu = jogo_principal(nave_escolhida, dados_jogador["niveis_melhorias"], fase_atual)
            pontos_totais += pontos_partida
            moedas_totais += moedas_partida

            dados_jogador["moedas"] += moedas_partida
            salvar_dados(dados_jogador)

            if not venceu:
                tela_game_over(pontos_totais, moedas_totais)
                break

            if fase_atual == 1:
                fase_atual = 2
                continue
            if fase_atual == 2:
                fase_atual = 3
                continue
            if fase_atual == 3:
                fase_atual = 4
                continue

            tela_vitoria(pontos_totais, moedas_totais)
            break
