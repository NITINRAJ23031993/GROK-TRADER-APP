from src.strategies.base_strategy import StrategyBase
import numpy as np
import pandas as pd

class MeanReversion(StrategyBase):
    def __init__(self, window=20, threshold=2.0):
        super().__init__('mean_reversion')
        self.window = window
        self.threshold = threshold

    def generate_signals(self, df):
        mean = df['Close'].rolling(self.window).mean()
        std = df['Close'].rolling(self.window).std()
        zscore = (df['Close'] - mean) / std
        sig = np.where(zscore < -self.threshold, 1, np.where(zscore > self.threshold, -1, 0))
        return pd.Series(sig, index=df.index).fillna(0)