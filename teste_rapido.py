import requests

# --- CONFIGURAÇÕES ---
API_KEY = "87cc26577dac7e7b62287fb2e3e54f40397395679518a15d1d731e041d00d462"
API_URL = "https://www.wasenderapi.com/api/send-message"

# ⚠️ COLOQUE SEU NÚMERO AQUI (COM 55 + DDD) ⚠️
MEU_NUMERO = "5531993413530"  

# A MESMA MENSAGEM DO DISPARADOR OFICIAL
MENSAGEM_ISCA = """Olá! Tudo bem?

Vi que você atua com BPO Financeiro. Uma dúvida rápida:

Como você apresenta os resultados dos seus clientes ? 

Nós criamos um sistema que gera BI ( Business Intelligence ) em tempo real para o seu cliente. 

DRE Gerêncial/Fluxo de Caixa  e Dashboards automáticos para te tirar do operacional e gerar valor na sua operação. 

Posso te liberar um acesso teste gratuito para você ver como funciona por dentro?"""

def enviar_teste():
    payload = {"to": MEU_NUMERO, "text": MENSAGEM_ISCA}
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    print(f"🚀 Enviando Isca de Teste para {MEU_NUMERO}...")
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Resposta API: {response.text}")
        print("\n✅ Agora verifique seu WhatsApp e responda para testar a Maria Clara!")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    enviar_teste()