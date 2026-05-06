import streamlit as st
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
import pandas as pd
import time

# 1. Configuração inicial da página
st.set_page_config(page_title="Dashboard Sócio-Pedagógico Completo", layout="wide")
st.title("Dashboard")

# 2. Conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Leitura dos dados
try:
    # Lê os dados da planilha
    df = conn.read(ttl=0)
    # Limpeza inicial: remove "nan" e trata como string para o editor
    for col in df.columns:
        df[col] = df[col].astype(str).replace('nan', '')
    st.subheader("Visualizar e Editar Dados")
    
    # 4. Tabela Interativa (Editor de Dados)
    df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    # 5. Botão para Salvar as alterações
    if st.button("SALVAR ALTERAÇÕES NA PLANILHA"):
        try:
            # Envia para o Google Sheets
            conn.update(data=df_editado)
            st.cache_data.clear()
            st.balloons()
            st.success("Dados salvos com sucesso! Atualizando...")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

    # 6. Seção de Gráficos
    if not df_editado.empty:
        st.divider()
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
                # ORDENAÇÃO ALFABÉTICA POR ANO E DEPOIS POR NOME 
                df_grafico = df_grafico.sort_values(by=[cols[1], cols[0]])
                ordem_turmas = sorted(df_grafico[cols[1]].unique())
                # PADRONIZAÇÃO DE CORES 
                turmas_unicas = sorted(df_grafico[cols[1]].unique())
                paleta_turmas = px.colors.qualitative.Set1 
                mapa_cores_turma = {turma: paleta_turmas[i % len(paleta_turmas)] for i, turma in enumerate(turmas_unicas)}
                # Paleta Automática para Alunos
                paleta_alunos = px.colors.qualitative.Prism
                if not df_grafico.empty:
                    # GRÁFICO 1: BARRAS SIMPLES
                    st.write("### Desempenho Individual")
                    fig_barras = px.bar(
                        df_grafico, 
                        x=cols[0], 
                        y=cols[2], 
                        color=cols[1],
                        color_discrete_map=mapa_cores_turma,
                        title="Notas por Aluno",
                        template="plotly_white",
                        category_orders={cols[0]: df_grafico[cols[0]].tolist()}
                    )
                    st.plotly_chart(fig_barras, use_container_width=True)
                    st.divider()

                    #  GRÁFICO 2: BARRAS EMPILHADAS 
                    st.write("### Distribuição Acumulada por Turma")
                    fig_stack = px.bar(
                        df_grafico, 
                        x=cols[1], 
                        y=cols[2], 
                        color=cols[0],
                        color_discrete_sequence=paleta_alunos,
                        title="Soma de Notas por Ano",
                        template="plotly_white", 
                        barmode='stack'
                    )
                    fig_stack.update_traces(marker_line_width=1.5, marker_line_color="white")
                    st.plotly_chart(fig_stack, use_container_width=True)
                    st.divider()

                    #  GRÁFICO 3: LINHAS 
                    st.write("### Evolução por Turma")
                    fig_linha = px.line(
                        df_grafico, 
                        x=cols[0], 
                        y=cols[2], 
                        color=cols[1],
                        color_discrete_map=mapa_cores_turma,
                        title="Tendência de Notas",
                        markers=True,
                        template="plotly_white",
                    )
                    fig_linha.update_traces(line=dict(width=3))
                    st.plotly_chart(fig_linha, use_container_width=True)
                    st.divider()

                    #  GRÁFICO 4: PIZZA 
                    st.write("### Distribuição Proporcional")
                    fig_pizza = px.pie(
                        df_grafico, 
                        values=cols[2], 
                        names=cols[1], 
                        title="Participação de cada Ano no Resultado Total",
                        color=cols[1],
                        color_discrete_map=mapa_cores_turma,
                        category_orders={cols[1]: ordem_turmas}
                    )
                    fig_pizza.update_traces(textinfo='percent+label', textposition='inside')
                    st.plotly_chart(fig_pizza, use_container_width=True)
                    st.divider()

                    #  GRÁFICO 5: DISPERSÃO
                    st.write("### Gráfico de Bolhas: Desempenho por Aluno")
                    fig_dispersao = px.scatter(
                        df_grafico, 
                        x=cols[0],           # Nome do Aluno
                        y=cols[2],           # Nota
                        color=cols[0],       # Cor por NOME
                        size=cols[2],        # Tamanho pela nota
                        color_discrete_sequence=paleta_alunos, # Mesma paleta do gráfico 2
                        title="Validação Individual",
                        template="plotly_white"
                    )
                    fig_dispersao.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
                    st.plotly_chart(fig_dispersao, use_container_width=True)
                    
                else:
                    st.warning("Insira valores numéricos válidos na terceira coluna para gerar os gráficos.")
            
            except Exception as e:
                st.error(f"Erro ao processar gráficos: {e}")
        else:
            st.warning("A planilha precisa de pelo menos 3 colunas (Ex: Nome, Turma, Nota).")

except Exception as e:
    st.error(f"Erro de conexão: {e}")
    st.info("Verifique os Secrets e o compartilhamento da planilha.")
