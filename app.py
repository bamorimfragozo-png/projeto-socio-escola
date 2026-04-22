import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Sistema Sócio-Pedagógico", layout="wide")

st.title("🏫 Sistema de Registro Sócio-Pedagógico")
st.markdown("Alimente os dados abaixo. As alterações são salvas diretamente na nuvem da escola.")

# 1. Conexão com o banco de dados (Planilha oculta)
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

# 2. Ler dados existentes
# Se a planilha estiver vazia, ele cria as colunas padrão
try:
    df_existente = conn.read(ttl=0) # ttl=0 garante que ele busque o dado mais recente
except:
    df_existente = pd.DataFrame(columns=["Nome do Aluno", "Turma", "Nota Comportamento", "Ocorrências", "Observações"])

# 3. Interface de Edição (O que o Sócio vai usar)
st.subheader("📝 Tabela de Registros")
df_editado = st.data_editor(
    df_existente, 
    num_rows="dynamic", 
    use_container_width=True,
    key="editor_pedagogico"
)

# 4. Botão de Salvar
if st.button("💾 SALVAR ALTERAÇÕES PERMANENTEMENTE"):
    conn.update(data=df_editado)
    st.success("Dados sincronizados com sucesso!")
    st.balloons()
    st.rerun()

st.divider()

# 5. Dashboard Visual (Atualiza sozinho com os dados salvos)
if not df_editado.empty:
    st.header("📊 Análise Gerencial")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de Comportamento
        fig_bar = px.bar(df_editado, x="Nome do Aluno", y="Nota Comportamento", color="Turma", title="Desempenho por Aluno")
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col2:
        # Gráfico de Ocorrências
        fig_pie = px.pie(df_editado, values="Ocorrências", names="Turma", title="Distribuição de Ocorrências por Turma")
        st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.info("Adicione dados na tabela acima para gerar os gráficos.")
