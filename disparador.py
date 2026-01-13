import pandas as pd
import requests
import time
import os
import random
from datetime import datetime

API_KEY = "87cc26577dac7e7b62287fb2e3e54f40397395679518a15d1d731e041d00d462"
API_URL = "https://www.wasenderapi.com/api/send-message"
NOME_ARQUIVO = "lista_clientes.xlsx"
TEMPO_MIN = 400
TEMPO_MAX = 900

def enviar_disparos():
    if not os.path.exists(NOME_ARQUIVO):
        print(f"ERRO: Arquivo '{NOME_ARQUIVO}' não encontrado.")
        return

    try:
        df = pd.read_excel(NOME_ARQUIVO)
        if 'Status' not in df.columns:
            df['Status'] = '' 
    except Exception as e:
        print(f"Erro ao ler Excel: {e}")
        return

    print(f"--- Iniciando campanha (Modo Curto e Direto) ---")

    for index, linha in df.iterrows():
        # --- TRAVA DE HORÁRIO ---
        agora = datetime.now()
        hora = agora.hour # Pega só a hora (ex: 9, 14, 19)
        
        # Se for antes das 9h OU depois das 18h (considerando 18:00 o limite)
        if hora < 9 or hora >= 19:
            print(f"🚫 Fora do horário comercial ({agora.strftime('%H:%M')}). Parando o robô por segurança.")
            break # Encerra o loop e para o programa
        nome = str(linha.get('Nome', 'Cliente')) 
        telefone_bruto = str(linha.get('Telefone', ''))
        status_atual = str(linha.get('Status', '')).strip().lower()

        if status_atual == 'enviado': continue
        
        telefone = "".join(filter(str.isdigit, telefone_bruto))
        if not telefone: continue
        if len(telefone) >= 10 and not telefone.startswith("55"): telefone = "55" + telefone

        mensagem = """Olá! Tudo bem?

Vi que você atua com BPO Financeiro. Uma dúvida rápida:

Como você apresenta os resultados dos seus clientes ? 

Nós criamos um sistema que gera BI ( Business Intelligence ) em tempo real para o seu cliente. 

DRE Gerêncial/Fluxo de Caixa  e Dashboards automáticos para te tirar do operacional e gerar valor na sua operação. 

Posso te liberar um acesso teste gratuito para você ver como funciona por dentro?"""

        
        payload = {"to": telefone, "text": mensagem}
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

        try:
            print(f"[{index+1}/{len(df)}] Enviando Isca para {nome}...")
            response = requests.post(API_URL, json=payload, headers=headers)
            
            if response.status_code == 200:
                print(f" -> Sucesso.")
                df.at[index, 'Status'] = 'Enviado'
                try:
                    df.to_excel(NOME_ARQUIVO, index=False)
                except: pass
            else:
                print(f" -> Erro API: {response.text}")
            
            tempo = random.randint(TEMPO_MIN, TEMPO_MAX)
            print(f"Aguardando {tempo}s...\n")
            time.sleep(tempo)

        except Exception as e:
            print(f" -> Erro envio: {e}")

if __name__ == "__main__":
    enviar_disparos()