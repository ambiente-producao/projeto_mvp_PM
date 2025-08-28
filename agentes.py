import chromadb
import uuid
import pandas as pd
import sqlite3
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Conexão com a OPENAI
from openai import OpenAI
with open('chave_openai.txt', 'r') as file:
    api_key = file.read().strip()
client_openai = OpenAI(api_key=api_key)

# Carregar o modelo
modelo = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def agente_feedback(pergunta, limite_resultados=1):

  # Conexão
  chroma_client = chromadb.PersistentClient(path='./banco_dados/vetor_db')
  colecao_feedback = chroma_client.get_collection('vetor_feedback')

  # Conveter pergunta
  vetor_pergunta = modelo.encode([pergunta]).tolist()

  # ========================
  # bloco: contexto
  # ========================
  resultados = colecao_feedback.query(
      query_embeddings=vetor_pergunta,
      n_results=limite_resultados
  )
  documentos = resultados['documents'][0]
  metadados = resultados['metadatas'][0]

  # Complimindo os docs
  documentos_metadados = list(zip(documentos, metadados))

  # ========================
  # extrair filtros do melhor resultado
  # ========================
  if not documentos_metadados:
        return None, None, None

  # Pegamos o documento mais relevante (primeiro resultado)
  documento, metadado = documentos_metadados[0]

  # Tentamos quebrar o documento em partes (assumindo o padrão do Excel)
  partes = documento.split()
  projeto = partes[0] + ' ' + partes[1] if len(partes) >= 2 else None
  squad = partes[2] if len(partes) >= 3 else None
  semana = partes[3] if len(partes) >= 4 else None

  # ========================
  # consultar tabela feedback no SQLite
  # ========================
  conexao = sqlite3.connect('./banco_dados/banco_pm.db')

  consulta_sql = 'SELECT * FROM tab_feedback WHERE 1=1'
  if projeto:
      consulta_sql += f" AND projeto = '{projeto}'"
  if squad:
      consulta_sql += f" AND squad = '{squad}'"
  if semana:
      consulta_sql += f" AND semana = '{semana}'"

  dados = pd.read_sql_query(consulta_sql, conexao)
  conexao.close()

  # Propt do Feedback
  PROMPT_FEEDBACK = f'''
    Você é um assistente especializado em Feedback e NPS de produtos digitais.

    Recebe como entrada:
    1) A pergunta original do usuário.
    2) Dados já filtrados do banco SQL em formato de tabela.

    Sua tarefa:
    - Ler os dados com atenção.
    - Responder de forma **clara e objetiva**, sem repetir a tabela bruta.
    - Se houver métricas como NPS, explique o resultado em **1-2 frases**.
    - Se houver reclamações e sugestões, cite os **principais pontos**, sem listar tudo se não for necessário.
    - Não invente dados que não estão na tabela.

    Se a tabela estiver vazia, responda:
    "Não encontrei dados para a pergunta enviada."

    Formato de saída:
    - Um parágrafo com as informações

    dados = {dados}
  '''

  prompt = f'''
    {PROMPT_FEEDBACK}
    Pergunta do usuário: {pergunta}
    '''

  # Chamanda OenAI
  resposta = client_openai.chat.completions.create(
      model='gpt-4o-mini',
      messages=[
          {'role': 'system', 'content': 'Você é um Você é um assistente especializado em Feedback e NPS de produtos digitais.'},
          {'role': 'user', 'content': prompt}
      ],
      temperature=0.5
  )

  # Extrair texto da resposta
  conteudo = resposta.choices[0].message.content.strip()
  #print(conteudo)

  try:
      return print(conteudo)
  except:
      return print({'erro': 'Não consegui interpretar a saída da IA', 'saida_bruta': conteudo})


