

# from flask import Flask, request, jsonify
# import requests
# import google.generativeai as genai
# import time
# import os
# import json
# import re



# app = Flask(__name__)

# # ==============================================================================
# # 1. SUAS CHAVES
# # ==============================================================================
# WASENDER_API_KEY = os.environ.get("WASENDER_API_KEY")
# # No topo do arquivo, garanta que tem: import os
# GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# # ==============================================================================
# # 2. INFORMAÇÕES GERAIS
# # ==============================================================================
# NOME_EMPRESA = "SistemClass"
# LINK_LANDING = "https://sistemclass.com.br"
# LINK_AGENDA = "https://calendly.com/sistemclassoficial" 

# # --- CONFIGURAÇÃO DE TRANSBORDO ---
# NUMERO_ADMIN = "5531993413530" 
# PALAVRAS_CHAVE = ["atendente", "humano", "falar com alguém", "especialista", "pessoa"]

# # ARQUIVO PARA SALVAR OS BLOQUEADOS (PERSISTÊNCIA)
# ARQUIVO_PAUSADOS = "pausados.json"

# def carregar_pausados():
#     """Lê a lista de pausados do arquivo para não perder se reiniciar"""
#     if os.path.exists(ARQUIVO_PAUSADOS):
#         try:
#             with open(ARQUIVO_PAUSADOS, 'r') as f:
#                 return json.load(f)
#         except: return []
#     return []

# def salvar_pausado(numero):
#     """Adiciona um número na lista e salva no arquivo"""
#     lista = carregar_pausados()
#     if numero not in lista:
#         lista.append(numero)
#         with open(ARQUIVO_PAUSADOS, 'w') as f:
#             json.dump(lista, f)
#     return lista

# def remover_pausado(numero):
#     """Remove um número e salva"""
#     lista = carregar_pausados()
#     if numero in lista:
#         lista.remove(numero)
#         with open(ARQUIVO_PAUSADOS, 'w') as f:
#             json.dump(lista, f)
#     return lista

# # Carrega a lista ao iniciar
# clientes_pausados = carregar_pausados()

# # ==============================================================================
# # 3. TEXTOS E BASE DE CONHECIMENTO
# # ==============================================================================

# DADOS_ACESSO = f"""
# Link: {LINK_LANDING}
# Usuário: Teste@cliente
# Senha: @Jp167958
# """

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
# 4. DIFERENCIAIS: API com Conta Azul, Omie, Nibo. Geração de insights e laudos financeiros. Compatível com exportação para Domínio Sistemas.
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
#     global clientes_pausados 
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
#         # Garante que a lista está atualizada com o arquivo
#         clientes_pausados = carregar_pausados()

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

#             # --- 3. COMANDOS DE ADMIN (PARE / RESET) ---
#             sender_limpo = "".join(filter(str.isdigit, str(sender)))
#             admin_limpo = "".join(filter(str.isdigit, NUMERO_ADMIN))
            
#             # Debug para você ver no log quem é quem
#             print(f"--- [DEBUG] Sender: {sender_limpo} | Admin: {admin_limpo} | FromMe: {enviada_por_mim}")
            
#             # Verifica se é admin (com ou sem o 55) ou se foi enviado por mim no Web
#             eh_admin = enviada_por_mim or (admin_limpo in sender_limpo) or (sender_limpo in admin_limpo)

#             comando = texto_cliente.lower().strip()

#             # COMANDO /PARE (CORRIGIDO PARA DAR FEEDBACK)
#             if comando.startswith("/pare"):
#                 if eh_admin:
#                     try:
#                         # Se digitar só "/pare", bloqueia o chat atual
#                         numero_alvo = sender_limpo
                        
#                         # Se digitar "/pare 5531..." bloqueia o número especificado
#                         partes = comando.split(" ")
#                         if len(partes) > 1:
#                             numero_alvo = "".join(filter(str.isdigit, partes[1]))
                        
