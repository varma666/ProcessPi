"""
Fit/run interface for distillation design, the same pattern as
PipelineEngine and HeatExchangerEngine:

    model = DistillationEngine()
    model.fit(feed=feed, components=[Benzene(), Toluene()],
              light_key="Benzene", heavy_key="Toluene",
              distillate_lk_fraction=0.97, bottoms_lk_fraction=0.02)
    results = model.run()
    print(results.summary())

`fit()` stores the inputs and returns the engine; `run()` builds a
DistillationColumn from them, designs it and returns DistillationResults.
DistillationColumn stays available as the flowsheet unit.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from processpi.streams.material import MaterialStream

from .column import DistillationColumn
from .results import DistillationResults


class DistillationEngine:
    """
    Distillation column design engine.

    Usage:
        1. Instantiate the engine: `model = DistillationEngine()`
        2. Configure inputs with `.fit()`: `model.fit(feed=feed, light_key=..., heavy_key=..., ...)`
        3. Run the design: `results = model.run()`
        4. Access results: `results.summary()`, `results["diameter"]`

    `fit()` takes the feed stream, optional `distillate` and `bottoms`
    streams (when both are given, `run()` writes the products to them), and
    every DistillationColumn spec (see DistillationColumn for the list).
    """

    def __init__(self, name: Optional[str] = None, **kwargs: Any) -> None:
        self.name = name or "DistillationColumn"
        self.data: Dict[str, Any] = {}
        self.column: Optional[DistillationColumn] = None
        self._results: Optional[DistillationResults] = None
        if kwargs:
            self.fit(**kwargs)

    def fit(self, feed: MaterialStream, distillate: Optional[MaterialStream] = None,
            bottoms: Optional[MaterialStream] = None, **specs: Any) -> "DistillationEngine":
        """
        Store the inputs for the next run().

        Raises:
            TypeError: if a stream is not a MaterialStream.
            ValueError: if a key component is missing, or only one product stream is given.
        """
        for label, stream in (("feed", feed), ("distillate", distillate), ("bottoms", bottoms)):
            if stream is not None and not isinstance(stream, MaterialStream):
                raise TypeError(f"{label} must be a MaterialStream, got {type(stream).__name__}.")
        if feed is None:
            raise ValueError("fit() needs a feed stream.")
        if (distillate is None) != (bottoms is None):
            raise ValueError("Give both distillate and bottoms streams, or neither.")
        for key in ("light_key", "heavy_key"):
            if not specs.get(key):
                raise ValueError(f"fit() needs {key}.")
        if "name" in specs:
            self.name = specs.pop("name")

        self.data = {"feed": feed, "distillate": distillate, "bottoms": bottoms, "specs": specs}
        self.column = None
        self._results = None
        return self

    def run(self) -> DistillationResults:
        """Design the column from the fitted inputs and return the results."""
        if not self.data:
            raise RuntimeError("Configure the model first using model.fit(...).")
        column = DistillationColumn(
            name=self.name,
            feed=self.data["feed"],
            distillate=self.data["distillate"],
            bottoms=self.data["bottoms"],
            **self.data["specs"],
        )
        if column.distillate is not None:
            column.simulate()
            results = column.results()
        else:
            results = column.design()
        self.column = column
        self._results = results
        return results

    def summary(self) -> Optional[str]:
        if self._results is None:
            return None
        return self._results.summary()

    def results(self) -> DistillationResults:
        if self._results is None:
            raise RuntimeError("Run the model first using model.run().")
        return self._results