def agente_roadmap(pergunta, limite_resultados=1):

  # Conexão
  chroma_client = chromadb.PersistentClient(path='./banco_dados/vetor_db')
  colecao_roadmap = chroma_client.get_collection('vetor_roadmap')

  # Conveter pergunta
  vetor_pergunta = modelo.encode([pergunta]).tolist()

  # ========================
  # bloco: contexto
  # ========================
  resultados = colecao_roadmap.query(
      query_embeddings=vetor_pergunta,
      n_results=limite_resultados
  )
  documentos = resultados['documents'][0]
  metadados = resultados['metadatas'][0]

  # Complimindo os docs
  documentos_metadados = list(zip(documentos, metadados))

  # ========================
  # extrair filtros do melhor resultado
  # ========================
  if not documentos_metadados:
        return None, None, None

  # Pegamos o documento mais relevante (primeiro resultado)
  documento, metadado = documentos_metadados[0]

  # Tentamos quebrar o documento em partes (assumindo o padrão do Excel)
  partes = documento.split()
  projeto = partes[0] + ' ' + partes[1] if len(partes) >= 2 else None
  squad = partes[2] if len(partes) >= 3 else None
  semana = partes[3] if len(partes) >= 4 else None

  # ========================
  # consultar tabela roadmap no SQLite
  # ========================
  conexao = sqlite3.connect('./banco_dados/banco_pm.db')

  consulta_sql = 'SELECT * FROM tab_roadmap WHERE 1=1'
  if projeto:
      consulta_sql += f" AND projeto = '{projeto}'"
  if squad:
      consulta_sql += f" AND squad = '{squad}'"
  if semana:
      consulta_sql += f" AND semana = '{semana}'"

  dados = pd.read_sql_query(consulta_sql, conexao)
  conexao.close()

  # Propt do roadmap
  PROMPT_roadmap = f'''
    Você é um assistente especializado em roadmap produtos digitais.

    Recebe como entrada:
    1) A pergunta original do usuário.
    2) Dados já filtrados do banco SQL em formato de tabela.

    Sua tarefa:
    - Ler os dados com atenção.
    - Responder de forma **clara e objetiva**, sem repetir a tabela bruta.
    - Se houver métricas como NPS, explique o resultado em **1-2 frases**.
    - Se houver reclamações e sugestões, cite os **principais pontos**, sem listar tudo se não for necessário.
    - Não invente dados que não estão na tabela.

    Se a tabela estiver vazia, responda:
    "Não encontrei dados para a pergunta enviada."

    Formato de saída:
    - Um parágrafo com as informações

    dados = {dados}
  '''

  prompt = f'''
    {PROMPT_roadmap}
    Pergunta do usuário: {pergunta_usuario}
    '''

  # Chamanda OenAI
  resposta = client_openai.chat.completions.create(
      model='gpt-4o-mini',
      messages=[
          {'role': 'system', 'content': 'Você é um Você é um assistente especializado em roadmap de produtos digitais.'},
          {'role': 'user', 'content': prompt}
      ],
      temperature=0.5
  )

  # Extrair texto da resposta
  conteudo = resposta.choices[0].message.content.strip()
  #print(conteudo)

  try:
      return print(conteudo)
  except:
      return print({'erro': 'Não consegui interpretar a saída da IA', 'saida_bruta': conteudo})


def agente_metricas(pergunta, limite_resultados=1):

  # Conexão
  chroma_client = chromadb.PersistentClient(path='./banco_dados/vetor_db')
  colecao_metricas = chroma_client.get_collection('vetor_metricas')

  # Conveter pergunta
  vetor_pergunta = modelo.encode([pergunta]).tolist()

  # ========================
  # bloco: contexto
  # ========================
  resultados = colecao_metricas.query(
      query_embeddings=vetor_pergunta,
      n_results=limite_resultados
  )
  documentos = resultados['documents'][0]
  metadados = resultados['metadatas'][0]

  # Complimindo os docs
  documentos_metadados = list(zip(documentos, metadados))

  # ========================
  # extrair filtros do melhor resultado
  # ========================
  if not documentos_metadados:
        return None, None, None

  # Pegamos o documento mais relevante (primeiro resultado)
  documento, metadado = documentos_metadados[0]

  # Tentamos quebrar o documento em partes (assumindo o padrão do Excel)
  partes = documento.split()
  projeto = partes[0] + ' ' + partes[1] if len(partes) >= 2 else None
  squad = partes[2] if len(partes) >= 3 else None
  semana = partes[3] if len(partes) >= 4 else None

  # ========================
  # consultar tabela metricas no SQLite
  # ========================
  conexao = sqlite3.connect('./banco_dados/banco_pm.db')

  consulta_sql = 'SELECT * FROM tab_metricas WHERE 1=1'
  if projeto:
      consulta_sql += f" AND projeto = '{projeto}'"
  if squad:
      consulta_sql += f" AND squad = '{squad}'"
  if semana:
      consulta_sql += f" AND semana = '{semana}'"

  dados = pd.read_sql_query(consulta_sql, conexao)
  conexao.close()

  # Propt do metricas
  PROMPT_metricas = f'''
    Você é um assistente especializado em metricas produtos digitais.

    Recebe como entrada:
    1) A pergunta original do usuário.
    2) Dados já filtrados do banco SQL em formato de tabela.

    Sua tarefa:
    - Ler os dados com atenção.
    - Responder de forma **clara e objetiva**, sem repetir a tabela bruta.
    - Se houver métricas como NPS, explique o resultado em **1-2 frases**.
    - Se houver reclamações e sugestões, cite os **principais pontos**, sem listar tudo se não for necessário.
    - Não invente dados que não estão na tabela.

    Se a tabela estiver vazia, responda:
    "Não encontrei dados para a pergunta enviada."

    Formato de saída:
    - Um parágrafo com as informações

    dados = {dados}
  '''

  prompt = f'''
    {PROMPT_metricas}
    Pergunta do usuário: {pergunta_usuario}
    '''

  # Chamanda OenAI
  resposta = client_openai.chat.completions.create(
      model='gpt-4o-mini',
      messages=[
          {'role': 'system', 'content': 'Você é um Você é um assistente especializado em metricas de produtos digitais.'},
          {'role': 'user', 'content': prompt}
      ],
      temperature=0.5
  )

  # Extrair texto da resposta
  conteudo = resposta.choices[0].message.content.strip()
  #print(conteudo)

  try:
      return print(conteudo)
  except:
      return print({'erro': 'Não consegui interpretar a saída da IA', 'saida_bruta': conteudo})



