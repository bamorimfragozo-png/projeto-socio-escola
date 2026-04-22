import streamlit as st
import pandas as pd
import gspread

st.set_page_config(page_title="Sistema Escola", layout="wide")

# --- FUNÇÃO PARA CONECTAR (Modo gspread) ---
def conectar_planilha():
    # Aqui, para salvar, o Google EXIGE que você use um e-mail de serviço.
    # Se você não quer criar um, a ÚNICA alternativa é ler a planilha
    # e, para salvar, você terá que baixar o arquivo e subir no Google.
    pass

st.title("🏫 Dashboard Sócio-Pedagógico")

# LINK DA SUA PLANILHA
URL_PLANILHA = "SUA_URL_AQUI"

try:
    # Lendo os dados para visualização (isso funciona!)
    url_csv = URL_PLANILHA.split("/edit")[0] + "/export?format=csv"
    df = pd.read_csv(url_csv)
    
    st.subheader("Visualizar e Editar Dados")
    df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    # --- O PROBLEMA DO SALVAR ---
    st.warning("⚠️ O Google bloqueia a gravação direta via link público por segurança.")
    
    # Alternativa Pro para o seu Projeto Integrador:
    st.markdown("### Como salvar suas alterações:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Gerar Arquivo Atualizado"):
            csv = df_editado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Clique aqui para Baixar o CSV",
                data=csv,
                file_name='dados_escola_atualizados.csv',
                mime='text/csv',
            )
            st.success("Arquivo gerado! Agora basta importar no seu Google Sheets.")

except Exception as e:
    st.error(f"Erro: {e}")
