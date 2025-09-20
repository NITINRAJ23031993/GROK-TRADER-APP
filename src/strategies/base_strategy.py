from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseStrategy(ABC):
    """Base strategy interface.

    Concrete strategies should implement `generate_signal` which returns
    a dict like `{"signal": "buy"|"sell"|"hold", "confidence": float}`.
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}

    @abstractmethod
    def generate_signal(self, market_data: Any) -> Dict[str, Any]:
        raise NotImplementedError()
