


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

# # --- SEU NOVO TEXTO DE APRESENTAÇÃO (TEXTÃO) ---
# # Adicionado o LINK DA AGENDA conforme solicitado
# SCRIPT_BOAS_VINDAS = f"""Olá! 
# Aqui é a Maria Clara da SistemClass.

# Desenvolvemos uma ferramenta de Gestão 3 em 1. Um ERP modelo SaaS. Que resolve todas as dores da operação de BPO Financeiro em um só lugar. O que elimina a necessidade de contratação de várias ferramentas na sua operação. Reduzindo os seus custos e otimizando o seu tempo. E sem limite mínimo de licenças na contratação. 

# Com o SistemClass você consegue fazer: 

# * Gestão interna dos seus clientes. 
# Gestão de contratos. Gestor de tarefas - estilo Trello e Playbpo. 

# * Gestão operacional. 
# Gestão de Contas a Pagar. Contas a Receber. Conciliação bancária. Emissão de notas fiscais. Relatórios e afins. 

# * Gestão Estratégica - BI - (Business Intelligence) 
# Geração automática de dashboards estratégicos em tempo real para o seu cliente. Sem a necessidade de esperar o fechamento do mês para apresentar resultados. O seu cliente tem acesso aos seus resultados de forma instantânea. 

# Apresentação de resultados através de DRE Gerencial / Fluxo de Caixa / KPI's e até Valuation. De forma automática. 

# O nosso sistema ainda conta com geração de insights em tempo real e geração de laudos financeiros e comerciais.  

# Tudo isso integrado dentro da mesma ferramenta. Com um custo que cabe dentro da sua operação e sem limite mínimo de licenças a ser contratado. 

# Diferenciais: Temos API com os principais sistemas de mercado. Conta Azul / Omie / Nibo e afins. 

# Caso você queira contratar apenas a parte estratégica, você também a opção de integrar as duas ferramentas. 

# Caso tenha interesse em conhecer a nossa ferramenta você poderá fazer o teste por 7 dias grátis.

# Vou deixar o link com usuário e senha de teste para você entrar e conhecer nossa ferramenta. Essa senha fica disponível por 24 horas, depois expira.

#  Link: {LINK_LANDING}
#  Usuário: Teste@cliente
#  Senha: @Jp167958

# Caso prefira uma apresentação guiada, você pode agendar uma reunião conosco aqui:
# 📅 Agendar Reunião: {LINK_AGENDA}

# Caso tenha gostado e queira começar a testar por 7 dias grátis, é só voltar a pagina de login e clicar em cadastro, após fazer o cadastro a sua licença já vai ser liberada na hora, sem precisar de colocar cartão de credito.

# Caso queira mais informações, estou á disposição!"""

# # --- INFORMAÇÕES TÉCNICAS (CÉREBRO PARA TIRAR DÚVIDAS DEPOIS) ---
# INFO_PRODUTO = f"""
# RESUMO TÉCNICO PARA O AGENTE (USAR APENAS SE O CLIENTE TIVER DÚVIDAS APÓS LER O TEXTO INICIAL):

# 1. INTELIGÊNCIA: Dashboards prontos de DRE, Fluxo de Caixa, Laudos Financeiros e Valuation.
# 2. ORGANIZAÇÃO: Gestor de Tarefas nativo.
# 3. ESCALA: Multi-CNPJ (Painel unificado).
# 4. Integrações: OMIE, NIBO, CONTA AZUL, OLIST, MERCADO PAGO.
# 5. Versatilidade: PDV, CRM, Orçamentos, Notas Fiscais.

# 🔴 REGRAS DE PERSONALIZAÇÃO (O QUE PODE E O QUE NÃO PODE):
# - LOGO DO CLIENTE: Apenas para planos ACIMA DE 5 CNPJs. (Para menos de 5, o sistema vai com a logo SistemClass padrão).
# - CORES (PALETA): NÃO fazemos personalização de cores. O layout é padrão e otimizado para performance. Se o cliente perguntar, diga educadamente que não é possível alterar as cores do sistema.

