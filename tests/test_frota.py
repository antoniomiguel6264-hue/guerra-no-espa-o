import os
import threading

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import config
import main
from entidades import Nave, NaveInimiga, calcular_meta_frota, gerar_frota_inimiga
from salvamento import listar_ranking, salvar_pontuacao


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


def test_modo_frota_nao_cria_asteroides():
    asteroides = main.criar_asteroides_iniciais(2, modo_frota=True)

    assert len(asteroides) == 0


def test_frota_inimiga_tem_vida_e_tiro_fraco():
    nave = NaveInimiga(100, 100, fase_atual=2)
    assert nave.vida >= 3

    alvo = main.Nave(200, 300, "Vanguard.png")
    tiro = nave.criar_tiro(alvo)

    assert tiro is not None
    assert tiro.velocidade < 10
    assert tiro.dano == 1


def test_jogador_usa_barra_de_vida():
    jogador = Nave(100, 100, "Vanguard.png")

    assert jogador.vida_maxima > 0
    assert jogador.vida == jogador.vida_maxima

    jogador.perder_vida()
    assert jogador.vida < jogador.vida_maxima
    assert not hasattr(jogador, "vidas")


def test_jogador_recupera_vida_ao_destruir_inimigo():
    jogador = Nave(100, 100, "Vanguard.png")
    jogador.vida = 40

    jogador.recuperar_vida(20)
    assert jogador.vida == 60
    jogador.recuperar_vida(80)
    assert jogador.vida == jogador.vida_maxima


def test_modo_infinito_nao_gera_frota_inimiga():
    frota_1 = main.gerar_frota_infinita(0)
    frota_2 = main.gerar_frota_infinita(500)

    assert frota_1 == []
    assert frota_2 == []


def test_ranking_salva_pontuacao_no_banco():
    salvar_pontuacao(1200, "infinito", "Vanguard.png")
    ranking = listar_ranking(limit=5)

    assert any(item["pontuacao"] == 1200 for item in ranking)
    assert any(item["modo"] == "infinito" for item in ranking)


def test_modo_frota_renderiza_hud_sem_erro():
    texto = main.texto_com_borda(main.fonte_hud, "MODO: FROTA INIMIGA", main.AMARELO)

    assert texto is not None
    assert texto.get_width() > 0
