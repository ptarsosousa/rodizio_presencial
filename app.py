import streamlit as st
import pandas as pd
from pulp import LpProblem, LpMaximize, LpVariable, lpSum

def criar_escala_rodizio_linear(df):
    """
    Cria a escala de rodízio usando modelagem linear.

    Args:
        df (pd.DataFrame): DataFrame com os dados dos funcionários e unidades.

    Returns:
        pd.DataFrame: DataFrame com a escala de rodízio em formato de tabela.
    """

    # Define o modelo de otimização
    modelo = LpProblem("Escala_Rodízio", LpMaximize)

    # Define as variáveis de decisão
    funcionarios = df['Funcionário'].unique()
    dias_da_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
    variaveis = {}
    for funcionario in funcionarios:
        for dia in dias_da_semana:
            variaveis[funcionario, dia] = LpVariable(f"{funcionario}_{dia}", 0, 1, cat='Binary')

    # Define a função objetivo: maximizar o número de funcionários trabalhando
    modelo += lpSum(variaveis[funcionario, dia] for funcionario in funcionarios for dia in dias_da_semana)

    # Define as restrições:
    # 1. Cada funcionário trabalha no máximo o número de dias definido
    for funcionario in funcionarios:
        modelo += lpSum(variaveis[funcionario, dia] for dia in dias_da_semana) <= df.loc[df['Funcionário'] == funcionario, 'Dias'].iloc[0]

    # 2. Cada dia tem no máximo o número de estações de trabalho
    for dia in dias_da_semana:
        modelo += lpSum(variaveis[funcionario, dia] for funcionario in funcionarios) <= df['Estações'].iloc[0]

    # 3. Cada funcionário da mesma unidade não trabalha no mesmo dia
    for unidade in df['Unidade'].unique():
        for dia in dias_da_semana:
            for i in range(len(df)):
                if df['Unidade'].iloc[i] == unidade:
                    for j in range(i + 1, len(df)):
                        if df['Unidade'].iloc[j] == unidade:
                            modelo += variaveis[df['Funcionário'].iloc[i], dia] + variaveis[df['Funcionário'].iloc[j], dia] <= 1

    # Resolve o modelo
    modelo.solve()

    # Cria a escala de rodízio em formato de tabela
    escala = {}
    for dia in dias_da_semana:
        escala[dia] = []
        for i in range(df['Estações'].iloc[0]):
            escala[dia].append(None)  # Inicializa as colunas com None

    for funcionario in funcionarios:
        for dia in dias_da_semana:
            if variaveis[funcionario, dia].varValue == 1:
                for i, coluna in enumerate(escala[dia]):
                    if coluna is None:
                        escala[dia][i] = funcionario
                        break

    escala_df = pd.DataFrame(escala)
    return escala_df

st.title("Gerenciador de Escala de Rodízio (Modelagem Linear) :flag-br:")
st.subheader("Olá, vamos experimentar esse app e ver se ele nos ajuda a montar o rodízio da galera!! :sunglasses:")

st.markdown('''
## 1º Passo - Gere um arquivo Excel
            
**Estrutura do Arquivo Excel:**

O arquivo Excel deve conter as seguintes colunas:

* **Unidade:** Nome da unidade organizacional (string)
* **Funcionário:** Nome do funcionário (string)
* **Dias:** Número de dias que o funcionário precisa trabalhar por semana (int)
* **Estações:** Número de estações de trabalho disponíveis (int)

**Exemplo:**

| Unidade | Funcionário | Dias | Estações |
|---|---|---|---|
| Desenvolvimento | João | 2 | 3 |
| Desenvolvimento | Maria | 2 | 3 |
| Marketing | Ana | 3 | 3 |
| Marketing | Bruno | 3 | 3 |
''')

st.markdown('''
## 2º Passo - Carregue aqui o arquivo Excel que você criou
''')

uploaded_file = st.file_uploader("Carregue o arquivo Excel com os dados", type=["xlsx", "xls"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Exibe o DataFrame para verificação
    st.dataframe(df)
    if 'Unidade' not in df.columns or 'Funcionário' not in df.columns or 'Dias' not in df.columns or 'Estações' not in df.columns:
        st.error("ERRO: O arquivo Excel deve conter as colunas 'Unidade', 'Funcionário', 'Dias' e 'Estações'.")
    else:
        st.markdown('''
        ## 3º Passo - Clique no botão abaixo para criar a escala''')

        if st.button("Gerar Escala e correr pro abraço :sparkles:"):
            escala_df = criar_escala_rodizio_linear(df)
            st.markdown('### :clap: :clap: Parabéns!!! Escala gerada com sucesso!!!')
            st.table(escala_df)