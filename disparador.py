
# # -*- coding: utf-8 -*-
# """
# Script: disparador.py (atualizado - 2026-01-17)
# Autor: Rodrigo + Copilot

# O que este script faz?
#   • Lê um Excel com colunas: Nome, Telefone, Status (opcional)
#   • Converte um PDF local para Base64 e faz UPLOAD para o WASenderApi
#   • Envia mensagem de texto + DOCUMENTO (PDF) usando documentUrl retornada no upload
#   • Atualiza a coluna 'Status' com 'Enviado' (dtype textual) e salva o Excel
#   • Intervalo aleatório entre disparos para reduzir risco de bloqueio
#   • Só dispara no horário comercial (09:00–19:00)

# Requisitos:
#   pip install pandas requests python-dotenv openpyxl

# Configuração necessária:
#   1) Arquivo .env na mesma pasta, com a variável:
#        WASENDER_API_KEY=SEU_TOKEN_AQUI
#   2) Colocar o Excel e o PDF na mesma pasta do script

# Observação importante:
#   Para enviar DOCUMENTOS no WASenderApi, o endpoint /api/send-message
#   aceita o parâmetro 'documentUrl' (URL pública). Portanto, o fluxo correto
#   é: (1) subir o arquivo com /api/upload e (2) enviar usando documentUrl.
  
#   Fonte (docs oficiais):
#     - Upload: https://www.wasenderapi.com/api-docs/messages/upload-media-file
#     - Envio de documento: https://www.wasenderapi.com/api-docs/messages/send-document-message
# """
# from __future__ import annotations
# import os
# import time
# import random
# import base64
# from datetime import datetime
# from typing import Optional, Tuple

# import pandas as pd
# import requests
# from dotenv import load_dotenv

# # =====================
# # Configurações gerais
# # =====================
# VERSAO = "2026-01-17"

# # --- Arquivos ---
# NOME_ARQUIVO_EXCEL = "lista_clientes.xlsx"
# NOME_PDF = "apresentacao_v2.pdf"  # Nome do PDF a ser enviado

# # --- Janela de envio (horário comercial) ---
# HORA_INICIO = 9   # 09:00
# HORA_FIM = 19     # 19:00 (envia até 18:59)

# # --- Proteção Anti-bloqueio (intervalo aleatório entre disparos) ---
# TEMPO_MIN = 400
# TEMPO_MAX = 900

# # --- Endpoints WASenderApi ---
# API_BASE = "https://www.wasenderapi.com"
# API_URL_SEND = f"{API_BASE}/api/send-message"   # envia mensagem
# API_URL_UPLOAD = f"{API_BASE}/api/upload"       # faz upload e retorna publicUrl


# # =====================
# # Funções utilitárias
# # =====================

# def carregar_env_e_headers() -> Tuple[str, dict]:
#     """Carrega o .env, obtém API_KEY e monta headers padrão."""
#     load_dotenv()
#     api_key = os.getenv("WASENDER_API_KEY")
#     if not api_key:
#         raise ValueError("ERRO: A chave WASENDER_API_KEY não foi encontrada no arquivo .env!")
#     headers = {
#         "Authorization": f"Bearer {api_key}",
#         "Content-Type": "application/json",
#     }
#     return api_key, headers


# def obter_base64_pdf(caminho_arquivo: str) -> Optional[str]:
#     """Lê o PDF e converte para Base64. Retorna None em caso de erro."""
#     if not os.path.exists(caminho_arquivo):
#         print(f"ERRO CRÍTICO: O arquivo '{caminho_arquivo}' não está na pasta!")
#         return None
#     try:
#         with open(caminho_arquivo, "rb") as f:
#             encoded = base64.b64encode(f.read()).decode("utf-8")
#         return encoded
#     except Exception as e:
#         print(f"Erro ao converter PDF: {e}")
#         return None