#                         if numero_alvo not in clientes_pausados:
#                             clientes_pausados = salvar_pausado(numero_alvo)
#                             print(f"🚫 COMANDO: {numero_alvo} foi silenciado pelo Admin.")
#                             # Força o envio da confirmação
#                             enviar_mensagem(sender, f"✅ Cliente {numero_alvo} SILENCIADO.")
#                         else:
#                             enviar_mensagem(sender, f"⚠️ {numero_alvo} já estava silenciado.")
#                         continue 
#                     except Exception as e:
#                         print(f"Erro no comando pare: {e}")
#                         continue
#                 else:
#                     print(f"--- [ALERTA] Tentativa de /pare negada para {sender_limpo} (Não é admin)")
#                     # Feedback opcional se falhar:
#                     # enviar_mensagem(sender, "⚠️ Comando negado. Não reconheci você como Admin.")
#                     continue

#             # COMANDO /RESET
#             if comando in ['reset', 'limpar', '/reset', '/limpar']:
#                 historico_conversas[sender] = []
                
#                 telefone_limpo_reset = sender.split('@')[0]
#                 numero_limpo_digits = "".join(filter(str.isdigit, telefone_limpo_reset))
                
#                 removido = False
#                 if telefone_limpo_reset in clientes_pausados:
#                     clientes_pausados = remover_pausado(telefone_limpo_reset)
#                     removido = True
#                 if numero_limpo_digits in clientes_pausados:
#                     clientes_pausados = remover_pausado(numero_limpo_digits)
#                     removido = True
                
#                 msg_retorno = "♻️ Memória reiniciada!"
#                 if removido: msg_retorno += " E cliente reativado (Despausado)."
                
#                 enviar_mensagem(sender, msg_retorno)
#                 continue 

#             if enviada_por_mim: continue

#             # --- 4. FILTRO ANTI-ROBÔ ---
            
#             # A) DETECÇÃO DE REPETIÇÃO
#             if sender in textos_por_usuario and len(textos_por_usuario[sender]) > 0:
#                 ultima_msg = textos_por_usuario[sender][-1]
#                 if texto_cliente.strip() == ultima_msg.strip():
#                     print(f"--- [IGNORADO] Loop de repetição detectado de {sender}")
#                     continue

#             # B) LISTA NEGRA DE TERMOS
#             termos_de_robo = [
#                 "digite a opção", "digite o número", "menu principal", 
#                 "atendimento eletrônico", "atendimento virtual", "assistente virtual",
#                 "mensagem automática", "não responda este e-mail", "não responda a esta mensagem",
#                 "protocolo de atendimento", "encerrar este chat", "encerrar atendimento",
#                 "voltar ao início", "tecla", "ura", "disque", "tecle",
#                 "escolha uma das opções", "para continuar", 
#                 "opção inválida", "opções abaixo", "opção invalida"
#             ]
#             if any(termo in texto_cliente.lower() for termo in termos_de_robo): 
#                 print(f"--- [IGNORADO] Menu/Robô detectado de {sender}")
#                 continue
                
#             # C) DETECÇÃO DE MENU NUMÉRICO
#             if len(texto_cliente) < 5 and texto_cliente.strip()[0].isdigit():
#                  print(f"--- [IGNORADO] Opção de Menu numérico detectada de {sender}")
#                  continue

#             # --- 5. VERIFICAÇÃO DE PAUSA (TRANSBORDO) ---
#             telefone_limpo = sender.split('@')[0]
#             numero_apenas_digitos = "".join(filter(str.isdigit, telefone_limpo))
            
#             if (telefone_limpo in clientes_pausados) or (numero_apenas_digitos in clientes_pausados):
#                 print(f"--- [SILENCIADO] Mensagem de {telefone_limpo} ignorada (está pausado).")
#                 continue 

