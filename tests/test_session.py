import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import main
import pygame

import game.session as game_session
from game.entities.enemies import ChefeFrota
from game.entities.projectiles import Tiro
from game.session import (
    SessionServices,
    _calcular_dano_colisao,
    _selecionar_fundo_sessao,
)
from game.balance import calcular_bonus_moedas_inimigo


def test_modo_infinito_usa_fundo_infinito_sem_mudar_fundos_de_fase():
    fundos_fase = ("fase 1", "fase 2", "fase 3", "fase 4")
    fundo_infinito = "infinito"

    assert _selecionar_fundo_sessao(
        "infinito", 1, fundos_fase, fundo_infinito
    ) == fundo_infinito
    assert _selecionar_fundo_sessao(
        "asteroides", 1, fundos_fase, fundo_infinito
    ) == fundos_fase[0]
    assert _selecionar_fundo_sessao(
        "frota_inimiga", 4, fundos_fase, fundo_infinito
    ) == fundos_fase[3]


def test_dano_de_contato_e_tiros_e_reduzido_apenas_no_modo_frota():
    assert _calcular_dano_colisao("frota_inimiga", False, 20) == 10
    assert _calcular_dano_colisao("frota_inimiga", False, 20, nivel_defesa=2) == 8
    assert _calcular_dano_colisao("frota_inimiga", False, 20, nivel_defesa=5) == 2
    assert _calcular_dano_colisao("asteroides", False, 20) == 20
    assert _calcular_dano_colisao("infinito", False, 10) == 20
    assert _calcular_dano_colisao("frota_inimiga", True, 20) == 20


def test_recompensa_bonus_aplica_apenas_por_inimigo_derrotado():
    assert calcular_bonus_moedas_inimigo(1) == 0
    assert calcular_bonus_moedas_inimigo(3) == 2


def test_jogo_principal_delega_sessao_com_servicos_explicitos(monkeypatch):
    main.inicializar_app()
    chamada = {}

    def executar_sessao(*args, services):
        chamada["args"] = args
        chamada["services"] = services
        return 120, 3, True, False

    monkeypatch.setattr(main, "run_game_session", executar_sessao)

    resultado = main.jogo_principal(
        "Vanguard.png",
        {"cadencia": 1},
        fase_atual=2,
        modo_jogo="frota_inimiga",
        dados_jogador={"moedas": 0},
    )

    assert resultado == (120, 3, True, False)
    assert chamada["args"] == (
        "Vanguard.png",
        {"cadencia": 1},
        2,
        "frota_inimiga",
        {"moedas": 0},
    )
    assert chamada["services"].clock is main.relogio
    assert chamada["services"].resize_display is main.atualizar_tamanho_tela
    assert chamada["services"].asteroid_damage is main.calcular_dano_asteroide
    assert chamada["services"].infinite_background is main.fundo_infinito


def test_abandonar_pela_pausa_encerra_sessao_sem_vitoria(monkeypatch):
    pygame.init()
    pygame.display.set_mode((800, 600))
    eventos = iter(
        (
            [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(730, 30))],
            [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(400, 392))],
        )
    )

    class NaveFalsa(pygame.sprite.Sprite):
        def __init__(self, *args):
            super().__init__()
            self.modelo = "vanguard"
            self.vida = 100
            self.vida_maxima = 100
            self.energia_especial = 0
            self.dano_sofrido = False

    class RelogioFalso:
        def tick(self, fps):
            return 16

    monkeypatch.setattr(game_session, "Nave", NaveFalsa)
    monkeypatch.setattr(pygame.event, "get", lambda: next(eventos))
    monkeypatch.setattr(game_session, "desenhar_tela_jogo", lambda *args, **kwargs: None)

    def grupo_vazio(*args, **kwargs):
        return pygame.sprite.Group()

    services = SessionServices(
        get_screen=lambda: pygame.display.get_surface(),
        clock=RelogioFalso(),
        fonts=(None, None, None),
        backgrounds=(None, None, None, None),
        infinite_background=None,
        resize_display=lambda evento: (800, 600),
        create_initial_asteroids=grupo_vazio,
        create_infinite_asteroids=grupo_vazio,
        asteroid_damage=lambda modo: 10,
        save_player=lambda dados: None,
        play_sound=lambda *args, **kwargs: None,
    )

    resultado = game_session.run_game_session(
        "Vanguard.png",
        {"cadencia": 1},
        services=services,
    )

    assert resultado == (0, 0, False, True)


