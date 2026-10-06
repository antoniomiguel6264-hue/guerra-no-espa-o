import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def resolver_caminho_arquivo(nome_arquivo):
    if not nome_arquivo:
        return nome_arquivo
    if os.path.isabs(nome_arquivo):
        return nome_arquivo
    return os.path.join(BASE_DIR, nome_arquivo)
