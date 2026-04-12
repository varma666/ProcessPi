from __future__ import annotations

from typing import Any, Dict

from .base import HeatExchanger


class BellDelawareHX(HeatExchanger):
    def design(self) -> Dict[str, Any]:
        raise NotImplementedError("Bell-Delaware method is reserved for a future release.")
