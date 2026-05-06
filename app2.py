import streamlit as st
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
import pandas as pd

# 1. Configuração
st.set_page_config(page_title="Análise Empilhada", layout="wide")
st.title("📊 Análise de Barras Empilhadas")

# 2. Conexão (Lembre-se de configurar os Secrets para este novo App!)
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read()
    
    # Limpeza para evitar erros de "nan" ou células vazias
    for col in df.columns:
        df[col] = df[col].astype(str).replace('nan', '')

    st.subheader("Dados da Planilha")
    # Mostramos apenas os dados para conferência
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        st.divider()
        df_grafico = df.copy()
        cols = df_grafico.columns.tolist()
        
        if len(cols) >= 3:
            # Conversão essencial: Notas para números
            df_grafico[cols[2]] = pd.to_numeric(df_grafico[cols[2]].str.replace(',', '.'), errors='coerce')
            df_grafico = df_grafico.dropna(subset=[cols[2]])

            # Filtro para remover linhas totalmente vazias que bugam o gráfico
            df_grafico = df_grafico[df_grafico[cols[0]] != ""]

            if not df_grafico.empty:
                # O segredo do empilhamento:
                # X = Turma (Categoria)
                # Y = Nota (Valor acumulado)
                # Color = Aluno (O que divide a barra)
                fig = px.bar(
                    df_grafico, 
                    x=cols[1], 
                    y=cols[2], 
                    color=cols[0],
                    title="Visão Geral por Turma (Soma de Notas)",
                    template="plotly_white",
                    barmode='stack' # Força uma barra em cima da outra
                )
                
                # Melhora o visual: força o eixo X a não pular números
                fig.update_layout(xaxis={'type': 'category'})
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Certifique-se de que a terceira coluna tem números válidos.")

except Exception as e:
    st.error(f"Erro: {e}")
    st.info("Dica: Se este é um novo App no Streamlit Cloud, você precisa colar o JSON nos Secrets dele também!")
