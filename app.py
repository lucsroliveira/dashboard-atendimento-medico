import streamlit as st
import pandas as pd
from datetime import datetime 
import plotly.express as px

# Acesso aos secrets
usuario_correto = st.secrets["login"]["usuario"]
senha_correta = st.secrets["login"]["senha"]

# Inicializa o estado de autenticação, se ainda não estiver setado
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# Se ainda não autenticado, mostra a tela de login
if not st.session_state.autenticado:
    st.title("🔐 Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario == usuario_correto and senha == senha_correta:
            st.session_state.autenticado = True
            st.success("Login bem-sucedido! ✅")
            st.experimental_rerun()  # força recarregamento da interface
        else:
            st.error("Credenciais inválidas ❌")

else:
    # DASHBOARD AQUI
    st.title("📊 Dashboard de Atendimentos Médicos")

    # Botão de logout
    if st.button("Sair"):
        st.session_state.autenticado = False
        st.experimental_rerun()

    # --- Aqui entra todo o seu código do dashboard ---
    # Exemplo:
    st.write("Bem-vindo ao painel!")

st.title("Dashboard de Atendimentos Médicos")

# Le a planilha com os dados locamente
df = pd.read_excel("dados-atendimento.xlsx")
df.columns = df.columns.str.strip()

# Conversao da data de atendimento
df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')

# Cria a coluna Ano-Mês
df['Ano-Mês'] = df['Data'].dt.to_period('M')

# Filtra para o ano de 2025
df_2025 = df[df['Data'].dt.year == 2025].copy()
df_2025.columns = df_2025.columns.str.strip()


# ========================================
# 👶 Crianças - Identificação por idade
# ========================================

# Se não tiver 'Idade', calcula a idade com base na coluna 'Nascimento'
if 'Idade' not in df_2025.columns and 'Nascimento' in df_2025.columns:
    df_2025['Nascimento'] = pd.to_datetime(df_2025['Nascimento'], dayfirst=True, errors='coerce')
    hoje = pd.to_datetime("today")
    df_2025['Idade'] = df_2025['Nascimento'].apply(lambda nasc: hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day)))


 # Relatórios

# Criar uma linha com dois gráficos lado a lado
col1, col2 = st.columns(2)


with col1:

    st.subheader("1. Atendimentos por médico por mês")
    atendimentos_medico = df_2025.groupby(['Ano-Mês', 'Medico']).size().reset_index(name='Atendimentos')
    st.dataframe(atendimentos_medico)
    chart_data = atendimentos_medico.pivot(index='Ano-Mês', columns='Medico', values='Atendimentos').fillna(0)
    #st.bar_chart(chart_data)

with col2:    

    st.subheader("2. Meses com mais atendimentos")
    atendimentos_mes = df_2025['Data'].dt.month.value_counts().sort_index()
    atendimentos_mes.index = atendimentos_mes.index.map(lambda x: pd.to_datetime(f'2025-{x:02}-01').strftime('%B'))
    st.bar_chart(atendimentos_mes)

# Segunda linha com outro gráfico e tabela
st.markdown("---")  # linha separadora

st.subheader("3. Retornos por paciente em 2025")
retornos = df_2025.groupby('Paciente').size()
retornos = retornos[retornos > 1]
st.dataframe(retornos.rename("Atendimentos"), use_container_width=True)


st.subheader("4. Cidade com mais pacientes")
pacientes_cidade = df_2025.groupby('Cidade')['Paciente'].nunique().sort_values(ascending=True)
st.bar_chart(pacientes_cidade.rename("Pacientes distintos"))


st.subheader("5. Distribuição percentual de atendimentos por médico (2025)")

# Conta total de atendimentos por médico no ano todo
atendimentos_por_medico = df_2025['Medico'].value_counts().reset_index()
atendimentos_por_medico.columns = ['Medico', 'Atendimentos']

# Gráfico de pizza
fig = px.pie(
    atendimentos_por_medico,
    names='Medico',
    values='Atendimentos',
    title='Participação percentual de cada médico nos atendimentos (2025)',
    hole=0.4  # para um estilo tipo "donut"
)

st.plotly_chart(fig)


