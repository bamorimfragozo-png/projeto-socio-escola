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
            import time  # Necessário para os balões aparecerem
            
            # 1. Envia para o Google Sheets
            conn.update(data=df_editado)
            
            # 2. Limpa o cache
            st.cache_data.clear()
            
            # 3. EXIBE A FESTA (Balões e Sucesso)
            st.balloons()
            st.success("✅ O dado foi enviado para o Google! Atualizando dashboard...")
            
            # 4. ESPERA 2 SEGUNDOS (Se não o rerun corta os balões)
            time.sleep(2)
            
            # 5. Agora sim, reinicia
            st.rerun()
            
        except Exception as e:
            st.error(f"A PORRA DO ERRO FOI: {e}")

    # --- 6. Seção de Gráficos ---
    if not df_editado.empty:
        st.divider()
        st.subheader("📊 Análise Visual Completa")
        
        df_grafico = df_editado.copy()
        cols = df_grafico.columns.tolist()
        
        if len(cols) >= 3:
            try:
                # 1. Tratamento Numérico
                df_grafico[cols[2]] = pd.to_numeric(
                    df_grafico[cols[2]].astype(str).str.replace(',', '.'), 
                    errors='coerce'
                )
                df_grafico = df_grafico.dropna(subset=[cols[2]])
                
                # --- NOVO: ORDENAÇÃO ALFABÉTICA POR TURMA E NOME ---
                # Isso garante: 1º Ano (Ana, Bianca), 2º Ano (Bruno, Caio)...
                df_grafico = df_grafico.sort_values(by=[cols[1], cols[0]])

                # --- NOVO: PADRONIZAÇÃO DE CORES POR ALUNO ---
                # Criamos uma lista de cores fixas para cada nome único
                nomes_unicos = sorted(df_grafico[cols[0]].unique())
                # Exemplo: Ana=Azul Escuro, Bianca=Vermelho, etc.
                # Você pode trocar 'Plotly' por outras paletas como 'Dark24' ou 'Alphabet'
                mapa_cores = {nome: cor for nome, cor in zip(nomes_unicos, px.colors.qualitative.Dark24)}
                
                # Se quiser forçar a Ana a ser Azul Escuro especificamente:
                if "Ana" in mapa_cores:
                    mapa_cores["Ana"] = "darkblue"

                if not df_grafico.empty:
                    
                    # --- GRÁFICO 1: BARRAS SIMPLES ---
                    st.write("### 📊 Desempenho por Aluno")
                    fig_barras = px.bar(
                        df_grafico, 
                        x=cols[0], 
                        y=cols[2], 
                        color=cols[0], # Colorir por NOME para usar o mapa de cores
                        color_discrete_map=mapa_cores, # APLICA AS CORES FIXAS
                        title="Notas Individuais (Ordem Alfabética por Turma)",
                        template="plotly_white"
                    )
                    st.plotly_chart(fig_barras, use_container_width=True)

                    st.divider()

                    # --- GRÁFICO 2: BARRAS EMPILHADAS (PERCENTUAL 100%) ---
                    st.write("### 📦 Participação por Turma (100%)")
                    fig_stack = px.bar(
                        df_grafico, 
                        x=cols[1], 
                        y=cols[2], 
                        color=cols[0],
                        color_discrete_map=mapa_cores, # MESMA COR AQUI
                        title="Contribuição de cada Aluno no total da Turma",
                        template="plotly_white", 
                        barmode='stack',
                        barnorm='percent' # Mostra 100% para comparar turmas de tamanhos diferentes
                    )
                    fig_stack.update_traces(
                        marker_line_width=1.5, 
                        marker_line_color="white",
                        hovertemplate="<b>Aluno:</b> %{fullData.name}<br><b>Percentual:</b> %{y:.1f}%<extra></extra>"
                    )
                    st.plotly_chart(fig_stack, use_container_width=True)

                    st.divider()

                    # --- GRÁFICO 3: LINHAS (Evolução) ---
                    st.write("### 📈 Evolução Temporal")
                    fig_linha = px.line(
                        df_grafico, 
                        x=cols[0], 
                        y=cols[2], 
                        color=cols[0], # Linha por NOME
                        color_discrete_map=mapa_cores, # MESMA COR AQUI
                        title="Tendência de Desempenho Individual",
                        markers=True,
                        template="plotly_white"
                    )
                    fig_linha.update_traces(line=dict(width=3))
                    st.plotly_chart(fig_linha, use_container_width=True)

                    st.divider()

                    # --- GRÁFICO 4: PIZZA ---
                    st.write("### 🍕 Distribuição de Notas da Escola")
                    fig_pizza = px.pie(
                        df_grafico, 
                        values=cols[2], 
                        names=cols[0], # Pizza por NOME
                        color=cols[0],
                        color_discrete_map=mapa_cores, # MESMA COR AQUI
                        title="Quem mais contribui para a média geral",
                    )
                    fig_pizza.update_traces(textinfo='percent+label', textposition='inside')
                    st.plotly_chart(fig_pizza, use_container_width=True)

            except Exception as e:
                st.error(f"Erro ao processar gráficos: {e}")
        else:
            st.warning("A planilha precisa de pelo menos 3 colunas (Ex: Nome, Turma, Nota).")

except Exception as e:
    st.error(f"Erro de conexão: {e}")
    st.info("Verifique os Secrets e se a planilha está compartilhada com o e-mail do robô.")
