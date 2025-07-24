import os
import requests
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")
if not API_KEY:
    raise ValueError("Chave da API não encontrada. Verifique seu arquivo .env")

TICKER = "PETR4.SA"
SEARCH_TERM = "Petrobras"
END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=30)


RAW_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
os.makedirs(RAW_DATA_PATH, exist_ok=True)

# --- Funções de Coleta ---

def fetch_stock_prices(ticker, start, end):
    """
    Busca dados históricos de preços de ações usando o yfinance.
    """
    print(f"Buscando preços das ações para {ticker} de {start.strftime('%Y-%m-%d')} a {end.strftime('%Y-%m-%d')}...")
    try:
        stock_data = yf.download(ticker, start=start, end=end, progress=False)
        if stock_data.empty:
            print(f"Nenhum dado encontrado para {ticker}.")
            return None
        # Salva os dados em um arquivo CSV
        filename = f"{ticker}_prices_{END_DATE.strftime('%Y%m%d')}.csv"
        stock_data.to_csv(os.path.join(RAW_DATA_PATH, filename))
        print(f"Dados de preços salvos em: {filename}")
        return stock_data
    except Exception as e:
        print(f"Erro ao buscar dados de ações: {e}")
        return None

def fetch_financial_news(api_key, query, start_date):
    """
    Busca notícias financeiras da News API.
    """
    print(f"Buscando notícias para '{query}'...")
    date_str = start_date.strftime('%Y-%m-%d')
    url = (f"https://newsapi.org/v2/everything?"
           f"q={query}"
           f"&from={date_str}"
           f"&sortBy=publishedAt"
           f"&language=pt"  # Busca por notícias em português
           f"&apiKey={api_key}")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lança um erro para respostas ruins (4xx ou 5xx)
        news_data = response.json()
        
        if news_data['totalResults'] == 0:
            print("Nenhuma notícia encontrada.")
            return None

        # Converte os artigos para um DataFrame do Pandas
        articles_df = pd.DataFrame(news_data['articles'])
        # Salva os dados em um arquivo CSV
        filename = f"{query.replace(' ', '_')}_news_{END_DATE.strftime('%Y%m%d')}.csv"
        articles_df.to_csv(os.path.join(RAW_DATA_PATH, filename), index=False)
        print(f"Notícias salvas em: {filename}")
        return articles_df
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar notícias: {e}")
        return None

# --- Execução Principal ---
if __name__ == "__main__":
    print("--- Iniciando Pipeline de Coleta de Dados ---")
    fetch_stock_prices(TICKER, START_DATE, END_DATE)
    fetch_financial_news(API_KEY, SEARCH_TERM, START_DATE)
    print("--- Pipeline de Coleta de Dados Finalizado ---")