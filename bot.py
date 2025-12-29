

from flask import Flask, request, jsonify
import requests
import google.generativeai as genai
import json
import time
import os

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

# BASE DE CONHECIMENTO
INFO_PRODUTO = f"""
QUEM SOMOS: SistemClass, software exclusivo para BPO Financeiro.
FUNCIONALIDADES:
- Financeiro: Contas a pagar/receber, Gestão de tarefas tipo Trello, Gestão de orçamento, dashboards interativos (Dre por competência e caixa, fluxo de caixa, Valuetion e laudo financeiro).
- Comercial: Notas Fiscais, Gestão de contratos, Gestão de metas, Precifícação, PDV, dashboards interativos (Analise por região, por clientes, por vendedor, curva ABC, e laudo comercial).
- DIFERENCIAL TOP (Dashboards): DRE (Caixa e Competência), Fluxo de Caixa, KPIs, insights, valuetion, laudo comercial.
- DIFERENCIAL OURO (Integrações): Conta Azul, OMIE, NIBO, Olist tiny, Asaas, banco Inter e Mercado Pago.

CONDIÇÕES BPO:
- Sem taxa de setup.
- Sem mínimo de licenças.
- Whitelabel (Sua logo) acima de 5 licenças.
- Multi-CNPJ (Gestão de vários clientes com 1 login).
- Entrando acima de 5 CNPJs ganha 10% de desconto na mensalidade de cada CNPJ que é progressivo de acordo com a quantidade que vai entrar na base.

PREÇOS por cada CNPJ:
- R$139,00 (Módulo Financeiro).
- R$189,00 (Módulo financeiro + Módulo comercial com direito a emissão de notas fiscais).
"""

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

