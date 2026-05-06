import streamlit as st
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
import pandas as pd 

# 1. Configuração inicial da página
st.set_page_config(page_title="Dashboard Sócio-Pedagógico", layout="wide")

st.title("🏫 Dashboard Sócio-Pedagógico")

# 2. Conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. Leitura dos dados ---
try:
    df = conn.read()
    
    for col in df.columns:
        df[col] = df[col].astype(str).replace('nan', '')

    st.subheader("Visualizar e Editar Dados")
    df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    # 5. Botão para Salvar
    if st.button("💾 SALVAR ALTERAÇÕES NA PLANILHA"):
        try:
            conn.update(data=df_editado)
            st.success("✅ Sucesso! Os dados foram atualizados.")
            st.balloons()
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

    # 6. Gráficos com Plotly
    if not df_editado.empty:
        st.divider()
        st.subheader("📊 Análise Visual")
        
        df_grafico = df_editado.copy()
        cols = df_grafico.columns.tolist()
        
        if len(cols) >= 3:
            try:
                df_grafico[cols[2]] = pd.to_numeric(df_grafico[cols[2]].astype(str).str.replace(',', '.'), errors='coerce')
                df_grafico = df_grafico.dropna(subset=[cols[2]])
                df_grafico = df_grafico.sort_values(by=[cols[1], cols[0]])

                if not df_grafico.empty:
                    # --- GRÁFICO 1: BARRAS SIMPLES ---
                    fig = px.bar(
                        df_grafico, 
                        x=cols[0], 
                        y=cols[2], 
                        color=cols[1],
                        title="Desempenho por Aluno (Agrupado por Turma)",
                        template="plotly_white",
                        category_orders={cols[0]: df_grafico[cols[0]].tolist()} 
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # --- GRÁFICO 2: BARRAS EMPILHADAS ---
                    st.divider()
                    st.subheader("📊 Análise de Barras Empilhadas")
                    fig_stack = px.bar(
                        df_grafico, x=cols[1], y=cols[2], color=cols[0],
                        title="Distribuição Empilhada por Aluno",
                        template="plotly_white", barmode='stack'
                    )
                    fig_stack.update_traces(marker_line_width=1.5, marker_line_color="white")
                    st.plotly_chart(fig_stack, use_container_width=True)

                else:
                    st.warning("Insira números válidos para visualizar os gráficos.")
            except Exception as e:
                st.error(f"Erro técnico: {e}")

except Exception as e:
    st.error(f"Erro de conexão: {e}")
