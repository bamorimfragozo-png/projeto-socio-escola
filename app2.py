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
    
    # Limpeza e normalização
    for col in df.columns:
        df[col] = df[col].astype(str).replace('nan', '')

    st.subheader("Visualizar e Editar Dados")
    df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    # 5. Botão para Salvar
    if st.button("💾 SALVAR ALTERAÇÕES NA PLANILHA"):
        try:
            conn.update(data=df_editado)
            st.success("✅ Dados atualizados com sucesso!")
            st.balloons()
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

    # 6. Gráfico de Barras Empilhadas
    if not df_editado.empty:
        st.divider()
        st.subheader("📊 Análise de Barras Empilhadas")
        
        df_grafico = df_editado.copy()
        cols = df_grafico.columns.tolist()
        
        if len(cols) >= 3:
            try:
                # Conversão da coluna de valores (Notas/Frequência)
                df_grafico[cols[2]] = pd.to_numeric(df_grafico[cols[2]].astype(str).str.replace(',', '.'), errors='coerce')
                df_grafico = df_grafico.dropna(subset=[cols[2]])

                if not df_grafico.empty:
                    # Criando o gráfico empilhado
                    # x = categoria principal (ex: Turma)
                    # y = valor (ex: Nota)
                    # color = o que divide a barra (ex: Aluno ou Disciplina)
                    fig = px.bar(
                        df_grafico, 
                        x=cols[1],           # Segunda coluna como base do eixo X (ex: Turma)
                        y=cols[2],           # Terceira coluna como valor (ex: Nota)
                        color=cols[0],       # Primeira coluna define o empilhamento (ex: Aluno)
                        title="Distribuição Empilhada por Categoria",
                        labels={cols[2]: "Total", cols[1]: "Categoria"},
                        template="plotly_white",
                        barmode='stack'      # Garante que as barras fiquem uma sobre a outra
                    )
                    
                    # Ajuste para mostrar o total no topo ou legendas claras
                    fig.update_layout(showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.caption(f"Legenda: O eixo X mostra **{cols[1]}**, empilhado por **{cols[0]}**.")
                else:
                    st.warning("Dados numéricos insuficientes para gerar o gráfico.")
                    
            except Exception as e:
                st.error(f"Erro técnico no gráfico: {e}")

except Exception as e:
    st.error(f"Erro ao conectar: {e}")
