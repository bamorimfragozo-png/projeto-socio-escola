import streamlit as st
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
import pandas as pd
import time

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
    st.info("💡 Dica: Use 'TAB' para pular para a próxima coluna e 'ENTER' para a linha de baixo.")
    
    # --- 4. Tabela Interativa (Editor de Dados) ---
    # O st.data_editor permite navegação por TAB por padrão
    df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    # 5. Botão para Salvar as alterações
    if st.button("💾 SALVAR ALTERAÇÕES NA PLANILHA"):
        try:
            # Envia para o Google Sheets
            conn.update(data=df_editado)
            st.cache_data.clear()
            st.balloons()
            st.success("✅ Dados salvos com sucesso! Atualizando...")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

    # --- 6. Seção de Gráficos ---
    if not df_editado.empty:
        st.divider()
        st.subheader("📊 Análise Visual Completa")
        
        df_grafico = df_editado.copy()
        cols = df_grafico.columns.tolist()
        
        if len(cols) >= 3:
            try:
                # Tratamento Numérico
                df_grafico[cols[2]] = pd.to_numeric(
                    df_grafico[cols[2]].astype(str).str.replace(',', '.'), 
                    errors='coerce'
                )
                df_grafico = df_grafico.dropna(subset=[cols[2]])
                
                # --- ORDENAÇÃO ALFABÉTICA POR ANO E DEPOIS POR NOME ---
                df_grafico = df_grafico.sort_values(by=[cols[1], cols[0]])

                # --- PADRONIZAÇÃO DE CORES POR TURMA ---
                # Definimos cores fixas para as turmas para que nunca mudem
                turmas_unicas = sorted(df_grafico[cols[1]].unique())
                paleta_turmas = px.colors.qualitative.Set1 # Paleta firme e clara
                mapa_cores_turma = {turma: paleta_turmas[i % len(paleta_turmas)] for i, turma in enumerate(turmas_unicas)}

                # Paleta Automática para Alunos (usada no gráfico empilhado e pizza)
                paleta_alunos = px.colors.qualitative.Prism

                if not df_grafico.empty:
                    
                    # --- GRÁFICO 1: BARRAS SIMPLES (Cores por Turma - Padronizado) ---
                    st.write("### 📊 Desempenho Individual (Ordenado por Ano/Nome)")
                    fig_barras = px.bar(
                        df_grafico, 
                        x=cols[0], 
                        y=cols[2], 
                        color=cols[1],
                        color_discrete_map=mapa_cores_turma, # Usa o mapa fixo
                        title="Notas por Aluno",
                        template="plotly_white",
                        # Garante que a ordem no eixo X siga a ordenação do DataFrame (Ano -> Nome)
                        category_orders={cols[0]: df_grafico[cols[0]].tolist()}
                    )
                    st.plotly_chart(fig_barras, use_container_width=True)

                    st.divider()

                    # --- GRÁFICO 2: BARRAS EMPILHADAS (Paleta Automática de Alunos) ---
                    st.write("### 📦 Distribuição Acumulada por Turma")
                    fig_stack = px.bar(
                        df_grafico, 
                        x=cols[1], 
                        y=cols[2], 
                        color=cols[0],
                        color_discrete_sequence=paleta_alunos, # Paleta automática
                        title="Soma de Notas por Ano",
                        template="plotly_white", 
                        barmode='stack'
                    )
                    fig_stack.update_traces(marker_line_width=1.5, marker_line_color="white")
                    st.plotly_chart(fig_stack, use_container_width=True)

                    st.divider()

                    # --- GRÁFICO 3: LINHAS (Cores por Turma - Padronizado) ---
                    st.write("### 📈 Evolução por Turma")
                    fig_linha = px.line(
                        df_grafico, 
                        x=cols[0], 
                        y=cols[2], 
                        color=cols[1],
                        color_discrete_map=mapa_cores_turma, # Mesmo mapa de cores
                        title="Tendência de Notas",
                        markers=True,
                        template="plotly_white"
                    )
                    fig_linha.update_traces(line=dict(width=3))
                    st.plotly_chart(fig_linha, use_container_width=True)

                    st.divider()

                    # --- GRÁFICO 4: PIZZA (Paleta Automática) ---
                    st.write("### 🍕 Distribuição Proporcional")
                    fig_pizza = px.pie(
                        df_grafico, 
                        values=cols[2], 
                        names=cols[1], 
                        title="Participação de cada Ano no Resultado Total",
                        color=cols[1],
                        color_discrete_map=mapa_cores_turma # Mantém a cor do ano aqui também
                    )
                    fig_pizza.update_traces(textinfo='percent+label', textposition='inside')
                    st.plotly_chart(fig_pizza, use_container_width=True)

                else:
                    st.warning("Insira valores numéricos válidos para gerar os gráficos.")
            
            except Exception as e:
                st.error(f"Erro ao processar gráficos: {e}")
        else:
            st.warning("A planilha precisa de pelo menos 3 colunas (Ex: Nome, Turma, Nota).")

except Exception as e:
    st.error(f"Erro de conexão: {e}")
    st.info("Verifique os Secrets e o compartilhamento da planilha.")
