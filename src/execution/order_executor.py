import yaml
from datetime import datetime
from src.utils.logger import info, error

def execute_order(side, volume, mode='paper', sl=None, tp=None):
    with open('config/settings.yaml', 'r') as f:
        cfg = yaml.safe_load(f)
    info(f'Execute order: side={side} volume={volume} mode={mode} SL={sl} TP={tp}')
    if mode == 'paper':
        return {'status':'filled','side':side,'volume':volume,'price':None,'time':str(datetime.utcnow()), 'pnl':0}
    elif mode == 'live':
        try:
            from src.execution.mt5_connector import mt5_place_order
            return mt5_place_order(side, volume, sl, tp)
        except Exception as e:
            error('Live execution failed: '+str(e))
            return {'status':'error','error':str(e)}
    else:
        raise ValueError('Unknown mode')