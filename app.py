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
        
        df_grafico = df_editado.copy()
        cols = df_grafico.columns.tolist()
        
        if len(cols) >= 3:
            try:
                import pandas as pd 
                
                # Conversão de Notas para números
                df_grafico[cols[2]] = pd.to_numeric(df_grafico[cols[2]].astype(str).str.replace(',', '.'), errors='coerce')
                df_grafico = df_grafico.dropna(subset=[cols[2]])
                
                # Ordenação para o primeiro gráfico
                df_grafico = df_grafico.sort_values(by=[cols[1], cols[0]])

                # --- GRÁFICO 1: BARRAS LADO A LADO ---
                fig1 = px.bar(
                    df_grafico, 
                    x=cols[0], 
                    y=cols[2], 
                    color=cols[1],
                    title="Desempenho Individual por Aluno",
                    template="plotly_white",
                    labels={cols[0]: "Nome", cols[2]: "Nota", cols[1]: "Turma"},
                    category_orders={cols[0]: df_grafico[cols[0]].tolist()} 
                )
                fig1.update_yaxes(range=[0, 10])
                st.plotly_chart(fig1, use_container_width=True)

                # --- AGORA A PORRA DO GRÁFICO EMPILHADO (GRÁFICO 2) ---
                st.write("---")
                st.subheader("📊 Distribuição Acumulada por Turma")
                
                fig2 = px.bar(
                    df_grafico, 
                    x=cols[1],           # Eixo X é a TURMA (1 ano, 2 ano...)
                    y=cols[2],           # Eixo Y é a NOTA
                    color=cols[0],       # CADA COR É UM ALUNO DIFERENTE
                    title="Análise Empilhada (Soma de Notas por Turma)",
                    template="plotly_white",
                    barmode='stack',     # ISSO AQUI FORÇA O EMPILHAMENTO
                    labels={cols[1]: "Turma", cols[2]: "Nota Acumulada", cols[0]: "Aluno"}
                )
                
                # Ajuste visual para separar as fatias da barra
                fig2.update_traces(marker_line_width=1.5, marker_line_color="white")
                fig2.update_layout(xaxis={'type': 'category'})
                
                st.plotly_chart(fig2, use_container_width=True)

            except Exception as e:
                st.error(f"Erro técnico no gráfico: {e}")

except Exception as e:
    st.error(f"Erro ao conectar com a planilha: {e}")
    st.info("Verifique se os Secrets estão configurados corretamente no Streamlit Cloud.")
