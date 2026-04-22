import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sistema Sócio-Pedagógico", layout="wide")

st.title("🏫 Sistema de Registro Sócio-Pedagógico")
st.markdown("Alimente os dados abaixo. As alterações são salvas diretamente na nuvem.")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df_existente = conn.read(ttl=0) 
except Exception as e:
    df_existente = pd.DataFrame(columns=["Nome do Aluno", "Turma", "Nota Comportamento", "Ocorrências", "Observações"])

st.subheader("📝 Tabela de Registros")
df_editado = st.data_editor(
    df_existente, 
    num_rows="dynamic", 
    use_container_width=True,
    key="editor_pedagogico_v3"
)

if st.button("💾 SALVAR ALTERAÇÕES PERMANENTEMENTE"):
    try:
        conn.update(data=df_editado, worksheet="dados")
        st.success("Dados sincronizados com sucesso!")
        st.balloons()
    except Exception as e:
        st.error(f"Erro de permissão: Verifique se a planilha está como EDITOR para qualquer pessoa com o link.")

if not df_editado.empty:
    st.divider()
    st.header("📊 Análise Gerencial")
    col1, col2 = st.columns(2)
    with col1:
        fig_bar = px.bar(df_editado, x="Nome do Aluno", y="Nota Comportamento", color="Turma")
        st.plotly_chart(fig_bar, use_container_width=True)
    with col2:
        fig_pie = px.pie(df_editado, values="Ocorrências", names="Turma")
        st.plotly_chart(fig_pie, use_container_width=True)
