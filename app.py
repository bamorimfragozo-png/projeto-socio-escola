import streamlit as st
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
import pandas as pd

# 1. Configuração inicial da página
st.set_page_config(page_title="Dashboard Sócio-Pedagógico Completo", layout="wide")

st.title("🏫 Dashboard Sócio-Pedagógico")

# 2. Conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. Leitura dos dados ---
try:
    # Lê os dados da planilha
    df = conn.read(ttl=0)
    
    # Limpeza inicial: remove "nan" e trata como string para o editor
    for col in df.columns:
        df[col] = df[col].astype(str).replace('nan', '')

    st.subheader("Visualizar e Editar Dados")
    st.info("Altere os dados na tabela e clique no botão abaixo para salvar.")
    
    # --- 4. Tabela Interativa (Editor de Dados) ---
    df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    # 5. Botão para Salvar as alterações
    if st.button("💾 SALVAR ALTERAÇÕES NA PLANILHA"):
        try:
            conn.update(data=df_editado)
            st.cache_data.clear()
            st.success("✅ Sucesso! Os dados foram atualizados na sua planilha do Google.")
            st.balloons()
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

    # --- 6. Seção de Gráficos ---
    if not df_editado.empty:
        st.divider()
        st.subheader("📊 Análise Visual Completa")
        
        # Prepara uma cópia para os gráficos
        df_grafico = df_editado.copy()
        cols = df_grafico.columns.tolist()
        
        # Verifica se temos colunas suficientes (Nome, Turma, Valor)
        if len(cols) >= 3:
            try:
                # Tratamento Numérico: Converte a 3ª coluna para número (troca vírgula por ponto)
                df_grafico[cols[2]] = pd.to_numeric(
                    df_grafico[cols[2]].astype(str).str.replace(',', '.'), 
                    errors='coerce'
                )
                df_grafico = df_grafico.dropna(subset=[cols[2]])
                
                # Ordenação para consistência visual
                df_grafico = df_grafico.sort_values(by=[cols[1], cols[0]])

                if not df_grafico.empty:
                    
                    # --- GRÁFICO 1: BARRAS SIMPLES (Por Aluno) ---
                    st.write("### 📊 Desempenho por Aluno")
                    fig_barras = px.bar(
                        df_grafico, 
                        x=cols[0], 
                        y=cols[2], 
                        color=cols[1],
                        title="Notas Individuais (Agrupado por Turma)",
                        template="plotly_white",
                        category_orders={cols[0]: df_grafico[cols[0]].tolist()} 
                    )
                    st.plotly_chart(fig_barras, use_container_width=True)

                    st.divider()

                    # --- GRÁFICO 2: BARRAS EMPILHADAS (Por Turma) ---
                    st.write("### 📦 Distribuição Acumulada por Turma")
                    fig_stack = px.bar(
                        df_grafico, 
                        x=cols[1], 
                        y=cols[2], 
                        color=cols[0],
                        title="Soma de Notas Empilhadas por Turma",
                        template="plotly_white", 
                        barmode='stack'
                    )
                    fig_stack.update_traces(marker_line_width=1.5, marker_line_color="white")
                    st.plotly_chart(fig_stack, use_container_width=True)

                    st.divider()

                    # --- GRÁFICO 3: LINHAS (Evolução/Temporal) ---
                    st.write("### 📈 Evolução Temporal")
                    fig_linha = px.line(
                        df_grafico, 
                        x=cols[0], 
                        y=cols[2], 
                        color=cols[1], 
                        title="Tendência de Desempenho",
                        markers=True,
                        template="plotly_white"
                    )
                    fig_linha.update_traces(line=dict(width=3))
                    st.plotly_chart(fig_linha, use_container_width=True)

                    st.divider()

                    # --- GRÁFICO 4: PIZZA (Proporcional) ---
                    st.write("### 🍕 Distribuição Proporcional")
                    fig_pizza = px.pie(
                        df_grafico, 
                        values=cols[2], 
                        names=cols[1], 
                        title="Participação Percentual por Turma",
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig_pizza.update_traces(textinfo='percent+label', textposition='inside')
                    st.plotly_chart(fig_pizza, use_container_width=True)

                else:
                    st.warning("Insira valores numéricos válidos na terceira coluna para gerar os gráficos.")
            
            except Exception as e:
                st.error(f"Erro ao processar gráficos: {e}")
        else:
            st.warning("A planilha precisa de pelo menos 3 colunas (Ex: Nome, Turma, Nota).")

except Exception as e:
    st.error(f"Erro de conexão: {e}")
    st.info("Verifique os Secrets e se a planilha está compartilhada com o e-mail do robô.")
