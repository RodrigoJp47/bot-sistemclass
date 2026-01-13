

# from flask import Flask, request, jsonify
# import requests
# import google.generativeai as genai
# import time
# import os
# import uuid
# import json

# app = Flask(__name__)

# # ==============================================================================
# # 1. SUAS CHAVES
# # ==============================================================================
# WASENDER_API_KEY = "87cc26577dac7e7b62287fb2e3e54f40397395679518a15d1d731e041d00d462"
# GEMINI_API_KEY = "AIzaSyAM2Z3HyOcANDfRq1vr5ROX5QaX8LMBlBg"

# # ==============================================================================
# # 2. INFORMAÇÕES GERAIS
# # ==============================================================================
# NOME_EMPRESA = "SistemClass"
# LINK_LANDING = "https://sistemclass.com.br"
# LINK_AGENDA = "https://calendly.com/sistemclassoficial" 

# # --- CONFIGURAÇÃO DE TRANSBORDO ---
# clientes_pausados = []
# NUMERO_ADMIN = "5531993413530" 
# PALAVRAS_CHAVE = ["atendente", "humano", "falar com alguém", "especialista", "pessoa"]

# # ==============================================================================
# # 3. TEXTOS E BASE DE CONHECIMENTO
# # ==============================================================================

# DADOS_ACESSO = f"""
# Link: {LINK_LANDING}
# Usuário: Teste@cliente
# Senha: @Jp167958
# """

# # TEXTO ESPECÍFICO DO TESTE GRÁTIS (SEM CARTÃO)
# TEXTO_TESTE_7_DIAS = """
# 💡 Dica: Caso queira testar com seus próprios dados, você tem 7 dias grátis! 
# Não precisa de cartão de crédito. Basta clicar em "Cadastre-se" na página de login e sua senha é liberada na hora com apenas seu e-mail.
# """

# TOPICOS_APRESENTACAO = """
# 1. O QUE É: Ferramenta de Gestão 3 em 1 (ERP modelo SaaS). Resolve todas as dores do BPO Financeiro num só lugar.
# 2. BENEFÍCIOS: Elimina contratação de várias ferramentas, reduz custos, otimiza tempo. Sem limite mínimo de licenças.
# 3. FUNCIONALIDADES CHAVE:
#    - Gestão Interna: Gestão de contratos e tarefas (estilo Trello/Playbpo).
#    - Gestão Operacional: Contas a pagar/receber, conciliação, notas fiscais.
#    - Gestão Estratégica (BI): Dashboards em tempo real, DRE Gerencial, Fluxo de Caixa, KPIs e Valuation automático.
# 4. DIFERENCIAIS: API com Conta Azul, Omie, Nibo. Geração de insights e laudos financeiros.
# """

# INFO_PRODUTO = f"""
# REGRA DE OURO SOBRE PERSONALIZAÇÃO:
# - LOGO DO CLIENTE: Apenas para planos ACIMA DE 5 CNPJs.
# - CORES (PALETA): NÃO fazemos personalização de cores sob nenhuma hipótese. O layout é padrão.

# PREÇOS (Apenas se perguntarem):
# - R$139/mês (Financeiro) ou R$189/mês (Comercial+Fiscal).
# - Descontos progressivos acima de 5 CNPJs.
# """

# genai.configure(api_key=GEMINI_API_KEY)
# model = genai.GenerativeModel('gemini-flash-latest') 

# historico_conversas = {} 
# mapa_ids = {}

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

#         textos_por_usuario = {} 

#         for msg in messages:
#             key = msg.get('key', {})
#             enviada_por_mim = key.get('fromMe') or msg.get('fromMe')

#             remote_jid = key.get('remoteJid') or msg.get('from')
#             sender = remote_jid

#             if sender and '@lid' in sender:
#                 if sender in mapa_ids: sender = mapa_ids[sender]
#                 else:
#                     real_number = key.get('senderPn') or key.get('participant')
#                     if real_number: mapa_ids[remote_jid] = real_number; sender = real_number

#             if sender not in historico_conversas: historico_conversas[sender] = []

