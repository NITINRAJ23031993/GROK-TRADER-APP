# Copy paper_loop.py, change mode='live', add init_mt5() call at start
from src.execution.mt5_connector import init_mt5
if not init_mt5():
    raise RuntimeError('MT5 init failed')
# ... rest same as paper_loop, mode='live'