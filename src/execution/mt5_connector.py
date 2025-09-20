import json
from src.utils.logger import info, error
cfg = json.load(open('config/settings.yaml'))
try:
    import MetaTrader5 as mt5
except Exception as e:
    mt5 = None
    error('MT5 import failed: '+str(e))

def init_mt5():
    if mt5 is None:
        return False
    path = cfg.get('mt5',{}).get('path')
    ok = mt5.initialize(path) if path else mt5.initialize()
    if not ok:
        error('MT5 initialize failed')
        return False
    info('MT5 initialized')
    return True

def mt5_place_order(side, volume, sl=None, tp=None):
    if mt5 is None:
        raise RuntimeError('MT5 not available')
    symbol = cfg.get('symbol','XAUUSD')
    tick = mt5.symbol_info_tick(symbol)
    price = tick.ask if side=='buy' else tick.bid
    order_type = mt5.ORDER_TYPE_BUY if side=='buy' else mt5.ORDER_TYPE_SELL
    req = {'action': mt5.TRADE_ACTION_DEAL, 'symbol':symbol, 'volume':float(volume), 'type':order_type, 'price':price, 'deviation':20}
    if sl:
        req['sl'] = sl
    if tp:
        req['tp'] = tp
    res = mt5.order_send(req)
    info('MT5 order_send result: '+str(res))
    return {'status':'sent','res':str(res)}