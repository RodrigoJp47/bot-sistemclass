

# from flask import Flask, request, jsonify
# import requests
# import google.generativeai as genai
# import time
# import os
# import uuid

# app = Flask(__name__)

# # ==============================================================================
# # 1. SUAS CHAVES
# # ==============================================================================
# WASENDER_API_KEY = "87cc26577dac7e7b62287fb2e3e54f40397395679518a15d1d731e041d00d462"
# GEMINI_API_KEY = "AIzaSyAM2Z3HyOcANDfRq1vr5ROX5QaX8LMBlBg"

# # ==============================================================================
# # 2. INFORMAÇÕES
# # ==============================================================================
# NOME_EMPRESA = "SistemClass"
# LINK_LANDING = "https://sistemclass.com.br"

# # ✅ CORREÇÃO DEFINITIVA DO LINK:
# # Usamos o link do seu PERFIL. Isso evita o erro 404 de links quebrados.
# LINK_AGENDA = "https://calendly.com/rodriabreu"

# # ==============================================================================
# # BASE DE CONHECIMENTO
# # ==============================================================================
# INFO_PRODUTO = f"""
# RESUMO ESTRATÉGICO PARA O AGENTE:
# Você é Maria Clara, especialista em SistemClass. Seu objetivo é mostrar como transformar o BPO Operacional em BPO Consultivo.

# O SEU DISCURSO DE VENDAS (A "Proposta de Valor"):
# Não somos apenas um sistema financeiro. Entregamos 3 pilares fundamentais para o BPO:

# 1. INTELIGÊNCIA (O PRINCIPAL): Entregamos Dashboards prontos de DRE, Fluxo de Caixa, Laudos Financeiros e Valuation. 
#    - Argumento: "Seu cliente não entende planilhas, ele entende gráficos e insights. Entregue valor estratégico."
   
# 2. ORGANIZAÇÃO: Temos um Gestor de Tarefas (estilo Trello) nativo dentro do sistema.
#    - Argumento: "Controle o fechamento da sua equipe sem sair da tela do financeiro."

# 3. ESCALA (PRODUTIVIDADE): Somos Multi-CNPJ.
#    - Argumento: "Gerencie 10, 20, 50 clientes com apenas 1 login e painel unificado."

# PREÇOS (Use apenas se perguntarem):
# - R$139/mês (Financeiro) ou R$189/mês (Comercial+Fiscal).
# - Descontos progressivos acima de 5 CNPJs.
# """

# genai.configure(api_key=GEMINI_API_KEY)
# model = genai.GenerativeModel('gemini-flash-latest') 

# historico_conversas = {} 
# mapa_ids = {}

# def baixar_audio(url_audio):
#     try:
#         nome_arquivo = f"temp_{uuid.uuid4()}.mp3"
#         resposta = requests.get(url_audio)
#         if resposta.status_code == 200:
#             with open(nome_arquivo, 'wb') as f:
#                 f.write(resposta.content)
#             return nome_arquivo
#         return None
#     except Exception as e:
#         print(f"Erro download áudio: {e}")
#         return None

# def enviar_mensagem(telefone, texto):
#     url = "https://www.wasenderapi.com/api/send-message"
#     phone = telefone.split('@')[0]
#     if not phone.startswith('+'): phone = f"+{phone}"

#     payload = {"to": phone, "text": texto}
#     headers = {
#         "Authorization": f"Bearer {WASENDER_API_KEY}",
#         "Content-Type": "application/json"
#     }
#     try:
#         requests.post(url, json=payload, headers=headers)
#     except Exception as e:
#         print(f"Erro ao enviar msg: {e}")

# @app.route('/webhook', methods=['POST'])
# def webhook():
#     try:
#         data = request.get_json()
        
#         messages = []
#         raw = None
#         if 'messages' in data: raw = data['messages']
#         elif 'data' in data: 
#             if 'messages' in data['data']: raw = data['data']['messages']
#             else: raw = data['data']
#         elif 'payload' in data: raw = data['payload']

#         if isinstance(raw, list): messages = raw
#         elif isinstance(raw, dict): messages = [raw]
            
#         if not messages: return jsonify({"status": "ignored"}), 200

#         for msg in messages:
#             key = msg.get('key', {})
#             if key.get('fromMe') or msg.get('fromMe'): continue

#             remote_jid = key.get('remoteJid') or msg.get('from')
#             sender = remote_jid

#             if sender and '@lid' in sender:
#                 if sender in mapa_ids: sender = mapa_ids[sender]
#                 else:
#                     real_number = key.get('senderPn') or key.get('participant')
#                     if real_number: mapa_ids[remote_jid] = real_number; sender = real_number

