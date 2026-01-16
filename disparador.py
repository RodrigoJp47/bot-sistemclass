
# import pandas as pd
# import requests
# import time
# import os
# import random
# from datetime import datetime
# from dotenv import load_dotenv # <--- NOVO: Importa a ferramenta do cofre

# # Carrega as senhas do arquivo .env
# load_dotenv()

# # Pega a chave do cofre. Se não achar, avisa o erro.
# API_KEY = os.getenv("WASENDER_API_KEY")
# if not API_KEY:
#     raise ValueError("ERRO: A chave WASENDER_API_KEY não foi encontrada no arquivo .env!")

# API_URL = "https://www.wasenderapi.com/api/send-message"
# NOME_ARQUIVO = "lista_clientes.xlsx"
# TEMPO_MIN = 400
# TEMPO_MAX = 900

# def enviar_disparos():
#     if not os.path.exists(NOME_ARQUIVO):
#         print(f"ERRO: Arquivo '{NOME_ARQUIVO}' não encontrado.")
#         return

#     try:
#         df = pd.read_excel(NOME_ARQUIVO)
#         if 'Status' not in df.columns:
#             df['Status'] = '' 
#     except Exception as e:
#         print(f"Erro ao ler Excel: {e}")
#         return

#     print(f"--- Iniciando campanha (Modo Curto e Direto) ---")

#     for index, linha in df.iterrows():
#         # --- TRAVA DE HORÁRIO ---
#         agora = datetime.now()
#         hora = agora.hour # Pega só a hora (ex: 9, 14, 19)
        
#         # Se for antes das 9h OU depois das 18h (considerando 18:00 o limite)
#         if hora < 9 or hora >= 19:
#             print(f"🚫 Fora do horário comercial ({agora.strftime('%H:%M')}). Parando o robô por segurança.")
#             break # Encerra o loop e para o programa
#         nome = str(linha.get('Nome', 'Cliente')) 
#         telefone_bruto = str(linha.get('Telefone', ''))
#         status_atual = str(linha.get('Status', '')).strip().lower()

#         if status_atual == 'enviado': continue
        
#         telefone = "".join(filter(str.isdigit, telefone_bruto))
#         if not telefone: continue
#         if len(telefone) >= 10 and not telefone.startswith("55"): telefone = "55" + telefone

#         mensagem = """Olá! Tudo bem?

# Vi que você atua com BPO Financeiro. Uma dúvida rápida:

# Como você apresenta os resultados dos seus clientes ? 

# Nós criamos um sistema que gera BI ( Business Intelligence ) em tempo real para o seu cliente. 

# DRE Gerêncial/Fluxo de Caixa  e Dashboards automáticos para te tirar do operacional e gerar valor na sua operação. 

# Posso te liberar um acesso teste gratuito para você ver como funciona por dentro?"""

        
#         payload = {"to": telefone, "text": mensagem}
#         headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

#         try:
#             print(f"[{index+1}/{len(df)}] Enviando Isca para {nome}...")
#             response = requests.post(API_URL, json=payload, headers=headers)
            
#             if response.status_code == 200:
#                 print(f" -> Sucesso.")
#                 df.at[index, 'Status'] = 'Enviado'
#                 try:
#                     df.to_excel(NOME_ARQUIVO, index=False)
#                 except: pass
#             else:
#                 print(f" -> Erro API: {response.text}")
            
#             tempo = random.randint(TEMPO_MIN, TEMPO_MAX)
#             print(f"Aguardando {tempo}s...\n")
#             time.sleep(tempo)

#         except Exception as e:
#             print(f" -> Erro envio: {e}")

# if __name__ == "__main__":
#     enviar_disparos()

import pandas as pd
import requests
import time
import os
import random
import base64  # <--- ESSENCIAL: Biblioteca que converte o PDF
from datetime import datetime
from dotenv import load_dotenv 

# Carrega as senhas do arquivo .env
load_dotenv()

API_KEY = os.getenv("WASENDER_API_KEY")
if not API_KEY:
    raise ValueError("ERRO: A chave WASENDER_API_KEY não foi encontrada no arquivo .env!")

# URL da API (Verifique se a sua API usa esta rota padrão)
API_URL = "https://www.wasenderapi.com/api/send-message" 

# --- CONFIGURAÇÕES DOS ARQUIVOS ---
NOME_ARQUIVO_EXCEL = "lista_clientes.xlsx"
NOME_PDF = "apresentacao_v2.pdf"  # <--- COLOQUE AQUI O NOME DO SEU PDF COMPRIMIDO

