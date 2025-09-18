from typing import Dict, Optional
from ..units import Pressure, Temperature, Density, VolumetricFlowRate, MassFlowRate, MolarFlowRate

class MaterialStream:
    """
    Represents a process material stream with thermodynamic state
    and composition information. Acts as a connector between equipment.
    """

    def __init__(
        self,
        name: str,
        pressure: Pressure,
        temperature: Temperature,
        density: Optional[Density] = None,
        flow_rate: Optional[VolumetricFlowRate] = None,
        components: Optional[Dict[str, float]] = None,
        basis: str = "mole",   # "mole" or "mass"
        molecular_weights: Optional[Dict[str, float]] = None,  # g/mol
        phase: Optional[str] = None,
    ):
        self.name = name
        self.pressure = pressure
        self.temperature = temperature
        self.density = density
        self.flow_rate = flow_rate
        self.phase = phase

        # Composition
        self.components = components or {}
        self.basis = basis
        self._normalize()

        # MW dictionary for molar ↔ mass conversions
        self.molecular_weights = molecular_weights or {}

        # For equipment connections (API clean-up)
        self._inlet_equipment = None
        self._outlet_equipment = None

    # -----------------------------
    # Composition handling
    # -----------------------------
    def _normalize(self):
        if self.components:
            total = sum(self.components.values())
            if total > 0:
                for k in self.components:
                    self.components[k] /= total

    def set_composition(self, components: Dict[str, float], basis: str = "mole"):
        self.components = components
        self.basis = basis
        self._normalize()

    # -----------------------------
    # Derived properties
    # -----------------------------
    @property
    def volumetric_flow(self) -> Optional[float]:
        return self.flow_rate.to("m3/s").value if self.flow_rate else None

    @property
    def rho(self) -> Optional[float]:
        return self.density.to("kg/m3").value if self.density else None

    def mass_flow(self) -> Optional[MassFlowRate]:
        if self.flow_rate and self.density:
            m_dot = self.volumetric_flow * self.rho
            return MassFlowRate(m_dot, "kg/s")
        return None

    def molar_flow(self) -> Optional[MolarFlowRate]:
        mass = self.mass_flow()
        if mass and self.avg_mw():
            n_dot = mass.to("kg/s").value / self.avg_mw()
            return MolarFlowRate(n_dot, "mol/s")
        return None

    def avg_mw(self) -> Optional[float]:
        """Average molecular weight (kg/mol) from composition + MW dict"""
        if not self.components or not self.molecular_weights:
            return None
        mw = 0.0
        if self.basis == "mole":
            for c, x in self.components.items():
                mw += x * (self.molecular_weights.get(c, 0) / 1000.0)
            return mw
        elif self.basis == "mass":
            total_mass = sum(self.components.values())
            if total_mass <= 0:
                return None
            mole_fracs = {}
            for c, w in self.components.items():
                mw_c = self.molecular_weights.get(c, 0) / 1000.0
                if mw_c > 0:
                    mole_fracs[c] = (w / total_mass) / mw_c
            norm = sum(mole_fracs.values())
            if norm == 0:
                return None
            for c in mole_fracs:
                mole_fracs[c] /= norm
            return sum(x * (self.molecular_weights.get(c, 0) / 1000.0) for c, x in mole_fracs.items())

    # -----------------------------
    # Equipment connectivity
    # -----------------------------
    def connect_inlet(self, equipment: "Equipment"):
        """Marks this stream as entering the given equipment."""
        self.end_node = equipment

    def connect_outlet(self, equipment: "Equipment"):
        """Marks this stream as leaving the given equipment."""
        self.start_node = equipment

    @property
    def inlet_equipment(self):
        return self._inlet_equipment

    @property
    def outlet_equipment(self):
        return self._outlet_equipment

    # -----------------------------
    # Stream utilities
    # -----------------------------
    def copy(self, name: str):
        return MaterialStream(
            name=name,
            pressure=self.pressure,
            temperature=self.temperature,
            density=self.density,
            flow_rate=self.flow_rate,
            components=self.components.copy(),
            basis=self.basis,
            molecular_weights=self.molecular_weights.copy(),
            phase=self.phase,
        )

    def split(self, ratio: float, name1="Split1", name2="Split2"):
        if not self.flow_rate:
            raise ValueError("Cannot split stream without flow_rate")
        f1 = self.volumetric_flow * ratio
        f2 = self.volumetric_flow * (1 - ratio)
        return (
            self.copy(name1)._with_flow(VolumetricFlowRate(f1, "m3/s")),
            self.copy(name2)._with_flow(VolumetricFlowRate(f2, "m3/s")),
        )

    def mix(self, other: "MaterialStream", name="Mixed"):
        if not self.flow_rate or not other.flow_rate:
            raise ValueError("Both streams must have flow_rate defined")
        f_total = self.volumetric_flow + other.volumetric_flow
        mix = self.copy(name)
        mix.flow_rate = VolumetricFlowRate(f_total, "m3/s")
        # TODO: proper mixing of P, T, composition (future thermodynamics)
        return mix

    def _with_flow(self, flow: VolumetricFlowRate):
        self.flow_rate = flow
        return self

    def __repr__(self) -> str:
        return (f"<MaterialStream {self.name}, P={self.pressure}, T={self.temperature}, "
                f"Q={self.flow_rate}, ρ={self.density}, comps={self.components}>")
