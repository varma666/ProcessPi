from ..units import Power
from typing import Dict, Optional, Union


class EnergyStream:
    """
    Represents an energy stream (heat or work transfer).
    Can bind to equipment and log Q/W duties automatically.

    Notes
    -----
    * Positive duty = energy input (to equipment)
    * Negative duty = energy output (from equipment)
    * Duties are stored with units (`Power`) to ensure consistency.
    """

    def __init__(self, name: str):
        self.name = name
        self.log: list[Dict[str, Union[str, Power]]] = []  # {equipment, tag, duty}

    def bind_equipment(self, equipment) -> None:
        """Optionally keep reference to equipment if needed later."""
        self.log.append({
            "equipment": equipment.name,
            "tag": "bind",
            "duty": Power(0.0, "W")
        })

    def record(self, duty: Union[float, Power], tag: str, equipment: str) -> None:
        """
        Log an energy duty.

        Parameters
        ----------
        duty : float | Power
            Energy duty (W). If float is given, assumed in watts.
        tag : str
            Label such as 'Q_in', 'Q_out', 'W_in', 'W_out'.
        equipment : str
            Name of equipment associated with this duty.
        """
        if isinstance(duty, (int, float)):
            duty = Power(duty, "W")

        self.log.append({
            "equipment": equipment,
            "tag": tag,
            "duty": duty
        })

    def total_duty(self, tag: Optional[str] = None) -> Power:
        """
        Return cumulative duty as a Power object.
        Optionally filter by tag.
        """
        duties = (
            [event["duty"] for event in self.log if tag is None or event["tag"] == tag]
        )
        total_value = sum(d.value for d in duties)
        return Power(total_value, "W")

    def __repr__(self) -> str:
        return (
            f"EnergyStream(name={self.name}, "
            f"total={self.total_duty()}, "
            f"entries={len(self.log)})"
        )
