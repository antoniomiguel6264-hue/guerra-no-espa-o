import os
import subprocess
import sys
from pathlib import Path


def test_importar_config_e_main_nao_inicializa_pygame():
    raiz_projeto = Path(__file__).resolve().parents[1]
    ambiente = os.environ.copy()
    ambiente.pop("SDL_VIDEODRIVER", None)
    ambiente.pop("SDL_AUDIODRIVER", None)

    resultado = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import pygame, config; "
                "antes = (pygame.get_init(), pygame.display.get_init(), pygame.font.get_init()); "
                "import main; "
                "depois = (pygame.get_init(), pygame.display.get_init(), pygame.font.get_init()); "
                "assert antes == (False, False, False); "
                "assert depois == antes; "
                "assert main.recursos_jogo is None"
            ),
        ],
        cwd=raiz_projeto,
        env=ambiente,
        check=False,
        capture_output=True,
        text=True,
    )

    assert resultado.returncode == 0, resultado.stderr
