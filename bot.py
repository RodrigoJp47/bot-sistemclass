


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
# # 2. INFORMAÇÕES E CONTEXTO DE VENDAS
# # ==============================================================================
# NOME_EMPRESA = "SistemClass"
# LINK_LANDING = "https://sistemclass.com.br"
# LINK_AGENDA = "https://calendly.com/rodriabreu/30min"

# INFO_PRODUTO = f"""
# RESUMO ESTRATÉGICO PARA O AGENTE:
# Você é Maria Clara, consultora especialista em crescimento de BPO Financeiro da SistemClass.
# Seu tom de voz é: Profissional, Empático, Seguro e Persuasivo. Você não é uma robô, é uma parceira de negócios.

# O GRANDE DIFERENCIAL (A "Bala de Prata"):
# O SistemClass resolve a maior dor do BPO: A improdutividade de gerenciar vários clientes.
# - Funcionalidade Chave: MULTI-CNPJ (Gerencie 10, 20, 50 clientes com APENAS 1 LOGIN e painel unificado).
# - Gestão de Tarefas: Um "Trello" nativo dentro do financeiro para controlar os fechamentos da equipe.

# O QUE ENTREGAMOS DE VALOR (Argumentos de Venda):
# 1. Para o Dono do BPO: Escala. "Pare de perder tempo logando e deslogando de bancos e ERPs."
# 2. Para o Cliente do BPO: Visualização. Dashboards de Valuation, DRE, Fluxo de Caixa e Laudos Financeiros automáticos para mostrar valor ao cliente final.
# 3. Integrações: Conta Azul, OMIE, NIBO, Tiny, Inter, Mercado Pago (Puxamos os dados para centralizar).

# PREÇOS (Use apenas se perguntarem ou no fechamento):
# - R$139/mês por CNPJ (Financeiro Completo).
# - R$189/mês por CNPJ (Financeiro + Comercial com Emissão de NF).
# - Desconto progressivo de 10% acima de 5 CNPJs.
# - Sem taxa de setup, sem fidelidade.
# """

# genai.configure(api_key=GEMINI_API_KEY)
# # Mantendo o modelo que funciona para você
# model = genai.GenerativeModel('gemini-flash-latest') 

# historico_conversas = {} 
# mapa_ids = {}

# # --- FUNÇÃO AUXILIAR PARA BAIXAR ÁUDIO ---
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

# # --- FUNÇÃO AUXILIAR PARA ENVIAR MENSAGEM ---
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
        
#         # Extração de mensagens
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
#             # Ignora mensagens próprias
#             key = msg.get('key', {})
#             if key.get('fromMe') or msg.get('fromMe'): continue

#             # Identificação do usuário
#             remote_jid = key.get('remoteJid') or msg.get('from')
#             sender = remote_jid

#             if sender and '@lid' in sender:
#                 if sender in mapa_ids:
#                     sender = mapa_ids[sender]
#                 else:
#                     real_number = key.get('senderPn') or key.get('participant')
#                     if real_number:
#                         mapa_ids[remote_jid] = real_number
#                         sender = real_number

#             # -----------------------------------------------------------
#             # DETECTA TIPO DE MENSAGEM (TEXTO OU ÁUDIO)
#             # -----------------------------------------------------------
#             tipo_msg = msg.get('messageType') or msg.get('type')
#             msg_content = msg.get('message', {})
            
#             texto_cliente = ''
#             caminho_audio = None
#             eh_audio = False

#             # 1. É Áudio?
#             if tipo_msg == 'audio' or 'audioMessage' in msg_content:
#                 eh_audio = True
#                 print(f"--- [CLIENTE] Áudio recebido de {sender}")
                
#                 url_media = (
#                     msg_content.get('audioMessage', {}).get('url') or 
#                     msg.get('mediaUrl') or 
#                     msg_content.get('url')
#                 )
                
#                 if url_media:
#                     caminho_audio = baixar_audio(url_media)
#                 else:
#                     print("--- [ERRO] Não encontrei a URL do áudio no JSON.")
#                     continue 

#             # 2. É Texto?
#             else:
#                 if 'conversation' in msg: texto_cliente = msg['conversation']
#                 elif 'messageBody' in msg: texto_cliente = msg['messageBody']
#                 elif 'body' in msg: texto_cliente = msg['body']
#                 elif 'message' in msg:
#                     texto_cliente = msg_content.get('conversation') or msg_content.get('extendedTextMessage', {}).get('text')

#                 if not texto_cliente: continue

#                 # --- COMANDO DE RESET (PARA TESTES) ---
#                 if texto_cliente.lower().strip() in ['/reset', '/limpar', 'limpar memoria']:
#                     historico_conversas[sender] = []
#                     print(f"--- [RESET] Memória limpa para {sender}")
#                     enviar_mensagem(sender, "♻️ Memória reiniciada! Pode começar um novo teste.")
#                     continue # Pula o resto e espera a próxima mensagem
                
#                 # Filtro Anti-Robô (Só aplica para texto)
#                 termos_de_robo = [
#                     "horário de atendimento", "não responda", "mensagem automática", 
#                     "digite a opção", "estamos ausentes", "não estamos disponíveis",
#                     "protocolo", "atendimento encerrado", "toque em", "clique no link"
#                 ]
#                 if any(termo in texto_cliente.lower() for termo in termos_de_robo):
#                     print(f"🛑 Mensagem ignorada (Parece robô): {texto_cliente[:50]}...")
#                     continue
                
#                 print(f"--- [CLIENTE] {sender}: {texto_cliente}")

#             # Memória
#             if sender not in historico_conversas:
#                 historico_conversas[sender] = []
            
