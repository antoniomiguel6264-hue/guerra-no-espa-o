import pygame

from config import AMARELO, AZUL_NEON, BRANCO
from game import screens
from game.ui import (
    desenhar_botao_pausa,
    desenhar_fundo,
    desenhar_hud_jogo,
    desenhar_tela_jogo,
    texto_com_borda,
)
from game.screens_common import animar_transicao


def test_texto_com_borda_adiciona_contorno():
    fonte = pygame.font.SysFont("Noto Sans", 16)
    texto = texto_com_borda(fonte, "Pausar", BRANCO, tamanho_borda=2)
    texto_sem_contorno = fonte.render("Pausar", True, BRANCO)

    assert texto.get_size() == (
        texto_sem_contorno.get_width() + 4,
        texto_sem_contorno.get_height() + 4,
    )


def test_fundo_e_redimensionado_para_area_de_tela():
    tela = pygame.Surface((4, 3))
    fundo = pygame.Surface((2, 2))
    fundo.fill((25, 50, 75))

    desenhar_fundo(tela, fundo)

    assert tela.get_at((3, 2))[:3] == (25, 50, 75)


def test_transicao_fade_entrada_e_saida(monkeypatch):
    tela = pygame.Surface((2, 2))
    tela.fill((40, 80, 120))
    capturas = []

    class RelogioFalso:
        def tick(self, fps):
            return 1000 // fps

    monkeypatch.setattr(
        pygame.display,
        "flip",
        lambda: capturas.append(tela.get_at((0, 0))[:3]),
    )

    animar_transicao(tela, RelogioFalso(), duracao_ms=50)
    assert capturas[0] == (0, 0, 0)
    assert capturas[-1] == (40, 80, 120)

    capturas.clear()
    animar_transicao(tela, RelogioFalso(), entrada=False, duracao_ms=50)
    assert capturas[0] == (40, 80, 120)
    assert capturas[-1] == (0, 0, 0)


def test_trilha_de_fases_inicia_fase_desbloqueada(monkeypatch):
    pygame.init()
    tela = pygame.Surface((800, 600))
    fontes = tuple(pygame.font.SysFont("Noto Sans", tamanho) for tamanho in (32, 16, 16))
    eventos = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN),
    ]
    monkeypatch.setattr("game.screens_menu._desenhar_fundo", lambda *args: None)
    monkeypatch.setattr("game.screens_menu.animar_transicao", lambda *args, **kwargs: None)
    monkeypatch.setattr(pygame.event, "get", lambda: eventos)
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    fase = screens.tela_selecao_fase(
        "asteroides", {"asteroides": 2}, tela, pygame.time.Clock(), fontes,
        None, lambda evento: None,
    )

    assert fase == 2


def test_trilha_de_fases_nao_inicia_fase_bloqueada(monkeypatch):
    pygame.init()
    tela = pygame.Surface((800, 600))
    fontes = tuple(pygame.font.SysFont("Noto Sans", tamanho) for tamanho in (32, 16, 16))
    eventos = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE),
    ]
    monkeypatch.setattr("game.screens_menu._desenhar_fundo", lambda *args: None)
    monkeypatch.setattr("game.screens_menu.animar_transicao", lambda *args, **kwargs: None)
    monkeypatch.setattr(pygame.event, "get", lambda: eventos)
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    fase = screens.tela_selecao_fase(
        "frota_inimiga", {"frota_inimiga": 1}, tela, pygame.time.Clock(), fontes,
        None, lambda evento: None,
    )

    assert fase is None


def test_trilha_de_fases_permite_iniciar_quinta_fase_desbloqueada(monkeypatch):
    pygame.init()
    tela = pygame.Surface((800, 600))
    fontes = tuple(pygame.font.SysFont("Noto Sans", tamanho) for tamanho in (32, 16, 16))
    eventos = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        for _ in range(4)
    ]
    eventos.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    monkeypatch.setattr("game.screens_menu._desenhar_fundo", lambda *args: None)
    monkeypatch.setattr("game.screens_menu.animar_transicao", lambda *args, **kwargs: None)
    monkeypatch.setattr(pygame.event, "get", lambda: eventos)
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    fase = screens.tela_selecao_fase(
        "asteroides", {"asteroides": 5}, tela, pygame.time.Clock(), fontes,
        None, lambda evento: None,
    )

    assert fase == 5


