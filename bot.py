

from flask import Flask, request, jsonify
import requests
import google.generativeai as genai
import time
import os
import uuid
import json # Adicionado para garantir estabilidade

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
# Link Geral do Calendly (Mais seguro contra erro 404)
LINK_AGENDA = "https://calendly.com/rodriabreu" 

# --- CONFIGURAÇÃO DE TRANSBORDO ---
# Lista de números que a IA não deve mais responder (Memória Volátil)
clientes_pausados = []

# Seu número pessoal para receber o aviso (formato internacional sem +)
# Exemplo: 5531999999999
NUMERO_ADMIN = "5531993413530" 

# Palavras que ativam o modo humano
PALAVRAS_CHAVE = ["atendente", "humano", "falar com alguém", "especialista", "pessoa"]

# ==============================================================================
# BASE DE CONHECIMENTO (O Cérebro da Maria Clara)
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

# ✅ VOLTAMOS PARA O MODELO ESTÁVEL (O "TANQUE DE GUERRA")
# Se o 1.5 estava falhando, este aqui vai garantir que o texto saia.
model = genai.GenerativeModel('gemini-flash-latest') 

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
            # Filtro de mensagens enviadas por mim mesmo (Isso ignora o disparo do Disparador, o que é CORRETO)
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

            # --- LÓGICA DE ÁUDIO (BLOQUEIO EDUCADO) ---
            if tipo_msg == 'audio' or 'audioMessage' in msg_content:
                print(f"--- [CLIENTE] Áudio recebido de {sender} (Não processado por segurança)")
                
                # Resposta padrão imediata
                msg_bloqueio = "Desculpe, ainda não consigo ouvir áudios por aqui. 🎧 Poderia escrever sua dúvida por favor? Assim consigo te responder rapidinho! 😊"
                enviar_mensagem(sender, msg_bloqueio)
                
                # Salva no histórico para não perder o fio da meada
                if sender not in historico_conversas: historico_conversas[sender] = []
                historico_conversas[sender].append(f"Rodrigo: {msg_bloqueio}")
                
                continue # Pula o resto e espera o cliente digitar 

            # --- LÓGICA DE TEXTO ---
            else:
                if 'conversation' in msg: texto_cliente = msg['conversation']
                elif 'messageBody' in msg: texto_cliente = msg['messageBody']
                elif 'body' in msg: texto_cliente = msg['body']
                elif 'message' in msg: texto_cliente = msg_content.get('conversation') or msg_content.get('extendedTextMessage', {}).get('text')
                if not texto_cliente: continue

                # COMANDO DE RESET
                if texto_cliente.lower().strip() in ['reset', 'limpar', '/reset', '/limpar']:
                    historico_conversas[sender] = []
                    print(f"--- [RESET] Memória limpa para {sender}")
                    enviar_mensagem(sender, "♻️ Memória reiniciada! Pode começar um novo teste.")
                    continue 
                
                # Filtros Anti-Robô (LISTA AMPLIADA)
                termos_de_robo = [
                    "horário de atendimento", "não responda", "mensagem automática",
                    "digite a opção", "agradecemos sua mensagem", "estamos ausentes",
                    "no momento não", "toque no link", "obrigado pelo contato",
                    "assim que possível", "dúvidas frequentes", "nosso expediente",
                    "está fechada", "resposta automática", "visualizar o catálogo"
                ]
                if any(termo in texto_cliente.lower() for termo in termos_de_robo): 
                    print(f"--- [IGNORADO] Mensagem automática detectada de {sender}")
                    continue
                # ==============================================================
                # INICIO DA LÓGICA DE TRANSBORDO (HUMANO)
                # ==============================================================
                
                telefone_limpo = sender.split('@')[0]
                mensagem_lower = texto_cliente.lower()

                # 1. VERIFICA SE JÁ ESTÁ NA LISTA DE PAUSADOS
                if telefone_limpo in clientes_pausados:
                    print(f"--- [PAUSADO] Ignorando {telefone_limpo} (Aguardando Humano)")
                    continue # Pula para a próxima mensagem e não aciona o Gemini

                # 2. VERIFICA SE O CLIENTE PEDIU HUMANO AGORA
                if any(palavra in mensagem_lower for palavra in PALAVRAS_CHAVE):
                    print(f"--- [TRANSBORDO] Cliente {telefone_limpo} pediu humano.")
                    
                    # A) Adiciona na lista negra (memória)
                    clientes_pausados.append(telefone_limpo)
                    
                    # B) Avisa o Cliente (Usando sua função existente)
                    msg_cliente = "Entendido. Um especialista humano vai seguir com seu atendimento a partir de agora. Aguarde um momento! 👨‍💻"
                    enviar_mensagem(sender, msg_cliente)
                    
                    # C) Avisa VOCÊ (Admin) (Usando sua função existente)
                    msg_admin = f"🚨 ALERTA DE TRANSBORDO!\nCliente: {telefone_limpo}\nDisse: {texto_cliente}\n\nEntre no WhatsApp para assumir!"
                    enviar_mensagem(NUMERO_ADMIN, msg_admin)
                    
                    continue # Encerra aqui e não chama o Gemini
                
                # ==============================================================
                # FIM DA LÓGICA DE TRANSBORDO
                # ==============================================================
                
                print(f"--- [CLIENTE] {sender}: {texto_cliente}")

            # Atualiza memória
            if sender not in historico_conversas: historico_conversas[sender] = []
            
            if not eh_audio: historico_conversas[sender].append(f"Cliente: {texto_cliente}")
            else: historico_conversas[sender].append(f"Cliente: [Enviou um áudio]")
            
            memoria = "\n".join(historico_conversas[sender][-15:]) 
            
            # Limpa o link
            link_agenda_limpo = LINK_AGENDA.strip()

            # --- O PROMPT ---
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

            🔴 REGRA DE OURO (GATILHO DE PARADA):
            Se o cliente der sinais de encerramento ou postergação, como:
            - "Vou analisar"
            - "Vou ver"
            - "Ok obrigado"
            - "Qualquer coisa eu chamo"
            - "Tá bom"
            
            Nesse caso, PARE DE VENDER IMEDIATAMENTE.
            Apenas responda de forma curta e educada: "Combinado! Fico à disposição se tiver dúvidas. Um abraço!"
            NÃO faça novas perguntas e NÃO mande mais textos longos após isso.

            DIRETRIZES DE RESPOSTA:
            - Se o cliente estiver engajado (fazendo perguntas), explique os benefícios (Dashboards, Tarefas).
            - Se o cliente perguntar preço, fale.
            - Seja concisa. Evite blocos de texto gigantes.
            
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