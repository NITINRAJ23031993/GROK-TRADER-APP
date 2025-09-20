import schedule
import time
from src.utils.logger import info
from src.models.train_ensemble import train_model
from src.features.build_features import build_features
from src.backtest.backtester import backtest_strategy
from src.backtest.metrics import compute_metrics
from src.strategies.ensemble import Ensemble
from src.notifier import send_telegram
import pandas as pd

def daily_retrain():
    info('Daily retrain...')
    build_features()
    train_model()
    df = pd.read_parquet('data/features.parquet')
    ens = Ensemble()
    signals = ens.generate_signals(df)
    returns = backtest_strategy(df, signals)
    stats = compute_metrics(returns)
    if stats['win_rate'] > 0.7:
        joblib.dump(ens.model, f'models/model_{pd.Timestamp.now().strftime("%Y%m%d")}.pkl')
        # RL update from backtest
        for i in range(1, len(returns)):
            state = df[ens.features].iloc[i-1].values
            action = signals.iloc[i]
            reward = returns.iloc[i]
            next_state = df[ens.features].iloc[i].values
            if action != 0:
                ens.update_rl(state, action, reward, next_state)
        info(f'Updated: Win {stats["win_rate"]:.2%}')
        send_telegram(f'Updated: Win {stats["win_rate"]:.2%}')
    else:
        info('No update')

schedule.every().day.at("00:00").do(daily_retrain)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(60)