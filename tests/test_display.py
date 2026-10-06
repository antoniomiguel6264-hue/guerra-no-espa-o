import pygame

from game.display import DisplayMode


def test_f11_alterna_fullscreen_e_restaura_tamanho_da_janela(monkeypatch):
    janela = pygame.Surface((800, 600))
    fullscreen = pygame.Surface((1920, 1080))
    chamadas = []

    def set_mode(size, flags):
        chamadas.append((size, flags))
        return fullscreen if flags == pygame.FULLSCREEN else pygame.Surface(size)

    monkeypatch.setattr(pygame.display, "set_mode", set_mode)
    modo_tela = DisplayMode(janela)

    tela_fullscreen = modo_tela.handle_event(
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11)
    )
    assert tela_fullscreen.get_size() == (1920, 1080)
    assert modo_tela.fullscreen

    tela_janela = modo_tela.handle_event(
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11)
    )
    assert tela_janela.get_size() == (800, 600)
    assert not modo_tela.fullscreen
    assert chamadas == [
        ((0, 0), pygame.FULLSCREEN),
        ((800, 600), pygame.RESIZABLE),
    ]


def test_redimensionar_janela_atualiza_o_tamanho_guardado(monkeypatch):
    chamadas = []

    def set_mode(size, flags):
        chamadas.append((size, flags))
        return pygame.Surface(size)

    monkeypatch.setattr(pygame.display, "set_mode", set_mode)
    modo_tela = DisplayMode(pygame.Surface((800, 600)))

    tela = modo_tela.handle_event(
        pygame.event.Event(pygame.VIDEORESIZE, w=1024, h=768)
    )

    assert tela.get_size() == (1024, 768)
    assert modo_tela.window_size == (1024, 768)
    assert chamadas == [((1024, 768), pygame.RESIZABLE)]
