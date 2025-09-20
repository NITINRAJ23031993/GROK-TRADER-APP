import argparse
from src.ingest.data_fetcher import fetch_historical_data  # Assuming you implement this
from src.features.build_features import build_features
from src.models.train_ensemble import train_ensemble_model
from src.models.daily_retrain import retrain_model
from src.backtest.backtester import run_backtest
from src.execution.live_loop import start_live_trading
from src.execution.mt5_connector import initialize_mt5
import config.settings as settings  # If settings.yaml is populated

def main(mode='paper', symbol='EURUSD', timeframe='1h', train=True):
    # Step 1: Ingest historical data
    data = fetch_historical_data(symbol, timeframe)  # Implement in data_fetcher.py

    # Step 2: Build features
    featured_data = build_features(data)

    # Step 3: Train or retrain model
    if train:
        model = train_ensemble_model(featured_data)
    else:
        model = retrain_model(featured_data)  # Daily retrain

    # Step 4: Backtest
    backtest_results = run_backtest(model, featured_data)
    print("Backtest results:", backtest_results)

    # Step 5: Execution
    initialize_mt5(mode)  # Connect to MT5 in paper or live
    start_live_trading(model, symbol, timeframe)  # Runs the loop

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', default='paper', choices=['paper', 'live'], help='Trading mode')
    parser.add_argument('--symbol', default='EURUSD', help='Trading symbol')
    parser.add_argument('--timeframe', default='1h', help='Timeframe for data')
    parser.add_argument('--no-train', action='store_false', dest='train', help='Skip initial training')
    args = parser.parse_args()
    main(mode=args.mode, symbol=args.symbol, timeframe=args.timeframe, train=args.train)