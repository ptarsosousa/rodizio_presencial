import streamlit as st
import pandas as pd
from collections import defaultdict
import random

def create_rotation_schedule(units, num_stations):
    day_names = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira"]
    schedule = {day: [] for day in day_names}
    person_days = defaultdict(int)
    
    # Cria uma lista de todas as pessoas com a quantidade de dias que devem trabalhar
    people_days = []
    for unit, people in units.items():
        for person, days in people:
            people_days.extend([person] * days)
    
    # Embaralha a lista para garantir aleatoriedade na distribuição
    random.shuffle(people_days)
    
    # Distribui as pessoas nos dias da semana
    for person in people_days:
        possible_days = [day for day in day_names if person not in schedule[day] and len(schedule[day]) < num_stations]
        if possible_days:
            selected_day = random.choice(possible_days)
            schedule[selected_day].append(person)
            person_days[person] += 1

    # Tenta balancear o número de pessoas por dia
    max_len = max(len(schedule[day]) for day in day_names)
    min_len = min(len(schedule[day]) for day in day_names)
    while max_len - min_len > 1:
        for day in day_names:
            if len(schedule[day]) == max_len:
                person_to_move = schedule[day].pop()
                for target_day in day_names:
                    if len(schedule[target_day]) == min_len and person_to_move not in schedule[target_day]:
                        schedule[target_day].append(person_to_move)
                        break
        max_len = max(len(schedule[day]) for day in day_names)
        min_len = min(len(schedule[day]) for day in day_names)

    return schedule

def print_schedule(schedule):
    # Converte o dicionário de listas para um DataFrame, alinhando os dias
    max_len = max(len(people) for people in schedule.values())
    for day in schedule:
        if len(schedule[day]) < max_len:
            schedule[day].extend([""] * (max_len - len(schedule[day])))

    df = pd.DataFrame(schedule)
    st.write("### Programação Semanal")
    st.dataframe(df)
    st.write("### Quantidade de Pessoas por Dia")
    count_df = pd.DataFrame({day: [len([p for p in schedule[day] if p])] for day in schedule})
    st.table(count_df)

# Configurações do Streamlit
st.title("Programação de Rodízio de Unidades Organizacionais")

num_stations = st.number_input("Informe o número de estações de trabalho disponíveis por dia:", min_value=1, step=1)

units = {}

# Carregar dados a partir de uma planilha Excel
uploaded_file = st.file_uploader("Carregar arquivo Excel", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    if 'unidade' in df.columns and 'servidor' in df.columns and 'dias' in df.columns:
        for unit in df['unidade'].unique():
            unit_people = df[df['unidade'] == unit]
            units[unit] = [(row['servidor'], row['dias']) for _, row in unit_people.iterrows()]
        st.write("Unidades e Membros do Excel:")
        st.write(units)
    else:
        st.error("O arquivo Excel deve conter as colunas 'unidade', 'servidor' e 'dias'.")

# Entrada manual de unidades e membros
num_unidade = 1
unit_name = st.text_input("Informe o nome da unidade organizacional (ou deixe em branco para finalizar):")

while unit_name:
    num_people = st.number_input(f"Informe o número de pessoas na {unit_name}:", min_value=1, step=1, key=unit_name)
    names = []
    for i in range(num_people):
        col1, col2 = st.columns([3, 1])
        with col1:
            name = st.text_input(f"Informe o nome da pessoa {i + 1} na {unit_name}:", key=f"{unit_name}_{i}")
        with col2:
            days = st.number_input(f"Dias", min_value=1, max_value=5, step=1, key=f"{unit_name}_{i}_days")
        if name:
            names.append((name, days))
    if names:
        units[unit_name] = names
        st.write(f"Adicionado {unit_name} com os membros:")
        st.table(names)
    num_unidade += 1
    unit_name = st.text_input("Informe o nome da unidade organizacional (ou deixe em branco para finalizar):", key=f"unit_{num_unidade}")

if st.button("Gerar Programação"):
    if units and num_stations:
        rotation_schedule = create_rotation_schedule(units, num_stations)
        print_schedule(rotation_schedule)
    else:
        st.write("Por favor, informe o número de estações de trabalho e pelo menos uma unidade organizacional com membros.")