historico_conversas = {} 
mapa_ids = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        
        # Extração de mensagens
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
            # Ignora mensagens próprias
            key = msg.get('key', {})
            if key.get('fromMe') or msg.get('fromMe'): continue

            # Identificação do usuário
            remote_jid = key.get('remoteJid') or msg.get('from')
            sender = remote_jid

            if sender and '@lid' in sender:
                if sender in mapa_ids:
                    sender = mapa_ids[sender]
                else:
                    real_number = key.get('senderPn') or key.get('participant')
                    if real_number:
                        mapa_ids[remote_jid] = real_number
                        sender = real_number
                    else:
                        # Se não achar numero, tenta continuar com o ID mesmo
                        # para não perder a mensagem (melhoria de segurança)
                        pass 

            # Texto
            texto_cliente = ''
            if 'conversation' in msg: texto_cliente = msg['conversation']
            elif 'messageBody' in msg: texto_cliente = msg['messageBody']
            elif 'body' in msg: texto_cliente = msg['body']
            elif 'message' in msg:
                m = msg['message']
                texto_cliente = m.get('conversation') or m.get('extendedTextMessage', {}).get('text')

            if not texto_cliente: continue

            print(f"--- [CLIENTE] {sender}: {texto_cliente}")
            # --- BLOCO DE SEGURANÇA: FILTRO ANTI-ROBÔ ---
            # --- BLOCO DE SEGURANÇA: FILTRO ANTI-ROBÔ (ATUALIZADO) ---
            termos_de_robo = [
                "horário de atendimento", 
                "não responda", 
                "mensagem automática", 
                "digite a opção", 
                "estamos ausentes",
                "não estamos disponíveis",  # <--- Adicionado
                "responderemos assim que possível", # <--- Adicionado
                "agradecemos sua mensagem", # <--- Adicionado
                "agradecemos o seu contato",
                "toque em",
                "clique no link",
                "protocolo",
                "atendimento encerrado",
                "bem-vindo ao"
            ]

            # Verifica se parece robô (converte para minúsculo para comparar)
            if any(termo in texto_cliente.lower() for termo in termos_de_robo):
                print(f"🛑 Mensagem ignorada (Parece robô): {texto_cliente[:50]}...")
                continue # Pula para a próxima mensagem e NÃO chama o Gemini
            # ----------------------------------------------------
            # Memória
            if sender not in historico_conversas:
                historico_conversas[sender] = []
            
            historico_conversas[sender].append(f"Cliente: {texto_cliente}")
            memoria = "\n".join(historico_conversas[sender][-15:]) 

            # ==================================================================
            # 3. NOVO PROMPT (COM DISCURSO COMPLETO E MULTI-CNPJ)
            # ==================================================================
            prompt = f"""
            Você é a Maria Clara, especialista da SistemClass. 
            OBJETIVO: Vender o software para BPO Financeiro e tirar dúvidas.
            
            BASE DE CONHECIMENTO:
            {INFO_PRODUTO}
            
            LINKS:
            - Site (Teste 7 dias): {LINK_LANDING}
            - Agenda (Reunião): {LINK_AGENDA}

            DIRETRIZES:
            1. NUNCA DEIXE O CLIENTE SEM RESPOSTA (Ciclo Contínuo).
            2. Não use Markdown nos links. Envie apenas a URL crua (https://...).
            3. Seja natural e direto.

            ROTEIRO DE CONVERSA (Siga esta estrutura):
            
            ETAPA 1 (Apresentação Poderosa):
            Se perguntarem "Quem é?" ou "Quem fala?", responda com estas partes:
            
            1. "Olá! Eu sou a Maria Clara, especialista aqui da SistemClass. Somos um sistema exclusivo para BPO Financeiro."
            
            2. "Nosso sistema foi desenvolvido para sanar as dores do BPO. Unimos o melhor de um sistema ERP, com todas as suas funcionalidades." 
            
            3. "Adicionamos um gestor de tarefas (modelo Trello) para você acompanhar sua equipe" 
            
            4. "E principalmente, dashboards completos com todos os KPIs e insights para seu cliente como: DRE, Fluxo de Caixa, Análise de Contas (Aging List), Valuation (Estimativa), Laudo financeiro, etc..."
            
            5. "Outro ponto importante: somos Multi-CNPJ. Você gerencia todos os seus clientes na mesma conta, com apenas um login."

            6. "Para quem atende várias empresas isso faz muita diferença e eu só te falei um pouco do sistema, entregamos muito mais."
            
            -> TERMINE EXATAMENTE ASSIM:  "Fez sentido para você?"

            ETAPA 2 (Conexão e Oferta):
            Se o cliente responder "Sim", "Faz sentido", ou mostrar interesse:
            Diga: "Que ótimo! Com a SistemClass você automatiza tudo isso e ganha escala."
            -> PERGUNTE: "Quer conhecer na prática? Posso te passar o link para testar 7 dias grátis ou prefere agendar uma demo?"

            ETAPA 3 (Fechamento):
            - Se quiser TESTAR: "Show! Crie sua conta Multi-CNPJ aqui: {LINK_LANDING}"
            - Se quiser REUNIÃO: "Perfeito! Vamos conversar. Escolha o horário na minha agenda: {LINK_AGENDA}"

            ETAPA 4 (Pós-Link / Continuidade):
            Se o cliente continuar falando após receber o link (ex: pediu reunião depois de ver o site), atenda o novo pedido!
            Responda qualquer dúvida sobre preço (R$139 ou R$189) ou funcionalidades.

            HISTÓRICO RECENTE:
            {memoria}
            
            Responda de forma fluida e profissional:
            """
            
            try:
                # Delay humano
                time.sleep(3) 
                
                response = model.generate_content(prompt)
                resposta_bot = response.text.strip()
                print(f"--- [RODRIGO] {resposta_bot}")

                historico_conversas[sender].append(f"Rodrigo: {resposta_bot}")

                # Envio
                url = "https://www.wasenderapi.com/api/send-message"
                phone = sender.split('@')[0]
                if not phone.startswith('+'): phone = f"+{phone}"

                payload = {"to": phone, "text": resposta_bot}
                headers = {
                    "Authorization": f"Bearer {WASENDER_API_KEY}",
                    "Content-Type": "application/json"
                }
                envio = requests.post(url, json=payload, headers=headers)
                
                # Debug extra caso falhe
                if envio.status_code != 200:
                    print(f"--- [ERRO ENVIO] Code: {envio.status_code} | {envio.text}")

            except Exception as e_api:
                print(f"--- [ERRO INTERNO] {e_api}")

    except Exception as e:
        print(f"--- [ERRO GERAL] {e}")

    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    # Pega a porta do Render ou usa 5000 se for local
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)