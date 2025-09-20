import time
import os
import pandas as pd
from src.strategies.ensemble import Ensemble
from src.execution.order_executor import execute_order
from src.risk.risk_manager import calc_lot, check_drawdown, calc_sl_tp
from src.utils.logger import info
from src.notifier import send_telegram
from src.utils.trade_logger import TradeLogger  # Added import
import yaml
from datetime import datetime

def paper_loop():
    with open('config/settings.yaml', 'r') as f:
        cfg = yaml.safe_load(f)
    mode = 'paper'  # Fixed for this loop
    logger = TradeLogger(mode=mode)  # Initialize logger
    print('Starting PAPER loop')
    ens = Ensemble()
    balance = 10000.0
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
                res = execute_order(side, lot, mode=mode, sl=sl, tp=tp)
                open_time = str(datetime.now())  # Capture open time
                info(f'Paper {side} {lot} @ {current_price}, SL:{sl}, TP:{tp} - {res}')
                logger.log_trade(side, current_price, sl, tp, open_time)  # Log after execute
                open_trade = res
                open_trade['time'] = open_time  # Store for close
                # Sim close
                if len(df) > 5:
                    pnl = (df['Close'].iloc[-1] - df['Close'].iloc[-6]) * lot * 100 if side == 'buy' else (df['Close'].iloc[-6] - df['Close'].iloc[-1]) * lot * 100
                    balance += pnl
                    peak_balance = max(peak_balance, balance)
                    res['pnl'] = pnl
                    state = df[ens.features].iloc[-6].values
                    action = sig + 1
                    reward = pnl / balance
                    next_state = df[ens.features].iloc[-1].values
                    ens.update_rl(state, action, reward, next_state)
                    logger.log_trade(side, current_price, sl, tp, open_time=open_trade['time'], close_time=str(datetime.now()), pnl=pnl)  # Log on close
                    logger.display_table()  # Optional console view
                    open_trade = None
                    send_telegram(f'Paper trade closed: PNL {pnl}')
            else:
                info('No signal or trade open')
            retries = 0
            time.sleep(60)
        except Exception as e:
            info(f'Paper loop error: {e}')
            retries += 1
            if retries > max_retries:
                break
            time.sleep(60)
        except KeyboardInterrupt:
            break