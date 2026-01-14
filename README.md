# Bot SistemClass - Automação Inteligente de Vendas (IA + WhatsApp) 🤖💬

Bot de atendimento e qualificação de leads desenvolvido em **Python**, integrado ao WhatsApp e potencializado pela Inteligência Artificial do Google Gemini. O projeto atua como um SDR (Sales Development Representative) digital, realizando o primeiro contato, tirando dúvidas e agendando demonstrações automaticamente.

## 🚀 Funcionalidades Principais

### 🧠 Inteligência Artificial (Core)
* **LLM Integrada:** Utiliza o modelo `gemini-flash-latest` (Google) para interpretar mensagens com processamento de linguagem natural (NLP).
* **Contexto Dinâmico:** O bot mantém o histórico da conversa (`historico_conversas`) para entender o fluxo do diálogo e responder de forma coerente, não apenas frases soltas.
* **Engenharia de Prompt:** Instruções sistêmicas complexas para definir "Personalidade" (Maria Clara), regras de recusa, apresentação de produto e gatilhos de venda.

### ⚙️ Backend & Automação
* **API Flask:** Servidor web (`app.py`) preparado para receber Webhooks em tempo real da API de WhatsApp (WaSender).
* **Disparador Ativo (`disparador.py`):** Script autônomo para envio de mensagens em massa (Outbound Marketing) com controle de horário comercial (09h-19h) e delay aleatório para evitar bloqueios (Anti-Ban).
* **Persistência de Estado:** Sistema de arquivos JSON (`pausados.json`) para gerenciar listas de exclusão e blacklists, mantendo os dados salvos mesmo após reinicialização do servidor.

### 🛡️ Segurança & Controle
* **Comandos de Admin:** Comandos ocultos como `/pare` e `/reset` permitem que o administrador intervenha, silencie um cliente ou reinicie a memória da IA diretamente pelo WhatsApp.
* **Filtro Anti-Robô:** Algoritmo que detecta e ignora mensagens automáticas de outros bots (ex: "digite 1 para...", menus de URA), evitando loops infinitos de conversa entre máquinas.
* **Transbordo Humano:** Detecção de palavras-chave ("falar com atendente") para pausar a IA e notificar a equipe de vendas.

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python 3.10+
* **Web Framework:** Flask
* **IA/LLM:** Google Generative AI (Gemini API)
* **Integração WhatsApp:** Requests (Consumo de API REST)
* **Manipulação de Dados:** Pandas (Leitura de Excel para disparos), JSON.
* **Deploy:** Preparado para Render/Heroku (gunicorn).

## 📂 Estrutura do Projeto
* `bot.py`: Núcleo do chatbot, servidor Webhook e lógica de IA.
* `disparador.py`: Módulo de disparo ativo de mensagens (Campanhas).
* `pausados.json`: Banco de dados local para controle de bloqueios.

## 👤 Autor
**Rodrigo Abreu**
Desenvolvedor Python Backend
