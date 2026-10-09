import json
import subprocess
import sys
from pathlib import Path

import pytest

import salvamento


def test_importar_salvamento_nao_importa_dominio_de_conquistas():
    raiz_projeto = Path(__file__).resolve().parents[1]
    resultado = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys, salvamento; assert 'game.achievements' not in sys.modules",
        ],
        cwd=raiz_projeto,
        check=False,
        capture_output=True,
        text=True,
    )

    assert resultado.returncode == 0, resultado.stderr


def test_salvar_dados_grava_dados_normalizados_atomicos(tmp_path, monkeypatch):
    caminho_save = tmp_path / "dados_jogador.json"
    monkeypatch.setattr(salvamento, "ARQUIVO_DADOS", str(caminho_save))
    dados = {
        "moedas": "25",
        "naves_desbloqueadas": ["Scout.png", "Scout.png"],
        "niveis_melhorias": {"velocidade": 2},
    }

    salvamento.salvar_dados(dados)

    assert json.loads(caminho_save.read_text()) == {
        "moedas": 25,
        "naves_desbloqueadas": ["Vanguard.png", "Scout.png"],
        "niveis_melhorias": {
            "velocidade": 2,
            "cadencia": 1,
            "especial": 1,
            "dano": 1,
            "defesa": 1,
            "vida": 1,
            "manobrabilidade": 1,
            "recarga": 1,
            "recompensa": 1,
        },
        "conquistas_desbloqueadas": [],
        "conquistas_desbloqueadas": [],
    }
    assert dados == {
        "moedas": "25",
        "naves_desbloqueadas": ["Scout.png", "Scout.png"],
        "niveis_melhorias": {"velocidade": 2},
    }
    assert list(tmp_path.iterdir()) == [caminho_save]


def test_falha_ao_substituir_save_preserva_arquivo_anterior(tmp_path, monkeypatch):
    caminho_save = tmp_path / "dados_jogador.json"
    caminho_save.write_text('{"moedas": 17}')
    monkeypatch.setattr(salvamento, "ARQUIVO_DADOS", str(caminho_save))

    def falhar_substituicao(origem, destino):
        raise OSError("disco indisponível")

    monkeypatch.setattr(salvamento.os, "replace", falhar_substituicao)

    with pytest.raises(OSError, match="disco indisponível"):
        salvamento.salvar_dados({"moedas": 30})

    assert json.loads(caminho_save.read_text()) == {"moedas": 17}
    assert list(tmp_path.iterdir()) == [caminho_save]


def test_carregar_save_corrompido_retorna_padrao(tmp_path, monkeypatch, capsys):
    caminho_save = tmp_path / "dados_jogador.json"
    caminho_save.write_text("{ JSON incompleto")
    monkeypatch.setattr(salvamento, "ARQUIVO_DADOS", str(caminho_save))

    dados = salvamento.carregar_dados()

    assert dados["moedas"] == 0
    assert dados["naves_desbloqueadas"] == ["Vanguard.png"]
    assert dados["niveis_melhorias"] == {
        "velocidade": 1,
        "cadencia": 1,
        "especial": 1,
        "dano": 1,
        "defesa": 1,
        "vida": 1,
        "manobrabilidade": 1,
        "recarga": 1,
        "recompensa": 1,
    }
    assert "Erro ao carregar save" in capsys.readouterr().out


def test_normalizacao_de_save_preserva_ids_de_conquista_sem_conhecer_catalogo():
    dados = salvamento.normalizar_dados_jogador(
        {"conquistas_desbloqueadas": ["sobrevivente", "conquista_futura"]}
    )

    assert dados["conquistas_desbloqueadas"] == [
        "sobrevivente",
        "conquista_futura",
    ]


def test_ranking_fecha_conexao_e_salva_no_banco_de_teste(tmp_path, monkeypatch):
    caminho_db = tmp_path / "ranking.db"
    monkeypatch.setattr(salvamento, "ARQUIVO_RANKING", str(caminho_db))

    salvamento.salvar_pontuacao(450, "frota_inimiga", "Aegis.png")

    ranking = salvamento.listar_ranking(limit=1)
    assert len(ranking) == 1
    assert ranking[0]["pontuacao"] == 450
    assert ranking[0]["modo"] == "frota_inimiga"
    assert ranking[0]["nave"] == "Aegis.png"
    assert ranking[0]["data"]


def test_ranking_mostra_recorde_independente_por_modo_e_nave(tmp_path, monkeypatch):
    caminho_db = tmp_path / "ranking.db"
    monkeypatch.setattr(salvamento, "ARQUIVO_RANKING", str(caminho_db))

    salvamento.salvar_pontuacao(450, "asteroides", "Aegis.png")
    salvamento.salvar_pontuacao(700, "asteroides", "Aegis.png")
    salvamento.salvar_pontuacao(600, "infinito", "Aegis.png")
    salvamento.salvar_pontuacao(500, "asteroides", "Scout.png")

    ranking = salvamento.listar_ranking(limit=10)

    assert [(item["pontuacao"], item["modo"], item["nave"]) for item in ranking] == [
        (700, "asteroides", "Aegis.png"),
        (600, "infinito", "Aegis.png"),
        (500, "asteroides", "Scout.png"),
    ]