#             tipo_msg = msg.get('messageType') or msg.get('type')
#             msg_content = msg.get('message', {})
#             texto_cliente = ''
#             caminho_audio = None
#             eh_audio = False

#             if tipo_msg == 'audio' or 'audioMessage' in msg_content:
#                 eh_audio = True
#                 print(f"--- [CLIENTE] Áudio recebido de {sender}")
#                 url_media = (msg_content.get('audioMessage', {}).get('url') or msg.get('mediaUrl') or msg_content.get('url'))
#                 if url_media: caminho_audio = baixar_audio(url_media)
#                 else: continue 

#             else:
#                 if 'conversation' in msg: texto_cliente = msg['conversation']
#                 elif 'messageBody' in msg: texto_cliente = msg['messageBody']
#                 elif 'body' in msg: texto_cliente = msg['body']
#                 elif 'message' in msg: texto_cliente = msg_content.get('conversation') or msg_content.get('extendedTextMessage', {}).get('text')
#                 if not texto_cliente: continue

#                 if texto_cliente.lower().strip() in ['reset', 'limpar', '/reset', '/limpar']:
#                     historico_conversas[sender] = []
#                     print(f"--- [RESET] Memória limpa para {sender}")
#                     enviar_mensagem(sender, "♻️ Memória reiniciada! Pode começar um novo teste.")
#                     continue 
                
#                 termos_de_robo = ["horário de atendimento", "não responda", "mensagem automática", "digite a opção"]
#                 if any(termo in texto_cliente.lower() for termo in termos_de_robo): continue
                
#                 print(f"--- [CLIENTE] {sender}: {texto_cliente}")

#             if sender not in historico_conversas: historico_conversas[sender] = []
            
#             if not eh_audio: historico_conversas[sender].append(f"Cliente: {texto_cliente}")
#             else: historico_conversas[sender].append(f"Cliente: [Enviou um áudio]")
            
#             memoria = "\n".join(historico_conversas[sender][-15:]) 
            
#             # Garante que o link não tenha espaços extras
#             link_agenda_limpo = LINK_AGENDA.strip()

#             instrucoes_base = f"""
#             {INFO_PRODUTO}

#             CONTEXTO:
#             Você abordou o cliente oferecendo uma ferramenta para BPO.
            
#             SUA MISSÃO:
#             Gerar desejo pelos DASHBOARDS e levar para Reunião/Teste.
            
#             DIRETRIZES TÉCNICAS (IMPORTANTÍSSIMO):
#             1. NÃO use formatação Markdown nos links. NUNCA faça isso: [Link](url).
#             2. Envie o link puro e simples. Exemplo: "Acesse aqui: https://..."
#             3. Isso evita que o link quebre no WhatsApp.

#             DIRETRIZES DE RESPOSTA:
#             - PRIMEIRA ABORDAGEM: Apresente o SistemClass (Dashboards + Tarefas + Multi-CNPJ).
#             - ENCERRAMENTO: Se o cliente disser "Agendado" ou "Ok", APENAS agradeça e encerre.
            
#             LINKS:
#             - Cadastro: {LINK_LANDING}
#             - Agenda: {link_agenda_limpo}

#             HISTÓRICO RECENTE:
#             {memoria}
#             """

#             try:
#                 time.sleep(3) 
#                 resposta_bot = ""
                
#                 if eh_audio and caminho_audio:
#                     print(f"--- [GEMINI] Processando áudio...")
#                     arquivo_gemini = genai.upload_file(caminho_audio, mime_type="audio/mp3")
                    
#                     prompt_audio = f"""
#                     ANALISE ESTE ÁUDIO COM ATENÇÃO.
#                     1. Se for PERGUNTA NOVA, responda (Preço, Funcionalidade).
#                     2. Se for CONFIRMAÇÃO (ex: "Agendado"), encerre a conversa.
#                     3. NÃO use Markdown nos links. Envie links puros.
                    
#                     Base de conhecimento:
#                     {INFO_PRODUTO}
                    
#                     Responda ao áudio:
#                     """
                    
#                     response = model.generate_content([prompt_audio, arquivo_gemini])
#                     resposta_bot = response.text.strip()
#                     try: os.remove(caminho_audio)
#                     except: pass

#                 else:
#                     instrucoes_texto = instrucoes_base + "\nResponda como Maria Clara:"
#                     response = model.generate_content(instrucoes_texto)
#                     resposta_bot = response.text.strip()

#                 print(f"--- [RODRIGO] {resposta_bot}")
#                 historico_conversas[sender].append(f"Rodrigo: {resposta_bot}")
#                 enviar_mensagem(sender, resposta_bot)

