import os
import yfinance as yf
from src.utils.logger import info

def fetch_data(symbol='GC=F', period='2y', interval='1h'):  # Gold futures
    os.makedirs('data', exist_ok=True)
    df = yf.download(symbol, period=period, interval=interval)
    df.to_parquet('data/xau_raw.parquet')
    info(f'Fetched {len(df)} bars')
    return df