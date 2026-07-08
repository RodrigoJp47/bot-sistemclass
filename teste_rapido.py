import requests
import os
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURAÇÕES ---
API_KEY = os.getenv("WASENDER_API_KEY")
API_URL = "https://www.wasenderapi.com/api/send-message"
# Seu número configurado para o teste
MEU_NUMERO = "5531993413530" 

# A Nova Mensagem de Prospecção (conforme a imagem enviada)
MENSAGEM_TESTE = (
    "Olá! Tudo bem?\n\n"
    "Vi que você atua com BPO Financeiro. Uma dúvida rápida:\n\n"
    "Como você apresenta os resultados dos seus clientes?\n\n"
    "Nós criamos um sistema que gera BI (Business Intelligence) em tempo real para o seu cliente.\n\n"
    "DRE Gerencial/Fluxo de Caixa e Dashboards automáticos para te tirar do operacional e gerar valor na sua operação.\n\n"
    "Posso te liberar um acesso teste gratuito para você ver como funciona por dentro?"
)

def enviar_teste_rapido():
    print(f"--- Iniciando Teste de Prospecção SistemClass ---")
    
    # Payload focado apenas em texto para máxima estabilidade
    payload = {
        "to": MEU_NUMERO, 
        "text": MENSAGEM_TESTE
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}", 
        "Content-Type": "application/json"
    }

    print(f"🚀 Enviando teste para seu número: {MEU_NUMERO}...")
    
    try:
        # Timeout de 30s para garantir resposta da API
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("\n✅ SUCESSO! A mensagem deve chegar em instantes no seu WhatsApp.")
            print("Avalie como o espaçamento ficou no celular antes de iniciar o disparo em massa.")
        else:
             print(f"\n❌ Erro na API: {response.text}")

    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

if __name__ == "__main__":
    enviar_teste_rapido()