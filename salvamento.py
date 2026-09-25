import json
import os
import sqlite3
from datetime import datetime

ARQUIVO_DADOS = "dados_jogador.json"
ARQUIVO_RANKING = "ranking.db"


def carregar_dados():
    dados_padrao = {
        "moedas": 0,
        "naves_desbloqueadas": ["Vanguard.png"],
        "niveis_melhorias": {
            "velocidade": 1,
            "cadencia": 1,
            "especial": 1
        }
    }
    
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r") as f:
                dados = json.load(f)
                for chave in dados_padrao:
                    if chave not in dados:
                        dados[chave] = dados_padrao[chave]
                for melh in dados_padrao["niveis_melhorias"]:
                    if melh not in dados["niveis_melhorias"]:
                        dados["niveis_melhorias"][melh] = 1
                return dados
        except Exception as e:
            print(f"Erro ao carregar save: {e}. Usando padrão.")
            return dados_padrao
    return dados_padrao


def salvar_dados(dados):
    try:
        with open(ARQUIVO_DADOS, "w") as f:
            json.dump(dados, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")


def inicializar_ranking():
    conexao = sqlite3.connect(ARQUIVO_RANKING)
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
    conexao.commit()
    conexao.close()


def salvar_pontuacao(pontuacao, modo, nave):
    inicializar_ranking()
    conexao = sqlite3.connect(ARQUIVO_RANKING)
    conexao.execute(
        "INSERT INTO ranking (pontuacao, modo, nave, data) VALUES (?, ?, ?, ?)",
        (int(pontuacao), modo, nave, datetime.now().strftime("%d/%m/%Y %H:%M")),
    )
    conexao.commit()
    conexao.close()


def listar_ranking(limit=10):
    inicializar_ranking()
    conexao = sqlite3.connect(ARQUIVO_RANKING)
    registros = conexao.execute(
        "SELECT pontuacao, modo, nave, data FROM ranking ORDER BY pontuacao DESC, id ASC LIMIT ?",
        (int(limit),),
    ).fetchall()
    conexao.close()
    return [
        {
            "pontuacao": pontuacao,
            "modo": modo,
            "nave": nave,
            "data": data,
        }
        for pontuacao, modo, nave, data in registros
    ]
