# from flask import Flask, request, jsonify
# import requests
# import google.generativeai as genai
# import time
# import os
# import uuid
# import json # Adicionado para garantir estabilidade

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
# # Link Geral do Calendly (Mais seguro contra erro 404)
# LINK_AGENDA = "https://calendly.com/financlassoficial" 

# # --- CONFIGURAÇÃO DE TRANSBORDO ---
# # Lista de números que a IA não deve mais responder (Memória Volátil)
# clientes_pausados = []

# # Seu número pessoal para receber o aviso (formato internacional sem +)
# # Exemplo: 5531999999999
# NUMERO_ADMIN = "5531993413530" 

# # Palavras que ativam o modo humano
# PALAVRAS_CHAVE = ["atendente", "humano", "falar com alguém", "especialista", "pessoa"]

# # ==============================================================================
# # BASE DE CONHECIMENTO (O Cérebro da Maria Clara)
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

# # ✅ VOLTAMOS PARA O MODELO ESTÁVEL (O "TANQUE DE GUERRA")
# # Se o 1.5 estava falhando, este aqui vai garantir que o texto saia.
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
#             # Filtro de mensagens enviadas por mim mesmo (Isso ignora o disparo do Disparador, o que é CORRETO)
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

#             # --- LÓGICA DE ÁUDIO (BLOQUEIO EDUCADO) ---
#             if tipo_msg == 'audio' or 'audioMessage' in msg_content:
#                 print(f"--- [CLIENTE] Áudio recebido de {sender} (Não processado por segurança)")
                
#                 # Resposta padrão imediata
#                 msg_bloqueio = "Desculpe, ainda não consigo ouvir áudios por aqui. 🎧 Poderia escrever sua dúvida por favor? Assim consigo te responder rapidinho! 😊"
#                 enviar_mensagem(sender, msg_bloqueio)
                
#                 # Salva no histórico para não perder o fio da meada
#                 if sender not in historico_conversas: historico_conversas[sender] = []
#                 historico_conversas[sender].append(f"Rodrigo: {msg_bloqueio}")
                
#                 continue # Pula o resto e espera o cliente digitar 

#             # --- LÓGICA DE TEXTO ---
#             else:
#                 if 'conversation' in msg: texto_cliente = msg['conversation']
#                 elif 'messageBody' in msg: texto_cliente = msg['messageBody']
#                 elif 'body' in msg: texto_cliente = msg['body']
#                 elif 'message' in msg: texto_cliente = msg_content.get('conversation') or msg_content.get('extendedTextMessage', {}).get('text')
#                 if not texto_cliente: continue

#                 # COMANDO DE RESET
#                 if texto_cliente.lower().strip() in ['reset', 'limpar', '/reset', '/limpar']:
#                     historico_conversas[sender] = []
#                     print(f"--- [RESET] Memória limpa para {sender}")
#                     enviar_mensagem(sender, "♻️ Memória reiniciada! Pode começar um novo teste.")
#                     continue 
                
#                 # Filtros Anti-Robô (LISTA AMPLIADA)
#                 termos_de_robo = [
#                     "horário de atendimento", "não responda", "mensagem automática",
#                     "digite a opção", "agradecemos sua mensagem", "estamos ausentes",
#                     "no momento não", "toque no link", "obrigado pelo contato",
#                     "assim que possível", "dúvidas frequentes", "nosso expediente",
#                     "está fechada", "resposta automática", "visualizar o catálogo"
#                 ]
#                 if any(termo in texto_cliente.lower() for termo in termos_de_robo): 
#                     print(f"--- [IGNORADO] Mensagem automática detectada de {sender}")
#                     continue
#                 # ==============================================================
#                 # INICIO DA LÓGICA DE TRANSBORDO (HUMANO)
#                 # ==============================================================
                
#                 telefone_limpo = sender.split('@')[0]
#                 mensagem_lower = texto_cliente.lower()

#                 # 1. VERIFICA SE JÁ ESTÁ NA LISTA DE PAUSADOS
#                 if telefone_limpo in clientes_pausados:
#                     print(f"--- [PAUSADO] Ignorando {telefone_limpo} (Aguardando Humano)")
#                     continue # Pula para a próxima mensagem e não aciona o Gemini