# def validar_base64(b64: str) -> bool:
#     """Valida se a string é Base64 bem formada."""
#     try:
#         base64.b64decode(b64, validate=True)
#         return True
#     except Exception:
#         return False


# def preparar_dataframe(caminho_excel: str) -> pd.DataFrame:
#     """Lê o Excel (.xlsx) e garante a coluna 'Status' com dtype textual."""
#     if not os.path.exists(caminho_excel):
#         raise FileNotFoundError(f"Arquivo '{caminho_excel}' não encontrado.")

#     df = pd.read_excel(caminho_excel, engine="openpyxl")

#     # Garante a existência da coluna 'Status' e o dtype textual (pandas 'string')
#     if 'Status' not in df.columns:
#         df['Status'] = pd.Series(dtype='string')
#     else:
#         df['Status'] = df['Status'].astype('string')

#     # (Opcional) Normaliza colunas esperadas
#     if 'Nome' not in df.columns:
#         df['Nome'] = pd.Series(dtype='string')
#     if 'Telefone' not in df.columns:
#         df['Telefone'] = pd.Series(dtype='string')

#     return df


# def salvar_dataframe(df: pd.DataFrame, caminho_excel: str) -> None:
#     try:
#         df.to_excel(caminho_excel, index=False, engine="openpyxl")
#     except Exception as e:
#         print(f"Aviso: não consegui salvar o Excel agora: {e}")


# def normalizar_telefone(telefone_bruto: str) -> str:
#     """Mantém apenas dígitos e prefixa '55' se tiver pelo menos 10 dígitos e ainda não tiver DDI."""
#     if telefone_bruto is None:
#         return ""
#     so_digitos = "".join(filter(str.isdigit, str(telefone_bruto)))
#     if not so_digitos:
#         return ""
#     if len(so_digitos) >= 10 and not so_digitos.startswith("55"):
#         so_digitos = "55" + so_digitos
#     return so_digitos


# def dentro_do_horario(agora: datetime) -> bool:
#     """Retorna True se o horário atual estiver dentro da janela (HORA_INICIO <= agora < HORA_FIM)."""
#     return (HORA_INICIO <= agora.hour < HORA_FIM)


# def montar_mensagem_padrao(nome: str) -> str:
#     return (
#         "Olá! Tudo bem?\n"
#         "Vi que você atua com BPO Financeiro. Hoje como você apresenta os resultados dos seus clientes?\n"
#         "Nós criamos um sistema que gera BI (Business Intelligence) em tempo real para o seu cliente.\n"
#         "DRE Gerencial, Fluxo de Caixa e Dashboards automáticos para te tirar do operacional e gerar valor na sua operação.\n"
#         "Estou lhe enviando abaixo uma apresentação do nosso sistema em PDF.\n"
#         "Se fizer sentido, posso te liberar um acesso teste gratuito para você ver como funciona por dentro. O que acha?\n"
#         "No mais, agradeço a sua atenção!"
#     )


# def fazer_upload_base64(pdf_base64: str, headers: dict, mimetype: str = "application/pdf") -> Optional[str]:
#     """Envia o arquivo em Base64 para o endpoint de upload do WASenderApi
#     e retorna a publicUrl (string) ou None em caso de falha.
#     """
#     body = {
#         # RECOMENDADO pela doc: incluir o prefixo data:... para facilitar a detecção do mimetype
#         "base64": f"data:{mimetype};base64,{pdf_base64}"
#         # Alternativa (também suportada): {"mimetype": mimetype, "base64": pdf_base64}
#     }
#     try:
#         resp = requests.post(API_URL_UPLOAD, json=body, headers=headers, timeout=60)
#         if resp.status_code in (200, 201):
#             data = resp.json()
#             public_url = data.get("publicUrl")
#             if public_url:
#                 return public_url
#             print("Upload OK mas não veio publicUrl:", data)
#         else:
#             print(f"Falha no upload ({resp.status_code}): {resp.text}")
#     except Exception as e:
#         print(f"Erro no upload: {e}")
#     return None


