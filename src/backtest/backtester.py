import pandas as pd
import numpy as np
from src.utils.logger import info

def backtest_strategy(df, signals, initial_balance=10000, commission=0.0001):
    df = df.copy()
    df['signal'] = signals
    df['position'] = df['signal'].shift(1).fillna(0)
    df['returns'] = df['Close'].pct_change()
    df['strategy_returns'] = df['position'] * df['returns'] - abs(df['position'].diff()) * commission
    equity = (1 + df['strategy_returns']).cumprod() * initial_balance
    trade_returns = df['strategy_returns'][abs(df['position']) > 0]
    info(f'Backtest: {len(trade_returns)} trades')
    return trade_returns