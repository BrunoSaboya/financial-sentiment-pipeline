import os
import pandas as pd
from datetime import datetime, timedelta

# --- Configurações ---
BASE_PATH = os.path.dirname(__file__)
RAW_DATA_PATH = os.path.join(BASE_PATH, '..', 'data', 'raw')
FINAL_DATA_PATH = os.path.join(BASE_PATH, '..', 'data', 'final')

os.makedirs(FINAL_DATA_PATH, exist_ok=True)
TODAY_STR = datetime.now().strftime('%Y%m%d')
SEARCH_TERM = "Petrobras"
TICKER = "PETR4.SA"

# --- Funções de Processamento ---

def clean_newsapi_data(df):
    """Limpa e pré-processa os dados das notícias da NewsAPI.org."""
    print("Limpando dados das notícias da NewsAPI.org...")
    
    # Remove linhas com dados faltantes
    df.dropna(subset=['body', 'publishedAt'], inplace=True)
    
    # Converte datas
    df['date'] = pd.to_datetime(df['publishedAt']).dt.date
    
    # Combina título e descrição com o corpo para análise mais completa
    df['full_text'] = df.apply(lambda row: 
        f"{row.get('title', '')} {row.get('description', '')} {row.get('body', '')}", 
        axis=1
    )
    
    print(f"Dados limpos: {len(df)} notícias")
    return df

def analyze_sentiment_keywords_newsapi(df):
    """Análise de sentimento baseada em palavras-chave para dados da NewsAPI.org."""
    print("Aplicando análise de sentimento baseada em palavras-chave...")
    
    # Palavras-chave positivas e negativas relacionadas a finanças e economia
    positive_keywords = [
        # Termos financeiros positivos
        'alta', 'subida', 'crescimento', 'lucro', 'ganho', 'positivo', 'melhora',
        'recuperação', 'forte', 'bom', 'excelente', 'ótimo', 'favorável', 'otimista',
        'avanço', 'progresso', 'sucesso', 'benefício', 'vantagem', 'superior',
        'elevado', 'ascendente', 'próspero', 'rentável', 'lucrativo', 'promissor',
        'expansão', 'desenvolvimento', 'inovação', 'tecnologia', 'investimento',
        'parceria', 'acordo', 'negociação', 'cooperação', 'integração',
        'sustentável', 'responsável', 'eficiente', 'produtivo', 'competitivo',
        'estratégico', 'planejamento', 'visão', 'futuro', 'oportunidade',
        'mercado', 'demanda', 'oferta', 'consumo', 'vendas', 'receita',
        'dividendo', 'retorno', 'performance', 'resultado', 'balanço',
        # Termos específicos da Petrobras
        'petróleo', 'óleo', 'gás', 'refinaria', 'exploração', 'produção',
        'reservas', 'pré-sal', 'bacia', 'poço', 'plataforma', 'navio',
        'exportação', 'importação', 'comercialização', 'distribuição'
    ]
    
    negative_keywords = [
        # Termos financeiros negativos
        'queda', 'perda', 'negativo', 'piora', 'crise', 'problema',
        'fraco', 'ruim', 'péssimo', 'desfavorável', 'pessimista', 'risco',
        'declínio', 'recessão', 'falência', 'prejuízo', 'déficit',
        'fracasso', 'insucesso', 'desvantagem', 'inferior', 'baixo', 'mínimo',
        'redução', 'diminuição', 'queda', 'decréscimo', 'contração',
        'instabilidade', 'volatilidade', 'incerteza', 'dúvida', 'preocupação',
        'ameaça', 'perigo', 'risco', 'vulnerabilidade', 'fragilidade',
        'dependência', 'limitação', 'obstáculo', 'barreira', 'impedimento',
        'conflito', 'disputa', 'guerra', 'sanção', 'tarifa', 'taxação',
        'inflação', 'desemprego', 'falta', 'escassez', 'carência',
        'dívida', 'endividamento', 'calote', 'inadimplência', 'falência',
        # Termos específicos negativos da Petrobras
        'vazamento', 'poluição', 'acidente', 'greve', 'paralisação',
        'investigação', 'multa', 'sanção', 'corrupção', 'escândalo',
        'prejuízo', 'perda', 'queda', 'redução', 'corte', 'demissão'
    ]
    
    def calculate_sentiment_score(text):
        if pd.isna(text) or not text:
            return 0
        
        text_lower = str(text).lower()
        
        # Conta palavras positivas e negativas
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        
        # Calcula o total de palavras para normalização
        total_words = len(text_lower.split())
        if total_words == 0:
            return 0
        
        # Calcula o score baseado na diferença entre palavras positivas e negativas
        score = (positive_count - negative_count) / max(total_words, 1)
        
        # Aplica uma função sigmóide para suavizar os valores extremos
        import math
        score = math.tanh(score * 3)  # Multiplica por 3 para dar mais peso
        
        return score
    
    # Aplica a análise ao texto completo
    df['sentiment_score'] = df['full_text'].apply(calculate_sentiment_score)
    
    # Agrupa por data e calcula a média
    sentiment_by_date = df.groupby('date')['sentiment_score'].mean().reset_index()
    
    print(f"Análise por palavras-chave concluída. {len(sentiment_by_date)} datas processadas.")
    print(f"Range de sentimento: {sentiment_by_date['sentiment_score'].min():.3f} a {sentiment_by_date['sentiment_score'].max():.3f}")
    print(f"Média de sentimento: {sentiment_by_date['sentiment_score'].mean():.3f}")
    
    # Mostra exemplos de análise
    print(f"\nExemplos de análise:")
    sample_news = df[['title', 'sentiment_score']].head(5)
    for idx, row in sample_news.iterrows():
        print(f"Título: {row['title'][:50]}...")
        print(f"Sentimento: {row['sentiment_score']:.3f}")
        print("-" * 50)
    
    return sentiment_by_date