#                 # 2. VERIFICA SE O CLIENTE PEDIU HUMANO AGORA
#                 if any(palavra in mensagem_lower for palavra in PALAVRAS_CHAVE):
#                     print(f"--- [TRANSBORDO] Cliente {telefone_limpo} pediu humano.")
                    
#                     # A) Adiciona na lista negra (memória)
#                     clientes_pausados.append(telefone_limpo)
                    
#                     # B) Avisa o Cliente (Usando sua função existente)
#                     msg_cliente = "Entendido. Um especialista humano vai seguir com seu atendimento a partir de agora. Aguarde um momento! 👨‍💻"
#                     enviar_mensagem(sender, msg_cliente)
                    
#                     # C) Avisa VOCÊ (Admin) (Usando sua função existente)
#                     msg_admin = f"🚨 ALERTA DE TRANSBORDO!\nCliente: {telefone_limpo}\nDisse: {texto_cliente}\n\nEntre no WhatsApp para assumir!"
#                     enviar_mensagem(NUMERO_ADMIN, msg_admin)
                    
#                     continue # Encerra aqui e não chama o Gemini
                
#                 # ==============================================================
#                 # FIM DA LÓGICA DE TRANSBORDO
#                 # ==============================================================
                
#                 print(f"--- [CLIENTE] {sender}: {texto_cliente}")

#             # Atualiza memória
#             if sender not in historico_conversas: historico_conversas[sender] = []
            
#             if not eh_audio: historico_conversas[sender].append(f"Cliente: {texto_cliente}")
#             else: historico_conversas[sender].append(f"Cliente: [Enviou um áudio]")
            
#             memoria = "\n".join(historico_conversas[sender][-15:]) 
            
#             # Limpa o link
#             link_agenda_limpo = LINK_AGENDA.strip()

#             # --- O PROMPT (Atualizado para ser menos chata) ---
#             instrucoes_base = f"""
#             {INFO_PRODUTO}

#             CONTEXTO ATUAL:
#             Você é Maria Clara. Você está conversando com um lead sobre BPO Financeiro.
            
#             SUA MISSÃO:
#             Ser útil e consultiva. Seu objetivo final é o agendamento, MAS você não deve ser insistente.
            
#             🔴 REGRA DE OURO (GATILHO DE PARADA):
#             Se o cliente der sinais de encerramento ou postergação, como:
#             - "Vou analisar"
#             - "Vou ver"
#             - "Ok obrigado"
#             - "Qualquer coisa eu chamo"
#             - "Tá bom"
            
#             Nesse caso, PARE DE VENDER IMEDIATAMENTE.
#             Apenas responda de forma curta e educada: "Combinado! Fico à disposição se tiver dúvidas. Um abraço!"
#             NÃO faça novas perguntas e NÃO mande mais textos longos após isso.

#             DIRETRIZES DE RESPOSTA:
#             - Se o cliente estiver engajado (fazendo perguntas), explique os benefícios (Dashboards, Tarefas).
#             - Se o cliente perguntar preço, fale.
#             - Seja concisa. Evite blocos de texto gigantes.
            
#             LINKS (Só envie se o cliente pedir ou se houver abertura clara):
#             - Cadastro: {LINK_LANDING}
#             - Agenda: {link_agenda_limpo}

#             HISTÓRICO RECENTE:
#             {memoria}
#             """

#             try:
#                 time.sleep(3) 
#                 instrucoes_texto = instrucoes_base + "\nResponda como Maria Clara:"
#                 response = model.generate_content(instrucoes_texto)
#                 resposta_bot = response.text.strip()

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
import json

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
LINK_AGENDA = "https://calendly.com/financlassoficial" 

# --- CONFIGURAÇÃO DE TRANSBORDO ---
clientes_pausados = []
NUMERO_ADMIN = "5531993413530" 
PALAVRAS_CHAVE = ["atendente", "humano", "falar com alguém", "especialista", "pessoa", "falar com gente"]

