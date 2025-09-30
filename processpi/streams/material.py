# processpi/streams/material.py
from typing import Dict, Optional, Union
from ..units import (
    Pressure, Temperature, Density, VolumetricFlowRate,
    MassFlowRate, MolarFlowRate, SpecificHeat
)

class MaterialStream:
    """
    Represents a process material stream with thermodynamic state
    and composition information.

    Supports two initialization modes:
    -----------------------------------
    1) Component-based:
        from processpi.components import Water
        s1 = MaterialStream("Hot Water",
                            component=Water(),
                            temperature=Temperature(350, "K"),
                            mass_flow=MassFlowRate(2, "kg/s"))

    2) Manual property-based:
        s2 = MaterialStream("Custom Fluid",
                            temperature=Temperature(350, "K"),
                            pressure=Pressure(2, "bar"),
                            density=Density(1000, "kg/m3"),
                            cp=HeatCapacity(4200, "J/kg-K"),
                            flow_rate=VolumetricFlowRate(0.001, "m3/s"))
    """

    def __init__(
        self,
        name: str,
        component: Optional[object] = None,   # e.g., Water(), Air()
        pressure: Optional[Pressure] = None,
        temperature: Optional[Temperature] = None,
        density: Optional[Density] = None,
        specific_heat: Optional[SpecificHeat] = None,
        flow_rate: Optional[VolumetricFlowRate] = None,
        mass_flow: Optional[MassFlowRate] = None,
        molar_flow: Optional[MolarFlowRate] = None,
        composition: Optional[Dict[str, float]] = None,
        basis: str = "mole",
        molecular_weights: Optional[Dict[str, float]] = None,
        phase: Optional[str] = None,
    ):
        self.name = name
        self.phase = phase
        self.temperature = temperature or getattr(component,"temperature", None)
        self.pressure = pressure or getattr(component,"pressure", None)
        self.flow_rate = flow_rate
        self._mass_flow = mass_flow
        self._molar_flow = molar_flow

        # --------------------
        # Component mode
        # --------------------
        self.component = component
        if component:
            # Pull props if available
            self.density = density or getattr(component,"density", None)()
            self.specific_heat = specific_heat or getattr(component,"specific_heat", None)()
            self.molecular_weights = molecular_weights or {component.name: getattr(component, "mw", None)}
            self.components = {component.name: 1.0}
        else:
            # --------------------
            # Manual property mode
            # --------------------
            self.density = density
            self.specific_heat = specific_heat
            self.molecular_weights = molecular_weights or {}
            self.components = composition or {}

        self.basis = basis
        self._normalize()

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
    # Derived flows
    # -----------------------------
    def mass_flow(self) -> Optional[MassFlowRate]:
        if self._mass_flow:
            return self._mass_flow
        if self.flow_rate and self.density:
            m_dot = self.flow_rate.to("m3/s").value * self.density.to("kg/m3").value
            return MassFlowRate(m_dot, "kg/s")
        return None

    def molar_flow(self) -> Optional[MolarFlowRate]:
        if self._molar_flow:
            return self._molar_flow
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
            # Convert to mol basis first
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
    # Stream utilities
    # -----------------------------
    def copy(self, name: str):
        return MaterialStream(
            name=name,
            component=self.component,
            pressure=self.pressure,
            temperature=self.temperature,
            density=self.density,
            cp=self.cp,
            flow_rate=self.flow_rate,
            mass_flow=self._mass_flow,
            molar_flow=self._molar_flow,
            composition=self.components.copy(),
            basis=self.basis,
            molecular_weights=self.molecular_weights.copy(),
            phase=self.phase,
        )

    def __repr__(self) -> str:
        return f"<MaterialStream {self.name}, P={self.pressure}, T={self.temperature}, Q={self.flow_rate}, comps={self.components}>"