# PREÇOS (Se perguntarem):
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
#                 print(f"--- [CLIENTE] Áudio recebido de {sender}")
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

#             # --- 3. COMANDOS DE ADMIN (AGORA FUNCIONA SE VOCÊ DIGITAR) ---
#             sender_limpo = "".join(filter(str.isdigit, str(sender)))
#             admin_limpo = "".join(filter(str.isdigit, NUMERO_ADMIN))
            
#             # Verifica se quem mandou é o Admin OU se a mensagem foi enviada por MIM (Dono no Web/Celular)
#             eh_admin = (admin_limpo in sender_limpo) or enviada_por_mim

#             if eh_admin and texto_cliente.lower().startswith("/pare"):
#                 try:
#                     # Se digitar só "/pare", pausa o chat atual (se estiver dentro da conversa)
#                     partes = texto_cliente.split(" ")
#                     if len(partes) > 1:
#                         numero_para_parar = partes[1].strip()
#                         numero_alvo_limpo = "".join(filter(str.isdigit, numero_para_parar))
#                     else:
#                         # Pega o número do chat atual (mesmo que seja o remoteJid)
#                         numero_alvo_limpo = sender_limpo
                    
#                     if numero_alvo_limpo not in clientes_pausados:
#                         clientes_pausados.append(numero_alvo_limpo)
#                         print(f"🚫 COMANDO /PARE: Cliente {numero_alvo_limpo} pausado.")
#                         # Só responde se não for eu mesmo falando pra não ficar estranho
#                         if not enviada_por_mim: 
#                             enviar_mensagem(sender, f"✅ O cliente {numero_alvo_limpo} foi SILENCIADO.")
#                     else:
#                         if not enviada_por_mim:
#                             enviar_mensagem(sender, f"⚠️ O cliente {numero_alvo_limpo} já estava silenciado.")
                    
#                     # Interrompe o processamento dessa mensagem
#                     continue
#                 except Exception as e:
#                     print(f"Erro no comando /pare: {e}")
#                     continue

#             # Se for msg minha e não for comando, ignora (para o bot não falar sozinho)
#             if enviada_por_mim: continue

#             # --- 4. RESET ---
#             if texto_cliente.lower().strip() in ['reset', 'limpar', '/reset', '/limpar']:
#                 historico_conversas[sender] = []
#                 enviar_mensagem(sender, "♻️ Memória reiniciada! Pode começar um novo teste.")
#                 continue 

#             # --- 5. FILTRO ANTI-ROBÔ ---
#             termos_de_robo = [
#                 "horário de atendimento", "não responda", "mensagem automática",
#                 "digite a opção", "agradecemos sua mensagem", "estamos ausentes",
#                 "no momento não", "toque no link", "obrigado pelo contato",
#                 "assim que possível", "dúvidas frequentes", "nosso expediente",
#                 "está fechada", "resposta automática", "visualizar o catálogo"
#             ]
#             if any(termo in texto_cliente.lower() for termo in termos_de_robo): 
#                 print(f"--- [IGNORADO] Robô detectado de {sender}")
#                 continue

#             # --- 6. TRANSBORDO ---
#             telefone_limpo = sender.split('@')[0]
#             if telefone_limpo in clientes_pausados:
#                 continue 

#             if any(palavra in texto_cliente.lower() for palavra in PALAVRAS_CHAVE):
#                 clientes_pausados.append(telefone_limpo)
#                 enviar_mensagem(sender, "Entendido. Um especialista humano vai seguir com seu atendimento. Aguarde um momento! 👨‍💻")
#                 enviar_mensagem(NUMERO_ADMIN, f"🚨 ALERTA TRANSBORDO!\nCliente: {telefone_limpo}\nDisse: {texto_cliente}")
#                 continue