def test_trilha_de_fases_permite_iniciar_fase_dez_desbloqueada(monkeypatch):
    pygame.init()
    tela = pygame.Surface((800, 600))
    fontes = tuple(pygame.font.SysFont("Noto Sans", tamanho) for tamanho in (32, 16, 16))
    eventos = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        for _ in range(9)
    ]
    eventos.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    monkeypatch.setattr("game.screens_menu._desenhar_fundo", lambda *args: None)
    monkeypatch.setattr("game.screens_menu.animar_transicao", lambda *args, **kwargs: None)
    monkeypatch.setattr(pygame.event, "get", lambda: eventos)
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    fase = screens.tela_selecao_fase(
        "asteroides", {"asteroides": 10}, tela, pygame.time.Clock(), fontes,
        None, lambda evento: None,
    )

    assert fase == 10


def test_menu_pos_fase_disponibiliza_resgate_manual(monkeypatch):
    pygame.init()
    tela = pygame.Surface((800, 600))
    fontes = tuple(pygame.font.SysFont("Noto Sans", tamanho) for tamanho in (32, 16, 16))
    eventos = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN),
    ]
    textos = []
    texto_original = screens.texto_com_borda

    def registrar_texto(fonte, texto, cor, *args, **kwargs):
        textos.append(texto)
        return texto_original(fonte, texto, cor, *args, **kwargs)

    monkeypatch.setattr("game.screens_results._desenhar_fundo", lambda *args: None)
    monkeypatch.setattr("game.screens_results.animar_transicao", lambda *args, **kwargs: None)
    monkeypatch.setattr("game.screens_results.texto_com_borda", registrar_texto)
    monkeypatch.setattr(pygame.event, "get", lambda: eventos)
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    acao = screens.tela_pos_fase(
        5, 1000, 50, "hyperion", tela, pygame.time.Clock(), fontes, None,
        lambda evento: None,
    )

    assert acao == "resgatar"
    assert any("Hyperion" in texto for texto in textos)


def test_trilha_mostra_habitat_da_nave_escolhida(monkeypatch):
    pygame.init()
    tela = pygame.Surface((800, 600))
    fontes = tuple(pygame.font.SysFont("Noto Sans", tamanho) for tamanho in (32, 16, 16))
    fundo = pygame.Surface((800, 600))
    fundo.fill((80, 80, 80))
    textos = []
    cores_fundo = []
    eventos = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)]
    texto_original = screens.texto_com_borda

    def registrar_texto(fonte, texto, cor, *args, **kwargs):
        textos.append(texto)
        return texto_original(fonte, texto, cor, *args, **kwargs)

    def registrar_fundo(superficie, imagem):
        superficie.blit(imagem, (0, 0))
        cores_fundo.append(superficie.get_at((0, 0))[:3])

    monkeypatch.setattr("game.screens_menu._desenhar_fundo", registrar_fundo)
    monkeypatch.setattr("game.screens_menu.animar_transicao", lambda *args, **kwargs: None)
    monkeypatch.setattr("game.screens_menu.texto_com_borda", registrar_texto)
    monkeypatch.setattr(pygame.event, "get", lambda: eventos)
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    screens.tela_selecao_fase(
        "asteroides", {"asteroides": 1}, tela, pygame.time.Clock(), fontes,
        fundo, lambda evento: None, "Titan.png",
    )

    assert "HABITAT: Lua Vulcânica" in textos
    assert cores_fundo[0] == (80, 80, 80)


def test_botao_de_pausa_muda_cor_quando_ativo():
    fonte = pygame.font.SysFont("Noto Sans", 16)
    tela = pygame.Surface((100, 50))
    botao = pygame.Rect(10, 10, 80, 30)

    desenhar_botao_pausa(tela, botao, "Continuar", fonte, ativo=True)

    assert tela.get_at((10, 25))[:3] == AMARELO


def test_botao_de_pausa_usa_borda_azul_quando_inativo():
    fonte = pygame.font.SysFont("Noto Sans", 16)
    tela = pygame.Surface((100, 50))
    botao = pygame.Rect(10, 10, 80, 30)

    desenhar_botao_pausa(tela, botao, "Pausar", fonte)

    assert tela.get_at((10, 25))[:3] == AZUL_NEON