#             except Exception as e_api:
#                 print(f"--- [ERRO PROCESSAMENTO] {e_api}")

#     except Exception as e:
#         print(f"--- [ERRO GERAL] {e}")

#     return jsonify({"status": "ok"}), 200

# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host='0.0.0.0', port=port)

from flask import Flask, request, jsonify
import requests
import google.generativeai as genai
import time
import os
import uuid

app = Flask(__name__)

# ==============================================================================
# 1. SUAS CHAVES
# ==============================================================================
WASENDER_API_KEY = "87cc26577dac7e7b62287fb2e3e54f40397395679518a15d1d731e041d00d462"
GEMINI_API_KEY = "AIzaSyAM2Z3HyOcANDfRq1vr5ROX5QaX8LMBlBg"

# ==============================================================================
# 2. INFORMAÇÕES
# ==============================================================================
NOME_EMPRESA = "SistemClass"
LINK_LANDING = "https://sistemclass.com.br"
# Link Geral (À prova de erros 404)
LINK_AGENDA = "https://calendly.com/rodriabreu" 

# ==============================================================================
# BASE DE CONHECIMENTO
# ==============================================================================
INFO_PRODUTO = f"""
RESUMO ESTRATÉGICO PARA O AGENTE:
Você é Maria Clara, especialista em SistemClass. Seu objetivo é mostrar como transformar o BPO Operacional em BPO Consultivo.

O SEU DISCURSO DE VENDAS (A "Proposta de Valor"):
Não somos apenas um sistema financeiro. Entregamos 3 pilares fundamentais para o BPO:

1. INTELIGÊNCIA (O PRINCIPAL): Entregamos Dashboards prontos de DRE, Fluxo de Caixa, Laudos Financeiros e Valuation. 
   - Argumento: "Seu cliente não entende planilhas, ele entende gráficos e insights. Entregue valor estratégico."
   
2. ORGANIZAÇÃO: Temos um Gestor de Tarefas (estilo Trello) nativo dentro do sistema.
   - Argumento: "Controle o fechamento da sua equipe sem sair da tela do financeiro."

3. ESCALA (PRODUTIVIDADE): Somos Multi-CNPJ.
   - Argumento: "Gerencie 10, 20, 50 clientes com apenas 1 login e painel unificado."

PREÇOS (Use apenas se perguntarem):
- R$139/mês (Financeiro) ou R$189/mês (Comercial+Fiscal).
- Descontos progressivos acima de 5 CNPJs.
"""

genai.configure(api_key=GEMINI_API_KEY)
# Modelo 1.5 Flash (Melhor para áudio e instruções complexas)
model = genai.GenerativeModel('gemini-1.5-flash') 

historico_conversas = {} 
mapa_ids = {}

def baixar_audio(url_audio):
    try:
        nome_arquivo = f"temp_{uuid.uuid4()}.mp3"
        resposta = requests.get(url_audio)
        if resposta.status_code == 200:
            with open(nome_arquivo, 'wb') as f:
                f.write(resposta.content)
            return nome_arquivo
        return None
    except Exception as e:
        print(f"Erro download áudio: {e}")
        return None

