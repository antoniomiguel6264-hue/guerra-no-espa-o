import os
from dataclasses import dataclass
from typing import Callable

import pygame

import config
from audio import iniciar_audio
from game.display import DisplayMode


@dataclass(frozen=True)
class GameResources:
    tela: pygame.Surface
    modo_tela: DisplayMode
    relogio: pygame.time.Clock
    fontes: tuple[pygame.font.Font, pygame.font.Font, pygame.font.Font]
    fundo_img: pygame.Surface | None
    fundo_infinito: pygame.Surface | None
    fundos_fase: tuple[
        pygame.Surface | None,
        pygame.Surface | None,
        pygame.Surface | None,
        pygame.Surface | None,
    ]
    fundo_selecao: pygame.Surface | None
    fundo_fim: pygame.Surface | None


def _preparar_driver_grafico():
    if (
        not os.environ.get("SDL_VIDEODRIVER")
        and not os.environ.get("DISPLAY")
        and not os.environ.get("WAYLAND_DISPLAY")
    ):
        os.environ["SDL_VIDEODRIVER"] = "dummy"


def _carregar_fundo(nome_arquivo, resolver_caminho_arquivo, tamanho):
    try:
        imagem = pygame.image.load(resolver_caminho_arquivo(nome_arquivo)).convert()
        return pygame.transform.scale(imagem, tamanho)
    except Exception as exc:
        print(f"Erro ao carregar {nome_arquivo}: {exc}. Usando fundo preto.")
        return None


def criar_recursos_jogo(
    resolver_caminho_arquivo: Callable[[str], str],
) -> GameResources:
    _preparar_driver_grafico()
    try:
        pygame.init()
        tela = pygame.display.set_mode(
            (config.LARGURA, config.ALTURA),
            pygame.RESIZABLE,
        )
        pygame.display.set_caption("Space Shooter - Soldado Cósmico")
    except Exception as exc:
        print(f"Erro ao iniciar o pygame: {exc}")
        print("Sem ambiente gráfico disponível. Em Linux/servidor, rode com 'xvfb-run -a python3 main.py' ou em uma máquina com interface gráfica.")
        raise SystemExit(1) from exc

    iniciar_audio()
    fontes = (
        pygame.font.SysFont("Noto Sans", 32, bold=True),
        pygame.font.SysFont("Noto Sans", 16),
        pygame.font.SysFont("Noto Sans", 16, bold=True),
    )
    tamanho_tela = tela.get_size()
    fundo_img = _carregar_fundo(
        "chagada.jpg",
        resolver_caminho_arquivo,
        tamanho_tela,
    )
    fundo_infinito = _carregar_fundo(
        "infinito.jpg",
        resolver_caminho_arquivo,
        tamanho_tela,
    )
    fundos_fase = tuple(
        _carregar_fundo(f"fase{fase}.jpg", resolver_caminho_arquivo, tamanho_tela)
        for fase in range(1, 5)
    )
    fundo_selecao = _carregar_fundo(
        "tela preta.jpg",
        resolver_caminho_arquivo,
        tamanho_tela,
    )
    fundo_fim = _carregar_fundo(
        "fim.jpg",
        resolver_caminho_arquivo,
        tamanho_tela,
    )

    return GameResources(
        tela=tela,
        modo_tela=DisplayMode(tela),
        relogio=pygame.time.Clock(),
        fontes=fontes,
        fundo_img=fundo_img,
        fundo_infinito=fundo_infinito,
        fundos_fase=fundos_fase,
        fundo_selecao=fundo_selecao,
        fundo_fim=fundo_fim,
    )
