import argparse
import threading
import time
from datetime import datetime, timedelta
from src.ingest.data_fetcher import fetch_data
from src.features.build_features import build_features
from src.models.train_ensemble import train_model
from src.models.daily_retrain import daily_retrain  # For scheduling
from src.backtest.backtester import backtest_strategy
from src.backtest.reporter import write_summary
from src.execution.paper_loop import paper_loop  # We'll create this as a function
from src.execution.live_loop import live_loop  # We'll create this as a function
import yaml

def main(mode='paper', duration=None):
    with open('config/settings.yaml', 'r') as f:
        config = yaml.safe_load(f)

    start_time = datetime.now()
    end_time = start_time + timedelta(hours=duration) if duration else None

    # Step 1-4: Setup (fetch, features, train, backtest)
    fetch_data()
    build_features()
    train_model()
    df = pd.read_parquet('data/features.parquet')
    from src.strategies.ensemble import Ensemble
    ens = Ensemble()
    signals = ens.generate_signals(df)
    returns = backtest_strategy(df, signals)
    stats = compute_metrics(returns)  # From metrics.py
    write_summary(stats, returns)

    # Step 5: Start daily retrain in thread
    retrain_thread = threading.Thread(target=daily_retrain_loop)
    retrain_thread.daemon = True
    retrain_thread.start()

    # Step 6: Start trading loop
    if mode == 'paper':
        paper_loop()
    else:
        live_loop()

    # Keep running until duration or interrupt
    while True:
        if end_time and datetime.now() > end_time:
            print("Duration reached, stopping.")
            break
        time.sleep(60)

def daily_retrain_loop():
    while True:
        daily_retrain()
        time.sleep(3600)  # Check hourly for schedule

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', default='paper', choices=['paper', 'live'])
    parser.add_argument('--duration', type=int, help='Hours to run (optional)')
    args = parser.parse_args()
    main(mode=args.mode, duration=args.duration)