# def enviar_documento_por_url(telefone: str, texto: str, document_url: str, nome_arquivo: str, headers: dict) -> Tuple[bool, Optional[requests.Response]]:
#     """Envia a mensagem com documentUrl no /api/send-message (WASenderApi)."""
#     payload = {
#         "to": telefone,
#         "text": texto,           # opcional
#         "documentUrl": document_url,
#         "fileName": nome_arquivo # opcional
#     }
#     try:
#         resp = requests.post(API_URL_SEND, json=payload, headers=headers, timeout=60)
#         if resp.status_code in (200, 201):
#             return True, resp
#         else:
#             print(f"  -> Erro API ({resp.status_code}): {getattr(resp, 'text', '')}")
#             return False, resp
#     except Exception as e:
#         print(f"  -> Erro de rede: {e}")
#         return False, None


# # =====================
# # Fluxo principal
# # =====================

# def enviar_disparos():
#     print(f"VERSAO: {VERSAO}")

#     # 1) Carrega env/headers
#     try:
#         _, headers = carregar_env_e_headers()
#     except Exception as e:
#         print(str(e))
#         return

#     # 2) Carrega e valida o PDF
#     print("Carregando PDF...")
#     pdf_b64 = obter_base64_pdf(NOME_PDF)
#     if not pdf_b64:
#         print("Abortando: PDF não pôde ser carregado.")
#         return
#     try:
#         tam_bytes = os.path.getsize(NOME_PDF)
#         print(f"Tamanho do PDF: {tam_bytes/1024/1024:.2f} MB")
#     except Exception as e:
#         print(f"Não foi possível obter o tamanho do PDF: {e}")
#     if not validar_base64(pdf_b64):
#         print("Base64 inválido. Verifique o arquivo PDF.")
#         return
#     print("PDF carregado com sucesso! Tamanho OK.")

#     # 3) Upload para obter documentUrl público
#     print("Realizando upload do PDF para obter URL pública...")
#     document_url = fazer_upload_base64(pdf_b64, headers, mimetype="application/pdf")
#     if not document_url:
#         print("Abortando: não foi possível obter a URL pública do PDF via upload.")
#         return
#     print("Upload concluído. URL pública obtida.")

#     # 4) Lê Excel e prepara DataFrame
#     try:
#         df = preparar_dataframe(NOME_ARQUIVO_EXCEL)
#     except Exception as e:
#         print(f"Erro ao ler Excel: {e}")
#         return

#     print("--- Iniciando campanha com PDF (via documentUrl) ---")

#     total = len(df)
#     for index, linha in df.iterrows():
#         # Trava de horário
#         agora = datetime.now()
#         if not dentro_do_horario(agora):
#             print(f"🚫 Fora do horário comercial ({agora.strftime('%H:%M')}). Parando o robô.")
#             break

#         nome = str(linha.get('Nome', 'Cliente'))
#         telefone_bruto = linha.get('Telefone', '')
#         status_atual = str(linha.get('Status', '')).strip().lower()

#         # Pula quem já recebeu
#         if status_atual == 'enviado':
#             continue

#         telefone = normalizar_telefone(telefone_bruto)
#         if not telefone:
#             print(f"[{index+1}/{total}] Telefone inválido para '{nome}'. Pulando...")
#             continue

#         mensagem_texto = montar_mensagem_padrao(nome)

#         print(f"[{index+1}/{total}] Enviando para {nome} ({telefone})...")

#         sucesso, resp = enviar_documento_por_url(
#             telefone=telefone,
#             texto=mensagem_texto,
#             document_url=document_url,
#             nome_arquivo=NOME_PDF,
#             headers=headers,
#         )

