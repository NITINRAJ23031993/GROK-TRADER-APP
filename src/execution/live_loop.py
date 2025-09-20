import time
import os
import pandas as pd
from src.execution.mt5_connector import init_mt5
from src.strategies.ensemble import Ensemble
from src.execution.order_executor import execute_order
from src.risk.risk_manager import calc_lot, check_drawdown, calc_sl_tp
from src.utils.logger import info
from src.notifier import send_telegram
from src.utils.trade_logger import TradeLogger  # Added import
import yaml
from datetime import datetime
import MetaTrader5 as mt5

def live_loop():
    with open('config/settings.yaml', 'r') as f:
        cfg = yaml.safe_load(f)
    mode = 'live'  # Fixed for this loop
    logger = TradeLogger(mode=mode)  # Initialize logger
    if not init_mt5(mode=mode):
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
                res = execute_order(side, lot, mode=mode, sl=sl, tp=tp)
                open_time = str(datetime.now())  # Capture open time
                info(f'Live {side} {lot} @ {current_price}, SL:{sl}, TP:{tp} - {res}')
                logger.log_trade(side, current_price, sl, tp, open_time)  # Log after execute
                open_trade = res
                open_trade['time'] = open_time  # Store for close
                # In live, MT5 handles close; monitor pnl
                positions = mt5.positions_get(symbol=cfg['symbol'])
                if positions:
                    pnl = positions[0].profit
                    if pnl:  # Close logic if needed (assume closed if PNL non-zero)
                        balance += pnl
                        peak_balance = max(peak_balance, balance)
                        logger.log_trade(side, current_price, sl, tp, open_time=open_trade['time'], close_time=str(datetime.now()), pnl=pnl)  # Log on close
                        logger.get_history(from_mt5=True)  # Pull from MT5
                        logger.display_table()  # Optional console view
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