# Enhanced Trader App

## Setup
1. Install deps: pip install pandas numpy lightgbm joblib yfinance ta-lib MetaTrader5 python-telegram-bot pyyaml torch schedule
2. Configure config/settings.yaml
3. Run initial: python src/features/build_features.py
4. Train: python src/models/train_ensemble.py
5. Paper test: python src/execution/paper_loop.py
6. Daily learn: python src/models/daily_retrain.py (background)
7. Live: python src/execution/live_loop.py (after paper success)

## Notes
- Targets 75-85% win rate in backtests; monitor live.
- Self-learns daily via ML retrain + RL from trades.
- Use paper for 1-2 weeks.