import streamlit as st
from streamlit_gsheets import GSheetsConnection
import plotly.express as px

# 1. Configuração inicial da página
st.set_page_config(page_title="Dashboard Sócio-Pedagógico", layout="wide")

st.title("🏫 Dashboard Sócio-Pedagógico")

# 2. Conexão com o Google Sheets usando os Secrets (JSON da Conta de Serviço)
# O Streamlit busca automaticamente as credenciais no menu Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Leitura dos dados
try:
    df = conn.read()
    
    st.subheader("Visualizar e Editar Dados")
    st.info("Clique nas células da tabela abaixo para editar. Depois, clique no botão 'Salvar' no final.")

    # 4. Tabela Interativa (Editor de Dados)
    # 'num_rows="dynamic"' permite adicionar ou excluir linhas no dashboard
    df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    # 5. Botão para Salvar as alterações na planilha original
    if st.button("💾 SALVAR ALTERAÇÕES NA PLANILHA"):
        try:
            # Envia a tabela editada de volta para o Google Sheets
            conn.update(data=df_editado)
            st.success("✅ Sucesso! Os dados foram atualizados na sua planilha do Google.")
            st.balloons()
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")
            st.warning("Dica: Verifique se você compartilhou a planilha com o e-mail do robô como 'Editor'.")

    # 6. Gráficos com Plotly (Para deixar o dashboard profissional)
    if not df_editado.empty:
        st.divider()
        st.subheader("📊 Análise Visual")
        
        # Criando um gráfico automático baseado nas suas colunas
        # Ele pega a 1ª coluna para o nome e a 3ª para os valores (ex: Notas)
        cols = df_editado.columns.tolist()
        
        if len(cols) >= 3:
            fig = px.bar(
                df_editado, 
                x=cols[0], 
                y=cols[2], 
                color=cols[1] if len(cols) > 1 else None,
                title="Desempenho por Aluno",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao conectar com a planilha: {e}")
    st.info("Verifique se os Secrets estão configurados corretamente no Streamlit Cloud.")