def test_hud_do_modo_infinito_exibe_pontos_sem_meta(monkeypatch):
    fonte = pygame.font.SysFont("Noto Sans", 16)
    tela = pygame.Surface((800, 600))
    textos_renderizados = []
    texto_original = texto_com_borda

    def registrar_texto(fonte, texto, cor, *args, **kwargs):
        textos_renderizados.append(texto)
        return texto_original(fonte, texto, cor, *args, **kwargs)

    monkeypatch.setattr("game.ui.texto_com_borda", registrar_texto)
    desenhar_hud_jogo(
        tela, fonte, 350, 0, 2, 12, 75, 100, 50, 0, "infinito", "vanguard",
        pygame.Rect(680, 20, 100, 35),
    )

    assert "Pontos: 350" in textos_renderizados
    assert "INFINITO" in textos_renderizados
    assert "Frota: 0" in textos_renderizados
    assert "MODO: INFINITO" in textos_renderizados


def test_hud_pausado_omite_indicadores_de_combate(monkeypatch):
    fonte = pygame.font.SysFont("Noto Sans", 16)
    tela = pygame.Surface((800, 600))
    textos_renderizados = []
    texto_original = texto_com_borda

    def registrar_texto(fonte, texto, cor, *args, **kwargs):
        textos_renderizados.append(texto)
        return texto_original(fonte, texto, cor, *args, **kwargs)

    monkeypatch.setattr("game.ui.texto_com_borda", registrar_texto)
    desenhar_hud_jogo(
        tela, fonte, 350, 500, 2, 12, 75, 100, 50, 3,
        "frota_inimiga", "titan", pygame.Rect(680, 20, 100, 35), pausado=True,
    )

    assert "Pontos: 350 / 500" in textos_renderizados
    assert "Continuar" in textos_renderizados
    assert "ESPECIAL [K]" not in textos_renderizados
    assert not any(texto.startswith("Titan:") for texto in textos_renderizados)


def test_hud_mostra_barra_de_vida_do_chefe(monkeypatch):
    pygame.font.init()
    fonte = pygame.font.SysFont("Noto Sans", 16)
    tela = pygame.Surface((800, 600))
    textos_renderizados = []
    texto_original = texto_com_borda

    def registrar_texto(fonte_texto, texto, cor, *args, **kwargs):
        textos_renderizados.append(texto)
        return texto_original(fonte_texto, texto, cor, *args, **kwargs)

    monkeypatch.setattr("game.ui.texto_com_borda", registrar_texto)
    desenhar_hud_jogo(
        tela,
        fonte,
        100,
        150,
        2,
        4,
        80,
        100,
        50,
        1,
        "frota_inimiga",
        "vanguard",
        pygame.Rect(680, 20, 100, 35),
        chefe_vida=75,
        chefe_vida_maxima=200,
    )

    assert "CHEFE" in textos_renderizados


def test_hud_titan_mostra_prontidao_e_tempo_restante(monkeypatch):
    fonte = pygame.font.SysFont("Noto Sans", 16)
    tela = pygame.Surface((800, 600))
    textos_renderizados = []
    texto_original = texto_com_borda

    def registrar_texto(fonte, texto, cor, *args, **kwargs):
        textos_renderizados.append(texto)
        return texto_original(fonte, texto, cor, *args, **kwargs)

    monkeypatch.setattr("game.ui.texto_com_borda", registrar_texto)
    argumentos = (
        tela, fonte, 0, 300, 1, 0, 100, 100, 100, 0,
        "asteroides", "titan", pygame.Rect(680, 20, 100, 35),
    )
    desenhar_hud_jogo(*argumentos)
    assert "Titan: pronto" in textos_renderizados

    textos_renderizados.clear()
    desenhar_hud_jogo(*argumentos, titan_restante=1.4)
    assert "Titan: 1.4s" in textos_renderizados


def test_tela_boas_vindas_despacha_comandos_e_ranking(monkeypatch):
    pygame.init()
    tela = pygame.Surface((800, 600))
    fontes = tuple(pygame.font.SysFont("Noto Sans", tamanho) for tamanho in (32, 16, 16))
    chamadas = []
    eventos = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_c),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN),
    ]
    atualizacoes = []
    monkeypatch.setattr("game.screens_menu._desenhar_fundo", None)
    monkeypatch.setattr("game.screens_menu.animar_transicao", lambda *args, **kwargs: None)
    monkeypatch.setattr(pygame.event, "get", lambda: [eventos.pop(0)])
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    screens.tela_boas_vindas(
        tela, pygame.time.Clock(), fontes, None, atualizacoes.append,
        lambda: chamadas.append("comandos"),
        lambda: chamadas.append("ranking"),
        lambda: chamadas.append("conquistas"),
    )

    assert chamadas == ["comandos", "ranking", "conquistas"]
    assert len(atualizacoes) == 1
    assert atualizacoes[0].key == pygame.K_F11
    assert tela.get_at((0, 0))[:3] == (5, 12, 30)


