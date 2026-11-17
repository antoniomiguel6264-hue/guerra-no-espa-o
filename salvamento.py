import copy
import json
import os
import sqlite3
import tempfile
from contextlib import closing
from datetime import datetime

from game.rewards import MAX_FASES_CAMPANHA, RECOMPENSAS_POR_MARCO

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
            "dano": 1,
            "defesa": 1,
            "vida": 1,
            "manobrabilidade": 1,
            "recarga": 1,
            "recompensa": 1,
        },
        "fases_desbloqueadas": {
            "asteroides": 1,
            "frota_inimiga": 1,
        },
        "fases_concluidas_por_modo": {
            "asteroides": 0,
            "frota_inimiga": 0,
        },
        "skins_desbloqueadas": [],
        "recompensas_pendentes": [],
        "recompensas_resgatadas": [],
        "conquistas_desbloqueadas": [],
        "recompensas_conquistas": [],
    }

    if not isinstance(dados, dict):
        dados = {}
    else:
        dados = copy.deepcopy(dados)
    possui_progresso_detalhado = "fases_concluidas_por_modo" in dados

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
    fases_desbloqueadas = dados.get("fases_desbloqueadas", {})
    if not isinstance(fases_desbloqueadas, dict):
        fases_desbloqueadas = {}
    fases_normalizadas = {}
    for modo in ("asteroides", "frota_inimiga"):
        try:
            fase = int(fases_desbloqueadas.get(modo, 1))
        except (TypeError, ValueError):
            fase = 1
        fases_normalizadas[modo] = min(MAX_FASES_CAMPANHA, max(1, fase))
    dados["fases_desbloqueadas"] = fases_normalizadas

    progresso_salvo = dados.get("fases_concluidas_por_modo", {})
    if not isinstance(progresso_salvo, dict):
        progresso_salvo = {}
    progresso_normalizado = {}
    for modo in ("asteroides", "frota_inimiga"):
        progresso_padrao = fases_normalizadas[modo] - 1
        try:
            fases_concluidas = int(
                progresso_salvo.get(modo, progresso_padrao)
                if possui_progresso_detalhado
                else progresso_padrao
            )
        except (TypeError, ValueError):
            fases_concluidas = progresso_padrao
        progresso_normalizado[modo] = min(
            MAX_FASES_CAMPANHA,
            max(0, fases_concluidas),
        )
    progresso_global = max(progresso_normalizado.values())
    for modo in fases_normalizadas:
        fases_normalizadas[modo] = max(
            fases_normalizadas[modo],
            min(MAX_FASES_CAMPANHA, progresso_global + 1),
        )
    dados["fases_concluidas_por_modo"] = progresso_normalizado

    for chave in (
        "skins_desbloqueadas",
        "recompensas_pendentes",
        "recompensas_resgatadas",
    ):
        valores = dados.get(chave, [])
        if not isinstance(valores, list):
            valores = []
        dados[chave] = list(
            dict.fromkeys(valor for valor in valores if isinstance(valor, str))
        )
    for marco, recompensa in RECOMPENSAS_POR_MARCO.items():
        recompensa_id = recompensa["id"]
        if (
            progresso_global >= marco
            and recompensa_id not in dados["recompensas_pendentes"]
            and recompensa_id not in dados["recompensas_resgatadas"]
        ):
            dados["recompensas_pendentes"].append(recompensa_id)
    conquistas = dados.get("conquistas_desbloqueadas", [])
    if not isinstance(conquistas, list):
        conquistas = []
    dados["conquistas_desbloqueadas"] = conquistas
    recompensas_conquistas = dados.get("recompensas_conquistas", [])
    if not isinstance(recompensas_conquistas, list):
        recompensas_conquistas = []
    recompensas_conquistas = [
        recompensa
        for recompensa in recompensas_conquistas
        if isinstance(recompensa, str)
    ]
    dados["recompensas_conquistas"] = list(dict.fromkeys(recompensas_conquistas))
    return dados


def carregar_dados():
    dados_padrao = {
        "moedas": 0,
        "naves_desbloqueadas": ["Vanguard.png"],
        "niveis_melhorias": {
            "velocidade": 1,
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
        "recompensas_conquistas": [],
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
                """
                SELECT pontuacao, modo, nave, data
                FROM ranking AS atual
                WHERE atual.id = (
                    SELECT historico.id
                    FROM ranking AS historico
                    WHERE historico.modo = atual.modo
                      AND historico.nave = atual.nave
                    ORDER BY historico.pontuacao DESC, historico.id ASC
                    LIMIT 1
                )
                ORDER BY pontuacao DESC, id ASC
                LIMIT ?
                """,
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
