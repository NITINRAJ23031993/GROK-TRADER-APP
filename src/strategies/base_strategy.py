from abc import ABC, abstractmethod
import pandas as pd

class StrategyBase(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate +1 buy, -1 sell, 0 hold signals."""
        pass