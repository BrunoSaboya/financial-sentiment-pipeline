import os
import yfinance as yf
import pandas as pd
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time

load_dotenv()

# Configurações da NewsAPI.org
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")  # Nova chave para newsapi.org
if not NEWSAPI_KEY:
    raise ValueError("Chave da NEWSAPI_KEY não encontrada. Verifique seu arquivo .env")

TICKER = "PETR4.SA"
SEARCH_TERM = "Petrobras"
END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=30)  # Reduzido para 30 dias para evitar problemas

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

def fetch_newsapi_news_fixed(api_key, query, start_date, end_date):
    """
    Busca notícias usando a NewsAPI.org com headers corretos.
    """
    print(f"Buscando notícias para '{query}' na NewsAPI.org...")
    
    # URL base da NewsAPI.org
    base_url = "https://newsapi.org/v2/everything"
    
    # Headers adequados para a API
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }
    
    articles = []
    current_date = start_date
    
    while current_date <= end_date:
        # Busca por dia para evitar limites da API
        date_str = current_date.strftime('%Y-%m-%d')
        
        print(f"Buscando notícias para {date_str}...")
        
        # Parâmetros da requisição
        params = {
            'q': query,
            'from': date_str,
            'to': date_str,
            'language': 'pt',  # Português
            'sortBy': 'publishedAt',
            'pageSize': 5,  # Reduzido para 5 artigos por dia
            'apiKey': api_key
        }
        
        try:
            # Faz a requisição com headers adequados
            response = requests.get(
                base_url, 
                params=params, 
                headers=headers,
                timeout=30  # Timeout de 30 segundos
            )
            
            # Verifica o status da resposta
            if response.status_code == 200:
                data = response.json()
                
                if data['status'] == 'ok':
                    day_articles = data.get('articles', [])
                    print(f"Encontradas {len(day_articles)} notícias para {date_str}")
                    
                    for article in day_articles:
                        articles.append({
                            'publishedAt': article.get('publishedAt', ''),
                            'title': article.get('title', ''),
                            'body': article.get('content', ''),  # NewsAPI usa 'content' em vez de 'body'
                            'url': article.get('url', ''),
                            'source': article.get('source', {}).get('name', ''),
                            'description': article.get('description', '')
                        })
                else:
                    print(f"Erro na API para {date_str}: {data.get('message', 'Erro desconhecido')}")
            elif response.status_code == 426:
                print(f"Erro 426 (Upgrade Required) para {date_str}. Tentando com headers diferentes...")
                # Tenta sem alguns headers
                response = requests.get(
                    base_url, 
                    params=params, 
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    if data['status'] == 'ok':
                        day_articles = data.get('articles', [])
                        print(f"Encontradas {len(day_articles)} notícias para {date_str} (segunda tentativa)")
                        for article in day_articles:
                            articles.append({
                                'publishedAt': article.get('publishedAt', ''),
                                'title': article.get('title', ''),
                                'body': article.get('content', ''),
                                'url': article.get('url', ''),
                                'source': article.get('source', {}).get('name', ''),
                                'description': article.get('description', '')
                            })
            else:
                print(f"Erro HTTP {response.status_code} para {date_str}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição para {date_str}: {e}")
        except Exception as e:
            print(f"Erro inesperado para {date_str}: {e}")
        
        # Pausa para evitar rate limiting
        time.sleep(1)  # Aumentado para 1 segundo entre requisições
        current_date += timedelta(days=1)
    
    if not articles:
        print("Nenhuma notícia foi encontrada na NewsAPI.org.")
        return None

    df = pd.DataFrame(articles)
    print(f"Total de notícias encontradas: {len(df)}")
    if len(df) > 0:
        print(f"Período das notícias: {df['publishedAt'].min()} a {df['publishedAt'].max()}")
        
        # Estatísticas por fonte
        if 'source' in df.columns:
            print("\nNotícias por fonte:")
            source_counts = df['source'].value_counts()
            for source, count in source_counts.head(10).items():
                print(f"  {source}: {count}")
    
    filename = f"{query.replace(' ', '_')}_news_newsapi_fixed_{END_DATE.strftime('%Y%m%d')}.csv"
    df.to_csv(os.path.join(RAW_DATA_PATH, filename), index=False)
    print(f"Notícias salvas em: {filename}")
    return df

def fetch_newsapi_headlines_fixed(api_key, query):
    """
    Busca headlines atuais da NewsAPI.org com headers corretos.
    """
    print(f"Buscando headlines atuais para '{query}' na NewsAPI.org...")
    
    # URL para top headlines
    base_url = "https://newsapi.org/v2/top-headlines"
    
    # Headers adequados
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }
    
    # Parâmetros da requisição
    params = {
        'q': query,
        'country': 'br',  # Brasil
        'category': 'business',  # Categoria negócios
        'pageSize': 10,  # Máximo de 10 artigos
        'apiKey': api_key
    }
    
    try:
        response = requests.get(
            base_url, 
            params=params, 
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data['status'] == 'ok':
                articles = data.get('articles', [])
                print(f"Encontradas {len(articles)} headlines atuais")
                
                headlines_data = []
                for article in articles:
                    headlines_data.append({
                        'publishedAt': article.get('publishedAt', ''),
                        'title': article.get('title', ''),
                        'body': article.get('content', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', ''),
                        'description': article.get('description', '')
                    })
                
                df = pd.DataFrame(headlines_data)
                filename = f"{query.replace(' ', '_')}_headlines_newsapi_fixed_{END_DATE.strftime('%Y%m%d')}.csv"
                df.to_csv(os.path.join(RAW_DATA_PATH, filename), index=False)
                print(f"Headlines salvas em: {filename}")
                return df
            else:
                print(f"Erro na API: {data.get('message', 'Erro desconhecido')}")
                return None
        else:
            print(f"Erro HTTP {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return None

# --- Execução Principal ---
if __name__ == "__main__":
    print("--- Iniciando Pipeline de Coleta de Dados (NewsAPI.org - Versão Corrigida) ---")
    print(f"Período de busca: {START_DATE.strftime('%Y-%m-%d')} a {END_DATE.strftime('%Y-%m-%d')}")
    
    # Coleta dados de ações
    fetch_stock_prices(TICKER, START_DATE, END_DATE)
    
    # Coleta notícias históricas
    fetch_newsapi_news_fixed(NEWSAPI_KEY, SEARCH_TERM, START_DATE, END_DATE)
    
    # Coleta headlines atuais
    fetch_newsapi_headlines_fixed(NEWSAPI_KEY, SEARCH_TERM)
    
    print("--- Pipeline de Coleta de Dados Finalizado ---") 