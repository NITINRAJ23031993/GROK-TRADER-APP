import numpy as np

def compute_metrics(returns):
    r = returns.dropna()
    total_return = (1 + r).cumprod().iloc[-1] - 1 if len(r)>0 else 0.0
    ann_return = (1 + total_return) ** (252/len(r)) - 1 if len(r)>0 else 0.0
    sharpe = (r.mean() / (r.std()+1e-9)) * (252**0.5) if len(r)>1 else 0.0
    cum = (1 + r).cumprod()
    peak = cum.cummax()
    drawdown = (cum - peak) / peak
    maxdd = drawdown.min() if len(drawdown)>0 else 0.0
    win_rate = (r>0).sum() / (r!=0).sum() if (r!=0).sum()>0 else 0.0
    return {'total_return': float(total_return), 'annual_return': float(ann_return), 'sharpe': float(sharpe), 'max_drawdown': float(maxdd), 'win_rate': float(win_rate)}