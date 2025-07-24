import os
import pandas as pd
from leia import SentimentIntensityAnalyzer 
from datetime import datetime

BASE_PATH = os.path.dirname(__file__)
RAW_DATA_PATH = os.path.join(BASE_PATH, '..', 'data', 'raw')
PROCESSED_DATA_PATH = os.path.join(BASE_PATH, '..', 'data', 'processed')
FINAL_DATA_PATH = os.path.join(BASE_PATH, '..', 'data', 'final')

os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
os.makedirs(FINAL_DATA_PATH, exist_ok=True)

TODAY_STR = datetime.now().strftime('%Y%m%d')

def clean_news_data(df):
    """Limpa e pré-processa os dados das notícias."""
    print("Limpando dados das notícias...")
    # Seleciona colunas relevantes
    df = df[['publishedAt', 'title', 'description', 'content']].copy()
    # Remove linhas com dados faltando no título ou conteúdo
    df.dropna(subset=['title', 'content'], inplace=True)
    # Converte 'publishedAt' para datetime e extrai apenas a data
    df['publishedAt'] = pd.to_datetime(df['publishedAt'])
    df['date'] = df['publishedAt'].dt.date
    return df

def analyze_sentiment(df):
    """Aplica análise de sentimento nos títulos das notícias."""
    print("Analisando sentimento...")
    analyzer = SentimentIntensityAnalyzer()
    # Calcula o score de sentimento para cada título
    df['sentiment_score'] = df['title'].apply(lambda title: analyzer.polarity_scores(title)['compound'])
    # Agrupa por data e calcula o score médio de sentimento do dia
    sentiment_by_date = df.groupby('date')['sentiment_score'].mean().reset_index()
    return sentiment_by_date

def process_stock_data(df):
    """Processa os dados de preços das ações."""
    print("Processando dados das ações...")
    df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
    # Converte 'Date' para datetime e extrai a data
    df['Date'] = pd.to_datetime(df['Date'])
    df['date'] = df['Date'].dt.date
    # Calcula a variação percentual diária do preço de fechamento
    df['price_change'] = df['Close'].pct_change()
    # Seleciona colunas relevantes
    df = df[['date', 'Close', 'price_change']]
    return df

# --- Execução Principal ---
if __name__ == "__main__":
    print("--- Iniciando Pipeline de Processamento de Dados ---")
    
    # Encontra os arquivos de dados mais recentes
    try:
        news_file = [f for f in os.listdir(RAW_DATA_PATH) if f.startswith('Petrobras_news') and f.endswith('.csv')][0]
        stock_file = [f for f in os.listdir(RAW_DATA_PATH) if f.startswith('PETR4.SA_prices') and f.endswith('.csv')][0]
    except IndexError:
        print("Arquivos de dados brutos não encontrados. Execute o data_collector.py primeiro.")
        exit()

    # Carrega os dados brutos
    news_df = pd.read_csv(os.path.join(RAW_DATA_PATH, news_file))
    colunas = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']
    stock_df = pd.read_csv(os.path.join(RAW_DATA_PATH, stock_file), header=2, names=colunas)

    # Processa os dados de notícias
    cleaned_news = clean_news_data(news_df)
    sentiment_data = analyze_sentiment(cleaned_news)
    
    # Salva os dados de sentimento processados
    sentiment_data.to_csv(os.path.join(PROCESSED_DATA_PATH, f'sentiment_scores_{TODAY_STR}.csv'), index=False)
    print("Dados de sentimento salvos.")

    # Processa os dados de ações
    processed_stock = process_stock_data(stock_df)
    processed_stock.to_csv(os.path.join(PROCESSED_DATA_PATH, f'processed_stocks_{TODAY_STR}.csv'), index=False)
    print("Dados de ações processados e salvos.")
    
    # Converte a coluna 'date' para o mesmo tipo antes do merge
    sentiment_data['date'] = pd.to_datetime(sentiment_data['date'])
    processed_stock['date'] = pd.to_datetime(processed_stock['date'])

    # Junta os dados de sentimento com os dados de ações
    final_df = pd.merge(processed_stock, sentiment_data, on='date', how='left')
    
    # Preenche dias sem notícias com sentimento neutro (0)
    final_df['sentiment_score'].fillna(0, inplace=True)
    # Remove linhas com valores nulos (geralmente a primeira linha do price_change)
    final_df.dropna(inplace=True)

    # Salva o dataset final
    final_filename = os.path.join(FINAL_DATA_PATH, f'final_dataset_{TODAY_STR}.csv')
    final_df.to_csv(final_filename, index=False)
    
    print(f"Dataset final criado e salvo em: {final_filename}")
    print("--- Pipeline de Processamento de Dados Finalizado ---")