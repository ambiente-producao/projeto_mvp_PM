# 🧩 Ferramenta de UX para PMs – Consulta Inteligente

## 📌 Visão Geral
Esta ferramenta permite que **Product Managers (PMs)** consultem informações de diferentes áreas do produto de forma rápida e simples, usando **linguagem natural**.

O usuário pode perguntar:
- *"Quero saber o NPS do Projeto Finanças"*
- *"Como está o roadmap do Projeto 360?"*
- *"Existem riscos críticos na Squad ClienteTop?"*

O sistema entende a intenção, busca nos bancos de dados corretos e retorna uma resposta **fluida e resumida**.

---

## 🏗️ Arquitetura

A aplicação é dividida em módulos para manter a organização e facilitar a evolução:

1. **Orquestrador**  
   - Interpreta a pergunta usando LLM (GPT-4o-mini).  
   - Identifica a intenção: *Feedback*, *Roadmap*, *Métricas*, *Riscos* ou *Resumo 360*.  
   - Encaminha para o agente correto.

2. **Agentes**  
   - Cada agente é responsável por uma área:
     - **Feedback/NPS** → Satisfação, reclamações e sugestões.  
     - **Roadmap** → Features, releases e prioridades.  
     - **Métricas** → KPIs, conversão, retenção e engajamento.  
     - **Riscos** → Bloqueios, dependências e severidade.  
   - Fluxo: **Busca Vetorial → SQL → Resposta Natural**.

3. **Banco Vetorial (ChromaDB)**  
   - Faz a busca semântica para identificar *projeto*, *squad* e *semana*, mesmo com erros ou variações na pergunta.

4. **Banco SQL (SQLite)**  
   - Armazena os dados tabulares.  
   - Consulta com filtros vindos do banco vetorial.

---

## 🔄 Fluxo Completo

1. Usuário faz pergunta
2. Orquestrador → Identifica intenção
3. Agente correto → Consulta no banco vetorial
4. SQL → Traz dados filtrados
5. Modelo de Linguagem → Gera resposta resumida
6. Usuário recebe resposta

---

## ⚙️ Instalação

```bash
1. Clone o repositório
git clone https://github.com/seu-usuario/ferramenta-ux-pm.git
cd ferramenta-ux-pm

2. Crie o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

3. Instale as dependências
pip install -r requirements.txt

## Executa o programa principal
python main.py
```

<img width="1455" height="522" alt="image" src="https://github.com/user-attachments/assets/02d9168a-70a8-4150-b23f-71812986feeb" />