#         if sucesso:
#             print("  -> Sucesso.")
#             # Atualiza status garantindo dtype textual da coluna
#             df.at[index, 'Status'] = 'Enviado'
#             salvar_dataframe(df, NOME_ARQUIVO_EXCEL)
#         else:
#             # Logs adicionais de depuração
#             print("  -> Falha no envio. Detalhes de depuração:")
#             resumo_payload = {
#                 "to": telefone,
#                 "text": "<omitted>",
#                 "documentUrl": document_url,
#                 "fileName": NOME_PDF,
#             }
#             print("     Headers:", {"Authorization": headers.get("Authorization", "***"), "Content-Type": headers.get("Content-Type")})
#             print("     Payload:", resumo_payload)

#         # Intervalo anti-bloqueio
#         tempo = random.randint(TEMPO_MIN, TEMPO_MAX)
#         print(f"Aguardando {tempo}s...\n")
#         time.sleep(tempo)


# if __name__ == "__main__":
#     enviar_disparos()


# -*- coding: utf-8 -*-
"""
Script: disparador.py (atualizado - 2026-01-17 - mensagens separadas + 429 handling)

Mudança principal: envia DUAS mensagens por contato —
  1) Texto (somente texto)
  2) Documento (somente PDF, sem texto)

E trata 429 (rate limit) respeitando 'retry_after' e Account Protection (1 req / 5s).
Docs relevantes:
  - Rate limits e Account Protection (1 req/5s quando ativo): https://www.wasenderapi.com/api-docs/rate-limits/understanding-rate-limits
  - Upload de mídia (retorna publicUrl): https://www.wasenderapi.com/api-docs/messages/upload-media-file
  - Envio de documento com documentUrl: https://www.wasenderapi.com/api-docs/messages/send-document-message
"""
from __future__ import annotations
import os
import time
import random
import base64
from datetime import datetime
from typing import Optional, Tuple

import pandas as pd
import requests
from dotenv import load_dotenv

VERSAO = "2026-01-17-separado-rl"

# === Arquivos ===
NOME_ARQUIVO_EXCEL = "lista_clientes.xlsx"
NOME_PDF = "apresentacao_v2.pdf"

# === Janela de envio ===
HORA_INICIO = 9
HORA_FIM = 19

# === Intervalos ===
TEMPO_MIN = 400
TEMPO_MAX = 900
# Delay entre o TEXTO e o DOCUMENTO (precisa ser >=5s quando Account Protection estiver ON)
DELAY_TEXTO_PARA_DOC = 6

# === Endpoints ===
API_BASE = "https://www.wasenderapi.com"
API_URL_SEND = f"{API_BASE}/api/send-message"
API_URL_UPLOAD = f"{API_BASE}/api/upload"


def carregar_env_e_headers() -> Tuple[str, dict]:
    load_dotenv()
    api_key = os.getenv("WASENDER_API_KEY")
    if not api_key:
        raise ValueError("ERRO: A chave WASENDER_API_KEY não foi encontrada no arquivo .env!")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return api_key, headers


def obter_base64_pdf(path: str) -> Optional[str]:
    if not os.path.exists(path):
        print(f"ERRO CRÍTICO: O arquivo '{path}' não está na pasta!")
        return None
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print("Erro ao converter PDF:", e)
        return None


def validar_base64(b64: str) -> bool:
    try:
        base64.b64decode(b64, validate=True)
        return True
    except Exception:
        return False


def preparar_dataframe(xlsx: str) -> pd.DataFrame:
    if not os.path.exists(xlsx):
        raise FileNotFoundError(f"Arquivo '{xlsx}' não encontrado.")
    df = pd.read_excel(xlsx, engine="openpyxl")
    if 'Status' not in df.columns:
        df['Status'] = pd.Series(dtype='string')
    else:
        df['Status'] = df['Status'].astype('string')
    if 'Nome' not in df.columns:
        df['Nome'] = pd.Series(dtype='string')
    if 'Telefone' not in df.columns:
        df['Telefone'] = pd.Series(dtype='string')
    return df


def salvar_dataframe(df: pd.DataFrame, xlsx: str) -> None:
    try:
        df.to_excel(xlsx, index=False, engine="openpyxl")
    except Exception as e:
        print("Aviso ao salvar Excel:", e)


