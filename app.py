import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Sistema Sócio-Pedagógico", layout="wide")

# 2. FUNÇÃO PARA LIMPAR O LINK (Resolve o erro de URL)
def preparar_url(url):
    if "/edit" in url:
        return url.split("/edit")[0] + "/export?format=csv"
    elif "/view" in url:
        return url.split("/view")[0] + "/export?format=csv"
    return url

# 3. INTERFACE
st.title("🏫 Sistema de Registro Sócio-Pedagógico")

# COLOQUE SEU LINK AQUI
LINK_DA_PLANILHA = "https://docs.google.com/spreadsheets/d/14ShnxHC_ktuEWvZ3r2NASqmT7A_M9deWsxRAJ7zDKec/edit?usp=sharing"

try:
    # 4. CARREGAMENTO DOS DADOS
    url_final = preparar_url(LINK_DA_PLANILHA)
    df = pd.read_csv(url_final)
    
    # 5. TABELA INTERATIVA
    st.subheader("📝 Registros de Alunos")
    df_editado = st.data_editor(df, use_container_width=True)

    # 6. GRÁFICO COM PLOTLY (Muito mais bonito)
    st.divider()
    st.subheader("📊 Análise Visual de Desempenho")
    
    # Criando um gráfico de barras interativo
    # Supondo que sua planilha tenha colunas 'Nome' e 'Nota'
    colunas = df_editado.columns.tolist()
    
    if len(colunas) >= 2:
        fig = px.bar(
            df_editado, 
            x=colunas[0], # Nome do Aluno
            y=colunas[2] if len(colunas) > 2 else colunas[1], # Nota
            title="Desempenho por Aluno",
            labels={colunas[0]: "Aluno", colunas[2] if len(colunas) > 2 else colunas[1]: "Pontuação"},
            color=colunas[0], # Dá uma cor para cada aluno
            template="plotly_white"
        )
        
        # Exibe o gráfico do Plotly no Streamlit
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("A planilha precisa de pelo menos 2 colunas para gerar o gráfico.")

    if st.button("💾 ATUALIZAR DASHBOARD"):
        st.balloons()
        st.success("Visualização atualizada!")

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