def test_tela_conquistas_exibe_estado_e_fecha_com_escape(monkeypatch):
    pygame.init()
    tela = pygame.Surface((800, 600))
    fontes = tuple(pygame.font.SysFont("Noto Sans", tamanho) for tamanho in (32, 16, 16))
    textos = []
    eventos = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]
    texto_original = texto_com_borda

    def registrar_texto(fonte, texto, cor, *args, **kwargs):
        textos.append(texto)
        return texto_original(fonte, texto, cor, *args, **kwargs)

    monkeypatch.setattr("game.screens_achievements.texto_com_borda", registrar_texto)
    monkeypatch.setattr(pygame.event, "get", lambda: [eventos.pop(0)])
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    screens.tela_conquistas(
        {"conquistas_desbloqueadas": ["intocavel"]},
        tela,
        pygame.time.Clock(),
        fontes,
        None,
        lambda evento: None,
        lambda dados: [
            {
                "nome": "Sobrevivente",
                "descricao": "Sobreviva cinco minutos.",
                "desbloqueada": False,
                "recompensa": 5000,
            },
            {
                "nome": "Intocável",
                "descricao": "Conclua sem dano.",
                "desbloqueada": True,
                "recompensa": 2500,
            },
        ],
    )

    assert "Sobrevivente - BLOQUEADA" in textos
    assert "Intocável - DESBLOQUEADA" in textos
    assert "Recompensa: 5000 moedas" in textos
    assert "Recompensa: 2500 moedas" in textos


def test_tela_selecao_modo_retorna_modo_confirmado(monkeypatch):
    pygame.init()
    tela = pygame.Surface((800, 600))
    fontes = tuple(pygame.font.SysFont("Noto Sans", tamanho) for tamanho in (32, 16, 16))
    textos = []
    eventos = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN),
    ]

    texto_original = screens.texto_com_borda

    def registrar_texto(fonte, texto, cor, *args, **kwargs):
        textos.append(texto)
        return texto_original(fonte, texto, cor, *args, **kwargs)

    monkeypatch.setattr("game.screens_menu.texto_com_borda", registrar_texto)
    monkeypatch.setattr(pygame.event, "get", lambda: [eventos.pop(0)])
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    modo = screens.tela_selecao_modo(
        tela, pygame.time.Clock(), fontes, None, lambda evento: None,
    )

    assert modo == "frota_inimiga"
    assert "ESCOLHA O MODO" in textos
    assert "Fases e chefes" in textos
    assert "Batalha contra naves" in textos
    assert "Sobreviva e pontue" in textos
    assert "← → / A D   •   ENTER escolher" in textos
    assert "Missão clássica contra meteoros e obstáculos." not in textos


def test_tela_selecao_nave_retorna_a_nave_selecionada(monkeypatch):
    pygame.init()
    tela = pygame.Surface((800, 600))
    pygame.display.set_mode((800, 600))
    fontes = tuple(pygame.font.SysFont("Noto Sans", tamanho) for tamanho in (32, 16, 16))
    eventos = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)]
    monkeypatch.setattr(pygame.event, "get", lambda: [eventos.pop(0)])
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    def carregar_imagem(path):
        if path.endswith("wrat.png"):
            raise FileNotFoundError(path)
        return pygame.Surface((200, 200), pygame.SRCALPHA)

    monkeypatch.setattr(pygame.image, "load", carregar_imagem)

    nave = screens.tela_selecao_nave(
        {"moedas": 0, "naves_desbloqueadas": ["Vanguard.png"], "niveis_melhorias": {}},
        tela, pygame.time.Clock(), fontes, None, lambda evento: None,
        lambda nome: nome, lambda dados: dados, lambda dados: None,
    )

    assert nave == "Vanguard.png"


def test_tela_melhorias_compra_e_persiste_upgrade(monkeypatch):
    tela = pygame.Surface((800, 600))
    fontes = tuple(pygame.font.SysFont("Noto Sans", tamanho) for tamanho in (32, 16, 16))
    eventos = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE),
    ]
    dados = {
        "moedas": 100,
        "naves_desbloqueadas": ["Vanguard.png"],
        "niveis_melhorias": {
            "velocidade": 1,
            "cadencia": 1,
            "especial": 1,
            "dano": 1,
            "defesa": 1,
            "vida": 1,
            "manobrabilidade": 1,
            "recarga": 1,
            "recompensa": 1,
        },
    }
    salvos = []
    monkeypatch.setattr(pygame.event, "get", lambda: [eventos.pop(0)])
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    screens.tela_melhorias(
        dados, tela, pygame.time.Clock(), fontes, None, lambda evento: None,
        lambda jogador: jogador, salvos.append, lambda nivel: 0.6,
    )

    assert dados["moedas"] == 70
    assert dados["niveis_melhorias"]["velocidade"] == 2
    assert salvos == [dados]


