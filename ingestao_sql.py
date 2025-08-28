import pandas as pd
import sqlite3

# dados
arquivo_excel = './dados_sintetiticos/base_dados_mvp_ux.xlsx'

# sheet_name=None traz todas as abas como dicionário
abas = pd.read_excel(arquivo_excel, sheet_name=None)

# Conexão com SQLite
con = sqlite3.connect('./banco_dados/banco_pm.db')

# Salvar cada aba como tabela no banco
for nome_tabela, df in abas.items():
    df.to_sql(nome_tabela.lower(), con, if_exists='replace', index=False)
    print(f"Tabela '{nome_tabela.lower()}' criada com {len(df)} registros.")

con.close()