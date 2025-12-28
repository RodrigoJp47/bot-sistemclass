import google.generativeai as genai
import os

# --- COLE SUA CHAVE AQUI ---
GEMINI_API_KEY = "AIzaSyAM2Z3HyOcANDfRq1vr5ROX5QaX8LMBlBg" 
# ---------------------------

genai.configure(api_key=GEMINI_API_KEY)

print("\n--- CONSULTANDO O GOOGLE... ---")
try:
    # Tenta listar os modelos
    modelos = genai.list_models()
    encontrou = False
    print("Modelos disponíveis para você:")
    for m in modelos:
        # Filtra apenas os que servem para gerar texto (chat)
        if 'generateContent' in m.supported_generation_methods:
            print(f" -> {m.name}")
            encontrou = True
    
    if not encontrou:
        print("Nenhum modelo de texto encontrado. Verifique sua Chave API.")

except Exception as e:
    print(f"ERRO AO LISTAR: {e}")
    print("\nDICA: Se der erro de autenticação, sua chave pode estar errada.")
    print("DICA: Se der erro de 'module', tente rodar: pip install -U google-generativeai")