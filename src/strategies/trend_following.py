from src.strategies.base_strategy import StrategyBase

class TrendFollowing(StrategyBase):
    def __init__(self, short=8, long=21):
        super().__init__('trend_following')
        self.short = short
        self.long = long

    def generate_signals(self, df):
        s = df['Close'].ewm(span=self.short).mean()
        l = df['Close'].ewm(span=self.long).mean()
        sig = (s > l).astype(int) - (s < l).astype(int)
        return sig.fillna(0)