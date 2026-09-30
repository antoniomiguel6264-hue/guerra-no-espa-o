import array
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

SAMPLE_RATE = 22050


def gerar_tom(frequencia=440, duracao=0.12, volume=0.5, ataque=0.02):
    if frequencia <= 0:
        frequencia = 440

    total_amostras = max(1, int(SAMPLE_RATE * duracao))
    amostras = array.array('h')

    for indice in range(total_amostras):
        tempo = indice / SAMPLE_RATE
        if ataque > 0 and tempo <= ataque:
            envelope = min(1.0, tempo / ataque)
        elif ataque > 0 and tempo >= duracao - ataque:
            envelope = max(0.0, 1.0 - ((tempo - (duracao - ataque)) / ataque))
        else:
            envelope = 1.0

        valor = math.sin(2 * math.pi * frequencia * tempo)
        som = int(32767 * volume * envelope * valor)
        amostras.append(max(-32767, min(32767, som)))

    return amostras


def gerar_som_melodico(notas=None, duracao=0.25, volume=0.5):
    if not notas:
        notas = [220]

    total_amostras = max(1, int(SAMPLE_RATE * duracao))
    amostras = array.array('h', [0]) * total_amostras

    for index_nota, frequencia in enumerate(notas):
        nota_duracao = duracao / max(1, len(notas))
        inicio = int(index_nota * total_amostras / max(1, len(notas)))
        fim = int((index_nota + 1) * total_amostras / max(1, len(notas)))

        for indice in range(inicio, min(fim, total_amostras)):
            tempo = indice / SAMPLE_RATE
            tempo_nota = tempo - (inicio / SAMPLE_RATE)
            if tempo_nota <= 0.02:
                envelope = min(1.0, tempo_nota / 0.02)
            elif tempo_nota >= nota_duracao - 0.02:
                envelope = max(0.0, 1.0 - ((tempo_nota - (nota_duracao - 0.02)) / 0.02))
            else:
                envelope = 1.0

            valor = math.sin(2 * math.pi * frequencia * tempo)
            amostras[indice] += int(14000 * volume * envelope * valor)

    for indice, valor in enumerate(amostras):
        amostras[indice] = max(-32767, min(32767, valor))

    return amostras


def iniciar_audio():
    try:
        pygame.mixer.pre_init(22050, -16, 2, 4096)
        pygame.mixer.init()
        return True
    except Exception:
        return False


def tocar_som(notas, duracao=0.12, volume=0.35):
    try:
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()
    except Exception:
        return None

    try:
        amostras = gerar_som_melodico(notas, duracao=duracao, volume=volume)
        som = pygame.mixer.Sound(buffer=amostras.tobytes())
        som.set_volume(1.0)
        som.play()
        return som
    except Exception:
        return None