#             # Transbordo por palavras-chave
#             if any(palavra in texto_cliente.lower() for palavra in PALAVRAS_CHAVE):
#                 clientes_pausados = salvar_pausado(numero_apenas_digitos)
#                 enviar_mensagem(sender, "Entendido. Um especialista humano vai seguir com seu atendimento. Aguarde um momento! 👨‍💻")
#                 enviar_mensagem(NUMERO_ADMIN, f"🚨 ALERTA TRANSBORDO!\nCliente: {telefone_limpo}\nDisse: {texto_cliente}")
#                 continue

#             if sender not in textos_por_usuario: textos_por_usuario[sender] = []
#             textos_por_usuario[sender].append(texto_cliente)

#         # ======================================================================
#         # LÓGICA DO GEMINI
#         # ======================================================================
#         for sender_user, lista_msgs in textos_por_usuario.items():
#             texto_completo = " ".join(lista_msgs)
#             historico_conversas[sender_user].append(f"Cliente: {texto_completo}")
#             memoria = "\n".join(historico_conversas[sender_user][-15:]) 
            
#             # --- PROMPT ATUALIZADO (REGRAS CONFIRMADAS) ---
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
            
#             AVISO IMPORTANTE (7 DIAS): "{TEXTO_TESTE_7_DIAS}"

#             HISTÓRICO RECENTE:
#             {memoria}
            
#             O QUE O CLIENTE DISSE AGORA: "{texto_completo}"

#             # DIRETRIZES ESTRITAS DE RESPOSTA (SIGA ESTA ORDEM):

#             0. REGRA SUPREMA (FILTRO DE RECUSA):
#                Analise a frase INTEIRA do cliente.
#                Se ele disser "não temos interesse", "no momento não", "não quero", "já tenho", "agradeço mas não":
#                -> IGNORE qualquer "Bom dia" ou "Tudo bem" que vier junto.
#                -> Vá direto para a regra 3 (DESINTERESSE).
            
#             1. SE FOR FASE DE INTERESSE (Primeiro contato / "Sim", "Quem é", "Como funciona"):
#                - Comece com uma frase humana e acolhedora.
#                - Explique o SistemClass usando os tópicos (bullets).
#                - Entregue o Usuário, Senha e Link de Teste.
#                - OBRIGATÓRIO: Logo após os dados de acesso, escreva: "{TEXTO_TESTE_7_DIAS}"
#                - Finalize enviando o Link da Agenda.
#                - Encerre a mensagem com a frase: "Qualquer dúvida estou à disposição!"
#                - IMPORTANTE: NÃO envie telefone comercial nesta primeira mensagem. Apenas a Agenda.
            
#             2. SE FOR DÚVIDA ESPECÍFICA (O cliente perguntou algo depois da apresentação):
#                - Responda direto ao ponto.
#                - Se o cliente perguntar PREÇO, PLANOS ou demonstrar interesse em FECHAR:
#                  -> Além de responder, diga: "Se preferir falar direto com nosso Comercial, chame no WhatsApp (31) 99341-3530 ou agende um horário no link acima!"

#             3. SE FOR DESINTERESSE:
#                - Responda apenas: "Entendido! Agradeço o retorno e desejo muito sucesso. Um abraço! 👋"
#                - NÃO tente vender nada.

#             IMPORTANTE: JAMAIS escreva "Passo A:", "Passo B:". Apenas o texto corrido.
#             """

#             try:
#                 time.sleep(1) 
#                 response = model.generate_content(instrucoes_base)
#                 resposta_bot = response.text.strip()
                
#                 resposta_bot = resposta_bot.replace("**Passo A**", "").replace("Passo A:", "")\
#                                            .replace("**Passo B**", "").replace("Passo B:", "")
                
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


# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import requests
import google.generativeai as genai
import time
import os
import json
import re

app = Flask(__name__)

# ==============================================================================
# 1) CHAVES (via variáveis de ambiente)
# ==============================================================================
WASENDER_API_KEY = os.environ.get("WASENDER_API_KEY")
GEMINI_API_KEY   = os.environ.get("GEMINI_API_KEY")

