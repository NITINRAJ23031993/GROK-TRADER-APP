from .paper_loop import paper_loop


def live_loop(step_callback, interval: float = 1.0):
    """Live trading loop stub. Same interface as paper_loop."""
    return paper_loop(step_callback, interval)