#             tipo_msg = msg.get('messageType') or msg.get('type')
#             msg_content = msg.get('message', {})
#             texto_cliente = ''
            
#             # --- 1. BLOQUEIO DE ÁUDIO ---
#             if tipo_msg == 'audio' or 'audioMessage' in msg_content:
#                 if enviada_por_mim: continue
#                 msg_bloqueio = "Desculpe, ainda não consigo ouvir áudios por aqui. 🎧 Poderia escrever sua dúvida por favor? Assim consigo te responder rapidinho! 😊"
#                 enviar_mensagem(sender, msg_bloqueio)
#                 historico_conversas[sender].append(f"Maria Clara: {msg_bloqueio}")
#                 continue 

#             # --- 2. EXTRAÇÃO DE TEXTO ---
#             if 'conversation' in msg: texto_cliente = msg['conversation']
#             elif 'messageBody' in msg: texto_cliente = msg['messageBody']
#             elif 'body' in msg: texto_cliente = msg['body']
#             elif 'message' in msg: texto_cliente = msg_content.get('conversation') or msg_content.get('extendedTextMessage', {}).get('text')
            
#             if not texto_cliente: continue

#             # --- 3. COMANDOS ---
#             sender_limpo = "".join(filter(str.isdigit, str(sender)))
#             admin_limpo = "".join(filter(str.isdigit, NUMERO_ADMIN))
#             eh_admin = (admin_limpo in sender_limpo) or enviada_por_mim

#             if eh_admin and texto_cliente.lower().startswith("/pare"):
#                 try:
#                     partes = texto_cliente.split(" ")
#                     numero_alvo_limpo = "".join(filter(str.isdigit, partes[1].strip())) if len(partes) > 1 else sender_limpo
                    
#                     if numero_alvo_limpo not in clientes_pausados:
#                         clientes_pausados.append(numero_alvo_limpo)
#                         if not enviada_por_mim: enviar_mensagem(sender, f"✅ Cliente {numero_alvo_limpo} SILENCIADO.")
#                     else:
#                         if not enviada_por_mim: enviar_mensagem(sender, f"⚠️ Já estava silenciado.")
#                     continue
#                 except: continue

#             if enviada_por_mim: continue

#             # --- 4. RESET ---
#             if texto_cliente.lower().strip() in ['reset', 'limpar', '/reset', '/limpar']:
#                 historico_conversas[sender] = []
#                 enviar_mensagem(sender, "♻️ Memória reiniciada!")
#                 continue 

#             # --- 5. FILTRO ANTI-ROBÔ (LISTA COMPLETA AGORA) ---
#             termos_de_robo = [
#                 "horário de atendimento", "não responda", "mensagem automática",
#                 "digite a opção", "agradecemos sua mensagem", "estamos ausentes",
#                 "no momento não", "toque no link", "obrigado pelo contato",
#                 "assim que possível", "dúvidas frequentes", "nosso expediente",
#                 "está fechada", "resposta automática", "visualizar o catálogo",
#                 "toque aqui", "saiba mais", "inscreva-se"
#             ]
#             if any(termo in texto_cliente.lower() for termo in termos_de_robo): continue

#             # --- 6. TRANSBORDO ---
#             telefone_limpo = sender.split('@')[0]
#             if telefone_limpo in clientes_pausados: continue 

#             if any(palavra in texto_cliente.lower() for palavra in PALAVRAS_CHAVE):
#                 clientes_pausados.append(telefone_limpo)
#                 enviar_mensagem(sender, "Entendido. Um especialista humano vai seguir com seu atendimento. Aguarde um momento! 👨‍💻")
#                 enviar_mensagem(NUMERO_ADMIN, f"🚨 ALERTA TRANSBORDO!\nCliente: {telefone_limpo}\nDisse: {texto_cliente}")
#                 continue

#             if sender not in textos_por_usuario: textos_por_usuario[sender] = []
#             textos_por_usuario[sender].append(texto_cliente)