# ==============================================================================
# 2) DADOS DO SISTEMA / CONFIGURAÇÃO
# ==============================================================================
NOME_EMPRESA  = "SistemClass"
LINK_LANDING  = "https://sistemclass.com.br"
LINK_AGENDA   = "https://calendly.com/sistemclassoficial"

# Transbordo
NUMERO_ADMIN   = "5531993413530"
PALAVRAS_CHAVE = ["atendente", "humano", "falar com alguém", "especialista", "pessoa"]

# Pausados (persistência)
ARQUIVO_PAUSADOS = "pausados.json"

def carregar_pausados():
    """Lê a lista de pausados do arquivo para não perder ao reiniciar."""
    if os.path.exists(ARQUIVO_PAUSADOS):
        try:
            with open(ARQUIVO_PAUSADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def salvar_pausado(numero: str):
    """Adiciona um número na lista e salva no arquivo."""
    lista = carregar_pausados()
    if numero not in lista:
        lista.append(numero)
        with open(ARQUIVO_PAUSADOS, "w", encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False)
    return lista

def remover_pausado(numero: str):
    """Remove um número e salva."""
    lista = carregar_pausados()
    if numero in lista:
        lista.remove(numero)
        with open(ARQUIVO_PAUSADOS, "w", encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False)
    return lista

# Carrega na memória ao subir
clientes_pausados = carregar_pausados()

# ==============================================================================
# 3) TEXTOS (mantidos)
# ==============================================================================
DADOS_ACESSO = f"""
Link: {LINK_LANDING}
Usuário: Teste@cliente
Senha: @Jp167958
"""

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
4. DIFERENCIAIS: API com Conta Azul, Omie, Nibo. Geração de insights e laudos financeiros. Compatível com exportação para Domínio Sistemas.
"""

INFO_PRODUTO = f"""
REGRA DE OURO SOBRE PERSONALIZAÇÃO:
- LOGO DO CLIENTE: Apenas para planos ACIMA DE 5 CNPJs.
- CORES (PALETA): NÃO fazemos personalização de cores sob nenhuma hipótese. O layout é padrão.

PREÇOS (Apenas se perguntarem):
- R$139/mês (Financeiro) ou R$189/mês (Comercial+Fiscal).
- Descontos progressivos acima de 5 CNPJs.
"""

# ==============================================================================
# 4) GEMINI (mantido)
# ==============================================================================
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

# Memória e mapeamento
historico_conversas: dict[str, list[str]] = {}
mapa_ids: dict[str, str] = {}

# ==============================================================================
# 5) Envio de mensagem (mantido)
# ==============================================================================
def enviar_mensagem(telefone: str, texto: str):
    url = "https://www.wasenderapi.com/api/send-message"
    phone = telefone.split('@')[0]
    if not phone.startswith('+'):
        phone = f"+{phone}"
    payload = {"to": phone, "text": texto}
    headers = {
        "Authorization": f"Bearer {WASENDER_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        requests.post(url, json=payload, headers=headers, timeout=30)
    except Exception as e:
        print(f"Erro ao enviar msg: {e}")

# ==============================================================================
# 6) Anti-loop (ajustes cirúrgicos)
# ==============================================================================
# >>> Heurística de velocidade simples por remetente
ULTIMO_TS: dict[str, float] = {}

# >>> Kill-switch do cliente
STOP_COMMANDS_CLIENTE = {
    "pare", "/pare", "parar", "stop", "/stop", "cancelar", "chega", "silenciar", "/silenciar", "mute", "/mute"
}

# >>> Vocabulário extra de “menu/robô” (somado ao que você já tinha)
TERMOS_ROBO_EXTRA = [
    "responda com", "clique", "clique no link", "autoatendimento", "press", "pressione",
    "para falar com um atendente", "para falar com atendente", "opção 1)", "opção 2)",
    "selecione uma opção", "menu de opções", "ura", "ura.", "voltar ao menu",
    "para continuar digite", "digite seu cpf", "digite seu cnpj", "protocolo",
    "este número não recebe mensagens", "mensagem automática"
]

def _agora() -> float:
    return time.time()

def _extrair_numero_digitos(texto: str) -> str | None:
    m = re.search(r'(\d{10,14})', texto or "")
    return m.group(1) if m else None

# ==============================================================================
# 7) Webhook
# ==============================================================================
@app.route('/webhook', methods=['POST'])
def webhook():
    global clientes_pausados
    try:
        data = request.get_json()
        messages = []
        raw = None

        # Normalização dos formatos comuns
        if 'messages' in data:
            raw = data['messages']
        elif 'data' in data:
            raw = data['data'].get('messages', data['data'])
        elif 'payload' in data:
            raw = data['payload']

        if isinstance(raw, list):   messages = raw
        elif isinstance(raw, dict): messages = [raw]
        if not messages:
            return jsonify({"status": "ignored"}), 200

        textos_por_usuario: dict[str, list[str]] = {}

        # Recarrega pausados do arquivo (mantém sincronia)
        clientes_pausados = carregar_pausados()

        for msg in messages:
            key            = msg.get('key', {})
            enviada_por_mim = key.get('fromMe') or msg.get('fromMe')
            remote_jid     = key.get('remoteJid') or msg.get('from')
            sender         = remote_jid

            # Mapeia LID -> número real
            if sender and '@lid' in sender:
                if sender in mapa_ids:
                    sender = mapa_ids[sender]
                else:
                    real_number = key.get('senderPn') or key.get('participant')
                    if real_number:
                        mapa_ids[remote_jid] = real_number
                        sender = real_number

            # >>> Ignora grupos (evita prender em menus de grupo)
            if sender and str(sender).endswith('@g.us'):
                print(f"--- [INFO] Mensagem de grupo ignorada: {sender}")
                continue

            if sender not in historico_conversas:
                historico_conversas[sender] = []

            tipo_msg    = msg.get('messageType') or msg.get('type')
            msg_content = msg.get('message', {})
            texto_cliente = ''

            # 1) Bloqueio de áudio (mantido)
            if tipo_msg == 'audio' or 'audioMessage' in msg_content:
                if enviada_por_mim:
                    continue
                msg_bloqueio = ("Desculpe, ainda não consigo ouvir áudios por aqui. 🎧 "
                                "Poderia escrever sua dúvida por favor? Assim consigo te responder rapidinho! 😊")
                enviar_mensagem(sender, msg_bloqueio)
                historico_conversas[sender].append(f"Maria Clara: {msg_bloqueio}")
                continue

            # 2) Extração de texto (mantido)
            if 'conversation' in msg:
                texto_cliente = msg['conversation']
            elif 'messageBody' in msg:
                texto_cliente = msg['messageBody']
            elif 'body' in msg:
                texto_cliente = msg['body']
            elif 'message' in msg:
                texto_cliente = msg_content.get('conversation') or msg_content.get('extendedTextMessage', {}).get('text')

            if not texto_cliente:
                continue

            # 3) Comandos (admin e cliente)
            sender_limpo = "".join(filter(str.isdigit, str(sender)))
            admin_limpo  = "".join(filter(str.isdigit, NUMERO_ADMIN))
            print(f"--- [DEBUG] Sender: {sender_limpo} | Admin: {admin_limpo} | FromMe: {enviada_por_mim}")

            # É admin se: veio "fromMe" OU número bate (com/sem 55)
            eh_admin = bool(enviada_por_mim) or (admin_limpo in sender_limpo) or (sender_limpo in admin_limpo)
            comando  = texto_cliente.lower().strip()

            # >>> Kill-switch do CLIENTE (além do admin)
            if comando in STOP_COMMANDS_CLIENTE:
                telefone_limpo_cli = sender.split('@')[0]
                numero_cli = "".join(filter(str.isdigit, telefone_limpo_cli))
                clientes_pausados = salvar_pausado(numero_cli)
                enviar_mensagem(sender, "✅ Entendido. Vou ficar em silêncio por aqui. Se precisar, mande '/reset'.")
                print(f"--- [SILENCIADO POR CLIENTE] {numero_cli}")
                continue

            # /pare (admin) – pausa chat atual ou número informado em qualquer formato
            if comando.startswith("/pare"):
                if eh_admin:
                    try:
                        numero_alvo = sender_limpo  # padrão: pausa o chat atual
                        alvo_regex = _extrair_numero_digitos(comando)
                        if alvo_regex:
                            numero_alvo = alvo_regex

                        if numero_alvo not in clientes_pausados:
                            clientes_pausados = salvar_pausado(numero_alvo)
                            print(f"🚫 COMANDO: {numero_alvo} foi silenciado pelo Admin.")
                            enviar_mensagem(sender, f"✅ Cliente {numero_alvo} SILENCIADO.")
                        else:
                            enviar_mensagem(sender, f"⚠️ {numero_alvo} já estava silenciado.")
                    except Exception as e:
                        print(f"Erro no comando /pare: {e}")
                    finally:
                        continue
                else:
                    print(f"--- [ALERTA] Tentativa de /pare negada para {sender_limpo} (Não é admin)")
                    # enviar_mensagem(sender, "⚠️ Comando negado. Não reconheci você como Admin.")
                    continue

            # /reset (mantido) – limpa memória e “despausa” se estiver pausado
            if comando in ['reset', 'limpar', '/reset', '/limpar']:
                historico_conversas[sender] = []
                telefone_limpo_reset = sender.split('@')[0]
                numero_limpo_digits  = "".join(filter(str.isdigit, telefone_limpo_reset))
                removido = False
                if telefone_limpo_reset in clientes_pausados:
                    clientes_pausados = remover_pausado(telefone_limpo_reset)
                    removido = True
                if numero_limpo_digits in clientes_pausados:
                    clientes_pausados = remover_pausado(numero_limpo_digits)
                    removido = True
                msg_retorno = "♻️ Memória reiniciada!"
                if removido:
                    msg_retorno += " E cliente reativado (Despausado)."
                enviar_mensagem(sender, msg_retorno)
                continue

            # Evita responder a mim mesmo
            if enviada_por_mim:
                continue

            # 4) FILTRO ANTI-ROBÔ (refinado)
            # 4.a) Velocidade (mensagens < 2s do mesmo remetente)
            ts_now = _agora()
            ultimo = ULTIMO_TS.get(sender)
            ULTIMO_TS[sender] = ts_now
            if ultimo and (ts_now - ultimo) < 2.0:
                print(f"--- [IGNORADO] Mensagens muito rápidas de {sender} (possível robô).")
                continue

            # 4.b) Repetição imediata
            if sender in textos_por_usuario and len(textos_por_usuario[sender]) > 0:
                ultima_msg = textos_por_usuario[sender][-1]
                if texto_cliente.strip() == ultima_msg.strip():
                    print(f"--- [IGNORADO] Loop de repetição detectado de {sender}")
                    continue

            # 4.c) Lista negra (somamos os seus termos + extras)
            termos_de_robo = [
                "digite a opção", "digite o número", "menu principal",
                "atendimento eletrônico", "atendimento virtual", "assistente virtual",
                "mensagem automática", "não responda este e-mail", "não responda a esta mensagem",
                "protocolo de atendimento", "encerrar este chat", "encerrar atendimento",
                "voltar ao início", "tecla", "ura", "disque", "tecle",
                "escolha uma das opções", "para continuar",
                "opção inválida", "opções abaixo", "opção invalida"
            ] + TERMOS_ROBO_EXTRA

            if any(termo in texto_cliente.lower() for termo in termos_de_robo):
                print(f"--- [IGNORADO] Menu/Robô detectado de {sender}")
                continue

            # 4.d) Menu numérico curto (ex.: "1", "2", "3")
            if len(texto_cliente) < 5 and texto_cliente.strip() and texto_cliente.strip()[0].isdigit():
                print(f"--- [IGNORADO] Opção de menu numérico detectada de {sender}")
                continue

            # 5) Verificação de pausa (mantido)
            telefone_limpo       = sender.split('@')[0]
            numero_apenas_digitos = "".join(filter(str.isdigit, telefone_limpo))
            if (telefone_limpo in clientes_pausados) or (numero_apenas_digitos in clientes_pausados):
                print(f"--- [SILENCIADO] Mensagem de {telefone_limpo} ignorada (está pausado).")
                continue

            # Transbordo por palavras-chave (mantido)
            if any(p in texto_cliente.lower() for p in PALAVRAS_CHAVE):
                clientes_pausados = salvar_pausado(numero_apenas_digitos)
                enviar_mensagem(sender, "Entendido. Um especialista humano vai seguir com seu atendimento. Aguarde um momento! 👨‍💻")
                enviar_mensagem(NUMERO_ADMIN, f"🚨 ALERTA TRANSBORDO!\nCliente: {telefone_limpo}\nDisse: {texto_cliente}")
                continue

            # Agrupa por usuário para processar com o Gemini
            textos_por_usuario.setdefault(sender, []).append(texto_cliente)

        # ======================================================================
        # LÓGICA DO GEMINI (mantida com suas regras)
        # ======================================================================
        for sender_user, lista_msgs in textos_por_usuario.items():
            texto_completo = " ".join(lista_msgs)
            historico_conversas[sender_user].append(f"Cliente: {texto_completo}")
            memoria = "\n".join(historico_conversas[sender_user][-15:])  # últimas 15 interações

            instrucoes_base = f"""
Você é Maria Clara, especialista do {NOME_EMPRESA}.
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

# DIRETRIZES ESTRITAS DE RESPOSTA (SIGA ESTA ORDEM):

0. REGRA SUPREMA (FILTRO DE RECUSA):
Analise a frase INTEIRA do cliente.
Se ele disser "não temos interesse", "no momento não", "não quero", "já tenho", "agradeço mas não":
-> IGNORE qualquer "Bom dia" ou "Tudo bem" que vier junto.
-> Vá direto para a regra 3 (DESINTERESSE).

1. SE FOR FASE DE INTERESSE (Primeiro contato / "Sim", "Quem é", "Como funciona"):
- Comece com uma frase humana e acolhedora.
- Explique o SistemClass usando os tópicos (bullets).
- Entregue o Usuário, Senha e Link de Teste.
- OBRIGATÓRIO: Logo após os dados de acesso, escreva: "{TEXTO_TESTE_7_DIAS}"
- Finalize enviando o Link da Agenda.
- Encerre a mensagem com a frase: "Qualquer dúvida estou à disposição!"
- IMPORTANTE: NÃO envie telefone comercial nesta primeira mensagem. Apenas a Agenda.

2. SE FOR DÚVIDA ESPECÍFICA (o cliente perguntou algo depois da apresentação):
- Responda direto ao ponto.
- Se o cliente perguntar PREÇO, PLANOS ou demonstrar interesse em FECHAR:
-> Além de responder, diga: "Se preferir falar direto com nosso Comercial, chame no WhatsApp (31) 99341-3530 ou agende um horário no link acima!"

3. SE FOR DESINTERESSE:
- Responda apenas: "Entendido! Agradeço o retorno e desejo muito sucesso. Um abraço! 👋"
- NÃO tente vender nada.

IMPORTANTE: JAMAIS escreva "Passo A:", "Passo B:". Apenas o texto corrido.
"""
            try:
                time.sleep(1)
                response = model.generate_content(instrucoes_base)
                resposta_bot = (response.text or "").strip()
                # limpeza de rótulos indesejados
                for lixo in ("**Passo A**", "Passo A:", "**Passo B**", "Passo B:"):
                    resposta_bot = resposta_bot.replace(lixo, "")
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