def process_stock_data(df):
    """Processa os dados de preços das ações."""
    print("Processando dados das ações...")
    df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])
    df['date'] = df['Date'].dt.date
    df['price_change'] = df['Close'].pct_change()
    df = df[['date', 'Close', 'price_change']]
    return df

def create_complete_dataset(stock_df, sentiment_df):
    """Cria dataset completo com sentimentos para todo o período."""
    print("Criando dataset completo...")
    
    # Converte datas para datetime
    stock_df['date'] = pd.to_datetime(stock_df['date'])
    sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
    
    # Merge com left join para manter todas as datas de ações
    final_df = pd.merge(stock_df, sentiment_df, on='date', how='left')
    
    # Para datas sem notícias, usa sentimento neutro (0)
    final_df['sentiment_score'].fillna(0, inplace=True)
    
    # Remove linhas com dados faltantes
    final_df.dropna(inplace=True)
    
    print(f"Dataset completo criado com {len(final_df)} registros")
    print(f"Período: {final_df['date'].min()} a {final_df['date'].max()}")
    print(f"Datas com notícias: {len(sentiment_df)}")
    print(f"Datas sem notícias (sentimento neutro): {len(final_df) - len(sentiment_df)}")
    
    return final_df

# --- Execução Principal ---
if __name__ == "__main__":
    print("--- Iniciando Pipeline de Processamento de Dados (NewsAPI.org - Versão Corrigida) ---")
    
    try:
        # Busca arquivos mais recentes da NewsAPI.org corrigida
        news_files = [f for f in os.listdir(RAW_DATA_PATH) if f.startswith(f"{SEARCH_TERM}_news_newsapi_fixed")]
        stock_files = [f for f in os.listdir(RAW_DATA_PATH) if f.startswith(f"{TICKER}_prices")]
        
        if not news_files:
            print("Arquivos de notícias da NewsAPI.org corrigida não encontrados. Execute o data_collector_newsapi_fixed.py primeiro.")
            exit()
        if not stock_files:
            print("Arquivos de ações não encontrados. Execute o data_collector_newsapi_fixed.py primeiro.")
            exit()
            
        news_file = sorted(news_files)[-1]
        stock_file = sorted(stock_files)[-1]
        
    except IndexError:
        print("Arquivos de dados brutos não encontrados. Execute o data_collector_newsapi_fixed.py primeiro.")
        exit()

    print(f"Carregando {news_file} e {stock_file}...")
    news_df = pd.read_csv(os.path.join(RAW_DATA_PATH, news_file))
    colunas = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']
    stock_df = pd.read_csv(os.path.join(RAW_DATA_PATH, stock_file), header=2, names=colunas)

    cleaned_news = clean_newsapi_data(news_df)
    sentiment_data = analyze_sentiment_keywords_newsapi(cleaned_news)
    processed_stock = process_stock_data(stock_df)
    
    # Cria dataset completo
    final_df = create_complete_dataset(processed_stock, sentiment_data)

    final_filename = os.path.join(FINAL_DATA_PATH, f'final_dataset_newsapi_fixed_{TODAY_STR}.csv')
    final_df.to_csv(final_filename, index=False)
    
    print(f"Dataset completo criado e salvo em: {final_filename}")
    print("--- Pipeline de Processamento de Dados Finalizado ---") 