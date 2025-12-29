import pandas as pd
import requests
import time
import os

# ==============================================================================
# 1. CONFIGURAÇÕES (Os Ajustes Ficam Aqui)
# ==============================================================================
# Coloque sua chave do Wasender aqui (a mesma do bot.py)
API_KEY = "87cc26577dac7e7b62287fb2e3e54f40397395679518a15d1d731e041d00d462"
API_URL = "https://www.wasenderapi.com/api/send-message"

# Nome do arquivo que você baixou da extensão e limpou
NOME_ARQUIVO = "lista_clientes.xlsx"

# Tempo de espera entre mensagens (EM SEGUNDOS)
# ATENÇÃO: Não diminua isso para menos de 60 se o chip for novo!
TEMPO_ESPERA = 60 

# ==============================================================================
# 2. O CÓDIGO DO ROBÔ
# ==============================================================================
def enviar_disparos():
    # Verifica se o arquivo existe
    if not os.path.exists(NOME_ARQUIVO):
        print(f"ERRO: Não encontrei o arquivo '{NOME_ARQUIVO}'.")
        print("Dica: Baixe a planilha, salve na mesma pasta deste script e renomeie para 'lista_clientes.xlsx'.")
        return

    # Lê a planilha
    try:
        df = pd.read_excel(NOME_ARQUIVO)
    except Exception as e:
        print(f"Erro ao ler Excel: {e}")
        return

    print(f"--- Iniciando campanha para {len(df)} contatos ---")
    print(f"--- Intervalo de segurança: {TEMPO_ESPERA} segundos ---\n")

    # Loop linha por linha
    for index, linha in df.iterrows():
        # Ajuste aqui conforme o nome das colunas no seu Excel
        # O ideal é você abrir o Excel antes e renomear o cabeçalho para 'Nome' e 'Telefone'
        nome = str(linha.get('Nome', 'Cliente')) 
        telefone_bruto = str(linha.get('Telefone', ''))

        # Limpeza básica do telefone (deixa só números)
        telefone = "".join(filter(str.isdigit, telefone_bruto))

        if not telefone:
            print(f"Pulei linha {index}: Sem telefone.")
            continue

        # Garante o 55 do Brasil
        if len(telefone) >= 10 and not telefone.startswith("55"):
            telefone = "55" + telefone

        # A MENSAGEM (Sua estratégia de venda)
        mensagem = f"Olá {nome}, tudo bem? Encontrei sua empresa no Google Maps e vi que a operação é intensa. Vocês já usam algum sistema financeiro integrado hoje?"

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
            
            # --- O DISPARO REAL ---
            response = requests.post(API_URL, json=payload, headers=headers)
            
            if response.status_code == 200:
                print(f" -> API Aceitou: {response.text}") # <--- Vai mostrar o detalhe técnico
            else:
                print(f" -> Erro na API: {response.text}")
            
            # --- PAUSA DE SEGURANÇA ---
            print(f"Aguardando {TEMPO_ESPERA} segundos para o próximo...\n")
            time.sleep(TEMPO_ESPERA)

        except Exception as e:
            print(f" -> Erro no envio: {e}")

    print("--- FIM DA LISTA ---")

if __name__ == "__main__":
    enviar_disparos()