#             # --- 7. ACUMULA BUFFER ---
#             if sender not in textos_por_usuario:
#                 textos_por_usuario[sender] = []
#             textos_por_usuario[sender].append(texto_cliente)

#         # ======================================================================
#         # PROCESSAMENTO COM A NOVA LÓGICA
#         # ======================================================================
#         for sender_user, lista_msgs in textos_por_usuario.items():
#             texto_completo = " ".join(lista_msgs)
            
#             print(f"--- [CLIENTE] {sender_user}: {texto_completo}")
#             historico_conversas[sender_user].append(f"Cliente: {texto_completo}")
            
#             memoria = "\n".join(historico_conversas[sender_user][-15:]) 
            
#             # --- PROMPT ATUALIZADO (C/ LINK AGENDA E REGRA DE REUNIÃO) ---
#             instrucoes_base = f"""
#             {INFO_PRODUTO}
#             LINK PARA AGENDAMENTO DE REUNIÃO: {LINK_AGENDA}

#             TEXTO PADRÃO DE BOAS-VINDAS (SCRIPT OBRIGATÓRIO):
#             {SCRIPT_BOAS_VINDAS}

#             CONTEXTO:
#             Você é Maria Clara, especialista do SistemClass. 
            
#             SITUAÇÃO ATUAL:
#             O cliente disse: "{texto_completo}"

#             # ==================================================================
#             # REGRAS DE DECISÃO (IMPORTANTE)
#             # ==================================================================

#             1. CASO SEJA O PRIMEIRO CONTATO APÓS A ISCA:
#                Se o cliente respondeu "Quem é?", "Sou eu", "Pode falar", "Sim", "O que é?" ou qualquer variação de interesse inicial:
#                ✅ AÇÃO: Responda EXATAMENTE com o texto completo que está em "TEXTO PADRÃO DE BOAS-VINDAS" acima. Não mude nada, copie e cole o texto todo.

#             2. CASO O CLIENTE DIGA "SIM" (Após já ter recebido o Textão):
#                (O seu texto padrão termina com "Digite sim para continuar").
#                Se o cliente digitou "Sim" agora, ele já leu o texto e quer seguir.
#                ✅ AÇÃO: Não mande o texto grande de novo.
#                Pergunte: "Que ótimo! Você conseguiu acessar o link de teste com a senha que te passei? Ou ficou com alguma dúvida sobre os Dashboards? Se preferir, também posso te enviar nosso link para agendar uma demonstração guiada."

#             3. CASO DÚVIDAS ESPECÍFICAS (Cores, Logo, Funcionalidades):
#                Se o cliente perguntar sobre personalização (Logo/Cores) ou funcionalidades.
#                ✅ AÇÃO: Consulte o campo INFO_PRODUTO acima e responda de forma curta e direta.
#                (Lembre-se: NÃO mudamos cores e Logo apenas acima de 5 CNPJs).
            
#             4. CASO PEDIDO DE REUNIÃO/AGENDA (NOVA REGRA):
#                Se o cliente pedir para marcar reunião, falar, call, videochamada ou demonstração:
#                ✅ AÇÃO: Responda "Com certeza! Será um prazer te apresentar o sistema em detalhes. Você pode escolher o melhor horário na nossa agenda aqui: {LINK_AGENDA}"

#             5. CASO NEGATIVO ("Não tenho interesse", "Não quero", "No momento não", "Agora não"):
#                ✅ AÇÃO: Responda "Entendido! Agradeço a atenção e fico à disposição. Um abraço!" e encerre a conversa. NÃO insista.

#             HISTÓRICO DA CONVERSA:
#             {memoria}
#             """

#             try:
#                 time.sleep(1) 
#                 response = model.generate_content(instrucoes_base)
#                 resposta_bot = response.text.strip()

