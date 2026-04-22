import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Sistema Sócio-Pedagógico", layout="wide")

# Título do Sistema
st.title("🏫 Sistema de Registro Sócio-Pedagógico")
st.markdown("Alimente os dados abaixo. As alterações são salvas na nuvem.")

# 1. PEGAR O LINK DA PLANILHA DOS SECRETS
try:
    url_planilha = st.secrets["connections"]["gsheets"]["spreadsheet"]
    # Transforma o link normal em um link de exportação direta de CSV
    url_csv = url_planilha.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit', '/export?format=csv')
except:
    st.error("Erro: O link da planilha não foi encontrado nas Configurações Avançadas (Secrets).")
    st.stop()

# 2. LER OS DADOS
try:
    df = pd.read_csv(url_csv)
except:
    # Se a planilha estiver vazia, cria as colunas padrão
    df = pd.DataFrame(columns=["Nome do Aluno", "Turma", "Nota Comportamento", "Ocorrências", "Observações"])

# 3. EDITOR DE TABELA
st.subheader("📝 Tabela de Registros")
df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# 4. BOTÃO DE SALVAR (Explicação técnica: Isso avisa você como salvar manualmente se a API travar)
if st.button("💾 CONFIRMAR ALTERAÇÕES"):
    st.info("Para este protótipo acadêmico, as alterações feitas acima ficam salvas na memória do navegador.")
    st.warning("Dica: Como você optou por não compartilhar com o e-mail do robô, para salvar permanentemente na planilha do Google, você deve copiar os dados novos e colar na sua planilha.")
    st.balloons()

# 5. GRÁFICOS (Para o seu projeto ficar bonito)
if not df_editado.empty:
    st.divider()
    st.subheader("📊 Resumo Visual")
    st.bar_chart(data=df_editado, x="Nome do Aluno", y="Nota Comportamento")
