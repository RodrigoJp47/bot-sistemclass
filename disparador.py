import pandas as pd
import requests
import time
import os
import random  # <--- IMPORTANTE: Adicionei esta biblioteca aqui!

# ==============================================================================
# 1. CONFIGURAÇÕES
# ==============================================================================
# Coloque sua chave do Wasender aqui (a mesma do bot.py)
API_KEY = "87cc26577dac7e7b62287fb2e3e54f40397395679518a15d1d731e041d00d462"
API_URL = "https://www.wasenderapi.com/api/send-message"

# Nome do arquivo da planilha
NOME_ARQUIVO = "lista_clientes.xlsx"

# Intervalo de tempo (Mínimo e Máximo em segundos)
TEMPO_MIN = 300
TEMPO_MAX = 600

# ==============================================================================
# 2. O CÓDIGO DO ROBÔ
# ==============================================================================
def enviar_disparos():
    # Verifica se o arquivo existe
    if not os.path.exists(NOME_ARQUIVO):
        print(f"ERRO: Não encontrei o arquivo '{NOME_ARQUIVO}'.")
        return

    # Lê a planilha
    try:
        df = pd.read_excel(NOME_ARQUIVO)
        # --- NOVO: SE A COLUNA STATUS NÃO EXISTIR, O ROBÔ CRIA ELA ---
        if 'Status' not in df.columns:
            df['Status'] = '' # Cria a coluna vazia na memória
    except Exception as e:
        print(f"Erro ao ler Excel: {e}")
        return

    print(f"--- Iniciando campanha para {len(df)} contatos ---")
    print(f"--- Modo Humano Ativado: Intervalos entre {TEMPO_MIN} e {TEMPO_MAX} segundos ---\n")

    # Loop linha por linha
    for index, linha in df.iterrows():
        # 1. LEITURA DOS DADOS (ISSO VEM PRIMEIRO)
        nome = str(linha.get('Nome', 'Cliente')) 
        telefone_bruto = str(linha.get('Telefone', ''))

        # 2. AGORA SIM, VERIFICA O STATUS
        status_atual = str(linha.get('Status', '')).strip().lower()
        if status_atual == 'enviado':
            print(f" -> Pulando {nome}: Já consta como Enviado.")
            continue
        

        # Limpeza do telefone
        telefone = "".join(filter(str.isdigit, telefone_bruto))

        if not telefone:
            continue

        if len(telefone) >= 10 and not telefone.startswith("55"):
            telefone = "55" + telefone

        # --- AJUSTE INTELIGENTE DE NOME ---
        if nome.lower() == "desconhecido":
            # Se não tem nome, usa saudação genérica
            mensagem = "Olá, tudo bem? Peguei seu contato no grupo de Bpo. Desenvolvemos uma ferramenta que pode ajudar e muito na sua operação. Posso te aprentar? Será bem rápido."
        else:
            # Se tem nome, usa o nome da pessoa
            mensagem = f"Olá {nome}, tudo bem? Peguei seu contato no grupo de Bpo. Desenvolvemos uma ferramenta que pode ajudar e muito na sua operação. Posso te aprentar? Será bem rápido."

        payload = {
            "to": telefone,
            "text": mensagem
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            print(f"[{index+1}/{len(df)}] Enviando para {nome} ({telefone})...")
            
            response = requests.post(API_URL, json=payload, headers=headers)
            
            if response.status_code == 200:
                print(f" -> Sucesso (API Aceitou): {response.text}")
                
                # --- NOVO: SALVA O STATUS NA PLANILHA ---
                df.at[index, 'Status'] = 'Enviado'
                try:
                    df.to_excel(NOME_ARQUIVO, index=False)
                except PermissionError:
                    print(f" [AVISO] Não foi possível salvar o Excel. Feche o arquivo '{NOME_ARQUIVO}'!")
            else:
                print(f" -> Erro na API: {response.text}")
            
            # --- O SEGREDO DO MODO HUMANO ---
            # Sorteia um número entre 60 e 120
            tempo_aleatorio = random.randint(TEMPO_MIN, TEMPO_MAX)
            
            print(f"Aguardando {tempo_aleatorio} segundos para parecer humano...\n")
            time.sleep(tempo_aleatorio)

        except Exception as e:
            print(f" -> Erro no envio: {e}")

    print("--- FIM DA LISTA ---")

if __name__ == "__main__":
    enviar_disparos()