#                 print(f"--- [MARIA CLARA] {resposta_bot}")
#                 historico_conversas[sender_user].append(f"Maria Clara: {resposta_bot}")
#                 enviar_mensagem(sender_user, resposta_bot)

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

            # --- 4. RESET ---
            if texto_cliente.lower().strip() in ['reset', 'limpar', '/reset', '/limpar']:
                historico_conversas[sender] = []
                enviar_mensagem(sender, "♻️ Memória reiniciada!")
                continue 

            # --- 5. FILTRO ANTI-ROBÔ (LISTA COMPLETA AGORA) ---
            termos_de_robo = [
                "horário de atendimento", "não responda", "mensagem automática",
                "digite a opção", "agradecemos sua mensagem", "estamos ausentes",
                "no momento não", "toque no link", "obrigado pelo contato",
                "assim que possível", "dúvidas frequentes", "nosso expediente",
                "está fechada", "resposta automática", "visualizar o catálogo",
                "toque aqui", "saiba mais", "inscreva-se"
            ]
            if any(termo in texto_cliente.lower() for termo in termos_de_robo): continue

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
        # LÓGICA DO GEMINI ATUALIZADA (CORREÇÃO DE FORMATO)
        # ======================================================================
        for sender_user, lista_msgs in textos_por_usuario.items():
            texto_completo = " ".join(lista_msgs)
            historico_conversas[sender_user].append(f"Cliente: {texto_completo}")
            memoria = "\n".join(historico_conversas[sender_user][-15:]) 
            
            # --- PROMPT CORRIGIDO ---
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

            INFORMAÇÃO CRUCIAL (7 DIAS GRÁTIS):
            {TEXTO_TESTE_7_DIAS}

            HISTÓRICO RECENTE:
            {memoria}
            
            O QUE O CLIENTE DISSE AGORA: "{texto_completo}"

            # DIRETRIZES ESTRITAS DE RESPOSTA:

            ESTRUTURA MENTAL (Siga esta lógica, mas NÃO escreva os nomes dos passos como "Passo A" ou "Passo B". Escreva apenas o texto final corrido):

            1. SE FOR FASE DE INTERESSE (Cliente disse "Sim", "Quem é", "Pode falar"):
               - Comece com uma frase humana e acolhedora (ex: "Que maravilha!").
               - Explique o SistemClass usando os tópicos de apresentação de forma fluida (use bullets para facilitar a leitura).
               - OBRIGATÓRIO: Entregue AGORA o Usuário, Senha e Link de Teste.
               - OBRIGATÓRIO: Entregue o link da Agenda.
            
            2. SE FOR DÚVIDA ESPECÍFICA:
               - Responda direto ao ponto usando as regras técnicas.

            3. SE FOR DESINTERESSE ("Não quero"):
               - Aceite o "não" de primeira. Agradeça e encerre. Não insista.
            
            IMPORTANTE: 
            - Sua resposta deve parecer uma conversa natural de WhatsApp.
            - JAMAIS escreva "Passo A:", "Passo B:". Isso é uma instrução para você, não para o cliente.
            """

            try:
                time.sleep(1) 
                response = model.generate_content(instrucoes_base)
                resposta_bot = response.text.strip()
                
                # Segurança extra: Remove rótulos caso a IA ainda teime em gerar
                resposta_limpa = resposta_bot.replace("**Passo A (Empatia):**", "").replace("*Passo A (Empatia):*", "")\
                                             .replace("**Passo B (Explicação):**", "").replace("*Passo B (Explicação):*", "")\
                                             .replace("**Passo C (CTA de Ouro):**", "").replace("*Passo C (CTA de Ouro):*", "")\
                                             .replace("**Passo D (Agenda):**", "").replace("*Passo D (Agenda):*", "")
                
                print(f"--- [MARIA CLARA] {resposta_limpa}")
                historico_conversas[sender_user].append(f"Maria Clara: {resposta_limpa}")
                enviar_mensagem(sender_user, resposta_limpa)

            except Exception as e:
                print(f"Erro Gemini: {e}")

    except Exception as e:
        print(f"--- [ERRO GERAL] {e}")

    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)