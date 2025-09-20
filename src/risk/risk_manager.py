def calc_lot(balance, risk_pct, stop_loss_ticks, pip_value=0.1, use_kelly=False, win_rate=0.7, avg_win=1.5, avg_loss=1.0):
    risk_amount = balance * (risk_pct / 100.0)
    if stop_loss_ticks * pip_value == 0:
        return 0.01
    if use_kelly:
        kelly = (win_rate * avg_win - (1 - win_rate)) / avg_win
        lot = (risk_amount / (stop_loss_ticks * pip_value)) * max(0, min(kelly, 0.25))
    else:
        lot = risk_amount / (stop_loss_ticks * pip_value)
    return max(0.01, round(lot, 2))

def check_drawdown(peak, current, max_dd_pct):
    dd = (peak - current) / peak * 100.0
    return dd >= max_dd_pct

def calc_sl_tp(entry_price, side, atr, risk_reward=2.0):
    multiplier = 1.5
    sl_dist = atr * multiplier
    tp_dist = sl_dist * risk_reward
    if side == 'buy':
        sl = entry_price - sl_dist
        tp = entry_price + tp_dist
    else:
        sl = entry_price + sl_dist
        tp = entry_price - tp_dist
    return sl, tp