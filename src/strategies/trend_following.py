from .base_strategy import BaseStrategy
from typing import Any, Dict


class TrendFollowingStrategy(BaseStrategy):
    """Simple trend-following strategy stub.

    Uses moving average crossover (placeholder) to produce signals.
    """

    def generate_signal(self, market_data: Any) -> Dict[str, Any]:
        # Placeholder logic: always return hold
        return {"signal": "hold", "confidence": 0.0}
