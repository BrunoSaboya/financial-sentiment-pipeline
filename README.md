# Financial Sentiment Pipeline

A comprehensive data pipeline that collects financial news and stock prices to perform sentiment analysis and find correlations between market sentiment and stock performance.

## 🎯 Project Overview

This project analyzes the relationship between news sentiment and stock price movements for Brazilian stocks (currently Petrobras - PETR4.SA). It collects financial news from reliable sources, performs sentiment analysis on news content, and correlates this data with stock price changes to identify potential patterns.

## ✨ Features

- **📰 News Collection**: Automated collection of financial news from NewsAPI.org
- **📊 Stock Data**: Historical stock price data from Yahoo Finance
- **🧠 Sentiment Analysis**: Keyword-based sentiment analysis on news content
- **📈 Correlation Analysis**: Dashboard to visualize sentiment vs stock price correlation
- **🔄 Automated Pipeline**: End-to-end data processing pipeline
- **📱 Interactive Dashboard**: Streamlit-based visualization interface

## 🏗️ Architecture

```
financial-sentiment-pipeline/
├── scripts/
│   ├── data_collector_newsapi_fixed.py    # News and stock data collection
│   └── data_processor_newsapi_fixed.py    # Data processing and sentiment analysis
├── data/
│   ├── raw/                               # Raw collected data
│   └── final/                             # Processed datasets
├── dashboard.py                           # Streamlit dashboard
└── requirements.txt                       # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- NewsAPI.org API key (free tier available)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/financial-sentiment-pipeline.git
   cd financial-sentiment-pipeline
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```env
   NEWSAPI_KEY=your_newsapi_key_here
   ```

### Usage

1. **Collect data**
   ```bash
   python scripts/data_collector_newsapi_fixed.py
   ```

2. **Process data**
   ```bash
   python scripts/data_processor_newsapi_fixed.py
   ```

3. **Launch dashboard**
   ```bash
   streamlit run dashboard.py
   ```

## 📊 Data Sources

### News Data
- **Source**: [NewsAPI.org](https://newsapi.org/)
- **Coverage**: Brazilian financial news
- **Period**: Last 30 days
- **Volume**: 3-5 articles per day
- **Languages**: Portuguese

### Stock Data
- **Source**: Yahoo Finance (via yfinance)
- **Symbol**: PETR4.SA (Petrobras)
- **Data**: OHLCV + price changes
- **Period**: Historical data

## 🧠 Sentiment Analysis

### Methodology
The system uses a **keyword-based approach** with domain-specific financial vocabulary:

**Positive Keywords**: alta, crescimento, lucro, positivo, investimento, petróleo, produção, etc.

**Negative Keywords**: queda, perda, crise, problema, vazamento, greve, etc.

### Scoring
- **Range**: -1.0 to +1.0
- **Neutral**: 0.0
- **Normalization**: Tanh function applied
- **Analysis**: Full text (title + description + body)

## 📈 Dashboard Features

- **📊 Correlation Analysis**: Sentiment vs price change correlation
- **📅 Time Series**: Sentiment and stock price over time
- **📋 Statistics**: Summary metrics and trends
- **🎯 Interactive Charts**: Plotly-based visualizations
- **📱 Responsive Design**: Works on desktop and mobile

## 🔧 Configuration

### Customizing the Analysis

Edit `scripts/data_collector_newsapi_fixed.py`:

```python
TICKER = "PETR4.SA"           # Stock symbol
SEARCH_TERM = "Petrobras"      # News search term
START_DATE = END_DATE - timedelta(days=30)  # Analysis period
```

### Adding New Stocks

1. Change `TICKER` to desired stock symbol
2. Update `SEARCH_TERM` to relevant company name
3. Run the collection pipeline

## 📁 Data Structure

### Raw Data Files
- `Petrobras_news_newsapi_fixed_YYYYMMDD.csv`: Collected news
- `PETR4.SA_prices_YYYYMMDD.csv`: Stock price data

### Processed Data Files
- `final_dataset_newsapi_fixed_YYYYMMDD.csv`: Combined dataset with sentiment scores

### Data Columns
```csv
date,Close,price_change,sentiment_score
2025-07-01,32.05,0.017,0.123
2025-07-02,31.89,-0.005,-0.045
```

## 🛠️ Technical Details

### Dependencies
- `pandas`: Data manipulation
- `yfinance`: Stock data collection
- `requests`: API communication
- `streamlit`: Dashboard interface
- `plotly`: Interactive visualizations
- `python-dotenv`: Environment management

### API Limits
- **NewsAPI.org**: 1000 requests/day (free tier)
- **Rate Limiting**: 1 second between requests
- **Data Retention**: 30 days historical data

## 📊 Results Example

| Date | Sentiment | Price Change | Correlation |
|------|-----------|--------------|-------------|
| 2025-07-01 | 0.123 | +1.7% | Positive |
| 2025-07-02 | -0.045 | -0.5% | Negative |
| 2025-07-03 | 0.197 | +2.3% | Positive |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [NewsAPI.org](https://newsapi.org/) for news data
- [Yahoo Finance](https://finance.yahoo.com/) for stock data
- [Streamlit](https://streamlit.io/) for dashboard framework
- [Plotly](https://plotly.com/) for interactive charts

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/financial-sentiment-pipeline/issues) page
2. Create a new issue with detailed description
3. Include error messages and system information

## 🔮 Future Enhancements

- [ ] Machine Learning-based sentiment analysis
- [ ] Multiple stock analysis
- [ ] Real-time data streaming
- [ ] Advanced correlation metrics
- [ ] Export functionality
- [ ] Email alerts for sentiment changes

---

**Made with ❤️ for financial analysis and data science**

*This project is for educational and research purposes. Always do your own research before making investment decisions.*
