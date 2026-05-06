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
                # Conversão de valores
                df_grafico[cols[2]] = pd.to_numeric(df_grafico[cols[2]].astype(str).str.replace(',', '.'), errors='coerce')
                df_grafico = df_grafico.dropna(subset=[cols[2]])

                if not df_grafico.empty:
                    
                    # --- GRÁFICO 1: LINHAS (Igual à primeira imagem) ---
                    # Mostra a evolução das notas/temperaturas
                    st.write("### 📈 Evolução Mensal/Temporal")
                    fig_linha = px.line(
                        df_grafico, 
                        x=cols[0], # Nome ou Data no eixo X
                        y=cols[2], # Valor no eixo Y
                        color=cols[1], # Linhas diferentes por Turma/Categoria
                        title="Desempenho ao Longo do Tempo",
                        markers=True, # Adiciona pontos na linha
                        template="plotly_white"
                    )
                    # Ajuste de cores para parecer com a imagem (opcional)
                    fig_linha.update_traces(line=dict(width=3))
                    st.plotly_chart(fig_linha, use_container_width=True)

                    st.divider()

                    # --- GRÁFICO 2: PIZZA (Igual à segunda imagem) ---
                    # Mostra a preferência ou distribuição proporcional
                    st.write("### 🍕 Distribuição Proporcional")
                    fig_pizza = px.pie(
                        df_grafico, 
                        values=cols[2], 
                        names=cols[1], # Categorias (Ex: Turma ou Gênero de Filme)
                        title="Distribuição Percentual por Categoria",
                        color_discrete_sequence=px.colors.qualitative.Pastel # Cores vibrantes
                    )
                    # Adiciona a porcentagem dentro da fatia igual na sua foto
                    fig_pizza.update_traces(textinfo='percent+label', textposition='inside')
                    st.plotly_chart(fig_pizza, use_container_width=True)

                else:
                    st.warning("Insira números válidos para gerar os gráficos.")
            except Exception as e:
                st.error(f"Erro técnico: {e}")

except Exception as e:
    st.error(f"Erro ao conectar com a planilha: {e}")