#         # ======================================================================
#         # LÓGICA DO GEMINI ATUALIZADA (CORREÇÃO DE FORMATO)
#         # ======================================================================
#         for sender_user, lista_msgs in textos_por_usuario.items():
#             texto_completo = " ".join(lista_msgs)
#             historico_conversas[sender_user].append(f"Cliente: {texto_completo}")
#             memoria = "\n".join(historico_conversas[sender_user][-15:]) 
            
#             # --- PROMPT CORRIGIDO ---
#             instrucoes_base = f"""
#             Você é Maria Clara, especialista do SistemClass. 
#             Seu tom de voz: Amigável, consultivo, "gente como a gente", mas profissional. Use emojis moderados.
            
#             DADOS SOBRE O PRODUTO:
#             {TOPICOS_APRESENTACAO}
            
#             REGRAS TÉCNICAS:
#             {INFO_PRODUTO}

#             DADOS DE ACESSO (PARA ENTREGAR AO CLIENTE):
#             {DADOS_ACESSO}
#             LINK DA AGENDA: {LINK_AGENDA}

#             INFORMAÇÃO CRUCIAL (7 DIAS GRÁTIS):
#             {TEXTO_TESTE_7_DIAS}

#             HISTÓRICO RECENTE:
#             {memoria}
            
#             O QUE O CLIENTE DISSE AGORA: "{texto_completo}"

#             # DIRETRIZES ESTRITAS DE RESPOSTA:

#             ESTRUTURA MENTAL (Siga esta lógica, mas NÃO escreva os nomes dos passos como "Passo A" ou "Passo B". Escreva apenas o texto final corrido):

#             0. REGRA SUPREMA (FILTRO DE RECUSA):
#                Analise a frase INTEIRA do cliente.
#                Se ele disser "não temos interesse", "no momento não", "não quero", "já tenho", "agradeço mas não":
#                -> IGNORE qualquer "Bom dia" ou "Tudo bem" que vier junto.
#                -> Vá direto para a regra 3 (DESINTERESSE).

#             1. SE FOR FASE DE INTERESSE (Cliente disse "Sim", "Quem é", "Pode falar"):
#                - Comece com uma frase humana e acolhedora (ex: "Que maravilha!").
#                - Explique o SistemClass usando os tópicos de apresentação de forma fluida (use bullets para facilitar a leitura).
#                - OBRIGATÓRIO: Entregue AGORA o Usuário, Senha e Link de Teste.
#                - OBRIGATÓRIO: Entregue o link da Agenda.
            
#             2. SE FOR DÚVIDA ESPECÍFICA:
#                - Responda direto ao ponto usando as regras técnicas.

#             3. SE FOR DESINTERESSE ("Não quero"):
#                - Aceite o "não" de primeira. Agradeça e encerre. Não insista.
            
#             IMPORTANTE: 
#             - Sua resposta deve parecer uma conversa natural de WhatsApp.
#             - JAMAIS escreva "Passo A:", "Passo B:". Isso é uma instrução para você, não para o cliente.
#             """

#             try:
#                 time.sleep(1) 
#                 response = model.generate_content(instrucoes_base)
#                 resposta_bot = response.text.strip()
                
#                 # Segurança extra: Remove rótulos caso a IA ainda teime em gerar
#                 resposta_limpa = resposta_bot.replace("**Passo A (Empatia):**", "").replace("*Passo A (Empatia):*", "")\
#                                              .replace("**Passo B (Explicação):**", "").replace("*Passo B (Explicação):*", "")\
#                                              .replace("**Passo C (CTA de Ouro):**", "").replace("*Passo C (CTA de Ouro):*", "")\
#                                              .replace("**Passo D (Agenda):**", "").replace("*Passo D (Agenda):*", "")
                
#                 print(f"--- [MARIA CLARA] {resposta_limpa}")
#                 historico_conversas[sender_user].append(f"Maria Clara: {resposta_limpa}")
#                 enviar_mensagem(sender_user, resposta_limpa)

#             except Exception as e:
#                 print(f"Erro Gemini: {e}")

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
import json
import re

app = Flask(__name__)

