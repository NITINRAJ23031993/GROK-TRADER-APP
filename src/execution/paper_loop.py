import time

def paper_loop(step_callback, interval: float = 1.0):
    """Simple paper trading loop that calls `step_callback` repeatedly.

    `step_callback` should accept no args or return immediately.
    """
    try:
        while True:
            step_callback()
            time.sleep(interval)
    except KeyboardInterrupt:
        return
