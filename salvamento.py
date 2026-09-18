import json
import os

ARQUIVO_DADOS = "dados_jogador.json"

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