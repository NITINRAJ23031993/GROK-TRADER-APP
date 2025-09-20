import pandas as pd
import os
from src.utils.logger import info
import MetaTrader5 as mt5
import yaml
from datetime import datetime

class TradeLogger:
    def __init__(self, mode='paper', symbol='XAUUSD'):
        self.mode = mode
        self.symbol = symbol
        self.trades = []  # List of dicts for trades
        timestamp = datetime.now().strftime("%Y%m%d_%H_%M_%S")
        self.csv_path = f'data/trade_history_{timestamp}.csv'  # New timestamped file each run
        os.makedirs('data', exist_ok=True)
        # No loading from existing—new file per run

    def log_trade(self, side, price, sl, tp, open_time, close_time=None, pnl=None):
        trade = {
            'Side': side,
            'Price': price,
            'S/L': sl,
            'T/P': tp,
            'Open Time': open_time,
            'Close Time': close_time if close_time else '',
            'Profit': pnl if pnl is not None else ''
        }
        self.trades.append(trade)
        self._save_to_csv()
        info(f"Logged trade: {trade}")

    def _save_to_csv(self):
        df = pd.DataFrame(self.trades)
        df.to_csv(self.csv_path, index=False)

    def get_history(self, from_mt5=False):
        if from_mt5 and self.mode == 'live':
            if not mt5.initialize():
                info("MT5 not initialized for history")
                return pd.DataFrame(self.trades)
            history = mt5.history_deals_get(symbol=self.symbol)  # Fetch recent history
            mt5.shutdown()
            if history:
                # Parse MT5 history to match columns
                parsed_trades = []
                for deal in history:
                    parsed_trades.append({
                        'Side': 'buy' if deal.type == mt5.DEAL_TYPE_BUY else 'sell',
                        'Price': deal.price,
                        'S/L': deal.sl,
                        'T/P': deal.tp,
                        'Open Time': datetime.fromtimestamp(deal.time).strftime('%Y.%m.%d %H:%M:%S'),
                        'Close Time': datetime.fromtimestamp(deal.time_close).strftime('%Y.%m.%d %H:%M:%S') if deal.time_close else '',
                        'Profit': deal.profit
                    })
                return pd.DataFrame(parsed_trades)
        return pd.DataFrame(self.trades)

    def display_table(self):
        df = self.get_history(from_mt5=(self.mode == 'live'))
        print(df.to_string(index=False))  # Console table
        return df  # Return for GUI