# ==============================================================================
# 1. SUAS CHAVES
# ==============================================================================
WASENDER_API_KEY = "87cc26577dac7e7b62287fb2e3e54f40397395679518a15d1d731e041d00d462"
GEMINI_API_KEY = "AIzaSyAM2Z3HyOcANDfRq1vr5ROX5QaX8LMBlBg"

# ==============================================================================
# 2. INFORMAÇÕES GERAIS
# ==============================================================================
NOME_EMPRESA = "SistemClass"
LINK_LANDING = "https://sistemclass.com.br"
LINK_AGENDA = "https://calendly.com/sistemclassoficial" 

# --- CONFIGURAÇÃO DE TRANSBORDO ---
clientes_pausados = []
NUMERO_ADMIN = "5531993413530" 
PALAVRAS_CHAVE = ["atendente", "humano", "falar com alguém", "especialista", "pessoa"]

# ==============================================================================
# 3. TEXTOS E BASE DE CONHECIMENTO
# ==============================================================================

DADOS_ACESSO = f"""
Link: {LINK_LANDING}
Usuário: Teste@cliente
Senha: @Jp167958
"""

# TEXTO ESPECÍFICO DO TESTE GRÁTIS (SEM CARTÃO)
TEXTO_TESTE_7_DIAS = """
💡 Dica: Caso queira testar com seus próprios dados, você tem 7 dias grátis! 
Não precisa de cartão de crédito. Basta clicar em "Cadastre-se" na página de login e sua senha é liberada na hora com apenas seu e-mail.
"""

TOPICOS_APRESENTACAO = """
1. O QUE É: Ferramenta de Gestão 3 em 1 (ERP modelo SaaS). Resolve todas as dores do BPO Financeiro num só lugar.
2. BENEFÍCIOS: Elimina contratação de várias ferramentas, reduz custos, otimiza tempo. Sem limite mínimo de licenças.
3. FUNCIONALIDADES CHAVE:
   - Gestão Interna: Gestão de contratos e tarefas (estilo Trello/Playbpo).
   - Gestão Operacional: Contas a pagar/receber, conciliação, notas fiscais.
   - Gestão Estratégica (BI): Dashboards em tempo real, DRE Gerencial, Fluxo de Caixa, KPIs e Valuation automático.
4. DIFERENCIAIS: API com Conta Azul, Omie, Nibo. Geração de insights e laudos financeiros.
"""

INFO_PRODUTO = f"""
REGRA DE OURO SOBRE PERSONALIZAÇÃO:
- LOGO DO CLIENTE: Apenas para planos ACIMA DE 5 CNPJs.
- CORES (PALETA): NÃO fazemos personalização de cores sob nenhuma hipótese. O layout é padrão.

PREÇOS (Apenas se perguntarem):
- R$139/mês (Financeiro) ou R$189/mês (Comercial+Fiscal).
- Descontos progressivos acima de 5 CNPJs.
"""

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest') 

