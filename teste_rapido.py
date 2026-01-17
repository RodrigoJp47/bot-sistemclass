import requests
import os
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURAÇÕES ---
API_KEY = os.getenv("WASENDER_API_KEY")
API_URL = "https://www.wasenderapi.com/api/send-message"
MEU_NUMERO = "5531993111538" 

# Link do seu PDF no Render
LINK_PDF = "https://sistemclass.com.br/static/apresentacao.pdf"

# A Mensagem que o cliente vai receber
MENSAGEM_TESTE = f"""Olá! Teste de Envio (Link no Texto).

Como o envio de arquivo direto estava instável, estamos testando o envio do link seguro.

👇 Toque abaixo para baixar a apresentação:
{LINK_PDF}

Se essa mensagem chegou e o link abriu, estamos prontos! 🚀"""

def enviar_teste():
    print(f"--- Testando Envio de Texto com Link ---")
    
    # PAYLOAD SIMPLES (O que a API pediu o tempo todo)
    # Não usamos 'document_url', usamos apenas 'text'
    payload = {
        "to": MEU_NUMERO, 
        "text": MENSAGEM_TESTE
    }
    
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    print(f"🚀 Enviando para {MEU_NUMERO}...")
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        if response.status_code in [200, 201]:
            print("\n✅ SUCESSO! Verifique seu WhatsApp.")
            print("Dica: Veja se o WhatsApp gerou uma 'prévia' (card) do link automaticamente.")
        else:
             print(f"\n❌ Erro: {response.text}")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    enviar_teste()