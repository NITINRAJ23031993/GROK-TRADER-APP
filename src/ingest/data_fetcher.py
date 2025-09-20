import os
import yfinance as yf
from src.utils.logger import info
try:
    import MetaTrader5 as mt5
except:
    mt5 = None

def fetch_data(symbol='GC=F', period='2y', interval='1h', use_mt5=False):
    os.makedirs('data', exist_ok=True)
    if use_mt5 and mt5:
        from src.execution.mt5_connector import init_mt5
        if init_mt5():
            timeframe = mt5.TIMEFRAME_H1 if interval == '1h' else mt5.TIMEFRAME_D1
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 100000)  # Last 100k bars
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'tick_volume': 'Volume'}, inplace=True)
            df.set_index('time', inplace=True)
            mt5.shutdown()
    else:
        df = yf.download(symbol, period=period, interval=interval)
    df.to_parquet('data/xau_raw.parquet')
    info(f'Fetched {len(df)} bars')
    return df