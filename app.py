import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Sistema Sócio-Pedagógico", layout="wide")

st.title("🏫 Painel de Controle Sócio-Pedagógico")

# 1. Conectando com a planilha (usando o segredo que vamos por no site)
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Lendo os dados atuais
df = conn.read()

st.subheader("Inserir ou Editar Dados")
# 3. O segredo: st.data_editor permite que você digite no Dashboard
df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# 4. BOTÃO QUE SALVA DE VERDADE NA PLANILHA
if st.button("💾 SALVAR ALTERAÇÕES NA PLANILHA"):
    try:
        conn.update(data=df_editado)
        st.success("✅ Dados salvos com sucesso na sua Planilha Google!")
        st.balloons()
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")

# --- GRÁFICOS ---
st.divider()
if not df_editado.empty:
    st.subheader("📊 Visualização dos Dados Salvos")
    # Gráfico simples usando as duas primeiras colunas
    st.bar_chart(df_editado.set_index(df_editado.columns[0])[df_editado.columns[1]])
