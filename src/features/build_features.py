import os
import pandas as pd
import numpy as np
import ta
from src.utils.logger import info
from src.ingest.data_fetcher import fetch_data
import requests
from bs4 import BeautifulSoup

def build_features(raw_path='data/xau_raw.parquet', out_path='data/features.parquet'):
    if not os.path.exists(raw_path):
        fetch_data()
    df = pd.read_parquet(raw_path)
    df['ret_1'] = df['Close'].pct_change(1)
    df['ret_5'] = df['Close'].pct_change(5)
    df['atr_14'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close'], window=14).average_true_range()
    df['rsi_14'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df['ema_8'] = ta.trend.EMAIndicator(df['Close'], window=8).ema_indicator()
    df['ema_21'] = ta.trend.EMAIndicator(df['Close'], window=21).ema_indicator()
    df['ema_55'] = ta.trend.EMAIndicator(df['Close'], window=55).ema_indicator()
    bb = ta.volatility.BollingerBands(df['Close'], window=20)
    df['boll_w'] = bb.bollinger_wband()
    df['vol_z'] = (df['Volume'].rolling(20).std() - df['Volume'].rolling(20).mean()) / df['Volume'].rolling(20).std()
    df['macd'] = ta.trend.MACD(df['Close']).macd()
    stoch = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'])
    df['stoch_k'] = stoch.stoch()
    # Added: VWAP
    df['vwap'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
    # Added: Sentiment
    try:
        response = requests.get("https://news.google.com/search?q=gold+price")
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = [h.text for h in soup.find_all('h3')[:5]]
        sentiment = sum(1 for h in headlines if 'up' in h.lower() or 'rise' in h.lower()) - sum(1 for h in headlines if 'down' in h.lower() or 'fall' in h.lower())
        df['sentiment'] = sentiment
    except:
        df['sentiment'] = 0
    df.index = pd.to_datetime(df.index)
    df['session_asia'] = (df.index.hour >= 0) & (df.index.hour < 8)
    df['session_london'] = (df.index.hour >= 8) & (df.index.hour < 16)
    df['session_ny'] = (df.index.hour >= 16) & (df.index.hour < 24)
    df.fillna(0, inplace=True)
    df.to_parquet(out_path)
    info(f'Features built: {len(df)} rows')