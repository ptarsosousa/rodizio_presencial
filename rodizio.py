import streamlit as st
import pandas as pd

def criar_escala_rodizio(estacoes, unidades_organizacionais):
    """
    Cria a escala de rodízio usando o método de alocação por turnos.

    Args:
        estacoes (int): Número de estações de trabalho disponíveis.
        unidades_organizacionais (dict): Dicionário com as unidades organizacionais, 
                                    cada uma contendo uma lista de funcionários e seus dias de trabalho.

    Returns:
        pd.DataFrame: DataFrame com a escala de rodízio.
    """

    escala = []
    dias_da_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']

    for unidade, dados in unidades_organizacionais.items():
        funcionarios = dados['funcionarios']
        dias_trabalho = dados['dias_trabalho']

        # Cria grupos de funcionários com base no número de estações
        grupos = [funcionarios[i:i+estacoes] for i in range(0, len(funcionarios), estacoes)]

        # Define a ordem dos grupos para cada dia da semana
        ordem_grupos = list(range(len(grupos)))
        for i in range(len(grupos) - 1):
            ordem_grupos.insert(i + 1, ordem_grupos.pop(0))

        # Cria a escala para cada dia da semana
        for dia in dias_da_semana:
            for i, grupo in enumerate(grupos):
                for j, funcionario in enumerate(grupo):
                    if dias_trabalho[j] > 0:
                        escala.append([dia, unidade, funcionario, dias_trabalho[j]])
                        dias_trabalho[j] -= 1

    escala_df = pd.DataFrame(escala, columns=['Dia', 'Unidade', 'Funcionário', 'Dias restantes'])
    return escala_df

def main():
    st.title("Gerenciador de Escala de Rodízio")

    estacoes = st.number_input("Número de Estações de Trabalho", min_value=1, value=1)

    unidades_organizacionais = {}
    num_unidades = st.number_input("Número de Unidades Organizacionais", min_value=1, value=1)
    for i in range(num_unidades):
        unidade = st.text_input(f"Nome da Unidade {i+1}")
        funcionarios = st.text_area(f"Funcionários da Unidade {i+1} (separe por vírgula)", value="João,Maria,José")
        funcionarios = funcionarios.split(',')
        dias_trabalho = [int(x) for x in st.text_input(f"Dias de trabalho por funcionário na Unidade {i+1} (separe por vírgula)", value="2,2,2").split(',')]
        unidades_organizacionais[unidade] = {'funcionarios': funcionarios, 'dias_trabalho': dias_trabalho}

    if st.button("Gerar Escala"):
        escala_df = criar_escala_rodizio(estacoes, unidades_organizacionais)
        st.dataframe(escala_df)

if __name__ == "__main__":
    main()