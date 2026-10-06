import copy
import json
import os
import sqlite3
import tempfile
from contextlib import closing
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_DADOS = os.path.join(BASE_DIR, "dados_jogador.json")
ARQUIVO_RANKING = os.path.join(BASE_DIR, "ranking.db")


def normalizar_dados_jogador(dados):
    dados_padrao = {
        "moedas": 0,
        "naves_desbloqueadas": ["Vanguard.png"],
        "niveis_melhorias": {
            "velocidade": 1,
            "cadencia": 1,
            "especial": 1,
        },
        "conquistas_desbloqueadas": [],
    }

    if not isinstance(dados, dict):
        dados = {}
    else:
        dados = copy.deepcopy(dados)

    for chave, valor_padrao in dados_padrao.items():
        if chave not in dados:
            dados[chave] = valor_padrao

    try:
        dados["moedas"] = int(dados.get("moedas", 0) or 0)
    except (TypeError, ValueError):
        dados["moedas"] = 0

    naves = dados.get("naves_desbloqueadas", [])
    if not isinstance(naves, list):
        naves = [naves] if naves else []
    naves = [str(nave) for nave in naves if nave is not None]
    if "Vanguard.png" not in naves:
        naves.insert(0, "Vanguard.png")
    dados["naves_desbloqueadas"] = list(dict.fromkeys(naves))

    niveis = dados.get("niveis_melhorias", {})
    if not isinstance(niveis, dict):
        niveis = {}

    for nome_melhoria, valor_padrao in dados_padrao["niveis_melhorias"].items():
        valor_atual = niveis.get(nome_melhoria, valor_padrao)
        try:
            nivel = int(valor_atual)
        except (TypeError, ValueError):
            nivel = valor_padrao
        if nivel < 1:
            nivel = valor_padrao
        niveis[nome_melhoria] = max(1, int(nivel))

    dados["niveis_melhorias"] = niveis
    conquistas = dados.get("conquistas_desbloqueadas", [])
    if not isinstance(conquistas, list):
        conquistas = []
    dados["conquistas_desbloqueadas"] = conquistas
    return dados


def carregar_dados():
    dados_padrao = {
        "moedas": 0,
        "naves_desbloqueadas": ["Vanguard.png"],
        "niveis_melhorias": {
            "velocidade": 1,
            "cadencia": 1,
            "especial": 1
        },
        "conquistas_desbloqueadas": [],
    }
    
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                dados = json.load(f)
                dados = normalizar_dados_jogador(dados)
                return dados
        except (OSError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar save: {e}. Usando padrão.")
            return normalizar_dados_jogador(dados_padrao)
    return normalizar_dados_jogador(dados_padrao)


def salvar_dados(dados):
    dados_normalizados = normalizar_dados_jogador(dados)
    diretorio = os.path.dirname(ARQUIVO_DADOS)
    nome_temporario = None
    try:
        descritor, nome_temporario = tempfile.mkstemp(
            prefix=f".{os.path.basename(ARQUIVO_DADOS)}.",
            suffix=".tmp",
            dir=diretorio,
        )
        with os.fdopen(descritor, "w", encoding="utf-8") as arquivo:
            json.dump(dados_normalizados, arquivo, indent=4, ensure_ascii=False)
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(nome_temporario, ARQUIVO_DADOS)
    except Exception:
        if nome_temporario is not None:
            try:
                os.unlink(nome_temporario)
            except FileNotFoundError:
                pass
        raise


def inicializar_ranking():
    with closing(sqlite3.connect(ARQUIVO_RANKING)) as conexao:
        with conexao:
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS ranking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pontuacao INTEGER NOT NULL,
                    modo TEXT NOT NULL,
                    nave TEXT NOT NULL,
                    data TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )


def salvar_pontuacao(pontuacao, modo, nave):
    inicializar_ranking()
    with closing(sqlite3.connect(ARQUIVO_RANKING)) as conexao:
        with conexao:
            conexao.execute(
                "INSERT INTO ranking (pontuacao, modo, nave, data) VALUES (?, ?, ?, ?)",
                (int(pontuacao), modo, nave, datetime.now().strftime("%d/%m/%Y %H:%M")),
            )


def listar_ranking(limit=10):
    inicializar_ranking()
    with closing(sqlite3.connect(ARQUIVO_RANKING)) as conexao:
        with conexao:
            registros = conexao.execute(
                "SELECT pontuacao, modo, nave, data FROM ranking ORDER BY pontuacao DESC, id ASC LIMIT ?",
                (int(limit),),
            ).fetchall()
    return [
        {
            "pontuacao": pontuacao,
            "modo": modo,
            "nave": nave,
            "data": data,
        }
        for pontuacao, modo, nave, data in registros
    ]