def test_tela_melhorias_compra_upgrade_de_dano(monkeypatch):
    tela = pygame.Surface((800, 600))
    fontes = tuple(pygame.font.SysFont("Noto Sans", tamanho) for tamanho in (32, 16, 16))
    eventos = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE),
    ]
    dados = {
        "moedas": 100,
        "naves_desbloqueadas": ["Vanguard.png"],
        "niveis_melhorias": {
            "velocidade": 1,
            "cadencia": 1,
            "especial": 1,
            "dano": 1,
            "defesa": 1,
            "vida": 1,
            "manobrabilidade": 1,
            "recarga": 1,
            "recompensa": 1,
        },
    }
    salvos = []
    monkeypatch.setattr(pygame.event, "get", lambda: [eventos.pop(0)])
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    screens.tela_melhorias(
        dados, tela, pygame.time.Clock(), fontes, None, lambda evento: None,
        lambda jogador: jogador, salvos.append, lambda nivel: 0.6,
    )

    assert dados["moedas"] == 50
    assert dados["niveis_melhorias"]["dano"] == 2
    assert salvos == [dados]


def test_tela_melhorias_compra_upgrade_de_defesa(monkeypatch):
    tela = pygame.Surface((800, 600))
    fontes = tuple(pygame.font.SysFont("Noto Sans", tamanho) for tamanho in (32, 16, 16))
    eventos = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE),
    ]
    dados = {
        "moedas": 100,
        "naves_desbloqueadas": ["Vanguard.png"],
        "niveis_melhorias": {
            "velocidade": 1,
            "cadencia": 1,
            "especial": 1,
            "dano": 1,
            "defesa": 1,
            "vida": 1,
            "manobrabilidade": 1,
            "recarga": 1,
            "recompensa": 1,
        },
    }
    salvos = []
    monkeypatch.setattr(pygame.event, "get", lambda: [eventos.pop(0)])
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    screens.tela_melhorias(
        dados, tela, pygame.time.Clock(), fontes, None, lambda evento: None,
        lambda jogador: jogador, salvos.append, lambda nivel: 0.6,
    )

    assert dados["moedas"] == 40
    assert dados["niveis_melhorias"]["defesa"] == 2
    assert salvos == [dados]


def test_tela_melhorias_nao_cobra_defesa_no_nivel_maximo(monkeypatch):
    tela = pygame.Surface((800, 600))
    fontes = tuple(pygame.font.SysFont("Noto Sans", tamanho) for tamanho in (32, 16, 16))
    eventos = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE),
    ]
    dados = {
        "moedas": 1000,
        "naves_desbloqueadas": ["Vanguard.png"],
        "niveis_melhorias": {
            "velocidade": 1,
            "cadencia": 1,
            "especial": 1,
            "dano": 1,
            "defesa": 5,
            "vida": 1,
            "manobrabilidade": 1,
            "recarga": 1,
            "recompensa": 1,
        },
    }
    salvos = []
    monkeypatch.setattr(pygame.event, "get", lambda: [eventos.pop(0)])
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    screens.tela_melhorias(
        dados, tela, pygame.time.Clock(), fontes, None, lambda evento: None,
        lambda jogador: jogador, salvos.append, lambda nivel: 0.6,
    )

    assert dados["moedas"] == 1000
    assert dados["niveis_melhorias"]["defesa"] == 5
    assert salvos == []


