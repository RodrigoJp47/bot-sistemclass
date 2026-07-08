

# import os
# import time
# import random
# import pandas as pd
# import urllib.parse
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

# # === Configurações de Arquivo ===
# NOME_ARQUIVO_EXCEL = "lista_clientes.xlsx"

# # === Configuração do Navegador ===
# dir_path = os.getcwd()
# profile = os.path.join(dir_path, "wpp_profile")

# chrome_options = Options()
# chrome_options.add_argument(f"user-data-dir={profile}")

# # Argumentos de Estabilidade (Correção para o erro SessionNotCreated)
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--remote-debugging-port=9222")
# chrome_options.add_argument("--disable-extensions")
# chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# # Para rodar em modo oculto futuramente, remova o '#' da linha abaixo:
# # chrome_options.add_argument("--headless=new")

# def mensagem_formatada():
#     """Retorna a mensagem com as quebras de linha preservadas."""
#     return (
#         "Olá! Tudo bem?\n\n"
#         "Vi que você atua com BPO Financeiro. Uma dúvida rápida:\n\n"
#         "Como você apresenta os resultados dos seus clientes?\n\n"
#         "Nós criamos um sistema que gera BI (Business Intelligence) em tempo real para o seu cliente.\n\n"
#         "DRE Gerencial/Fluxo de Caixa e Dashboards automáticos para te tirar do operacional e gerar valor na sua operação.\n\n"
#         "Posso te liberar um acesso teste gratuito para você ver como funciona por dentro?"
#     )

# def disparar_selenium():
#     print("🚀 Iniciando o robô de prospecção do SistemClass...")
    
#     try:
#         service = Service(ChromeDriverManager().install())
#         driver = webdriver.Chrome(service=service, options=chrome_options)
#         driver.maximize_window()
        
#         driver.get("https://web.whatsapp.com")
        
#         print("📢 Aguardando login no WhatsApp Web (leia o QR Code)...")
#         # Espera o carregamento inicial da página do WhatsApp
#         WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, "side")))
        
#     except Exception as e:
#         print(f"❌ Erro ao iniciar o Chrome: {e}")
#         print("Dica: Rode 'taskkill /F /IM chrome.exe /T' no terminal e tente novamente.")
#         return

#     try:
#         df = pd.read_excel(NOME_ARQUIVO_EXCEL, engine="openpyxl")
#     except Exception as e:
#         print(f"❌ Erro ao ler a planilha {NOME_ARQUIVO_EXCEL}: {e}")
#         driver.quit()
#         return

#     texto_bruto = mensagem_formatada()
#     # Codificação URL para garantir que o WhatsApp não agrupe o texto
#     texto_codificado = urllib.parse.quote(texto_bruto)

#     print(f"--- Iniciando disparos para {len(df)} contatos ---")

#     for idx, linha in df.iterrows():
#         nome = str(linha.get('Nome', 'Cliente'))
#         telefone = str(linha.get('Telefone', '')).strip().replace(".0", "")
#         status = str(linha.get('Status', '')).strip().lower()

#         if status == 'enviado' or not telefone:
#             continue

#         print(f"👉 Processando: {nome} ({telefone})...")
        
#         # Abre a URL direta da mensagem
#         url_mensagem = f"https://web.whatsapp.com/send?phone={telefone}&text={texto_codificado}"
#         driver.get(url_mensagem)

#         try:
#             # Espera o botão de envio (ícone de aviãozinho) aparecer e ficar clicável
#             btn_enviar = WebDriverWait(driver, 40).until(
#                 EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
#             )
            
#             # Pequena pausa humana para carregar o texto no campo
#             time.sleep(3)
#             btn_enviar.click()
            
#             print(f"✅ Mensagem enviada com sucesso!")
            
#             # Atualiza a planilha imediatamente para não perder o progresso
#             df.at[idx, 'Status'] = 'Enviado'
#             df.to_excel(NOME_ARQUIVO_EXCEL, index=False)
            
#         except Exception as e:
#             print(f"⚠️ Falha ao enviar para {nome}. O número pode não ter WhatsApp ou a página demorou a carregar.")