def enviar_mensagem(telefone, texto):
    url = "https://www.wasenderapi.com/api/send-message"
    phone = telefone.split('@')[0]
    if not phone.startswith('+'): phone = f"+{phone}"

    payload = {"to": phone, "text": texto}
    headers = {
        "Authorization": f"Bearer {WASENDER_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f"Erro ao enviar msg: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        
        messages = []
        raw = None
        if 'messages' in data: raw = data['messages']
        elif 'data' in data: 
            if 'messages' in data['data']: raw = data['data']['messages']
            else: raw = data['data']
        elif 'payload' in data: raw = data['payload']

        if isinstance(raw, list): messages = raw
        elif isinstance(raw, dict): messages = [raw]
            
        if not messages: return jsonify({"status": "ignored"}), 200

        for msg in messages:
            key = msg.get('key', {})
            if key.get('fromMe') or msg.get('fromMe'): continue

            remote_jid = key.get('remoteJid') or msg.get('from')
            sender = remote_jid

            if sender and '@lid' in sender:
                if sender in mapa_ids: sender = mapa_ids[sender]
                else:
                    real_number = key.get('senderPn') or key.get('participant')
                    if real_number: mapa_ids[remote_jid] = real_number; sender = real_number

            tipo_msg = msg.get('messageType') or msg.get('type')
            msg_content = msg.get('message', {})
            texto_cliente = ''
            caminho_audio = None
            eh_audio = False

            if tipo_msg == 'audio' or 'audioMessage' in msg_content:
                eh_audio = True
                print(f"--- [CLIENTE] Áudio recebido de {sender}")
                url_media = (msg_content.get('audioMessage', {}).get('url') or msg.get('mediaUrl') or msg_content.get('url'))
                if url_media: caminho_audio = baixar_audio(url_media)
                else: continue 

            else:
                if 'conversation' in msg: texto_cliente = msg['conversation']
                elif 'messageBody' in msg: texto_cliente = msg['messageBody']
                elif 'body' in msg: texto_cliente = msg['body']
                elif 'message' in msg: texto_cliente = msg_content.get('conversation') or msg_content.get('extendedTextMessage', {}).get('text')
                if not texto_cliente: continue

                if texto_cliente.lower().strip() in ['reset', 'limpar', '/reset', '/limpar']:
                    historico_conversas[sender] = []
                    print(f"--- [RESET] Memória limpa para {sender}")
                    enviar_mensagem(sender, "♻️ Memória reiniciada! Pode começar um novo teste.")
                    continue 
                
                termos_de_robo = ["horário de atendimento", "não responda", "mensagem automática", "digite a opção"]
                if any(termo in texto_cliente.lower() for termo in termos_de_robo): continue
                
                print(f"--- [CLIENTE] {sender}: {texto_cliente}")

            if sender not in historico_conversas: historico_conversas[sender] = []
            
            if not eh_audio: historico_conversas[sender].append(f"Cliente: {texto_cliente}")
            else: historico_conversas[sender].append(f"Cliente: [Enviou um áudio]")
            
            memoria = "\n".join(historico_conversas[sender][-15:]) 
            link_agenda_limpo = LINK_AGENDA.strip()

            instrucoes_base = f"""
            {INFO_PRODUTO}

            CONTEXTO ATUAL:
            Você é Maria Clara. Você abordou o cliente oferecendo uma ferramenta para BPO.
            
            SUA MISSÃO:
            Gerar desejo pelos DASHBOARDS e levar para Reunião/Teste.
            
            DIRETRIZES TÉCNICAS:
            1. NÃO use Markdown nos links (apenas a URL pura).
            
            DIRETRIZES DE RESPOSTA:
            - PRIMEIRA ABORDAGEM: Apresente o SistemClass (Dashboards + Tarefas + Multi-CNPJ). Seja concisa.
            
            🔴 REGRA DE FINALIZAÇÃO (MUITO IMPORTANTE):
            Sempre que você oferecer os links (Teste Grátis ou Agenda), você deve finalizar a mensagem EXATAMENTE com esta frase (sem fazer outra pergunta depois):
            "Qualquer dúvida sobre o teste de 7 dias grátis, sobre o agendamento ou outra dúvida comum é só me chamar, ok? Estou à disposição!"

            - ENCERRAMENTO: Se o cliente disser "Agendado" ou "Ok", APENAS agradeça e encerre.
            
            LINKS:
            - Cadastro: {LINK_LANDING}
            - Agenda: {link_agenda_limpo}

            HISTÓRICO RECENTE:
            {memoria}
            """

            try:
                time.sleep(3) 
                resposta_bot = ""
                
                if eh_audio and caminho_audio:
                    print(f"--- [GEMINI] Processando áudio...")
                    arquivo_gemini = genai.upload_file(caminho_audio, mime_type="audio/mp3")
                    
                    prompt_audio = f"""
                    Você é Maria Clara, da SistemClass.
                    O cliente acabou de te enviar esse áudio.
                    
                    AÇÃO OBRIGATÓRIA:
                    1. Escute o áudio.
                    2. Se ele perguntar algo, RESPONDA como Maria Clara.
                    3. Se for confirmação de agendamento, agradeça e encerre.
                    4. Se for mudo, diga: "Desculpe, o áudio falhou. Consegue escrever?"
                    
                    Base de conhecimento:
                    {INFO_PRODUTO}
                    """
                    
                    response = model.generate_content([prompt_audio, arquivo_gemini])
                    resposta_bot = response.text.strip()
                    try: os.remove(caminho_audio)
                    except: pass

                else:
                    instrucoes_texto = instrucoes_base + "\nResponda como Maria Clara:"
                    response = model.generate_content(instrucoes_texto)
                    resposta_bot = response.text.strip()

                print(f"--- [RODRIGO] {resposta_bot}")
                historico_conversas[sender].append(f"Rodrigo: {resposta_bot}")
                enviar_mensagem(sender, resposta_bot)

            except Exception as e_api:
                print(f"--- [ERRO PROCESSAMENTO] {e_api}")

    except Exception as e:
        print(f"--- [ERRO GERAL] {e}")

    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)