# ==============================================================================
# 3. O CÉREBRO DA MARIA CLARA (TEXTO NOVO + PREÇOS ANTIGOS)
# ==============================================================================
INFO_PRODUTO = f"""
RESUMO ESTRATÉGICO PARA O AGENTE (MARIA CLARA):
Você é Maria Clara, consultora da SistemClass. 
Você está conversando com BPOs Financeiros. Seu objetivo é levar para o Teste Grátis ou Agendamento, mas sendo consultiva.

--- O PRODUTO (SISTEMCLASS - ERP 3 EM 1) ---
Desenvolvemos uma ferramenta de Gestão 3 em 1 (Modelo SaaS) que resolve todas as dores da operação de BPO em um só lugar.
Elimina a necessidade de contratar várias ferramentas (Trello, Emissores, Planilhas), reduzindo custos.

OS 3 PILARES (Use isso para explicar o funcionamento):
1. GESTÃO INTERNA (ORGANIZAÇÃO):
   - Gestão de contratos.
   - Gestor de tarefas nativo (estilo Trello e PlayBPO) para controlar a equipe.

2. GESTÃO OPERACIONAL (DIA A DIA):
   - Contas a Pagar/Receber, Conciliação Bancária, Emissão de Notas Fiscais.
   - Relatórios operacionais completos.

3. GESTÃO ESTRATÉGICA (O GRANDE DIFERENCIAL - BI):
   - Geração automática de Dashboards em tempo real (sem esperar fechar o mês).
   - DRE Gerencial, Fluxo de Caixa, KPIs e VALUATION automático.
   - Geração de insights e laudos financeiros/comerciais.
   - OBS: O cliente final acessa os resultados instantaneamente.

INTEGRAÇÕES E FLEXIBILIDADE:
- Temos API com: Conta Azul, Omie, Nibo e principais do mercado.
- Opção Modular: Se o cliente já tem ERP, pode contratar APENAS a parte Estratégica (BI) e integrar.
- Sem limite mínimo de licenças.

--- TABELA DE PREÇOS (SÓ FALE SE PERGUNTAREM) ---
- R$139,00/mês: Plano Financeiro.
- R$189,00/mês: Plano Completo (Comercial + Financeiro + Fiscal).
- Temos descontos progressivos acima de 5 CNPJs.

--- LINKS ---
- Link para Teste Grátis (7 dias): {LINK_LANDING}
- Link para Agenda: {LINK_AGENDA}
"""

