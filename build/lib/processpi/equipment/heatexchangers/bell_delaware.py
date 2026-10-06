from __future__ import annotations

from typing import Any

from .shell_and_tube import ShellAndTubeHX


class BellDelawareHX(ShellAndTubeHX):
    """Shell-and-tube exchanger sized with the Bell-Delaware shell-side method.

    A named shortcut for ``ShellAndTubeHX(method="bell_delaware")``: the
    design, rating and results are those of ``ShellAndTubeHX`` with that
    method, which is also what ``HeatExchangerEngine(method="bell_delaware")``
    builds for a shell-and-tube exchanger. The class used to be a stub whose
    ``design()`` raised ``NotImplementedError`` although it was exported.

    ``method`` may be omitted or given as ``"bell_delaware"``; any other value
    is refused rather than quietly ignored, since this class only runs one
    method.
    """

    METHOD = "bell_delaware"

    def __init__(self, *args: Any, method: str = METHOD, **kwargs: Any):
        if str(method).lower() != self.METHOD:
            raise ValueError(
                f"BellDelawareHX always uses method='{self.METHOD}', got "
                f"method={method!r}; use ShellAndTubeHX(method={method!r}) "
                "for another method"
            )
        super().__init__(*args, method=self.METHOD, **kwargs)
