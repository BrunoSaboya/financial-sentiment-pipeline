import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Análise de Sentimentos",
    page_icon="📊",
    layout="wide"
)

# --- Carregamento dos Dados ---
@st.cache_data
def load_data():
    """
    Carrega o dataset final mais recente da pasta data/final.
    Retorna um DataFrame vazio se nenhum arquivo for encontrado.
    """
    FINAL_DATA_PATH = os.path.join('data', 'final')
    try:
        # Procura por todos os arquivos que começam com 'final_dataset' e pega o mais recente.
        files = [f for f in os.listdir(FINAL_DATA_PATH) if f.startswith('final_dataset')]
        if not files:
            st.error("Nenhum arquivo de dados final encontrado. Execute os scripts de coleta e processamento primeiro.")
            return pd.DataFrame()
            
        latest_file = sorted(files, reverse=True)[0]
        file_path = os.path.join(FINAL_DATA_PATH, latest_file)
        
        # Carrega o CSV e converte a coluna 'date' para o tipo datetime.
        df = pd.read_csv(file_path, parse_dates=['date'])
        
        # Verifica se as colunas necessárias existem
        required_columns = ['date', 'Close', 'price_change', 'sentiment_score']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Colunas necessárias não encontradas: {missing_columns}")
            return pd.DataFrame()
            
        return df
        
    except (IndexError, FileNotFoundError) as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = load_data()

# O código do dashboard só é executado se os dados forem carregados com sucesso.
if not df.empty:
    # --- Título do Dashboard ---
    st.title('📊 Análise de Sentimentos do Mercado Financeiro para PETR4.SA')
    st.markdown("Este dashboard interativo apresenta a correlação entre o sentimento das notícias e o preço das ações da Petrobras.")

    # --- Barra Lateral (Sidebar) com Filtros ---
    st.sidebar.header("Filtros")
    min_date = df['date'].min().to_pydatetime()
    max_date = df['date'].max().to_pydatetime()
    
    # Cria um seletor de intervalo de datas na barra lateral.
    start_date, end_date = st.sidebar.date_input(
        "Selecione o Período",
        [min_date, max_date], # Valor padrão (todo o período)
        min_value=min_date,
        max_value=max_date
    )

    # Filtra o DataFrame com base no período selecionado pelo usuário.
    df_filtered = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

    # Verifica se há dados após a filtragem
    if df_filtered.empty:
        st.warning("Nenhum dado encontrado para o período selecionado.")
    else:
        # --- Métricas Principais ---
        st.header("Métricas Principais no Período Selecionado")
        col1, col2, col3 = st.columns(3)
        
        # Calcula as métricas com base nos dados filtrados.
        latest_price = df_filtered['Close'].iloc[-1]
        avg_sentiment = df_filtered['sentiment_score'].mean()
        price_change_sum = df_filtered['price_change'].sum() * 100

        # Exibe as métricas usando o componente st.metric.
        col1.metric("Último Preço de Fechamento", f"R$ {latest_price:.2f}")
        col2.metric("Sentimento Médio", f"{avg_sentiment:.3f}")
        col3.metric("Variação Acumulada no Período", f"{price_change_sum:.2f}%")

        # --- Gráficos Interativos ---
        st.header("Visualizações")

        # Gráfico de Preço de Fechamento usando Plotly Express
        try:
            fig_price = px.line(df_filtered, x='date', y='Close', title='Preço de Fechamento (PETR4.SA)',
                            labels={'date': 'Data', 'Close': 'Preço (R$)'})
            fig_price.update_traces(line_color='#007bff') # Define a cor da linha
            st.plotly_chart(fig_price, use_container_width=True) # Exibe o gráfico
        except Exception as e:
            st.error(f"Erro ao criar gráfico de preços: {e}")

        # Gráfico de Sentimento
        try:
            fig_sentiment = px.bar(df_filtered, x='date', y='sentiment_score', title='Score de Sentimento Diário',
                               labels={'date': 'Data', 'sentiment_score': 'Score de Sentimento'})
            # Pinta as barras de verde (positivo) ou vermelho (negativo).
            fig_sentiment.update_traces(marker_color=['#28a745' if s >= 0 else '#dc3545' for s in df_filtered['sentiment_score']])
            st.plotly_chart(fig_sentiment, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao criar gráfico de sentimento: {e}")
        
        # --- Análise de Correlação ---
        st.header("Análise de Correlação")
        st.markdown("""
        A análise abaixo explora se o sentimento das notícias de um dia (D-1) tem correlação com a variação de preço no dia seguinte (D). 
        Um valor de correlação próximo de 1 indica uma forte correlação positiva, enquanto um valor próximo de -1 indica uma forte correlação negativa.
        """)
        
        # Cria uma nova coluna com o sentimento do dia anterior usando .shift(1)
        df_filtered['sentiment_shifted'] = df_filtered['sentiment_score'].shift(1)
        
        # Remove linhas com valores NaN para a correlação
        df_corr = df_filtered.dropna(subset=['sentiment_shifted', 'price_change'])
        
        if len(df_corr) > 1:
            # Calcula a correlação de Pearson entre as duas colunas.
            correlation = df_corr[['sentiment_shifted', 'price_change']].corr().iloc[0, 1]
            
            st.metric("Correlação (Sentimento D-1 vs. Variação de Preço D)", f"{correlation:.4f}")
            
            # Gráfico de Dispersão (Scatter Plot) para visualizar a correlação.
            try:
                fig_corr = px.scatter(df_corr, x='sentiment_shifted', y='price_change', 
                                  title='Correlação: Sentimento do Dia Anterior vs. Variação de Preço',
                                  labels={'sentiment_shifted': 'Score de Sentimento (D-1)', 'price_change': 'Variação Percentual do Preço (D)'},
                                  trendline="ols", trendline_color_override="red")
                st.plotly_chart(fig_corr, use_container_width=True)
            except Exception as e:
                st.warning(f"Não foi possível criar a linha de tendência: {e}")
                # Fallback: gráfico sem trendline
                fig_corr = px.scatter(df_corr, x='sentiment_shifted', y='price_change', 
                                  title='Correlação: Sentimento do Dia Anterior vs. Variação de Preço',
                                  labels={'sentiment_shifted': 'Score de Sentimento (D-1)', 'price_change': 'Variação Percentual do Preço (D)'})
                st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.warning("Dados insuficientes para calcular correlação. São necessários pelo menos 2 pontos de dados.")

        # --- Tabela de Dados ---
        st.header("Dados Detalhados")
        # Exibe o DataFrame filtrado com formatação para melhor leitura.
        try:
            st.dataframe(df_filtered.style.format({
                "Close": "R$ {:.2f}",
                "price_change": "{:.2%}",
                "sentiment_score": "{:.3f}"
            }))
        except Exception as e:
            st.error(f"Erro ao exibir tabela de dados: {e}")
            st.dataframe(df_filtered)
else:
    st.error("""
    ## ❌ Dados não encontrados
    
    Para usar este dashboard, você precisa:
    
    1. **Executar o coletor de dados**: `python scripts/data_collector.py`
    2. **Executar o processador de dados**: `python scripts/data_processor.py`
    3. **Verificar se os arquivos foram criados** na pasta `data/final/`
    
    ### Alternativas:
    
    - **Versão alternativa do processador**: `python scripts/data_processor_alternative.py`
    - **Diagnóstico de dados**: `python diagnose_sentiment.py`
    """)