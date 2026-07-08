



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
# 1. SUAS CHAVES
# ==============================================================================
WASENDER_API_KEY = os.environ.get("WASENDER_API_KEY")
GEMINI_API_KEY   = os.environ.get("GEMINI_API_KEY")

# ==============================================================================
# 2. INFORMAÇÕES GERAIS
# ==============================================================================
NOME_EMPRESA  = "SistemClass"
LINK_LANDING  = "https://sistemclass.com.br"
LINK_AGENDAMENTO = "https://sistemclass.zohobookings.com/#/sistemclass"


# --- CONFIGURAÇÃO DE TRANSBORDO ---
NUMERO_ADMIN   = "5531993413530"
PALAVRAS_CHAVE = ["atendente", "humano", "falar com alguém", "especialista", "pessoa"]

# ARQUIVO PARA SALVAR OS BLOQUEADOS (PERSISTÊNCIA)
ARQUIVO_PAUSADOS = "pausados.json"

def carregar_pausados():
    """Lê a lista de pausados do arquivo para não perder se reiniciar"""
    if os.path.exists(ARQUIVO_PAUSADOS):
        try:
            with open(ARQUIVO_PAUSADOS, 'r', encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def salvar_pausado(numero: str):
    """Adiciona um número na lista e salva no arquivo"""
    lista = carregar_pausados()
    if numero not in lista:
        lista.append(numero)
        with open(ARQUIVO_PAUSADOS, 'w', encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False)
    return lista

def remover_pausado(numero: str):
    """Remove um número e salva"""
    lista = carregar_pausados()
    if numero in lista:
        lista.remove(numero)
        with open(ARQUIVO_PAUSADOS, 'w', encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False)
    return lista

# Carrega a lista ao iniciar
clientes_pausados = carregar_pausados()

# ==============================================================================
# 3. TEXTOS E BASE DE CONHECIMENTO  (MEMÓRIA ORIGINAL)
# ==============================================================================
DADOS_ACESSO = f"""
Link: {LINK_LANDING}
Usuário: SistemClass_2026
Senha: @Jp123456
"""

TEXTO_ACESSO_DEMO = """
💡 Importante: este é um acesso de demonstração compartilhado, com dados fictícios, para você explorar o sistema por dentro à vontade.
Por gentileza, não altere a senha. Se quiser um ambiente exclusivo para testar com seus próprios dados, é só me avisar que nosso time libera para você! 😊
"""

TOPICOS_APRESENTACAO = """
1. O QUE É: SaaS de gestão empresarial multiempresa (ERP) voltado para pequenas e médias empresas brasileiras. Reúne num único ambiente os módulos Financeiro, Comercial, Fiscal, Contábil e BPO, com IA integrada.

2. MÓDULO FINANCEIRO (todos os planos):
 - Contas a Pagar e Receber com recorrência automática, classificação por Área DRE, Centro de Custo e Projeto.
 - DRE Gerencial completa (Receita Bruta → Lucro Líquido), análise vertical e horizontal, regime competência ou caixa.
 - Fluxo de Caixa Analítico com gráfico de evolução e saldo projetado.
 - Painel Financeiro com Valuation automático, Ponto de Equilíbrio e KPIs avançados.
 - Laudo Financeiro gerado por IA (Google Gemini) com um clique.
 - Conciliação Bancária via importação OFX com matching automático.
 - Agendamento de pagamentos via API bancária (Inter, Asaas, Cora).

3. MÓDULO BPO FINANCEIRO (plano exclusivo para escritórios):
 - Multi-CNPJ: um único login gerencia todos os clientes da carteira.
 - Acessa e opera o sistema em nome de qualquer cliente com um clique, sem trocar senha.
 - Dashboard BPO com visão consolidada da carteira, alertas e indicadores.
 - Contratos BPO com cálculo automático de rentabilidade por cliente.
 - Registro de tempo da equipe por cliente (Desempenho da Equipe).
 - Análise de Carteira e Desempenho com IA: ranking, alertas e recomendações.
 - Agente BPO Automático (robô): sincroniza APIs bancárias, concilia transações e gera relatório Excel por cliente automaticamente.

4. AGENTES INTELIGENTES (IA):
 - Agente WhatsApp (LIA): captura boletos e notas fiscais enviados via WhatsApp, extrai dados com IA e cria rascunhos de lançamento para aprovação.
 - Agente de E-mail: monitora caixa de entrada (Gmail, Outlook, Yahoo), lê e-mails de fornecedores e cria rascunhos automaticamente.
 - Classificação Automática: o sistema aprende com o histórico e sugere Categoria, DRE, Centro de Custo e Projeto para novos lançamentos.
 - LIA (assistente financeira): responde dúvidas sobre lançamentos, detecta duplicatas e sugere classificações em lote.

5. MÓDULO COMERCIAL (plano Pro Comercial e acima):
 - PDV (frente de caixa), Orçamentos, Vendas, CRM/Pipeline, Estoque, Metas e Precificação.
 - Laudo Comercial e Laudo Marketplace com IA.

6. MÓDULO FISCAL (plano Elite Fiscal):
 - Emissão de NF-e (produtos) via Focus NFe e NFS-e (serviços) via Asaas.
 - Gestão de Contratos com geração automática de contas a receber.

7. MÓDULO CONTÁBIL (add-on em qualquer plano):
 - Balanço Patrimonial, Cofre de Documentos, Obrigações Fiscais e Painel Contábil BI.

8. INTEGRAÇÕES DISPONÍVEIS:
 - Bancos: Banco Inter, Itaú, Cora, Asaas, MercadoPago, Sicredi.
 - ERPs: Conta Azul, Omie, Nibo, Tiny/Olist, Bling.
 - Fiscal: Focus NFe (NF-e), Asaas (NFS-e).
 - Comunicação: Z-API (WhatsApp), Google Gemini, Zoho Mail.

9. DIFERENCIAIS GERAIS:
 - Exportação universal em PDF e Excel em todas as páginas principais.
 - Recorrência automática de lançamentos configurável por N meses.
 - Tema claro/escuro em todas as páginas.
 - Controle granular de permissões por colaborador e por módulo.
 - Suporte direto pelo WhatsApp (31) 99341-3530.
"""

INFO_PRODUTO = f"""
REGRA DE OURO SOBRE PERSONALIZAÇÃO:
- LOGO DO CLIENTE: Apenas para planos ACIMA DE 5 CNPJs (BPO).
- CORES (PALETA): NÃO fazemos personalização de cores sob nenhuma hipótese. O layout é padrão.

PREÇOS ATUAIS (Apenas se perguntarem):
- Start Financeiro: R$ 169/mês — até 2 usuários. Módulo Financeiro completo.
- Pro Comercial: R$ 219/mês — até 2 usuários. Tudo do Start + Módulo Comercial (PDV, Estoque, CRM, Metas).
- Elite Fiscal: R$ 349/mês — até 2 usuários. Tudo do Pro + Módulo Fiscal (NF-e, NFS-e, Contratos).
- BPO Financeiro: Sob consulta — multi-CNPJ. Plano especial para escritórios que gerenciam múltiplos clientes.
- Módulo Contábil: Add-on disponível em qualquer plano (valor sob consulta).

LIMITE DE USUÁRIOS: Todos os planos individuais incluem até 2 usuários. Usuários adicionais sob consulta.

NOTAS FISCAIS (Elite Fiscal):
- NF-e: Limite de 100 notas/mês incluídas. Excedente cobrado a R$ 0,25/nota. Requer Certificado Digital A1 (.pfx).
- NFS-e: Configurada pela equipe SistemClass via subconta Asaas.

AGENDAMENTO BANCÁRIO:
- Disponível para Inter, Asaas e Cora. Os pagamentos exigem aprovação no app do banco pelo cliente.
"""

# ==============================================================================
# 4. GEMINI (inalterado)
# ==============================================================================
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

historico_conversas = {}
mapa_ids = {}

# ==============================================================================
# 5. Envio de mensagem (inalterado)
# ==============================================================================
def enviar_mensagem(telefone, texto):
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
# 6. AJUSTES OPERACIONAIS (anti-loop + comandos)
# ==============================================================================

# Heurística de velocidade por remetente (anti-bot)
ULTIMO_TS: dict[str, float] = {}

# Kill-switch do cliente
STOP_COMMANDS_CLIENTE = {
    "pare", "/pare", "parar", "stop", "/stop", "cancelar", "chega", "silenciar", "/silenciar", "mute", "/mute"
}

# Vocabulário extra de “menu/robô” (somado ao que você já tinha)
TERMOS_ROBO_EXTRA = [
    "responda com", "clique", "clique no link", "autoatendimento", "press", "pressione",
    "para falar com um atendente", "para falar com atendente", "opção 1)", "opção 2)",
    "selecione uma opção", "menu de opções", "ura", "ura.", "voltar ao menu",
    "para continuar digite", "digite seu cpf", "digite seu cnpj", "protocolo",
    "este número não recebe mensagens", "mensagem automática",
    # Mensagens automáticas de ausência (respostas de "fora do horário")
    "nossa equipe não está disponível",
    "equipe não está disponível no momento",
    "não estamos disponíveis no momento",
    "no momento não estamos disponíveis",
    "horário de atendimento é",
    "nosso horário de funcionamento é",
    "responderemos assim que possível",
    "retornaremos assim que possível",
    "responderemos em breve",
    "retornaremos em breve",
    "retornaremos o contato em breve",
    "deixe sua mensagem",
    "deixe a sua mensagem",
    "fora do horário de atendimento",
    "fora do nosso horário"
]

def _agora() -> float:
    return time.time()

def _extrair_numero_digitos(texto: str) -> str | None:
    m = re.search(r'(\d{10,14})', texto or "")
    return m.group(1) if m else None

# ==============================================================================
# 7. Webhook
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

        textos_por_usuario = {}

        # Garante que a lista está atualizada com o arquivo
        clientes_pausados = carregar_pausados()

        for msg in messages:
            key             = msg.get('key', {})
            enviada_por_mim = key.get('fromMe') or msg.get('fromMe')
            remote_jid      = key.get('remoteJid') or msg.get('from')
            sender          = remote_jid

            # Mapeia LID -> número real
            if sender and '@lid' in sender:
                if sender in mapa_ids:
                    sender = mapa_ids[sender]
                else:
                    real_number = key.get('senderPn') or key.get('participant')
                    if real_number:
                        mapa_ids[remote_jid] = real_number
                        sender = real_number

            # IGNORA GRUPOS (evita prender em menus de grupo)
            if sender and str(sender).endswith('@g.us'):
                print(f"--- [INFO] Mensagem de grupo ignorada: {sender}")
                continue

            if sender not in historico_conversas:
                historico_conversas[sender] = []

            tipo_msg    = msg.get('messageType') or msg.get('type')
            msg_content = msg.get('message', {})
            texto_cliente = ''

            # --- 1. BLOQUEIO DE ÁUDIO (original)
            if tipo_msg == 'audio' or 'audioMessage' in msg_content:
                if enviada_por_mim:
                    continue
                msg_bloqueio = "Desculpe, ainda não consigo ouvir áudios por aqui. 🎧 Poderia escrever sua dúvida por favor? Assim consigo te responder rapidinho! 😊"
                enviar_mensagem(sender, msg_bloqueio)
                historico_conversas[sender].append(f"Maria Clara: {msg_bloqueio}")
                continue

            # --- 2. EXTRAÇÃO DE TEXTO (original)
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

            # --- 3. COMANDOS DE ADMIN / CLIENTE ---
            sender_limpo = "".join(filter(str.isdigit, str(sender)))
            admin_limpo  = "".join(filter(str.isdigit, NUMERO_ADMIN))
            print(f"--- [DEBUG] Sender: {sender_limpo} \n Admin: {admin_limpo} \n FromMe: {enviada_por_mim}")

            # É admin se: veio fromMe OU número bate (com/sem 55)
            eh_admin = bool(enviada_por_mim) or (admin_limpo in sender_limpo) or (sender_limpo in admin_limpo)
            comando  = texto_cliente.lower().strip()

            # Kill-switch do CLIENTE (semelhante ao /pare, mas para o próprio cliente)
            if comando in STOP_COMMANDS_CLIENTE:
                telefone_limpo_cli = sender.split('@')[0]
                numero_cli = "".join(filter(str.isdigit, telefone_limpo_cli))
                clientes_pausados = salvar_pausado(numero_cli)
                enviar_mensagem(sender, "✅ Entendido. Vou ficar em silêncio por aqui. Se precisar, mande '/reset'.")
                print(f"--- [SILENCIADO POR CLIENTE] {numero_cli}")
                continue

            
            # /pare — SEM número: SEMPRE pausa o chat atual;
            # /pare <numero>: permite se (a) fromMe=True, ou (b) chat atual é do próprio <numero>, ou (c) eh_admin=True
            if comando.startswith("/pare"):
                try:
                    # Em vez de caçar dígitos no texto inteiro, olhamos APENAS o que vier DEPOIS de /pare
                    tokens = comando.split()
                    alvo_regex = None
                    if len(tokens) > 1:
                        # usuário digitou algo explícito após /pare; extrai só desses tokens posteriores
                        resto = " ".join(tokens[1:])
                        m = re.search(r'(\d{10,14})', resto)
                        if m:
                            alvo_regex = m.group(1)

                    if not alvo_regex:
                        # /pare (sem número) -> pausa o chat atual, sempre
                        numero_alvo = sender_limpo
                        permitido = True
                        motivo = "chat_atual"
                    else:
                        numero_alvo = alvo_regex
                        # três jeitos de permitir:
                        # 1) veio da conta do bot (fromMe=True),
                        # 2) você está NO chat do próprio cliente (alvo == sender_limpo),
                        # 3) você é admin (eh_admin=True).
                        permitido = bool(enviada_por_mim) or (numero_alvo == sender_limpo) or bool(eh_admin)
                        motivo = (
                            "fromMe" if enviada_por_mim else
                            "chat_alvo" if (numero_alvo == sender_limpo) else
                            "admin" if eh_admin else "negado"
                        )

                    print(f"--- [/pare] alvo={numero_alvo} | sender={sender_limpo} | fromMe={enviada_por_mim} | eh_admin={eh_admin} | motivo={motivo}")

                    if not permitido:
                        enviar_mensagem(sender, "⚠️ Comando negado. /pare <número> só é permitido para Admin ou no chat do próprio cliente.")
                        continue

                    if numero_alvo not in clientes_pausados:
                        clientes_pausados = salvar_pausado(numero_alvo)
                        print(f"🚫 COMANDO: {numero_alvo} foi silenciado. (motivo={motivo})")
                        enviar_mensagem(sender, f"✅ Cliente {numero_alvo} SILENCIADO.")
                    else:
                        enviar_mensagem(sender, f"⚠️ {numero_alvo} já estava silenciado.")
                    continue

                except Exception as e:
                    print(f"Erro no comando /pare: {e}")
                    enviar_mensagem(sender, "⚠️ Ocorreu um erro ao processar /pare.")
                    continue


            # /status — informa se o contato atual está pausado
            if comando in ("/status", "status"):
                telefone_limpo = sender.split('@')[0]
                numero_digitos = "".join(filter(str.isdigit, telefone_limpo))
                pausado = (telefone_limpo in clientes_pausados) or (numero_digitos in clientes_pausados)
                estado = "PAUSADO" if pausado else "ATIVO"
                enviar_mensagem(sender, f"ℹ️ Estado atual deste contato: {estado}.")
                continue

            # COMANDO /RESET (original)
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

            # --- 4. FILTRO ANTI-ROBÔ (refinado, mas mantendo seu espírito) ---
            # A) Velocidade (<2s)
            ts_now = _agora()
            ultimo = ULTIMO_TS.get(sender)
            ULTIMO_TS[sender] = ts_now
            if ultimo and (ts_now - ultimo) < 2.0:
                print(f"--- [IGNORADO] Mensagens muito rápidas de {sender} (possível robô).")
                continue

            # B) Repetição imediata
            if sender in textos_por_usuario and len(textos_por_usuario[sender]) > 0:
                ultima_msg = textos_por_usuario[sender][-1]
                if texto_cliente.strip() == ultima_msg.strip():
                    print(f"--- [IGNORADO] Loop de repetição detectado de {sender}")
                    continue

            # C) Lista negra (sua lista + extras)
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

            # D) Menu numérico curto
            t_strip = texto_cliente.strip()
            if 0 < len(t_strip) < 5 and t_strip[0].isdigit():
                print(f"--- [IGNORADO] Opção de Menu numérico detectada de {sender}")
                continue

            # --- 5. VERIFICAÇÃO DE PAUSA (TRANSBORDO) ---
            telefone_limpo        = sender.split('@')[0]
            numero_apenas_digitos = "".join(filter(str.isdigit, telefone_limpo))
            if (telefone_limpo in clientes_pausados) or (numero_apenas_digitos in clientes_pausados):
                print(f"--- [SILENCIADO] Mensagem de {telefone_limpo} ignorada (está pausado).")
                continue

            # Transbordo por palavras-chave (original)
            if any(palavra in texto_cliente.lower() for palavra in PALAVRAS_CHAVE):
                clientes_pausados = salvar_pausado(numero_apenas_digitos)
                enviar_mensagem(sender, "Entendido. Um especialista humano vai seguir com seu atendimento. Aguarde um momento! 👨‍💻")
                enviar_mensagem(NUMERO_ADMIN, f"🚨 ALERTA TRANSBORDO!\nCliente: {telefone_limpo}\nDisse: {texto_cliente}")
                continue

            if sender not in textos_por_usuario:
                textos_por_usuario[sender] = []
            textos_por_usuario[sender].append(texto_cliente)

        # ======================================================================
        # LÓGICA DO GEMINI  (PROMPT ORIGINAL INALTERADO)
        # ======================================================================
        for sender_user, lista_msgs in textos_por_usuario.items():
            texto_completo = " ".join(lista_msgs)
            historico_conversas[sender_user].append(f"Cliente: {texto_completo}")
            memoria = "\n".join(historico_conversas[sender_user][-15:])

            instrucoes_base = f"""
 Você é Maria Clara, especialista do SistemClass.
 Seu tom de voz: Amigável, consultivo, "gente como a gente", mas profissional. Use emojis moderados.
 DADOS SOBRE O PRODUTO:
 {TOPICOS_APRESENTACAO}
 REGRAS TÉCNICAS:
 {INFO_PRODUTO}
 DADOS DE ACESSO (PARA ENTREGAR AO CLIENTE):
 {DADOS_ACESSO}
 AVISO SOBRE O ACESSO DEMO: "{TEXTO_ACESSO_DEMO}"
 HISTÓRICO RECENTE:
 {memoria}
 O QUE O CLIENTE DISSE AGORA: "{texto_completo}"
 # DIRETRIZES ESTRITAS DE RESPOSTA (SIGA ESTA ORDEM):
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
 - OBRIGATÓRIO: Logo após os dados de acesso, escreva: "{TEXTO_ACESSO_DEMO}"
 - OBRIGATÓRIO: Ao final, ofereça as duas opções: falar agora com o Comercial pelo WhatsApp 🟢 (31) 99341-3530 OU agendar uma apresentação on-line de 30 minutos pelo link {LINK_AGENDAMENTO} (apenas texto, não gere links formatados).
 2. SE FOR DÚVIDA ESPECÍFICA: Responda direto ao ponto.
 2.1. SE O CLIENTE PEDIR APRESENTAÇÃO, DEMONSTRAÇÃO AO VIVO, REUNIÃO, CALL OU FALAR EM "AGENDAR":
 - Envie o link de agendamento: {LINK_AGENDAMENTO}
 - Explique que ele escolhe o melhor dia e horário, a apresentação é on-line de 30 minutos e o link da reunião chega no e-mail dele na hora (apenas texto, não gere links formatados).
 3. SE FOR DESINTERESSE:
 - Responda apenas: "Entendido! Agradeço o retorno e desejo muito sucesso. Um abraço! 👋"
 - NÃO tente vender nada.
 IMPORTANTE: JAMAIS escreva "Passo A:", "Passo B:". Apenas o texto corrido.
 """
            try:
                time.sleep(1)
                response = model.generate_content(instrucoes_base)
                resposta_bot = response.text.strip()
                # limpeza de rótulos indesejados
                resposta_bot = (resposta_bot
                                .replace("**Passo A**", "").replace("Passo A:", "")
                                .replace("**Passo B**", "").replace("Passo B:", ""))
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
