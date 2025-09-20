import yaml
from src.utils.logger import info, error
try:
    import MetaTrader5 as mt5
except Exception as e:
    mt5 = None
    error('MT5 import failed: '+str(e))

def init_mt5(mode='paper'):
    if mt5 is None:
        return False
    with open('config/settings.yaml', 'r') as f:
        cfg = yaml.safe_load(f)['mt5']
    server = cfg.get('server')
    if mode == 'paper':
        server = server.replace('Live', 'Demo')
    path = cfg.get('path')
    login = cfg.get('account')
    password = cfg.get('password')
    ok = mt5.initialize(path=path, login=login, password=password, server=server)
    if not ok:
        error('MT5 initialize failed')
        return False
    info('MT5 initialized in ' + mode)
    return True

def mt5_place_order(side, volume, sl=None, tp=None):
    if mt5 is None:
        raise RuntimeError('MT5 not available')
    with open('config/settings.yaml', 'r') as f:
        cfg = yaml.safe_load(f)
    symbol = cfg.get('symbol', 'XAUUSD')
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