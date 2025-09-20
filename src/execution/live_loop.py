import time
import os
import pandas as pd
from src.execution.mt5_connector import init_mt5
from src.strategies.ensemble import Ensemble
from src.execution.order_executor import execute_order
from src.risk.risk_manager import calc_lot, check_drawdown, calc_sl_tp
from src.utils.logger import info
from src.notifier import send_telegram
import yaml

def live_loop():
    with open('config/settings.yaml', 'r') as f:
        cfg = yaml.safe_load(f)
    if not init_mt5(mode='live'):
        raise RuntimeError('MT5 init failed')
    print('Starting LIVE loop')
    ens = Ensemble()
    # Assume balance from MT5; placeholder
    balance = mt5.account_info().balance
    peak_balance = balance
    open_trade = None
    retries = 0
    max_retries = 3

    while True:
        try:
            if not os.path.exists('data/features.parquet'):
                time.sleep(60)
                continue
            df = pd.read_parquet('data/features.parquet')
            sig = ens.generate_signals(df).iloc[-1]
            current_price = df['Close'].iloc[-1]
            atr = df['atr_14'].iloc[-1] if 'atr_14' in df else 0.5

            if check_drawdown(peak_balance, balance, cfg.get('risk', {}).get('max_dd', 5.0)):
                send_telegram('Drawdown limit reached - halting')
                break

            if sig != 0 and open_trade is None:
                side = 'buy' if sig == 1 else 'sell'
                stop_loss_pips = atr * 10
                lot = calc_lot(balance, cfg.get('risk', {}).get('pct', 1.0), stop_loss_pips, use_kelly=True)
                sl, tp = calc_sl_tp(current_price, side, atr)
                res = execute_order(side, lot, mode='live', sl=sl, tp=tp)
                info(f'Live {side} {lot} @ {current_price}, SL:{sl}, TP:{tp} - {res}')
                open_trade = res
                # In live, MT5 handles close; monitor pnl
                positions = mt5.positions_get(symbol=cfg['symbol'])
                if positions:
                    pnl = positions[0].profit
                    if pnl:  # Close logic if needed
                        balance += pnl
                        peak_balance = max(peak_balance, balance)
                        state = df[ens.features].iloc[-1].values
                        action = sig + 1
                        reward = pnl / balance
                        next_state = state  # Placeholder
                        ens.update_rl(state, action, reward, next_state)
                        open_trade = None
                        send_telegram(f'Live trade closed: PNL {pnl}')
            else:
                info('No signal or trade open')
            retries = 0
            time.sleep(60)
        except Exception as e:
            info(f'Live loop error: {e}')
            retries += 1
            if retries > max_retries:
                break
            time.sleep(60)
        except KeyboardInterrupt:
            break
    mt5.shutdown()