def normalizar_telefone(raw: str) -> str:
    if raw is None:
        return ""
    d = "".join(filter(str.isdigit, str(raw)))
    if not d:
        return ""
    if len(d) >= 10 and not d.startswith("55"):
        d = "55" + d
    return d


def dentro_do_horario(dt: datetime) -> bool:
    return HORA_INICIO <= dt.hour < HORA_FIM


def mensagem_padrao(nome: str) -> str:
    return (
        "Olá! Tudo bem?\n\n"
        "Vi que você atua com BPO Financeiro. Hoje como você apresenta os resultados dos seus clientes?\n\n"
        "Nós criamos um sistema que gera BI (Business Intelligence) em tempo real para o seu cliente.\n\n"
        "DRE Gerencial, Fluxo de Caixa e Dashboards automáticos para te tirar do operacional e gerar valor na sua operação.\n\n"
        "Estou lhe enviando abaixo uma apresentação do nosso sistema em PDF.\n\n"
        "Se fizer sentido, posso te liberar um acesso teste gratuito para você ver como funciona por dentro. O que acha?\n\n"
        "No mais, agradeço a sua atenção!"
    )


# ---------- Auxiliar: POST com tratamento de 429 ----------
def post_with_rate_limit_retry(url: str, json_payload: dict, headers: dict,
                               timeout: int = 60, max_retries: int = 2,
                               min_gap_seconds: int = 5) -> Tuple[bool, Optional[requests.Response]]:
    """
    Faz POST e trata 429 (Too Many Requests), respeitando 'retry_after' quando presente.
    Também garante um gap mínimo entre chamadas consecutivas (min_gap_seconds), útil para Account Protection (1/5s).
    """
    # Gap mínimo antes da primeira tentativa (ajuda quando a chamada anterior foi <5s atrás)
    time.sleep(min_gap_seconds)

    for attempt in range(1, max_retries + 2):  # ex.: com max_retries=2 -> até 3 tentativas
        try:
            r = requests.post(url, json=json_payload, headers=headers, timeout=timeout)
        except Exception as e:
            print(f"  -> Erro de rede: {e}")
            return False, None

        if r.status_code in (200, 201):
            return True, r

        if r.status_code == 429:
            # Tenta extrair retry_after do corpo ou do header 'Retry-After'
            wait_s = None
            try:
                data = r.json()
                wait_s = data.get("retry_after")
            except Exception:
                pass
            if wait_s is None:
                # tenta header padrão
                ra = r.headers.get("Retry-After")
                if ra:
                    try:
                        wait_s = int(ra)
                    except Exception:
                        pass
            # fallback conservador (Account Protection = 1/5s)
            if wait_s is None or wait_s < min_gap_seconds:
                wait_s = min_gap_seconds

            print(f"  -> 429 recebido. Aguardando {wait_s}s e tentando novamente... "
                  "(Account Protection ativo — 1 msg/5s).")
            time.sleep(wait_s)
            continue  # nova tentativa

        # Outros erros
        print(f"  -> Erro API ({r.status_code}): {getattr(r, 'text', '')}")
        return False, r

    # Se sair do loop, não conseguiu
    return False, r


# ---------- Upload e envios ----------
def upload_pdf_base64(pdf_b64: str, headers: dict, mimetype: str = "application/pdf") -> Optional[str]:
    body = {"base64": f"data:{mimetype};base64,{pdf_b64}"}
    ok, r = post_with_rate_limit_retry(API_URL_UPLOAD, body, headers, timeout=60, max_retries=2, min_gap_seconds=5)
    if ok and r is not None:
        try:
            data = r.json()
            return data.get("publicUrl")
        except Exception:
            print("Upload OK, mas não consegui ler JSON da resposta.")
            return None
    return None