genai.configure(api_key=GEMINI_API_KEY)
# Mantendo o modelo flash-latest que é mais rápido e barato, 
# mas você pode voltar para o 'gemini-1.5-flash' se preferir.
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

        for msg in messages:
            key = msg.get('key', {})
            if key.get('fromMe') or msg.get('fromMe'): continue

            remote_jid = key.get('remoteJid') or msg.get('from')
            sender = remote_jid

            # Tratamento do ID do remetente
            if sender and '@lid' in sender:
                if sender in mapa_ids: sender = mapa_ids[sender]
                else:
                    real_number = key.get('senderPn') or key.get('participant')
                    if real_number: mapa_ids[remote_jid] = real_number; sender = real_number

            tipo_msg = msg.get('messageType') or msg.get('type')
            msg_content = msg.get('message', {})
            texto_cliente = ''
            eh_audio = False

            # --- 1. BLOQUEIO DE ÁUDIO (MANTIDO DO ORIGINAL) ---
            if tipo_msg == 'audio' or 'audioMessage' in msg_content:
                print(f"--- [ÁUDIO] Recebido de {sender} (Bloqueado)")
                msg_bloqueio = "Desculpe, ainda não consigo ouvir áudios por aqui. 🎧 Poderia escrever sua dúvida por favor? Assim consigo te responder rapidinho! 😊"
                enviar_mensagem(sender, msg_bloqueio)
                
                if sender not in historico_conversas: historico_conversas[sender] = []
                historico_conversas[sender].append(f"Rodrigo: {msg_bloqueio}")
                continue 

            # --- 2. PROCESSAMENTO DE TEXTO ---
            else:
                if 'conversation' in msg: texto_cliente = msg['conversation']
                elif 'messageBody' in msg: texto_cliente = msg['messageBody']
                elif 'body' in msg: texto_cliente = msg['body']
                elif 'message' in msg: texto_cliente = msg_content.get('conversation') or msg_content.get('extendedTextMessage', {}).get('text')
                
                if not texto_cliente: continue

                # COMANDO DE RESET
                if texto_cliente.lower().strip() in ['reset', 'limpar', '/reset']:
                    historico_conversas[sender] = []
                    enviar_mensagem(sender, "♻️ Memória reiniciada! Pode começar um novo teste.")
                    continue 
                
                # FILTROS ANTI-ROBÔ
                termos_de_robo = [
                    "horário de atendimento", "não responda", "mensagem automática",
                    "digite a opção", "agradecemos sua mensagem", "estamos ausentes",
                    "no momento não", "toque no link", "obrigado pelo contato",
                    "assim que possível", "dúvidas frequentes"
                ]
                if any(termo in texto_cliente.lower() for termo in termos_de_robo): 
                    continue

                telefone_limpo = sender.split('@')[0]
                mensagem_lower = texto_cliente.lower()

                # --- 3. LÓGICA DE TRANSBORDO HUMANO ---
                if telefone_limpo in clientes_pausados:
                    print(f"--- [PAUSADO] {telefone_limpo} aguardando humano.")
                    continue 

                if any(palavra in mensagem_lower for palavra in PALAVRAS_CHAVE):
                    print(f"--- [TRANSBORDO] Cliente {telefone_limpo} pediu humano.")
                    clientes_pausados.append(telefone_limpo)
                    
                    msg_cliente = "Entendido. Um especialista humano vai seguir com seu atendimento a partir de agora. Aguarde um momento! 👨‍💻"
                    enviar_mensagem(sender, msg_cliente)
                    
                    msg_admin = f"🚨 ALERTA DE TRANSBORDO!\nCliente: {telefone_limpo}\nDisse: {texto_cliente}\nEntre no WhatsApp para assumir!"
                    enviar_mensagem(NUMERO_ADMIN, msg_admin)
                    continue 
                
                print(f"--- [CLIENTE] {sender}: {texto_cliente}")

            # --- 4. COMUNICAÇÃO COM O GEMINI ---
            if sender not in historico_conversas: historico_conversas[sender] = []
            
            historico_conversas[sender].append(f"Cliente: {texto_cliente}")
            memoria = "\n".join(historico_conversas[sender][-12:]) 

            # Prompt Estruturado
            instrucoes_base = f"""
            {INFO_PRODUTO}

            CONTEXTO DA CONVERSA:
            O cliente pode ter vindo de um disparo onde oferecemos um "ERP 3 em 1".
            
            SE O CLIENTE DISSER "SIM", "QUERO", "PODE":
            Mostre entusiasmo. Resuma os benefícios (Gestão Interna, Operacional e Estratégica) e convide para o teste grátis de 7 dias.

            SE O CLIENTE PERGUNTAR PREÇO:
            Seja direto: informe os valores (R$139 e R$189) e mencione os descontos para volume.
            
            REGRA DE OURO:
            Se o cliente disser "Vou ver", "Obrigado", "Qualquer coisa chamo" -> Encerre educadamente com "Fico à disposição" e PARE de vender.

            HISTÓRICO RECENTE:
            {memoria}
            """

            try:
                # Pequeno delay para naturalidade
                time.sleep(3) 
                
                response = model.generate_content(instrucoes_base + "\nResponda como Maria Clara:")
                resposta_bot = response.text.strip()

                print(f"--- [RODRIGO] {resposta_bot}")
                historico_conversas[sender].append(f"Rodrigo: {resposta_bot}")
                enviar_mensagem(sender, resposta_bot)

            except Exception as e_api:
                print(f"--- [ERRO GEMINI] {e_api}")

    except Exception as e:
        print(f"--- [ERRO GERAL] {e}")

    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)