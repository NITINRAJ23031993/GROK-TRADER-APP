from .base_strategy import BaseStrategy
from typing import Any, Dict


class MeanReversionStrategy(BaseStrategy):
    """Simple mean-reversion strategy stub."""

    def generate_signal(self, market_data: Any) -> Dict[str, Any]:
        # Placeholder logic: always return hold
        return {"signal": "hold", "confidence": 0.0}
