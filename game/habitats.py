import pygame


HABITATS_POR_NAVE = {
    "Vanguard.png": {
        "nome": "Órbita Azul", "cor": (38, 112, 176), "fundo": "Órbita Azul.jpg",
    },
    "Scout.png": {
        "nome": "Cinturão de Cristal", "cor": (184, 126, 57),
        "fundo": "Cinturão de Cristal.jpg",
    },
    "Titan.png": {
        "nome": "Lua Vulcânica", "cor": (184, 67, 48), "fundo": "Lua Vulcânica.jpg",
    },
    "Phantom.png": {
        "nome": "Nebulosa Oculta", "cor": (77, 104, 133),
        "fundo": "Nebulosa Oculta.jpg",
    },
    "Aegis.png": {
        "nome": "Abismo Oceânico", "cor": (28, 148, 163),
        "fundo": "Abismo Oceânico.jpg",
    },
    "Tempest.png": {
        "nome": "Tempestade Iônica", "cor": (66, 151, 111),
        "fundo": "Tempestade Iônica.jpg",
    },
    "Nova.png": {
        "nome": "Mar de Plasma", "cor": (188, 154, 54),
        "fundo": "Mar de Plasma.jpg",
    },
    "Wraith.png": {
        "nome": "Colônia Silenciosa", "cor": (112, 123, 135),
        "fundo": "Colônia Silenciosa.jpg",
    },
    "Dreadnought.png": {
        "nome": "Fornalha de Guerra", "cor": (150, 48, 55),
        "fundo": "Fornalha de Guerra.jpg",
    },
    "Vortex.png": {
        "nome": "Redemoinho Cósmico", "cor": (45, 139, 173),
        "fundo": "Redemoinho Cósmico.jpg",
    },
    "Seraph.png": {
        "nome": "Jardins Celestes", "cor": (104, 158, 119),
        "fundo": "Jardins Celestes.jpg",
    },
}

HABITAT_PADRAO = HABITATS_POR_NAVE["Vanguard.png"]


def obter_habitat(arquivo_nave):
    if arquivo_nave == "titan Hellion Core.png":
        return HABITATS_POR_NAVE["Titan.png"]
    return HABITATS_POR_NAVE.get(arquivo_nave, HABITAT_PADRAO)


def aplicar_habitat(fundo, arquivo_nave):
    if fundo is None:
        return None

    camada = pygame.Surface(fundo.get_size(), pygame.SRCALPHA)
    camada.fill((*obter_habitat(arquivo_nave)["cor"], 48))
    fundo_habitat = fundo.copy()
    fundo_habitat.blit(camada, (0, 0))
    return fundo_habitat


def fundos_para_habitat(arquivo_nave, fundos_fase, fundo_habitat=None):
    fundos_tonalizados = tuple(
        aplicar_habitat(fundo_fase, arquivo_nave) for fundo_fase in fundos_fase
    )
    return (
        (fundo_habitat or fundos_tonalizados[0], *fundos_tonalizados)
        if fundos_tonalizados
        else ()
    )