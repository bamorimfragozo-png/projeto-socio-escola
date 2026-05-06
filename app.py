import streamlit as st
from streamlit_gsheets import GSheetsConnection
import plotly.express as px

# 1. Configuração inicial da página
st.set_page_config(page_title="Dashboard Sócio-Pedagógico", layout="wide")

st.title("🏫 Dashboard Sócio-Pedagógico")

# 2. Conexão com o Google Sheets usando os Secrets (JSON da Conta de Serviço)
# O Streamlit busca automaticamente as credenciais no menu Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. Leitura dos dados ---
try:
    # Lê os dados da planilha
    df = conn.read()
    
    # --- NOVO: FORÇAR AS COLUNAS A ACEITAREM TEXTO ---
    # Isso evita que o "M" de Maria vire "0"
    for col in df.columns:
        df[col] = df[col].astype(str).replace('nan', '')
    # -----------------------------------------------

    st.subheader("Visualizar e Editar Dados")
    st.info("Clique nas células da tabela abaixo para editar. Depois, clique no botão 'Salvar' no final.")

    # --- 4. Tabela Interativa (Editor de Dados) ---
    # Agora com os dados preparados para aceitar letras!
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
    # 6. Gráficos com Plotly
    if not df_editado.empty:
        st.divider()
        st.subheader("📊 Análise Visual")
        
        # Criamos uma cópia para o gráfico
        df_grafico = df_editado.copy()
        cols = df_grafico.columns.tolist()
        
        if len(cols) >= 3:
            try:
                # Importante: Importe o pandas no topo do arquivo: import pandas as pd
                import pandas as pd 
                
                # Converte a 3ª coluna (Notas) para número, ignorando erros
                df_grafico[cols[2]] = pd.to_numeric(df_grafico[cols[2]].astype(str).str.replace(',', '.'), errors='coerce')
                
                # Remove linhas sem nota para não sujar o gráfico
                df_grafico = df_grafico.dropna(subset=[cols[2]])

                if not df_grafico.empty:
                    fig = px.bar(
                        df_grafico, 
                        x=cols[0], 
                        y=cols[2], 
                        color=cols[1] if len(cols) > 1 else None,
                        title="Desempenho por Aluno",
                        template="plotly_white",
                        labels={cols[2]: "Nota"}
                    )
                    fig.update_yaxes(range=[0, 10]) # Escala de 0 a 10
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Insira números válidos na coluna de notas para visualizar o gráfico.")
                    
            except Exception as e:
                st.error(f"Erro técnico no gráfico: {e}")

except Exception as e:
    st.error(f"Erro ao conectar com a planilha: {e}")
    st.info("Verifique se os Secrets estão configurados corretamente no Streamlit Cloud.")