# --- CONFIGURAÇÕES DE TEMPO (Proteção Anti-Bloqueio) ---
TEMPO_MIN = 400
TEMPO_MAX = 900

def obter_base64_pdf(caminho_arquivo):
    """Lê o arquivo PDF e converte para código Base64"""
    if not os.path.exists(caminho_arquivo):
        print(f"ERRO CRÍTICO: O arquivo '{caminho_arquivo}' não está na pasta!")
        return None
        
    try:
        with open(caminho_arquivo, "rb") as pdf_file:
            # Lê o arquivo e transforma em código
            encoded_string = base64.b64encode(pdf_file.read()).decode('utf-8')
        return encoded_string
    except Exception as e:
        print(f"Erro ao converter PDF: {e}")
        return None

def enviar_disparos():
    # 1. Verifica se a lista de clientes existe
    if not os.path.exists(NOME_ARQUIVO_EXCEL):
        print(f"ERRO: Arquivo '{NOME_ARQUIVO_EXCEL}' não encontrado.")
        return

    # 2. Prepara o PDF (Carrega na memória)
    print("Carregando PDF...")
    pdf_base64 = obter_base64_pdf(NOME_PDF)
    if not pdf_base64:
        print("Abortando: PDF não pôde ser carregado.")
        return
    print(f"PDF carregado com sucesso! Tamanho OK.")

    # 3. Lê o Excel
    try:
        df = pd.read_excel(NOME_ARQUIVO_EXCEL)
        if 'Status' not in df.columns:
            df['Status'] = '' 
    except Exception as e:
        print(f"Erro ao ler Excel: {e}")
        return

    print(f"--- Iniciando campanha com PDF ---")

    for index, linha in df.iterrows():
        # --- TRAVA DE HORÁRIO ---
        agora = datetime.now()
        hora = agora.hour
        
        # Só envia entre 9h e 19h
        if hora < 9 or hora >= 19:
            print(f"🚫 Fora do horário comercial ({agora.strftime('%H:%M')}). Parando o robô.")
            break 
            
        nome = str(linha.get('Nome', 'Cliente')) 
        telefone_bruto = str(linha.get('Telefone', ''))
        status_atual = str(linha.get('Status', '')).strip().lower()

        # Pula quem já recebeu
        if status_atual == 'enviado': continue
        
        # Limpa o telefone
        telefone = "".join(filter(str.isdigit, telefone_bruto))
        if not telefone: continue
        if len(telefone) >= 10 and not telefone.startswith("55"): telefone = "55" + telefone

        # --- TEXTO DA MENSAGEM ---
        mensagem_texto = f"""Olá! Tudo bem?

Vi que você atua com BPO Financeiro. Hoje como você apresenta os resultados dos seus clientes? 

Nós criamos um sistema que gera BI (Business Intelligence) em tempo real para o seu cliente. 

DRE Gerencial, Fluxo de Caixa e Dashboards automáticos para te tirar do operacional e gerar valor na sua operação. 

Estou lhe enviando abaixo uma apresentação do nosso sistema em PDF.

Se fizer sentido, posso te liberar um acesso teste gratuito para você ver como funciona por dentro. O que acha?

No mais, agradeço a sua atenção!"""

        # --- PACOTE DE ENVIO (JSON) ---
        payload = {
            "to": telefone,
            "text": mensagem_texto,
            "media": pdf_base64,      # O PDF convertido vai aqui
            "mediaName": NOME_PDF,    # Nome que aparece no WhatsApp
            "type": "document"        # Tipo de arquivo
        }
        
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

        try:
            print(f"[{index+1}/{len(df)}] Enviando para {nome}...")
            
            # Timeout aumentado para 30s porque enviar arquivo demora mais que texto
            response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                print(f" -> Sucesso.")
                df.at[index, 'Status'] = 'Enviado'
                try:
                    df.to_excel(NOME_ARQUIVO_EXCEL, index=False)
                except: pass
            else:
                print(f" -> Erro API: {response.status_code} - {response.text}")
            
            # --- INTERVALO ALEATÓRIO ---
            tempo = random.randint(TEMPO_MIN, TEMPO_MAX)
            print(f"Aguardando {tempo}s...\n")
            time.sleep(tempo)

        except Exception as e:
            print(f" -> Erro envio: {e}")

if __name__ == "__main__":
    enviar_disparos()