historico_conversas = {} 
mapa_ids = {}

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

        textos_por_usuario = {} 

        for msg in messages:
            key = msg.get('key', {})
            enviada_por_mim = key.get('fromMe') or msg.get('fromMe')

            remote_jid = key.get('remoteJid') or msg.get('from')
            sender = remote_jid

            if sender and '@lid' in sender:
                if sender in mapa_ids: sender = mapa_ids[sender]
                else:
                    real_number = key.get('senderPn') or key.get('participant')
                    if real_number: mapa_ids[remote_jid] = real_number; sender = real_number

            if sender not in historico_conversas: historico_conversas[sender] = []

            tipo_msg = msg.get('messageType') or msg.get('type')
            msg_content = msg.get('message', {})
            texto_cliente = ''
            
            # --- 1. BLOQUEIO DE ÁUDIO ---
            if tipo_msg == 'audio' or 'audioMessage' in msg_content:
                if enviada_por_mim: continue
                msg_bloqueio = "Desculpe, ainda não consigo ouvir áudios por aqui. 🎧 Poderia escrever sua dúvida por favor? Assim consigo te responder rapidinho! 😊"
                enviar_mensagem(sender, msg_bloqueio)
                historico_conversas[sender].append(f"Maria Clara: {msg_bloqueio}")
                continue 

            # --- 2. EXTRAÇÃO DE TEXTO ---
            if 'conversation' in msg: texto_cliente = msg['conversation']
            elif 'messageBody' in msg: texto_cliente = msg['messageBody']
            elif 'body' in msg: texto_cliente = msg['body']
            elif 'message' in msg: texto_cliente = msg_content.get('conversation') or msg_content.get('extendedTextMessage', {}).get('text')
            
            if not texto_cliente: continue

            # --- 3. COMANDOS ---
            sender_limpo = "".join(filter(str.isdigit, str(sender)))
            admin_limpo = "".join(filter(str.isdigit, NUMERO_ADMIN))
            eh_admin = (admin_limpo in sender_limpo) or enviada_por_mim

            if eh_admin and texto_cliente.lower().startswith("/pare"):
                try:
                    partes = texto_cliente.split(" ")
                    numero_alvo_limpo = "".join(filter(str.isdigit, partes[1].strip())) if len(partes) > 1 else sender_limpo
                    
                    if numero_alvo_limpo not in clientes_pausados:
                        clientes_pausados.append(numero_alvo_limpo)
                        if not enviada_por_mim: enviar_mensagem(sender, f"✅ Cliente {numero_alvo_limpo} SILENCIADO.")
                    else:
                        if not enviada_por_mim: enviar_mensagem(sender, f"⚠️ Já estava silenciado.")
                    continue
                except: continue

            if enviada_por_mim: continue

            # --- 4. RESET (CORRIGIDO PARA DESPAUSAR) ---
            if texto_cliente.lower().strip() in ['reset', 'limpar', '/reset', '/limpar']:
                historico_conversas[sender] = []
                # Remove da lista de pausados se estiver lá
                telefone_limpo_reset = sender.split('@')[0]
                if telefone_limpo_reset in clientes_pausados:
                    clientes_pausados.remove(telefone_limpo_reset)
                
                enviar_mensagem(sender, "♻️ Memória reiniciada e Robô reativado!")
                continue 

            # --- 5. FILTRO ANTI-ROBÔ (Blindagem Total) ---
            
            # A) DETECÇÃO DE REPETIÇÃO (Se o cliente mandar a mesma coisa 2x seguidas)
            if sender in textos_por_usuario and len(textos_por_usuario[sender]) > 0:
                ultima_msg = textos_por_usuario[sender][-1]
                # Se a mensagem for idêntica (ex: loop de erro), ignora
                if texto_cliente.strip() == ultima_msg.strip():
                    print(f"--- [IGNORADO] Loop de repetição detectado de {sender}")
                    continue

            # B) LISTA NEGRA DE TERMOS DE ROBÔ (Atualizada com o seu Print)
            termos_de_robo = [
                "digite a opção", "digite o número", "menu principal", 
                "atendimento eletrônico", "atendimento virtual", "assistente virtual",
                "mensagem automática", "não responda este e-mail", "não responda a esta mensagem",
                "protocolo de atendimento", "encerrar este chat", "encerrar atendimento",
                "voltar ao início", "tecla", "ura", "disque", "tecle",
                "escolha uma das opções", "para continuar", 
                "opção inválida", "opções abaixo", "opção invalida"
            ]
            
            # Verifica se tem algum termo proibido
            if any(termo in texto_cliente.lower() for termo in termos_de_robo): 
                print(f"--- [IGNORADO] Menu/Robô detectado de {sender}")
                continue
                
            # C) DETECÇÃO DE MENU NUMÉRICO (Ex: "1. Financeiro")
            # Se a mensagem for muito curta e começar com número, é menu.
            if len(texto_cliente) < 5 and texto_cliente.strip()[0].isdigit():
                 print(f"--- [IGNORADO] Opção de Menu numérico detectada de {sender}")
                 continue

            # --- 6. TRANSBORDO ---
            telefone_limpo = sender.split('@')[0]
            if telefone_limpo in clientes_pausados: continue 

            if any(palavra in texto_cliente.lower() for palavra in PALAVRAS_CHAVE):
                clientes_pausados.append(telefone_limpo)
                enviar_mensagem(sender, "Entendido. Um especialista humano vai seguir com seu atendimento. Aguarde um momento! 👨‍💻")
                enviar_mensagem(NUMERO_ADMIN, f"🚨 ALERTA TRANSBORDO!\nCliente: {telefone_limpo}\nDisse: {texto_cliente}")
                continue

            if sender not in textos_por_usuario: textos_por_usuario[sender] = []
            textos_por_usuario[sender].append(texto_cliente)

        # ======================================================================
        # LÓGICA DO GEMINI
        # ======================================================================
        for sender_user, lista_msgs in textos_por_usuario.items():
            texto_completo = " ".join(lista_msgs)
            historico_conversas[sender_user].append(f"Cliente: {texto_completo}")
            memoria = "\n".join(historico_conversas[sender_user][-15:]) 
            
            # --- PROMPT COM A CORREÇÃO DE LEITURA DO "NÃO" ---
            instrucoes_base = f"""
            Você é Maria Clara, especialista do SistemClass. 
            Seu tom de voz: Amigável, consultivo, "gente como a gente", mas profissional. Use emojis moderados.
            
            DADOS SOBRE O PRODUTO:
            {TOPICOS_APRESENTACAO}
            
            REGRAS TÉCNICAS:
            {INFO_PRODUTO}

            DADOS DE ACESSO (PARA ENTREGAR AO CLIENTE):
            {DADOS_ACESSO}
            LINK DA AGENDA: {LINK_AGENDA}
            
            AVISO IMPORTANTE (7 DIAS): "{TEXTO_TESTE_7_DIAS}"

            HISTÓRICO RECENTE:
            {memoria}
            
            O QUE O CLIENTE DISSE AGORA: "{texto_completo}"

            # DIRETRIZES ESTRITAS DE RESPOSTA (SIGA ESTA ORDEM DE PRIORIDADE):

            0. REGRA SUPREMA (FILTRO DE RECUSA):
               Analise a frase INTEIRA do cliente.
               Se ele disser "não temos interesse", "no momento não", "não quero", "já tenho", "agradeço mas não":
               -> IGNORE qualquer "Bom dia" ou "Tudo bem" que vier junto.
               -> Vá direto para a regra 3 (DESINTERESSE).
            
            1. SE FOR FASE DE INTERESSE (E não houver recusa):
               (Ex: "Sim", "Quem é", "Pode falar", "Bom dia, como funciona?"):
               - Comece com uma frase humana e acolhedora (ex: "Que maravilha!").
               - Explique o SistemClass usando os tópicos (bullets).
               - Entregue o Usuário, Senha e Link de Teste.
               - OBRIGATÓRIO: Logo após os dados de acesso, escreva exatamente: "{TEXTO_TESTE_7_DIAS}"
               - Finalize com o link da Agenda.
            
            2. SE FOR DÚVIDA ESPECÍFICA: Responda direto ao ponto.

            3. SE FOR DESINTERESSE (Detectado na Regra 0):
               - Responda apenas: "Entendido! Agradeço o retorno e desejo muito sucesso. Um abraço! 👋"
               - NÃO tente vender nada. NÃO faça perguntas. Apenas encerre.

            IMPORTANTE: JAMAIS escreva "Passo A:", "Passo B:". Apenas o texto corrido.
            """

            try:
                time.sleep(1) 
                response = model.generate_content(instrucoes_base)
                resposta_bot = response.text.strip()
                
                # Segurança simples para remover labels caso a IA gere
                resposta_bot = resposta_bot.replace("**Passo A**", "").replace("Passo A:", "")\
                                           .replace("**Passo B**", "").replace("Passo B:", "")
                
                print(f"--- [MARIA CLARA] {resposta_bot}")
                historico_conversas[sender_user].append(f"Maria Clara: {resposta_bot}")
                enviar_mensagem(sender_user, resposta_bot)

            except Exception as e:
                print(f"Erro Gemini: {e}")

    except Exception as e:
        print(f"--- [ERRO GERAL] {e}")

    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

