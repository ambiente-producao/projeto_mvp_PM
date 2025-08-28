import pandas as pd
import sqlite3
import json
from openai import OpenAI

from agentes import agente_feedback, agente_roadmap, agente_metricas, agente_risco

# Conexão com a OPENAI
with open('chave_openai.txt', 'r') as file:
    api_key = file.read().strip()
client_openai = OpenAI(api_key=api_key)

# Prompt do Orquestrador
PROMPT_ORQUESTRADOR = """

Você é o Orquestrador de um sistema para PMs de squads.

Entrada: pergunta do usuário.

Objetivo:
- Classificar a pergunta em uma ou mais intenções:
  - roadmap → tabela tab_roadmap
  - metricas → tabela tab_metricas
  - feedback → tabela tab_feedback
  - riscos → tabela tab_risco
  - resumo_360 → todas as tabelas acima

Regras:
1. Se encontrar **uma única intenção clara**, retorne apenas ela.
2. Se encontrar **duas ou mais intenções válidas**, retorne todas em "tabelas".
3. Se não encontrar intenção clara, retorne "ambigua" e não sugira tabelas.

Palavras-chave para detecção:
- roadmap: "feature", "release", "sprint", "backlog", "prioridade"
- metricas: "KPI", "OKR", "conversão", "retenção", "engajamento"
- feedback: "NPS", "reclamações", "pesquisa", "comentários"
- riscos: "bloqueio", "impedimento", "incidente", "dependência"
- resumo_360: "resumo geral", "status geral", "como está o produto"

Formato de saída JSON obrigatório:
{
  "intencao": "<roadmap|metricas|feedback|riscos|resumo_360|multi|ambigua>",
  "tabelas": ["lista de tabelas identificadas"],
  "mensagem": "resumo breve da decisão"
}

Exemplo 1 (intenção única):
Pergunta: "Quero saber o NPS do Projeto Finanças"
Saída:
{
  "intencao": "feedback",
  "tabelas": ["tab_feedback"],
  "mensagem": "Consultando Feedback conforme solicitado."
}

Exemplo 2 (múltiplas intenções):
Pergunta: "Quero saber NPS e Riscos"
Saída:
{
  "intencao": "multi",
  "tabelas": ["tab_feedback","tab_risco"],
  "mensagem": "Consultando Feedback e Riscos conforme solicitado."
}

Exemplo 3 (sem intenção clara):
Pergunta: "Estou confuso"
Saída:
{
  "intencao": "ambigua",
  "tabelas": [],
  "mensagem": "A pergunta não está clara. Por favor, reformule com projeto, métrica, feedback ou risco."
}

"""

# Mapeamento intenção → tabela no SQLite
MAPEAMENTO_TABELAS = {
    'roadmap': ['tab_roadmap'],
    'metricas': ['tab_metricas'],
    'feedback': ['tab_feedback'],
    'riscos': ['tab_risco'],
    'resumo_360': ['tab_roadmap','tab_metricas','tab_feedback','tab_risco']
}

# Classificar a pergunta
def classificar_pergunta(pergunta: str):

    prompt = f'''
    {PROMPT_ORQUESTRADOR}
    Pergunta do usuário: {pergunta}
    Gere apenas o JSON de saída, sem explicações extras.
    '''

    # Chamanda OenAI
    resposta = client_openai.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': 'Você é um orquestrador de intenções para consultas SQL.'},
            {'role': 'user', 'content': prompt}
        ],
        temperature=0
    )

    # Extrair texto da resposta
    conteudo = resposta.choices[0].message.content.strip()

    try:
        return json.loads(conteudo)
    except:
        return {'erro': 'Não consegui interpretar a saída da IA', 'saida_bruta': conteudo}


def ferramenta_pm():
    """
    Ferramenta de UX para PMs:
    - O usuário faz uma pergunta em linguagem natural
    - O orquestrador classifica a intenção
    - O agente correto é chamado (Feedback, Roadmap, Métricas, Riscos)
    - O agente retorna uma resposta estruturada ou resumida
    """

    print('='*50)
    print('      Ferramenta de UX para PMs - Consulta Inteligente')
    print('='*50)
    print('Exemplo de perguntas:')
    print('- "Quero saber o NPS do Projeto Finanças"')
    print('- "Como está o roadmap do Projeto 360?"')
    print('- "Quais métricas da Squad Acelera na última semana?"')
    print('- "Existem riscos críticos na Squad ClienteTop?"')
    print('='*50)
    print('')

    # Input do usuário
    pergunta_usuario = input('Como posso te ajudar? ').strip()

    if not pergunta_usuario:
        print('Nenhuma pergunta recebida. Encerrando...')
        return

    # Chama o orquestrador para classificar a pergunta
    resultado_orquestrador = classificar_pergunta(pergunta_usuario)
    intencao = resultado_orquestrador.get('intencao', 'ambigua')

    # Decide qual agente chamar com base na intenção
    if intencao == 'feedback':
        resposta = agente_feedback(pergunta_usuario)
    elif intencao == 'roadmap':
        resposta = agente_roadmap(pergunta_usuario)
    elif intencao == 'metricas':
        resposta = agente_metricas(pergunta_usuario)
    elif intencao == 'riscos':
        resposta = agente_risco(pergunta_usuario)
    else:
        resposta = 'Não consegui entender a pergunta. Por favor, seja mais específico.'

    # Mostra o resultado
    print('\n=== Resposta ===')
    print(resposta)
    print('='*50)

ferramenta_pm()