import json, os
from src.backtest.metrics import compute_metrics

def write_summary(stats, returns, out='backtest_outputs/summary.json'):
    full_stats = {**stats, **compute_metrics(returns)}
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w') as f:
        json.dump(full_stats, f, indent=2)
    print('Wrote summary to', out)