#         # Intervalo de segurança para evitar banimento (entre 45 e 80 segundos)
#         intervalo = random.randint(45, 80)
#         print(f"⏳ Aguardando {intervalo}s para o próximo envio...\n")
#         time.sleep(intervalo)

#     print("🏁 Todos os contatos da lista foram processados!")
#     driver.quit()

# if __name__ == "__main__":
#     disparar_selenium()

import os
import time
import random
import pandas as pd
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# === Configurações de Arquivo ===
NOME_ARQUIVO_EXCEL = "lista_clientes.xlsx"

# === Configuração do Navegador ===
dir_path = os.getcwd()
profile = os.path.join(dir_path, "wpp_profile")

chrome_options = Options()
chrome_options.add_argument(f"user-data-dir={profile}")

# Argumentos de Estabilidade (Correção para o erro SessionNotCreated)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Para rodar em modo oculto futuramente, remova o '#' da linha abaixo:
# chrome_options.add_argument("--headless=new")

def mensagem_formatada():
    """Retorna a mensagem com as quebras de linha preservadas."""
    return (
        "Olá! Uma pergunta direta:\n\n"
        "Quanto tempo sua equipe gasta por mês montando relatórios financeiros pros clientes?\n\n"
        "Desenvolvemos um sistema que automatiza isso — DRE, Fluxo de Caixa e BI em tempo real. O cliente acessa sozinho, sem você precisar montar nada.\n\n"
        "Posso te dar um acesso teste gratuito agora?"
    )

def disparar_selenium():
    print("🚀 Iniciando o robô de prospecção do SistemClass...")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.maximize_window()
        
        driver.get("https://web.whatsapp.com")
        
        print("📢 Aguardando login no WhatsApp Web (leia o QR Code)...")
        # Espera o carregamento inicial da página do WhatsApp
        WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, "side")))
        
    except Exception as e:
        print(f"❌ Erro ao iniciar o Chrome: {e}")
        print("Dica: Rode 'taskkill /F /IM chrome.exe /T' no terminal e tente novamente.")
        return

    try:
        df = pd.read_excel(NOME_ARQUIVO_EXCEL, engine="openpyxl")
    except Exception as e:
        print(f"❌ Erro ao ler a planilha {NOME_ARQUIVO_EXCEL}: {e}")
        driver.quit()
        return

    texto_bruto = mensagem_formatada()
    # Codificação URL para garantir que o WhatsApp não agrupe o texto
    texto_codificado = urllib.parse.quote(texto_bruto)

    print(f"--- Iniciando disparos para {len(df)} contatos ---")

    for idx, linha in df.iterrows():
        nome = str(linha.get('Nome', 'Cliente'))
        telefone = str(linha.get('Telefone', '')).strip().replace(".0", "")
        status = str(linha.get('Status', '')).strip().lower()

        if status == 'enviado' or not telefone:
            continue

        print(f"👉 Processando: {nome} ({telefone})...")
        
        # Abre a URL direta da mensagem
        url_mensagem = f"https://web.whatsapp.com/send?phone={telefone}&text={texto_codificado}"
        driver.get(url_mensagem)

        try:
            # Espera o botão de envio (ícone de aviãozinho) aparecer e ficar clicável
            btn_enviar = WebDriverWait(driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"] | //span[@data-icon="wds-ic-send-filled"] | //button[@aria-label="Enviar"]'))
            )
            
            # Pequena pausa humana para carregar o texto no campo
            time.sleep(3)
            btn_enviar.click()
            
            print(f"✅ Mensagem enviada com sucesso!")
            
            # Atualiza a planilha imediatamente para não perder o progresso
            df.at[idx, 'Status'] = 'Enviado'
            df.to_excel(NOME_ARQUIVO_EXCEL, index=False)
            
        except Exception as e:
            print(f"⚠️ Falha ao enviar para {nome}. O número pode não ter WhatsApp ou a página demorou a carregar.")

        # Intervalo de segurança para evitar banimento (entre 45 e 80 segundos)
        intervalo = random.randint(45, 80)
        print(f"⏳ Aguardando {intervalo}s para o próximo envio...\n")
        time.sleep(intervalo)

    print("🏁 Todos os contatos da lista foram processados!")
    driver.quit()

if __name__ == "__main__":
    disparar_selenium()