def test_modo_frota_exige_derrotar_chefe_depois_da_meta(monkeypatch):
    pygame.init()
    pygame.display.set_mode((800, 600))

    class NaveJogadorFalsa(pygame.sprite.Sprite):
        dano_registrado = 0

        def __init__(self, *args):
            super().__init__()
            self.image = pygame.Surface((68, 68))
            self.rect = self.image.get_rect(center=(400, 520))
            self.modelo = "vanguard"
            self.vida = 100
            self.vida_maxima = 100
            self.energia_especial = 0
            self.dano_sofrido = False

        def update(self, *args):
            pass

        def criar_tiros_basicos(self):
            return [Tiro(self.rect.centerx, self.rect.centery, 90)]

        def perder_vida(self, dano):
            self.vida -= dano
            self.dano_sofrido = True
            return self.vida <= 0

        def aplicar_pontos_para_cura(self, pontos):
            pass

        def recuperar_vida(self, quantidade):
            self.vida = min(self.vida_maxima, self.vida + quantidade)

        def adicionar_energia(self, quantidade):
            pass

        def adicionar_energia_por_dano(self, dano):
            type(self).dano_registrado += dano

    class InimigoFalso(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.image = pygame.Surface((50, 50))
            self.rect = self.image.get_rect(center=(400, 500))
            self.vida = 1
            self.cooldown_tiro = 10000

        def update(self):
            pass

    class ChefeTeste(ChefeFrota):
        def __init__(self, x, y, fase_atual):
            super().__init__(x, y, fase_atual)
            self.vida = 2
            self.vida_maxima = 2
            self.cooldown_tiro = 10000

        def update(self):
            pass

    class Teclas:
        def __getitem__(self, tecla):
            return tecla == pygame.K_j

    class RelogioFalso:
        def tick(self, fps):
            return 16

    monkeypatch.setattr(game_session, "Nave", NaveJogadorFalsa)
    monkeypatch.setattr(game_session, "ChefeFrota", ChefeTeste)
    monkeypatch.setattr(game_session, "gerar_frota_inimiga", lambda fase: [InimigoFalso()])
    monkeypatch.setattr(game_session, "calcular_meta_frota", lambda fase, frota: 1)
    monkeypatch.setattr(pygame.event, "get", lambda: [])
    monkeypatch.setattr(pygame.key, "get_pressed", lambda: Teclas())
    monkeypatch.setattr(game_session, "desenhar_tela_jogo", lambda *args, **kwargs: None)

    def grupo_vazio(*args, **kwargs):
        return pygame.sprite.Group()

    services = SessionServices(
        get_screen=lambda: pygame.display.get_surface(),
        clock=RelogioFalso(),
        fonts=(None, None, None),
        backgrounds=(None, None, None, None),
        infinite_background=None,
        resize_display=lambda evento: (800, 600),
        create_initial_asteroids=grupo_vazio,
        create_infinite_asteroids=grupo_vazio,
        asteroid_damage=lambda modo: 10,
        save_player=lambda dados: None,
        play_sound=lambda *args, **kwargs: None,
    )

    resultado = game_session.run_game_session(
        "Vanguard.png",
        {"velocidade": 1, "cadencia": 1, "especial": 1},
        modo_jogo="frota_inimiga",
        services=services,
    )

    assert resultado == (180, 12, True, False)
    assert NaveJogadorFalsa.dano_registrado == 3