def agente_risco(pergunta, limite_resultados=1):

  # Conexão
  chroma_client = chromadb.PersistentClient(path='./banco_dados/vetor_db')
  colecao_risco = chroma_client.get_collection('vetor_risco')

  # Conveter pergunta
  vetor_pergunta = modelo.encode([pergunta]).tolist()

  # ========================
  # bloco: contexto
  # ========================
  resultados = colecao_risco.query(
      query_embeddings=vetor_pergunta,
      n_results=limite_resultados
  )
  documentos = resultados['documents'][0]
  metadados = resultados['metadatas'][0]

  # Complimindo os docs
  documentos_metadados = list(zip(documentos, metadados))

  # ========================
  # extrair filtros do melhor resultado
  # ========================
  if not documentos_metadados:
        return None, None, None

  # Pegamos o documento mais relevante (primeiro resultado)
  documento, metadado = documentos_metadados[0]

  # Tentamos quebrar o documento em partes (assumindo o padrão do Excel)
  partes = documento.split()
  projeto = partes[0] + ' ' + partes[1] if len(partes) >= 2 else None
  squad = partes[2] if len(partes) >= 3 else None
  semana = partes[3] if len(partes) >= 4 else None

  # ========================
  # consultar tabela risco no SQLite
  # ========================
  conexao = sqlite3.connect('./banco_dados/banco_pm.db')

  consulta_sql = 'SELECT * FROM tab_risco WHERE 1=1'
  if projeto:
      consulta_sql += f" AND projeto = '{projeto}'"
  if squad:
      consulta_sql += f" AND squad = '{squad}'"
  if semana:
      consulta_sql += f" AND semana = '{semana}'"

  dados = pd.read_sql_query(consulta_sql, conexao)
  conexao.close()

  # Propt do risco
  PROMPT_risco = f'''
    Você é um assistente especializado em risco produtos digitais.

    Recebe como entrada:
    1) A pergunta original do usuário.
    2) Dados já filtrados do banco SQL em formato de tabela.

    Sua tarefa:
    - Ler os dados com atenção.
    - Responder de forma **clara e objetiva**, sem repetir a tabela bruta.
    - Se houver métricas como NPS, explique o resultado em **1-2 frases**.
    - Se houver reclamações e sugestões, cite os **principais pontos**, sem listar tudo se não for necessário.
    - Não invente dados que não estão na tabela.

    Se a tabela estiver vazia, responda:
    "Não encontrei dados para a pergunta enviada."

    Formato de saída:
    - Um parágrafo com as informações

    dados = {dados}
  '''

  prompt = f'''
    {PROMPT_risco}
    Pergunta do usuário: {pergunta_usuario}
    '''

  # Chamanda OenAI
  resposta = client_openai.chat.completions.create(
      model='gpt-4o-mini',
      messages=[
          {'role': 'system', 'content': 'Você é um Você é um assistente especializado em risco de produtos digitais.'},
          {'role': 'user', 'content': prompt}
      ],
      temperature=0.5
  )

  # Extrair texto da resposta
  conteudo = resposta.choices[0].message.content.strip()
  #print(conteudo)

  try:
      return print(conteudo)
  except:
      return print({'erro': 'Não consegui interpretar a saída da IA', 'saida_bruta': conteudo})