#             if not eh_audio:
#                 historico_conversas[sender].append(f"Cliente: {texto_cliente}")
#             else:
#                 historico_conversas[sender].append(f"Cliente: [Enviou um áudio]")
            
#             memoria = "\n".join(historico_conversas[sender][-15:]) 

#             # ==================================================================
#             # 3. PROMPT DE RESPOSTA (Híbrido: Texto ou Áudio)
#             # ==================================================================
            
#             instrucoes_base = f"""
#             {INFO_PRODUTO}

#             CONTEXTO ATUAL:
#             Você abordou o cliente via WhatsApp perguntando se podia apresentar uma ferramenta para operação de BPO.
            
#             SUA MISSÃO:
#             Conduzir o cliente para um TESTE GRÁTIS ou uma REUNIÃO.
            
#             DIRETRIZES:
#             1. Se for áudio, ESCUTE com atenção o tom de voz e a dúvida.
#             2. Seja cordial, mas vá direto ao ponto da "dor" (produtividade/Multi-CNPJ).
#             3. Use emojis moderadamente.

#             🔴 REGRA CRÍTICA DE ENCERRAMENTO (LEIA COM ATENÇÃO):
#             - Se o cliente disser: "Agendado", "Já agendei", "Ok obrigado", "Vou ver", "Vou agendar" ou "Obrigado".
#             - AÇÃO: NÃO FAÇA MAIS PERGUNTAS DE VENDAS.
#             - RESPOSTA: Apenas agradeça, confirme e encerre a conversa.
#             - Exemplo: "Perfeito! Te aguardo na reunião. Um abraço!" (E nada mais).

#             🟢 REGRA PARA FLUXO NORMAL (Se o cliente ainda tiver dúvidas):
#             - Termine com uma pergunta para engajar.

#             CENÁRIOS COMUNS:
#             - "Já tenho sistema": Diga "Ótimo, integramos com eles! Mas o SistemClass centraliza tudo (Multi-CNPJ) num login só."
#             - "Preço": R$139/mês. Fale do ROI (Atender mais clientes com a mesma equipe).
#             - "Sem tempo": "Temos um Trello nativo para organizar seu caos. Teste grátis quando der."
#             - "Interesse": "Prefere testar 7 dias grátis ou uma demo rápida?"

#             LINKS (Envie apenas se pedir ou aceitar oferta):
#             - Cadastro: {LINK_LANDING}
#             - Agenda: {LINK_AGENDA}

#             HISTÓRICO RECENTE:
#             {memoria}

#             Responda como Maria Clara (apenas texto):
#             """

#             try:
#                 time.sleep(3) 
                
#                 resposta_bot = ""
                
#                 if eh_audio and caminho_audio:
#                     # --- FLUXO DE ÁUDIO ---
#                     print(f"--- [GEMINI] Processando áudio: {caminho_audio}...")
                    
#                     # 1. Upload para o Gemini
#                     arquivo_gemini = genai.upload_file(caminho_audio, mime_type="audio/mp3")
                    
#                     # 2. Gera resposta ouvindo o áudio
#                     prompt_audio = "Escute esse áudio do cliente, entenda a dúvida ou objeção dele e responda seguindo as instruções abaixo.\n\n" + instrucoes_base
#                     response = model.generate_content([prompt_audio, arquivo_gemini])
#                     resposta_bot = response.text.strip()
                    
#                     # 3. Limpeza
#                     try:
#                         os.remove(caminho_audio)
#                     except:
#                         pass

#                 else:
#                     # --- FLUXO DE TEXTO ---
#                     response = model.generate_content(instrucoes_base)
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
LINK_AGENDA = "https://calendly.com/rodriabreu/30min"

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
# Mantendo o modelo Flash
model = genai.GenerativeModel('gemini-flash-latest') 

historico_conversas = {} 
mapa_ids = {}

# --- FUNÇÃO AUXILIAR PARA BAIXAR ÁUDIO ---
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

# --- FUNÇÃO AUXILIAR PARA ENVIAR MENSAGEM ---
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

            CONTEXTO:
            Você abordou o cliente oferecendo uma ferramenta para BPO.
            
            SUA MISSÃO:
            Gerar desejo pelos DASHBOARDS e levar para Reunião/Teste.
            
            DIRETRIZES DE RESPOSTA:
            1. PRIMEIRA ABORDAGEM (Se perguntarem "Quem é?"):
               - Apresente o SistemClass: Inteligência (Dashboards de Valuation/DRE) + Organização (Tarefas) + Escala (Multi-CNPJ).
               - Foque no VALOR dos Dashboards.

            2. REGRA DE ENCERRAMENTO:
               - Se o cliente disser explicitamente: "Agendado", "Já agendei", "Ok obrigado".
               - PARE DE VENDER. Agradeça e encerre.

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
                    
                    # --- AQUI ESTÁ A CORREÇÃO MÁGICA ---
                    # Instruímos a IA a ignorar o histórico de "tchau" se o áudio for uma pergunta nova.
                    prompt_audio = f"""
                    ANALISE ESTE ÁUDIO COM ATENÇÃO MÁXIMA.
                    
                    1. O cliente pode estar fazendo uma PERGUNTA NOVA (sobre Preço, Funcionalidade, etc).
                    2. Se ele perguntar algo, IGNORE o fato de que a conversa estava encerrada no histórico e RESPONDA a dúvida.
                    3. Se ele perguntar PREÇO: Responda R$139 (Financeiro) ou R$189 (Completo).
                    4. SÓ encerre a conversa se o áudio for confirmando o agendamento (Ex: "Beleza, combinado").
                    
                    Base de conhecimento:
                    {INFO_PRODUTO}
                    
                    Responda ao áudio:
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