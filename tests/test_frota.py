import os
import threading

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import config
import main
from entidades import calcular_meta_frota, gerar_frota_inimiga


def test_frota_inimiga_preserva_fases_e_gera_navios():
    frota = gerar_frota_inimiga(3)

    assert len(frota) > 0
    assert all(getattr(nave, "fase", None) == 3 for nave in frota)
    assert all(0 <= nave.rect.x <= config.LARGURA for nave in frota)
    assert all(nave.rect.y < config.ALTURA for nave in frota)


def test_meta_dedicada_para_modo_frota():
    frota = gerar_frota_inimiga(2)
    meta = calcular_meta_frota(2, frota)

    assert meta > 0
    assert meta >= len(frota) * 25


def test_modo_frota_renderiza_hud_sem_erro():
    threading.Timer(0.2, lambda: pygame.event.post(pygame.event.Event(pygame.QUIT))).start()

    try:
        main.jogo_principal(
            "Vanguard.png",
            {"velocidade": 1, "cadencia": 1, "especial": 1},
            1,
            "frota_inimiga",
        )
    except SystemExit:
        pass