def enviar_texto(telefone: str, texto: str, headers: dict) -> Tuple[bool, Optional[requests.Response]]:
    payload = {"to": telefone, "text": texto}
    return post_with_rate_limit_retry(API_URL_SEND, payload, headers, timeout=30, max_retries=2, min_gap_seconds=5)


def enviar_documento_url(telefone: str, document_url: str, nome_arquivo: str, headers: dict) -> Tuple[bool, Optional[requests.Response]]:
    payload = {"to": telefone, "documentUrl": document_url, "fileName": nome_arquivo}
    return post_with_rate_limit_retry(API_URL_SEND, payload, headers, timeout=60, max_retries=2, min_gap_seconds=5)


def enviar_disparos():
    print(f"VERSAO: {VERSAO}")
    # headers
    try:
        _, headers = carregar_env_e_headers()
    except Exception as e:
        print(str(e)); return

    # PDF -> Base64
    print("Carregando PDF...")
    pdf_b64 = obter_base64_pdf(NOME_PDF)
    if not pdf_b64:
        print("Abortando: PDF não pôde ser carregado."); return
    try:
        size_mb = os.path.getsize(NOME_PDF)/1024/1024
        print(f"Tamanho do PDF: {size_mb:.2f} MB")
    except Exception:
        pass
    if not validar_base64(pdf_b64):
        print("Base64 inválido."); return
    print("PDF carregado com sucesso! Tamanho OK.")

    # Upload (uma vez só)
    print("Realizando upload do PDF para obter URL pública...")
    document_url = upload_pdf_base64(pdf_b64, headers)
    if not document_url:
        print("Abortando: não foi possível obter a URL pública do PDF via upload."); return
    print("Upload concluído. URL pública obtida.")

    # Excel
    try:
        df = preparar_dataframe(NOME_ARQUIVO_EXCEL)
    except Exception as e:
        print("Erro ao ler Excel:", e); return

    print("--- Iniciando campanha (mensagens separadas + 429 handling) ---")

    total = len(df)
    for idx, linha in df.iterrows():
        agora = datetime.now()
        if not dentro_do_horario(agora):
            print(f"🚫 Fora do horário comercial ({agora.strftime('%H:%M')}). Parando o robô.")
            break

        nome = str(linha.get('Nome', 'Cliente'))
        telefone_bruto = linha.get('Telefone', '')
        status_atual = str(linha.get('Status', '')).strip().lower()
        if status_atual == 'enviado':
            continue

        telefone = normalizar_telefone(telefone_bruto)
        if not telefone:
            print(f"[{idx+1}/{total}] Telefone inválido para '{nome}'. Pulando...")
            continue

        texto = mensagem_padrao(nome)

        print(f"[{idx+1}/{total}] Enviando TEXTO para {nome} ({telefone})...")
        ok_texto, _ = enviar_texto(telefone, texto, headers)
        if not ok_texto:
            print("  -> Falha ao enviar o TEXTO. Vou continuar para o próximo contato.")
            tempo = random.randint(TEMPO_MIN, TEMPO_MAX)
            print(f"Aguardando {tempo}s...\n"); time.sleep(tempo)
            continue

        # Gap adicional entre texto e documento (>=5s por causa do Account Protection)
        time.sleep(DELAY_TEXTO_PARA_DOC)

        print(f"[{idx+1}/{total}] Enviando DOCUMENTO para {nome} ({telefone})...")
        ok_doc, _ = enviar_documento_url(telefone, document_url, NOME_PDF, headers)
        if ok_doc:
            print("  -> Sucesso (texto + documento).")
            df.at[idx, 'Status'] = 'Enviado'
            salvar_dataframe(df, NOME_ARQUIVO_EXCEL)
        else:
            print("  -> Falha ao enviar o DOCUMENTO. (O texto foi enviado).")

        tempo = random.randint(TEMPO_MIN, TEMPO_MAX)
        print(f"Aguardando {tempo}s...\n")
        time.sleep(tempo)


if __name__ == "__main__":
    enviar_disparos()

