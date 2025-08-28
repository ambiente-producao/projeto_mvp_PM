import chromadb
import uuid
import pandas as pd
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Carregar o modelo
modelo = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Cria o cliente local e a coleção
chroma_client = chromadb.PersistentClient(path='./banco_dados/vetor_db')

# Definir as coleções
colecoes = {
    'tab_roadmap': chroma_client.get_or_create_collection('vetor_roadmap'),
    'tab_metricas': chroma_client.get_or_create_collection('vetor_metricas'),
    'tab_feedback': chroma_client.get_or_create_collection('vetor_feedback'),
    'tab_risco': chroma_client.get_or_create_collection('vetor_risco')
}

# Dados
arquivo_excel = './dados_sintetiticos/base_dados_mvp_ux.xlsx'

# Função para fazer em lote as coleções no banco vetorial
def ingestar_por_aba(arquivo_excel, colecoes):

    abas = pd.read_excel(arquivo_excel, sheet_name=None)

    # Rodando o Excel
    for nome_aba, df in abas.items():
        if nome_aba not in colecoes:
            print(f"Aba {nome_aba} ignorada (sem coleção).")
            continue

        # Listas de apoio
        textos = []
        metadados = []
        ids = []

        # Rodando o DF
        for _, row in df.iterrows():
            texto = " ".join([str(v) for v in row.values if pd.notnull(v)])
            textos.append(texto)
            metadados.append({"tabela": nome_aba})
            ids.append(str(uuid.uuid4()))

        # Fazendo o Embedding
        embeddings = modelo.encode(textos).tolist()

        # Mandando pro DB Vetorial
        colecoes[nome_aba].add(
            documents=textos,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadados
        )

        # Print de loh
        print(f"Ingestão concluída para {nome_aba} com {len(textos)} registros.")

# Função para buscar coleção
def buscar_em_colecao(pergunta, nome_colecao, n_results=3):

    # Verificar a coleção
    if nome_colecao not in colecoes:
        print(f"Coleção {nome_colecao} não existe.")
        return []

    # Embedding da pergunta do usuário
    emb_query = modelo.encode([pergunta]).tolist()

    # Resultdoos
    resultados = colecoes[nome_colecao].query(
        query_embeddings=emb_query,
        n_results=n_results
    )

    # Mostrando
    return list(zip(resultados["documents"][0], resultados["metadatas"][0]))

ingestar_por_aba(arquivo_excel, colecoes)