def test_tela_melhorias_compra_as_quatro_novas_melhorias(monkeypatch):
    pygame.init()
    tela = pygame.Surface((800, 600))
    fontes = tuple(pygame.font.SysFont("Noto Sans", tamanho) for tamanho in (32, 16, 16))
    monkeypatch.setattr(pygame.display, "flip", lambda: None)
    custos = {
        "vida": 45,
        "manobrabilidade": 35,
        "recarga": 50,
        "recompensa": 55,
    }

    for indice, (melhoria, custo) in enumerate(custos.items(), start=5):
        eventos = [
            *[
                pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
                for _ in range(indice)
            ],
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE),
        ]
        dados = {
            "moedas": 100,
            "naves_desbloqueadas": ["Vanguard.png"],
            "niveis_melhorias": {
                "velocidade": 1,
                "cadencia": 1,
                "especial": 1,
                "dano": 1,
                "defesa": 1,
                "vida": 1,
                "manobrabilidade": 1,
                "recarga": 1,
                "recompensa": 1,
            },
        }
        salvos = []
        monkeypatch.setattr(pygame.event, "get", lambda: [eventos.pop(0)])

        screens.tela_melhorias(
            dados, tela, pygame.time.Clock(), fontes, None, lambda evento: None,
            lambda jogador: jogador, salvos.append, lambda nivel: 0.6,
        )

        assert dados["moedas"] == 100 - custo
        assert dados["niveis_melhorias"][melhoria] == 2
        assert salvos == [dados]


def test_tela_game_over_salva_pontuacao_e_retorna(monkeypatch):
    tela = pygame.Surface((800, 600))
    fontes = tuple(pygame.font.SysFont("Noto Sans", tamanho) for tamanho in (32, 16, 16))
    eventos = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)]
    salvos = []
    monkeypatch.setattr(pygame.event, "get", lambda: [eventos.pop(0)])
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    screens.tela_game_over(
        80, 4, "infinito", "Vanguard.png", tela, pygame.time.Clock(), fontes,
        None, lambda evento: None,
        lambda *args: salvos.append(args),
        lambda limite: [],
    )

    assert salvos == [(80, "infinito", "Vanguard.png")]


def test_renderizador_compoe_fundo_sprites_hud_e_apresenta_frame(monkeypatch):
    tela = pygame.Surface((800, 600))
    fundo = pygame.Surface((800, 600))
    sprites = pygame.sprite.Group()
    fontes = tuple(pygame.font.SysFont("Noto Sans", tamanho) for tamanho in (32, 16, 16))
    hud = {
        "pontos": 50,
        "meta_pontos": 300,
        "fase_atual": 1,
        "moedas": 2,
        "vida": 80,
        "vida_maxima": 100,
        "energia_especial": 40,
        "inimigos_restantes": 0,
        "modo_jogo": "asteroides",
        "modelo_nave": "vanguard",
        "botao_pausa": pygame.Rect(680, 20, 100, 35),
    }
    chamadas = []
    monkeypatch.setattr("game.ui.desenhar_hud_jogo", lambda *args, **kwargs: chamadas.append("hud"))
    monkeypatch.setattr(pygame.display, "flip", lambda: chamadas.append("flip"))
    monkeypatch.setattr(sprites, "draw", lambda destino: chamadas.append("sprites"))

    desenhar_tela_jogo(tela, fundo, sprites, fontes, hud)

    assert tela.get_at((0, 0)) == fundo.get_at((0, 0))
    assert chamadas == ["sprites", "hud", "flip"]


def test_renderizador_de_pausa_desenha_overlay_e_textos(monkeypatch):
    tela = pygame.Surface((800, 600))
    sprites = pygame.sprite.Group()
    fontes = tuple(pygame.font.SysFont("Noto Sans", tamanho) for tamanho in (32, 16, 16))
    hud = {
        "pontos": 50,
        "meta_pontos": 300,
        "fase_atual": 1,
        "moedas": 2,
        "vida": 80,
        "vida_maxima": 100,
        "energia_especial": 40,
        "inimigos_restantes": 0,
        "modo_jogo": "asteroides",
        "modelo_nave": "vanguard",
        "botao_pausa": pygame.Rect(680, 20, 100, 35),
        "botao_abandonar": pygame.Rect(270, 370, 260, 44),
    }
    textos = []
    exibicoes = []
    original_texto = texto_com_borda

    def registrar_texto(fonte, texto, cor, *args, **kwargs):
        textos.append(texto)
        return original_texto(fonte, texto, cor, *args, **kwargs)

    monkeypatch.setattr("game.ui.texto_com_borda", registrar_texto)
    monkeypatch.setattr("game.ui.desenhar_hud_jogo", lambda *args, **kwargs: None)
    monkeypatch.setattr(pygame.display, "flip", lambda: exibicoes.append(True))

    desenhar_tela_jogo(tela, None, sprites, fontes, hud, pausado=True)

    assert "PAUSADO" in textos
    assert "Pressione [P] ou clique no botão para continuar" in textos
    assert "Abandonar partida" in textos
    assert tela.get_at((0, 0))[:3] == (10, 11, 20)
    assert exibicoes == [True]
