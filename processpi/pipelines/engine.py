# processpi/pipelines/engine.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
import math

# Local package imports (assumed to exist in your project)
from ..units import (
    Diameter, Length, Pressure, Density, Viscosity, VolumetricFlowRate, Velocity, MassFlowRate
)
from .pipelineresults import PipelineResults
from .nozzle import Nozzle
from ..components import Component
from .standards import (
    get_k_factor, get_roughness, list_available_pipe_diameters, get_standard_pipe_data,
    get_recommended_velocity, get_next_standard_nominal, get_next_next_standard_nominal, get_previous_standard_nominal
)
from .pipes import Pipe
from .fittings import Fitting
from .equipment import Equipment
from .network import PipelineNetwork
from .piping_costs import PipeCostModel
from ..calculations.fluids import (
    FluidVelocity, ReynoldsNumber, PressureDropDarcy, OptimumPipeDiameter, PressureDropFanning, ColebrookWhite, PressureDropHazenWilliams
)
from processpi.pipelines import network


# ------------------------------- Constants ---------------------------------
G = 9.80665  # m/s^2, Standard gravity
DEFAULT_PUMP_EFFICIENCY = 0.70
DEFAULT_FLOW_TOL = 1e-6  # m3/s, Absolute flow tolerance for solvers
MAX_HC_ITER = 200  # Max iterations for Hardy-Cross solver
MAX_MATRIX_ITER = 100 # Max iterations for matrix solver

# ------------------------------- Helpers -----------------------------------


def _to_m3s(maybe_flow: Any) -> VolumetricFlowRate:
    """
    Normalize flow to VolumetricFlowRate (m^3/s).

    Args:
        maybe_flow (Any): The flow rate, which can be a VolumetricFlowRate object,
                          a MassFlowRate object, or a number.

    Returns:
        VolumetricFlowRate: The flow rate in m^3/s.

    Raises:
        ValueError: If flow is None.
        TypeError: If a MassFlowRate object is provided without density context.
    """
    if maybe_flow is None:
        raise ValueError("Flow cannot be None")
    if isinstance(maybe_flow, VolumetricFlowRate):
        return maybe_flow
    if isinstance(maybe_flow, MassFlowRate):
        raise TypeError("MassFlowRate provided without density context. Convert before calling.")
    # assume numeric m3/s
    return VolumetricFlowRate(float(maybe_flow), "m3/s")


def _ensure_diameter_obj(d: Any, assume_mm: bool = True) -> Diameter:
    """
    Ensures the input is a Diameter object.

    If the input `d` is not a Diameter object, it attempts to convert it to one.
    The `assume_mm` flag determines if a raw number is treated as millimeters.

    Args:
        d (Any): The diameter value or object.
        assume_mm (bool): If True, a numeric input is assumed to be in millimeters.

    Returns:
        Diameter: The validated or converted Diameter object.
    """
    if isinstance(d, Diameter):
        return d
    val = float(d)
    unit = "mm" if assume_mm else "m"
    return Diameter(val, unit)


@dataclass
class ElementReport:
    """
    A data class to store the results of a single pipeline element calculation.
    """
    name: str
    type: str
    diameter_m: Optional[float] = None
    flow_m3s: Optional[float] = None
    velocity_m_s: Optional[float] = None
    reynolds: Optional[float] = None
    friction_factor: Optional[float] = None
    dp_pa: Optional[float] = None
    elevation_dp_pa: Optional[float] = None
    head_m: Optional[float] = None
    warnings: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        """Convert the dataclass to a dictionary."""
        return {
            "name": self.name,
            "type": self.type,
            "diameter_m": self.diameter_m,
            "flow_m3s": self.flow_m3s,
            "velocity_m_s": self.velocity_m_s,
            "reynolds": self.reynolds,
            "friction_factor": self.friction_factor,
            "pressure_drop_Pa": self.dp_pa,
            "elevation_loss_Pa": self.elevation_dp_pa,
            "head_loss_m": self.head_m,
            "warnings": self.warnings,
        }


# ----------------------------- Pipeline Engine -----------------------------
class PipelineEngine:
    """
    Pipeline simulation and sizing engine.

    This class provides a comprehensive set of tools for modeling fluid flow
    in pipelines. It can handle single pipes, series networks, and parallel
    networks, calculating pressure drop, velocity, Reynolds number, and other
    key fluid properties.

    Usage:
        1. Instantiate the engine: `engine = PipelineEngine()`
        2. Configure inputs with `.fit()`: `engine.fit(fluid=water, flowrate=1.0)`
        3. Run the simulation: `results = engine.run()`
        4. Access results: `results.summary()`

    The object stores the last results in `self._results` (PipelineResults).
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes the PipelineEngine.

        Args:
            **kwargs: Initial configuration parameters passed to `fit()`.
        """
        self.data: Dict[str, Any] = {}
        self._results: Optional[PipelineResults] = None
        if kwargs:
            self.fit(**kwargs)

    # ---------------------- Configuration / Fit ----------------------------
    def fit(self, **kwargs: Any) -> "PipelineEngine":
        """
        Configures engine inputs. Converts and normalizes keys/aliases.

        Args:
            **kwargs: A dictionary of input parameters.

        Returns:
            PipelineEngine: The configured engine instance.

        Raises:
            TypeError: If the `network` provided is not a PipelineNetwork instance.
        """
        self.data = dict(kwargs)

        # Map aliases to canonical keys
        alias_map = {
            "flowrate": ["flow_rate", "q", "Q", "flowrate"],
            "mass_flowrate": ["mass_flow", "m_dot", "mdot"],
            "velocity": ["v"],
            "diameter": ["dia", "D", "nominal_diameter", "internal_diameter"],
            "length": ["len", "L"],
            "inlet_pressure": ["in_pressure", "pin", "p_in"],
            "outlet_pressure": ["out_pressure", "pout", "p_out"],
        }
        for canon, alts in alias_map.items():
            if canon not in self.data:
                for a in alts:
                    if a in self.data:
                        self.data[canon] = self.data[a]
                        break

        # Set default values for common parameters
        self.data.setdefault("assume_mm_for_numbers", True)
        self.data.setdefault("flow_split", {})
        self.data.setdefault("tolerance_m3s", DEFAULT_FLOW_TOL)
        self.data.setdefault("pump_efficiency", DEFAULT_PUMP_EFFICIENCY)
        self.data.setdefault("method", "darcy_weisbach")
        self.data.setdefault("hw_coefficient", 130.0)  # Hazen-Williams roughness coefficient
        self.data.setdefault("solver", "auto")

        # Validate network type
        net = self.data.get("network")
        if net is not None and not isinstance(net, PipelineNetwork):
            raise TypeError("`network` must be a PipelineNetwork instance.")

        # Bind normalized attributes for internal use
        self.flowrate = self.data.get("flowrate")
        self.diameter = self.data.get("diameter")
        self.velocity = self.data.get("velocity")
        self.mass_flowrate = self.data.get("mass_flowrate")
        # print(self) # For debugging purposes

        return self


    # ---------------------- Fluid properties --------------------------------
    def _get_density(self) -> Density:
        """
        Retrieves the fluid's density.

        Returns:
            Density: The fluid density object.

        Raises:
            ValueError: If density is not provided or cannot be inferred from the fluid component.
        """
        if "density" in self.data and self.data["density"] is not None:
            return self.data["density"]
        fluid = self.data.get("fluid")
        if isinstance(fluid, Component):
            return fluid.density()
        raise ValueError("Provide 'density' or a 'fluid' Component with density().")

    def _get_viscosity(self) -> Viscosity:
        """
        Retrieves the fluid's dynamic viscosity.

        Returns:
            Viscosity: The fluid viscosity object.

        Raises:
            ValueError: If viscosity is not provided or cannot be inferred from the fluid component.
        """
        if "viscosity" in self.data and self.data["viscosity"] is not None:
            return self.data["viscosity"]
        fluid = self.data.get("fluid")
        if isinstance(fluid, Component):
            return fluid.viscosity()
        raise ValueError("Provide 'viscosity' or a 'fluid' Component with viscosity().")

    # ---------------------- Flow inference ----------------------------------
    def _infer_flowrate(self) -> VolumetricFlowRate:
        """
        Infers the volumetric flow rate from available data.

        It checks for `flowrate`, then `mass_flowrate`, and finally `velocity`
        and `diameter` to calculate the flow rate.

        Returns:
            VolumetricFlowRate: The calculated volumetric flow rate.

        Raises:
            ValueError: If flow rate cannot be inferred from the provided data.
        """
        if "flowrate" in self.data and self.data["flowrate"] is not None:
            return self.data["flowrate"]
        # Convert mass flow to volumetric flow
        if "mass_flowrate" in self.data and self.data["mass_flowrate"] is not None:
            rho = self._get_density()
            m = self.data["mass_flowrate"]
            m_val = m.value if hasattr(m, "value") else float(m)
            q_val = m_val / (rho.value if hasattr(rho, "value") else float(rho))
            q = VolumetricFlowRate(q_val, "m3/s")
            self.data["flowrate"] = q
            return q
        # Calculate flow from velocity and diameter
        v = self.data.get("velocity")
        d = self.data.get("diameter")
        if v is not None and d is not None:
            if not isinstance(v, Velocity):
                v = Velocity(float(v), "m/s")
            d_obj = _ensure_diameter_obj(d, self.data.get("assume_mm_for_numbers", True))
            q = VolumetricFlowRate(v.value * math.pi * (d_obj.to("m").value ** 2) / 4.0, "m3/s")
            self.data["flowrate"] = q
            return q
        raise ValueError("Unable to infer flowrate. Provide 'flowrate' or 'mass_flowrate' or ('velocity' and 'diameter').")
    
    def _maybe_velocity(self, pipe):
        """
        Ensures velocity is available.

        If not explicitly provided, it calculates velocity using volumetric flow
        rate and pipe diameter.

        Args:
            pipe (Pipe): The pipe object to check for velocity.

        Returns:
            Velocity: The velocity object.

        Raises:
            ValueError: If velocity cannot be calculated.
        """
        if hasattr(pipe, "velocity") and pipe.velocity is not None:
            return pipe.velocity
        elif hasattr(pipe, "flow_rate") and hasattr(pipe, "diameter"):
            area = math.pi * (pipe.diameter.value ** 2) / 4.0
            velocity_value = pipe.flow_rate.value / area
            return Velocity(velocity_value, pipe.flow_rate.unit + "/" + pipe.diameter.unit)
        else:
            raise ValueError(
                "Insufficient data: cannot calculate velocity without diameter and flow rate."
            )


    # ---------------------- Diameter resolution -----------------------------
    def _resolve_internal_diameter(self, pipe: Optional[Pipe] = None) -> Diameter:
        """
        Resolves the internal diameter for a given pipe or the simulation.

        Priority order:
        1. `pipe.internal_diameter`
        2. `pipe.nominal_diameter`
        3. `engine.diameter` from `self.data`
        4. Calculates the optimum diameter as a fallback.

        Args:
            pipe (Optional[Pipe]): The pipe object for which to resolve the diameter.

        Returns:
            Diameter: The resolved internal diameter.
        """
        if pipe is not None:
            if getattr(pipe, "internal_diameter", None) is not None:
                d = pipe.internal_diameter
                return d if isinstance(d, Diameter) else Diameter(float(d), "m")
            if getattr(pipe, "nominal_diameter", None) is not None:
                d = pipe.nominal_diameter
                return d if isinstance(d, Diameter) else Diameter(float(d), "m")
        d = self.data.get("diameter")
        if d is not None:
            # print(d) # For debugging
            return d if isinstance(d, Diameter) else _ensure_diameter_obj(d, self.data.get("assume_mm_for_numbers", True))
        # fallback to compute optimum for a single pipe
        q = self._infer_flowrate()
        calc = OptimumPipeDiameter(flow_rate=q, density=self._get_density())
        return calc.calculate()

    # ---------------------- Primitive calculators ---------------------------
    def _velocity(self, q: VolumetricFlowRate, d: Diameter) -> Velocity:
        """
        Calculates the fluid velocity given flow rate and diameter.
        """
        return FluidVelocity(volumetric_flow_rate=q, diameter=d).calculate()

    def _reynolds(self, v: Velocity, d: Diameter) -> float:
        """
        Calculates the Reynolds number.
        """
        return ReynoldsNumber(density=self._get_density(), velocity=v, diameter=d, viscosity=self._get_viscosity()).calculate()

    def _friction_factor(self, Re: float, d: Diameter, material: Optional[str] = None) -> float:
        """
        Calculates the friction factor using the Colebrook-White equation.
        """
        eps = get_roughness(material) if material else 0.0
        # print(Re) # For debugging
        return ColebrookWhite(reynolds_number=Re, roughness=eps, diameter=d).calculate()

    def _major_dp_pa(self, f: float, L: Length, d: Diameter, v: Velocity) -> Pressure:
        """
        Calculates the major pressure drop (friction loss) using the Darcy-Weisbach equation.
        """
        return PressureDropDarcy(friction_factor=f, length=L, diameter=d, density=self._get_density(), velocity=v).calculate()

    def _minor_dp_pa(self, fitting: Fitting, v: Velocity, f: Optional[float], d: Diameter) -> Pressure:
        """
        Calculates the minor pressure drop (fitting loss).

        It prioritizes the K-factor method and falls back to the equivalent length method.
        """
        # try K factor first
        rho = self._get_density().value
        v_val = v.value if hasattr(v, "value") else float(v)
        K = getattr(fitting, "K", None) or getattr(fitting, "K_factor", None) or getattr(fitting, "total_K", None)
        if K is not None:
            return Pressure(0.5 * rho * v_val * v_val * float(K), "Pa")
        # equivalent length fallback
        Le = getattr(fitting, "Le", None) or getattr(fitting, "equivalent_length", None)
        if Le is not None:
            if f is None:
                # recompute friction factor if not provided
                Re = self._reynolds(v, d)
                f_val = self._friction_factor(Re, d)
            else:
                f_val = float(f)
            return Pressure(float(f_val) * (float(Le) / d.to("m").value) * 0.5 * rho * v_val * v_val, "Pa")
        return Pressure(0.0, "Pa")

    # ---------------------- Pipe calculation (major+minor+elevation) ---------
    def _pipe_calculation(self, pipe: Pipe, flow_rate: Optional[VolumetricFlowRate]) -> Dict[str, Any]:
        """
        Calculates velocity, Reynolds number, friction factor, and pressure drops for a single pipe.

        Args:
            pipe (Pipe): The pipe object to analyze.
            flow_rate (Optional[VolumetricFlowRate]): The flow rate for this pipe. If None, it is inferred.

        Returns:
            Dict[str, Any]: A dictionary containing all calculated properties for the pipe.
        """

        # ---------------------------
        # Diameter
        # ---------------------------
        d = pipe.internal_diameter or self._resolve_internal_diameter(pipe)
        if d is None or getattr(d, "value", d) <= 0:
            d = Diameter(0.01, "m")

        # ---------------------------
        # Flow Rate & Velocity
        # ---------------------------
        q_used = flow_rate or getattr(pipe, "assigned_flow_rate", None) or self._infer_flowrate()
        if q_used is None or getattr(q_used, "value", q_used) <= 0:
            q_used = VolumetricFlowRate(1e-12, "m3/s")

        v = self.data.get("velocity")
        if v is None:
            v = FluidVelocity(volumetric_flow_rate=q_used, diameter=d).calculate()
        elif not isinstance(v, Velocity):
            v = Velocity(float(v), "m/s")

        # ---------------------------
        # Reynolds Number & Friction
        # ---------------------------
        Re = self._reynolds(v, d)
        material = getattr(pipe, "material", None)
        method = self.data.get("method", "darcy_weisbach").lower()

        if getattr(Re, "value", Re) <= 1e-8:
            f = 0.0
            dp_major = self._major_dp_pa(f, pipe.length or Length(1.0, "m"), d, v)
        elif method == "hazen_williams":
            hw_coeff = getattr(pipe, "hw_coefficient", None) or self.data.get("hw_coefficient", 130.0)
            dp_major = PressureDropHazenWilliams({
                "length": pipe.length or Length(1.0, "m"),
                "flow_rate": q_used,
                "coefficient": hw_coeff,
                "diameter": d,
                "density": self._get_density(),
            }).calculate()
            f = None
        else:
            f = self._friction_factor(Re, d, material)
            dp_major = self._major_dp_pa(f, pipe.length or Length(1.0, "m"), d, v)

        # ---------------------------
        # Minor Losses
        # ---------------------------
        dp_minor = Pressure(0.0, "Pa")
        for ft in getattr(pipe, "fittings", []) or []:
            dp_minor += self._minor_dp_pa(ft, v, f, d)

        # ---------------------------
        # Elevation Loss
        # ---------------------------
        rho_val = self._get_density().value
        start_node = getattr(pipe, "start_node", None)
        end_node = getattr(pipe, "end_node", None)
        elev_loss = Pressure(0.0, "Pa")
        try:
            elev_diff_m = float(getattr(end_node, "elevation", 0.0)) - float(getattr(start_node, "elevation", 0.0))
            elev_loss = Pressure(rho_val * 9.80665 * elev_diff_m, "Pa")
        except Exception:
            pass

        # ---------------------------
        # Total Pressure Drop
        # ---------------------------
        total_dp_pa = sum(getattr(x, "value", x) for x in [dp_major, dp_minor, elev_loss])

        return {
            "diameter": d,
            "velocity": v,
            "reynolds": Re,
            "friction_factor": f,
            "major_dp": dp_major,
            "minor_dp": dp_minor,
            "elevation_dp": elev_loss,
            "pressure_drop": Pressure(total_dp_pa, "Pa"),
            "major_dp_pa": getattr(dp_major, "value", dp_major),
            "minor_dp_pa": getattr(dp_minor, "value", dp_minor),
            "elevation_dp_pa": getattr(elev_loss, "value", elev_loss),
        }


    # ---------------------- Series/Parallel evaluation -------------------------

    def _compute_series(self, series: Any, flow_rate: Optional[VolumetricFlowRate] = None) -> Tuple[Pressure, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Compute pressure drop for a series of pipes.

        Args:
            series (Any): A single Pipe, a list of Pipes (treated as series),
                          or a list of branches (each branch is a list of Pipes).
            flow_rate (Optional[VolumetricFlowRate]): The flow rate for the series.

        Returns:
            Tuple[Pressure, List[Dict[str, Any]], Dict[str, Any]]:
                - total pressure drop
                - list of element reports
                - series summary dictionary
        """

        # ---------------------------
        # Normalize input
        # ---------------------------
        if isinstance(series, Pipe):
            # Single pipe -> one series with one pipe
            series = [series]
        elif all(isinstance(p, Pipe) for p in series):
            # Already a list of pipes -> fine
            pass
        elif all(isinstance(b, list) for b in series):
            # List of branches -> flatten for series calculation
            series = [p for branch in series for p in branch]
            if not all(isinstance(p, Pipe) for p in series):
                raise TypeError("After flattening, series contains non-Pipe elements")
        else:
            raise TypeError("series must be a Pipe, list of Pipes, or list of branches (list of Pipes)")

        # ---------------------------
        # Series flow calculation
        # ---------------------------
        total_dp = 0.0
        element_reports = []

        for idx, pipe in enumerate(series):
            pipe_res = self._pipe_calculation(pipe, flow_rate)
            dp_val = getattr(pipe_res["pressure_drop"], "value", pipe_res["pressure_drop"])
            total_dp += dp_val

            element_reports.append({
                "name": getattr(pipe, "name", f"Pipe_{idx}"),
                "type": "pipe",
                **pipe_res
            })

        # ---------------------------
        # Series summary
        # ---------------------------
        series_summary = {
            "total_pressure_drop": Pressure(total_dp, "Pa"),
            "number_of_elements": len(series),
            "average_velocity": Velocity(
                sum(getattr(el["velocity"], "value", el["velocity"]) for el in element_reports) / len(element_reports),
                "m/s"
            ),
            "elements": element_reports
        }

        return Pressure(total_dp, "Pa"), element_reports, series_summary


    def _compute_network(self, network: Any, flow_rate: Optional[VolumetricFlowRate] = None
                        ) -> Tuple[Pressure, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Compute pressure drop for a network.

        Args:
            network (Any): Single Pipe, list of Pipes (series branch), list of
                           branches (each branch is list of Pipes), or a
                           PipelineNetwork object.
            flow_rate (Optional[VolumetricFlowRate]): The flow rate for the network.

        Returns:
            Tuple[Pressure, List[Dict[str, Any]], Dict[str, Any]]:
                - total network pressure drop
                - element reports
                - network summary
        """

        # ---------------------------
        # Normalize input
        # ---------------------------
        if isinstance(network, Pipe):
            branches = [[network]]
        elif isinstance(network, list):
            # Check if this is a list of pipes (series) or list of branches
            if all(isinstance(p, Pipe) for p in network):
                branches = [network]
            elif all(isinstance(b, list) for b in network):
                # list of branches
                branches = []
                for b in network:
                    if isinstance(b, Pipe):
                        branches.append([b])
                    elif isinstance(b, list) and all(isinstance(p, Pipe) for p in b):
                        branches.append(b)
                    else:
                        raise TypeError("Invalid element inside branch list")
            else:
                raise TypeError("Network list must contain Pipes or branches (list of Pipes)")
        elif hasattr(network, "branches") and isinstance(network.branches, list):
            # PipelineNetwork object detected
            branches = []
            for b in network.branches:
                if isinstance(b, Pipe):
                    branches.append([b])
                elif isinstance(b, list) and all(isinstance(p, Pipe) for p in b):
                    branches.append(b)
                else:
                    raise TypeError("PipelineNetwork branches must contain Pipes or lists of Pipes")
        else:
            raise TypeError("Network must be Pipe, list of Pipes/branches, or PipelineNetwork object")

        # ---------------------------
        # Compute network
        # ---------------------------
        total_dp = 0.0
        element_reports = []

        for branch_idx, branch in enumerate(branches):
            dp_branch, el_reports, _ = self._compute_series(branch, flow_rate)
            total_dp += getattr(dp_branch, "value", dp_branch)
            # tag branch index in element reports
            for el in el_reports:
                el["branch_index"] = branch_idx
            element_reports.extend(el_reports)

        # ---------------------------
        # Network summary
        # ---------------------------
        network_summary = {
            "total_pressure_drop": Pressure(total_dp, "Pa"),
            "number_of_branches": len(branches),
            "number_of_elements": len(element_reports),
            "elements": element_reports
        }

        return Pressure(total_dp, "Pa"), element_reports, network_summary


    def _resolve_parallel_flows(
        self, net: PipelineNetwork, q_total: VolumetricFlowRate, branches: list, tol: float = 1e-3, max_iter: int = 100
    ) -> list:
        """
        Resolves flow in parallel branches using iterative ΔP balancing.
        
        Args:
            net (PipelineNetwork): The parallel network object.
            q_total (VolumetricFlowRate): Total volumetric flow rate (m3/s).
            branches (list): List of branch networks.
            tol (float): Convergence tolerance on ΔP equality.
            max_iter (int): Maximum iterations.
        
        Returns:
            List[float]: A list of flow rates (m3/s) for each branch.
        """
        n = len(branches)
        # --- Initial guess: equal split ---
        q_branches = [q_total.value / n] * n

        # Check for user-defined split ratios
        split_cfg = (self.data.get("flow_split") or {}).get(net.name)
        if split_cfg:
            vals = [float(x) for x in split_cfg]
            if sum(vals) > 1.5 * q_total.value:  # absolute flows
                return vals
            s = sum(vals)  # ratios
            return [q_total.value * (v / s) for v in vals]

        # --- Iterative ΔP balancing ---
        for iteration in range(max_iter):
            dps = []
            for i, branch in enumerate(branches):
                flow_i = VolumetricFlowRate(q_branches[i], "m3/s")
                dp, _, _ = self._compute_network(branch, flow_i)
                dps.append(dp.to("Pa").value)

            dp_avg = sum(dps) / n
            # Convergence: all ΔPs within tolerance
            if max(abs(dp - dp_avg) for dp in dps) / (dp_avg + 1e-6) < tol:
                break

            # Adjust flows proportionally: higher ΔP → reduce flow, lower ΔP → increase flow
            for i in range(n):
                if dps[i] == 0:  # avoid division by zero
                    continue
                factor = dp_avg / dps[i]
                q_branches[i] *= factor
            # Normalize total flow
            q_sum = sum(q_branches)
            q_branches = [q * q_total.value / q_sum for q in q_branches]

        return q_branches





    # ---------------------- Network Solvers ---------------------------------
    def _hardy_cross(self, network: PipelineNetwork, q_total: VolumetricFlowRate, tol: float) -> Tuple[bool, float, List[ElementReport]]:
        """
        Hardy-Cross iterative solver for a parallel/looped network.

        Args:
            network (PipelineNetwork): The network object to solve.
            q_total (VolumetricFlowRate): The total flow rate entering the network.
            tol (float): The convergence tolerance.

        Returns:
            Tuple[bool, float, List[ElementReport]]:
                - bool: True if the solver converged.
                - float: The final maximum residual.
                - List[ElementReport]: A list of element reports with calculated properties.
        """
        # Get parallel branches for this network block
        branches = network.get_parallel_branches() if hasattr(network, "get_parallel_branches") else getattr(network, "elements", [])
        # If not a parallel block, fallback to single-branch result
        if not branches:
            # compute whole network as series
            dp, el_reports, branch_reports = self._compute_network(network, q_total)
            reports = [ElementReport(name=r.get("name", "el"), type=r.get("type", "el"), dp_pa=r.get("pressure_drop_Pa")) for r in el_reports]
            return True, 0.0, reports

        n = len(branches)
        branch_flows = [q_total.value / n] * n

        for it in range(MAX_HC_ITER):
            max_residual = 0.0
            reports: List[ElementReport] = []
            for i, branch in enumerate(branches):
                q_b = VolumetricFlowRate(branch_flows[i], "m3/s")
                dp_branch, el_reports, _ = self._compute_network(branch, q_b)
                # convert to head (m)
                H = dp_branch.to("Pa").value / (self._get_density().value * G)
                # derivative estimate dH/dQ ≈ n * H / Q (heuristic better than 2*H/Q in mixed networks)
                if abs(q_b.value) < 1e-12:
                    dHdQ = 1e12
                else:
                    dHdQ = 2.0 * H / q_b.value
                dq = -H / dHdQ
                branch_flows[i] += dq
                max_residual = max(max_residual, abs(dq))
                # collect element reports
                for r in el_reports:
                    rep = ElementReport(
                        name=r.get("name", "element"),
                        type=r.get("type", "element"),
                        diameter_m=(r.get("diameter").to("m").value if isinstance(r.get("diameter"), Diameter) else None),
                        flow_m3s=float(q_b.value),
                        velocity_m_s=(r.get("velocity").value if hasattr(r.get("velocity"), "value") else None),
                        reynolds=r.get("reynolds"),
                        friction_factor=r.get("friction_factor"),
                        dp_pa=r.get("pressure_drop_Pa"),
                        elevation_dp_pa=r.get("elevation_dp_Pa"),
                        head_m=(dp_branch.to("Pa").value / (self._get_density().value * G)),
                        warnings=[]
                    )
                    reports.append(rep)
            if max_residual < tol:
                return True, max_residual, reports
        return False, max_residual, reports

    def _matrix_solver(self, network: Any, q_total: VolumetricFlowRate, tol: float = 1e-6
                  ) -> Tuple[bool, List[VolumetricFlowRate], List[Dict[str, Any]]]:
        """
        Solve the network using an iterative approach.

        Args:
            network (Any): The network to solve.
            q_total (VolumetricFlowRate): Total volumetric flow rate.
            tol (float): Convergence tolerance.

        Returns:
            Tuple[bool, List[VolumetricFlowRate], List[Dict[str, Any]]]:
                - matrix_ok: bool indicating convergence
                - matrix_res: list of branch flow rates
                - matrix_reports: detailed element reports
        """

        # Normalize network using _compute_network
        _, element_reports, network_summary = self._compute_network(network, q_total)
        n_branches = network_summary["number_of_branches"]

        # Initialize branch flows equally if not set
        branch_flows = [q_total / n_branches for _ in range(n_branches)]
        matrix_ok = False
        iteration = 0
        max_iter = 100

        while iteration < max_iter:
            iteration += 1
            # dp_prev = [self._compute_network(branch, q)[0].value for branch, q in zip(self._normalize_branches(network), branch_flows)]

            # Recompute pressure drops for each branch with current flows
            dp_new = []
            for idx, branch in enumerate(self._normalize_branches(network)):
                dp, _, _ = self._compute_network(branch, branch_flows[idx])
                dp_new.append(getattr(dp, "value", dp))

            # Compute flow correction
            corrections = [dp / max(dp_new) * branch_flows[idx] for idx, dp in enumerate(dp_new)]
            max_change = max(abs(c - f.value if hasattr(f, "value") else f - bf) for c, bf in zip(corrections, branch_flows))
            branch_flows = corrections

            if max_change < tol:
                matrix_ok = True
                break

        matrix_reports = []
        for branch_idx, branch in enumerate(self._normalize_branches(network)):
            _, el_reports, _ = self._compute_network(branch, branch_flows[branch_idx])
            for el in el_reports:
                el["branch_index"] = branch_idx
            matrix_reports.extend(el_reports)

        return matrix_ok, branch_flows, matrix_reports


    def _solve_network_dual(
        self, network: Any, q_total: VolumetricFlowRate, tol: float = 1e-6
    ) -> Tuple[Dict[str, Any], Any]:
        """
        Top-level solver for networks with multiple branches.

        This method normalizes the network structure and iteratively balances
        pressure drops across parallel branches.

        Args:
            network (Any): The network to solve.
            q_total (VolumetricFlowRate): The total volumetric flow rate.
            tol (float): The convergence tolerance.

        Returns:
            Tuple[Dict[str, Any], Any]:
                - A dictionary containing the solve status, branch flows, reports, and iteration count.
                - The second element is always None.
        """
        # Normalize branches
        branches = self._normalize_branches(network)
        n_branches = len(branches)

        # Initialize flows
        branch_flows = [q_total.value / n_branches for _ in range(n_branches)]
        max_iter = 50
        tol_dp = tol
        converged = False

        for iteration in range(max_iter):
            dp_values = []
            for idx, branch in enumerate(branches):
                dp, _, _ = self._compute_network(branch, branch_flows[idx])
                dp_values.append(getattr(dp, "value", dp))

            dp_mean = sum(dp_values) / len(dp_values)
            corrections = [bf * dp_mean / max(dpv, 1e-12) for bf, dpv in zip(branch_flows, dp_values)]
            max_change = max(abs(c - bf) for c, bf in zip(corrections, branch_flows))
            branch_flows = corrections

            if max_change < tol_dp:
                converged = True
                break

        # Generate final reports
        final_reports = []
        for idx, branch in enumerate(branches):
            _, el_reports, _ = self._compute_network(branch, branch_flows[idx])
            for el in el_reports:
                el["branch_index"] = idx
            final_reports.extend(el_reports)

        # Return dict for consistent handling
        result_dict = {
            "success": converged,
            "branch_flows": branch_flows,
            "reports": final_reports,
            "iterations": iteration + 1,
        }
        return result_dict, None

    def _normalize_branches(self, network) -> list[list[Pipe]]:
        """
        Converts any PipelineNetwork or list of branches into a flat list of
        branches, where each branch is a list of Pipe objects.

        Args:
            network (Any): The network or list of pipes to normalize.

        Returns:
            list[list[Pipe]]: A flattened list of branches.
        """
        if isinstance(network, Pipe):
            return [[network]]
        elif isinstance(network, list):
            # Flatten each branch recursively
            normalized = []
            for item in network:
                normalized.extend(self._normalize_branches(item))
            return normalized
        elif isinstance(network, PipelineNetwork):
            branches = []
            if network.connection_type == "series":
                # Treat entire series network as a single branch
                series_branch = []
                for el in network.elements:
                    if isinstance(el, Pipe):
                        series_branch.append(el)
                    elif isinstance(el, PipelineNetwork):
                        # Flatten nested series inside this branch
                        nested_branches = self._normalize_branches(el)
                        # For series, nested branch is appended to current branch
                        if nested_branches:
                            series_branch.extend(nested_branches[0])
                branches.append(series_branch)
            elif network.connection_type == "parallel":
                # Each element is a separate branch
                for el in network.elements:
                    if isinstance(el, Pipe):
                        branches.append([el])
                    elif isinstance(el, PipelineNetwork):
                        nested = self._normalize_branches(el)
                        branches.extend(nested)
            return branches
        else:
            raise TypeError("Network must be Pipe, list of Pipes/branches, or PipelineNetwork-like object")




    # ---------------------- Diameter selection -------------------------------
    def _select_standard_diameter(self, ideal_d_m: float) -> Tuple[str, float]:
        """
        Maps a continuous ideal diameter (m) to nearest standard nominal.
        Picks the smallest standard size that yields diameter >= ideal.
        
        Args:
            ideal_d_m (float): The ideal diameter in meters.

        Returns:
            Tuple[str, float]: A tuple of the label and the value in meters.
        """
        standard_list = list_available_pipe_diameters()
        if not standard_list:
            raise ValueError("No standard pipe diameters available.")

        # Ensure numeric values
        standard_list_m = [d.to("m").value if isinstance(d, Diameter) else float(d) for d in standard_list]
        nearest = min(standard_list_m, key=lambda x: abs(x - ideal_d_m))
        label = f"{nearest*1000:.0f} mm"
        return label, nearest

    # ---------------------- Utility helpers ---------------------------------
    def _as_pressure(self, maybe_pressure: Any, default_unit: str = "Pa") -> Optional[Pressure]:
        """
        Converts input to a Pressure object.
        """
        if maybe_pressure is None:
            return None
        if isinstance(maybe_pressure, Pressure):
            return maybe_pressure
        return Pressure(float(maybe_pressure), default_unit)

    def _pump_gain_pa(self, pump: Any) -> Pressure:
        """
        Converts pump object head/pressure to Pa.
        Accepts `head` (m) or inlet/outlet pressures.
        """
        rho = getattr(pump, "density", None) or self._get_density().value
        pin = getattr(pump, "inlet_pressure", None)
        pout = getattr(pump, "outlet_pressure", None)
        if pin is not None and pout is not None:
            return self._as_pressure(pout).to("Pa") - self._as_pressure(pin).to("Pa")
        head = getattr(pump, "head", None)
        if head is not None:
            return Pressure(rho * G * float(head), "Pa")
        return Pressure(0.0, "Pa")

    def _equipment_dp_pa(self, eq: Any) -> Pressure:
        """
        Converts Equipment pressure_drop (assumed bar) to Pa if needed.
        """
        dp = getattr(eq, "pressure_drop", 0.0) or 0.0
        return Pressure(float(dp), "bar").to("Pa") if not isinstance(dp, Pressure) else dp

    def _fitting_dp_pa(self, fitting: Fitting, v: Velocity, f: Optional[float], d: Diameter) -> Pressure:
        """
        Compute fitting pressure drop using K or Le approaches.
        """
        rho = self._get_density().value
        v_val = v.value if hasattr(v, "value") else float(v)
        K = getattr(fitting, "K", None) or getattr(fitting, "K_factor", None) or getattr(fitting, "total_K", None)
        if K is not None:
            try:
                return Pressure(0.5 * rho * v_val * v_val * float(K), "Pa")
            except (TypeError, ValueError):
                pass
        Le = getattr(fitting, "Le", None) or getattr(fitting, "equivalent_length", None)
        if Le is not None:
            if f is None:
                Re = self._reynolds(v, d)
                f_val = self._friction_factor(Re, d)
            else:
                f_val = float(f)
            d_m = d.to("m").value
            return Pressure(float(f_val) * (float(Le) / d_m) * 0.5 * rho * v_val * v_val, "Pa")
        return Pressure(0.0, "Pa")

    # -------------------- RUN / SUMMARY --------------------------------------

    def run(self, tol: float = 1e-5) -> "PipelineResults":
        """
        Runs the pipeline/network solver and returns a PipelineResults object.

        Handles single pipes, series networks, and parallel subnetworks.
        Reports are flattened so all components (pipes, fittings, etc.) are included.

        Args:
            tol (float): The convergence tolerance for the solver.

        Returns:
            PipelineResults: An object containing the simulation results.

        Raises:
            ValueError: If the engine is not fitted with network, flow, or fluid data.
            TypeError: If the network type is unsupported.
        """
        net = self.data.get("network", None)
        q_in = self.data.get("flow_rate", None)
        fluid = self.data.get("fluid", None)

        if net is None or q_in is None or fluid is None:
            raise ValueError("Engine is not fitted. Please call fit() first.")

        results_out: Dict[str, Any] = {}

        # -----------------------------
        # Helper to recursively solve pipes and networks
        # -----------------------------
        def _solve_and_collect(node_or_net, flow_rate) -> list[dict]:
            reports = []

            if isinstance(node_or_net, Pipe):
                # Solve single pipe
                pipe_res = self._pipe_calculation(node_or_net, flow_rate)
                # Convert to dict for flattened reporting
                reports.append(pipe_res.as_dict() if hasattr(pipe_res, "as_dict") else pipe_res)

            elif isinstance(node_or_net, PipelineNetwork):
                # Ensure non-zero initial flows
                for p in node_or_net.get_all_pipes():
                    if p.flow_rate is None or getattr(p.flow_rate, "value", 0) <= 0:
                        p.flow_rate = VolumetricFlowRate(1e-4, "m3/s")

                # Solve network
                solved_dict, branch_flows = self._solve_network_dual(node_or_net, flow_rate, tol)

                # Solve all pipes recursively (main + subnetworks)
                for sub in getattr(node_or_net, "subnetworks", []):
                    reports.extend(_solve_and_collect(sub, flow_rate))
                for p in node_or_net.get_all_pipes():
                    pipe_res = self._pipe_calculation(p, p.flow_rate)
                    reports.append(pipe_res.as_dict() if hasattr(pipe_res, "as_dict") else pipe_res)
            else:
                raise TypeError(f"Unsupported network type: {type(node_or_net)}")

            return reports

        # -----------------------------
        # Single pipe
        # -----------------------------
        if isinstance(net, Pipe):
            comp_list = _solve_and_collect(net, q_in)

            total_dp_pa = float(comp_list[0].get("pressure_drop_Pa", 0.0))
            rho_val = fluid.density.value
            total_head_m = total_dp_pa / (rho_val * G)
            pump_eff = self.data.get("pump_efficiency", 0.7)
            shaft_power_kw = (total_dp_pa * q_in.value) / (1000.0 * pump_eff)

            results_out["mode"] = "single"
            results_out["summary"] = {
                "inlet_flow_m3s": q_in.value,
                "total_pressure_drop_Pa": total_dp_pa,
                "total_head_m": total_head_m,
                "pump_shaft_power_kW": shaft_power_kw,
            }
            results_out["components"] = comp_list

        # -----------------------------
        # Network (series or parallel)
        # -----------------------------
        elif isinstance(net, PipelineNetwork):
            comp_list = _solve_and_collect(net, q_in)

            # Compute total pressure drop, head, and pump power
            total_dp_pa = sum(float(r.get("pressure_drop_Pa", 0.0)) for r in comp_list)
            rho_val = fluid.density().value
            total_head_m = total_dp_pa / (rho_val * G)
            pump_eff = self.data.get("pump_efficiency", 0.7)
            shaft_power_kw = (total_dp_pa * q_in.value) / (1000.0 * pump_eff)

            results_out["mode"] = "network"
            results_out["summary"] = {
                "inlet_flow_m3s": q_in.value,
                "total_pressure_drop_Pa": total_dp_pa,
                "total_head_m": total_head_m,
                "pump_shaft_power_kW": shaft_power_kw,
                # optional: solver info if _solve_network_dual returns it
            }
            results_out["components"] = comp_list

        else:
            raise TypeError(f"Unsupported network type: {type(net)}")

        return PipelineResults(results_out)




    def summary(self) -> Optional[PipelineResults]:
        """
        Returns the summary of the last run.
        """
        if not self._results:
            print("No results available for summary.")
            return None
        return self._results.summary()

    # ---------------------- Backwards compatibility / helpers ---------------
    def _ensure_pipe_object(self) -> Pipe:
        """
        Constructs a Pipe object from engine data if not provided.
        """
        if isinstance(self.data.get("pipe"), Pipe):
            return self.data["pipe"]
        d = self.data.get("diameter")
        L = self.data.get("length") or Length(1.0, "m")
        if d is None:
            # compute optimum
            ideal = OptimumPipeDiameter(flow_rate=self._infer_flowrate(), density=self._get_density()).calculate()
            p = Pipe(name="Main Pipe", nominal_diameter=ideal, length=L)
            self.data["pipe"] = p
            return p
        if not isinstance(d, Diameter):
            d = _ensure_diameter_obj(d, self.data.get("assume_mm_for_numbers", True))
        p = Pipe(name="Main Pipe", internal_diameter=d, length=L)
        self.data["pipe"] = p
        return p

# ---------------------- Diameter helper ---------------------------------
    def _internal_diameter_m(self, element: Any = None) -> Diameter:
        """
        Returns the nominal internal diameter as a Diameter object in meters.
        Handles Pipe, Fitting (via parent pipe), and falls back to a default value.
        """
        if element is None:
            # fallback: default diameter
            return Diameter(0.1, "m")

        if hasattr(element, "nominal_diameter"):
            d = element.nominal_diameter
            if isinstance(d, Diameter):
                return d.to("m")
            elif isinstance(d, (int, float)):
                return Diameter(d, "m")  # wrap float in Diameter
            else:
                raise TypeError(f"Unsupported diameter type: {type(d)}")

        # For Fitting, use parent pipe
        if isinstance(element, Fitting) and hasattr(element, "parent_pipe") and element.parent_pipe is not None:
            return self._internal_diameter_m(element.parent_pipe)

        # fallback
        return Diameter(0.1, "m")


    
    
    
    def _resolve_internal_diameter(self, pipe: Pipe) -> Diameter:
        """
        Return internal diameter as a Diameter object, safely.

        Args:
            pipe (Pipe): The pipe object to get the diameter from.

        Returns:
            Diameter: The resolved diameter object.
        """
        if getattr(pipe, "internal_diameter", None):
            return pipe.internal_diameter
        if getattr(pipe, "nominal_diameter", None):
            d = pipe.nominal_diameter
            return d if isinstance(d, Diameter) else Diameter(float(d), "m")
        if getattr(self, "diameter", None):
            d = self.diameter
            return d if isinstance(d, Diameter) else Diameter(float(d), "m")

        # compute optimum and pick nearest standard
        opt_d = OptimumPipeDiameter(flow_rate=self._infer_flowrate(), density=self._get_density()).calculate()
        _, std_d = self._select_standard_diameter(opt_d.to("m").value)
        return std_d


    def _select_standard_diameter(self, ideal_d_m: float) -> Tuple[str, Diameter]:
        """
        Maps a continuous ideal diameter (m) to the nearest standard nominal pipe size.

        Always returns (label, Diameter), never a raw float.
        Picks the smallest standard size that is >= ideal_d_m.

        Args:
            ideal_d_m (float): The ideal diameter in meters.

        Returns:
            Tuple[str, Diameter]: The label and the Diameter object.

        Raises:
            ValueError: If no standard pipe diameters are available.
        """
        candidates: List[Tuple[str, Diameter]] = []

        for nominal in list_available_pipe_diameters():
            try:
                d_internal = nominal  # already a Diameter object
                if not isinstance(d_internal, Diameter):
                    d_internal = Diameter(float(d_internal), "m")
                candidates.append((f"{nominal} mm", d_internal))
            except Exception:
                continue

        # sort ascending by internal diameter
        candidates.sort(key=lambda x: x[1].to("m").value)

        for label, d in candidates:
            if d.to("m").value >= ideal_d_m:
                return label, d

        # fallback: return largest available
        if candidates:
            return candidates[-1][0], candidates[-1][1]

        raise ValueError("No standard pipe diameters available in catalog")
    
    def _solve_for_diameter(self, **kwargs):
        """
        Sizing a single pipeline to meet either a target velocity or an available pressure drop.
        The function iteratively tests three standard pipe sizes around an initial guess
        based on recommended velocities to find the best fit.

        Args:
            **kwargs: Configuration parameters, including 'fluid', 'flow_rate',
                      and 'available_dp' (optional).

        Returns:
            PipelineResults: An object containing the sizing results.
        """
        import math

        # Helper to safely set diameter on a pipe object
        def _set_pipe_diameter_m(pipe_obj, D_m: float):
            try:
                pipe_obj.internal_diameter = Diameter(D_m, "m")
            except Exception:
                pass
            try:
                pipe_obj.diameter = Diameter(D_m, "m")
            except Exception:
                pass

        # ---------------------------
        # Inputs
        # ---------------------------
        fluid = kwargs.get("fluid") or self.data.get("fluid")
        flow_rate = self._infer_flowrate()
        available_dp = kwargs.get("available_dp") or self.data.get("available_dp")
        pump_eff = kwargs.get("pump_efficiency", self.data.get("pump_efficiency", 0.75))
        G = 9.80665  # gravitational acceleration

        if not fluid or not flow_rate:
            raise ValueError("flow_rate and fluid are required for diameter sizing.")

        # Recommended velocity range
        vel_range = get_recommended_velocity(getattr(fluid, "name", "").strip().lower().replace(" ", "_"))
        if vel_range is None:
            v_min, v_max = 0.5, 100.0
        elif isinstance(vel_range, tuple):
            v_min, v_max = vel_range
        else:
            v_min = v_max = float(vel_range)

        # Ensure pipe object
        pipe = self._ensure_pipe_object()

        # Initial diameter guess based on average recommended velocity
        v_start = 0.5 * (v_min + v_max)
        D_initial = math.sqrt(4.0 * flow_rate.value / (math.pi * v_start))

        # Standard diameters
        all_standard_diameters = list_available_pipe_diameters()
        selected_diameter_obj = next((d for d in all_standard_diameters if d.value >= D_initial), None)
        selected_index = all_standard_diameters.index(selected_diameter_obj) if selected_diameter_obj else len(all_standard_diameters) - 1

        if selected_diameter_obj is None and all_standard_diameters:
            selected_diameter_obj = all_standard_diameters[-1]

        D_std_next = selected_diameter_obj
        D_std_before = all_standard_diameters[selected_index - 1] if selected_index > 0 else None
        D_std_next_next = all_standard_diameters[selected_index + 1] if selected_index < len(all_standard_diameters) - 1 else None

        diameters_to_test = [d for d in [D_std_before, D_std_next, D_std_next_next] if d is not None]
        if not diameters_to_test:
            raise RuntimeError("Could not find any suitable standard diameter to test.")

        # print(f"Testing diameters: {[d.to('in') for d in diameters_to_test]}") # For debugging

        # ---------------------------
        # Run calculations for each diameter
        # ---------------------------
        results_list = []
        for D_test in diameters_to_test:
            _set_pipe_diameter_m(pipe, D_test.value)
            calc = self._pipe_calculation(pipe, flow_rate)
            results_list.append({"diameter": D_test, "calc": calc})

        # ---------------------------
        # Select result
        # ---------------------------
        if available_dp:
            # Pick diameter with lowest pressure drop
            best_result = min(
                results_list,
                key=lambda r: getattr(r["calc"]["pressure_drop"], "value", r["calc"]["pressure_drop"])
            )
            final_calc = best_result["calc"]
            D_final = best_result["diameter"]
            print(f"✅ Found optimal diameter for available pressure drop.")
            print(f"   Selected Diameter: {D_final.to('in')} ({D_final.value:.3f} m)")
            print(f"   Calculated Pressure Drop: {getattr(final_calc['pressure_drop'], 'value', final_calc['pressure_drop']):.2f} Pa")
        else:
            print("🔍 No available pressure drop given. Displaying results for three standard diameters:")
            for result in results_list:
                D_final = result["diameter"]
                final_calc = result["calc"]
                v_val = getattr(final_calc.get("velocity"), "value", final_calc.get("velocity"))
                print(f"\n--- Results for Diameter: {D_final.to('in')} ({D_final.value:.3f} m) ---")
                print(f"Velocity: {v_val:.2f} m/s")
                print(f"Reynolds: {final_calc.get('reynolds'):.2f}")
                print(f"Total Pressure Drop: {getattr(final_calc.get('pressure_drop'), 'value', final_calc.get('pressure_drop')):.2f} Pa")
            final_calc = results_list[len(results_list) // 2]["calc"]
            D_final = results_list[len(results_list) // 2]["diameter"]

        # ---------------------------
        # Compute head and power
        # ---------------------------
        total_dp_pa = getattr(final_calc["pressure_drop"], "value", final_calc["pressure_drop"])
        dens_obj = getattr(fluid, "density", 1000.0)
        if callable(dens_obj):
            dens_obj = dens_obj()
        rho_val = getattr(dens_obj, "value", dens_obj)

        total_head_m = total_dp_pa / (rho_val * G) if rho_val else float("inf")
        shaft_power_kw = (total_dp_pa * flow_rate.value) / (1000.0 * pump_eff)
        v_final = float(getattr(final_calc.get("velocity"), "value", final_calc.get("velocity")))

        if not (v_min <= v_final <= v_max):
            print(f"⚠️ Warning: Final velocity {v_final:.2f} m/s outside recommended range ({v_min:.2f}-{v_max:.2f} m/s) for {getattr(fluid, 'name', 'fluid')}.")

        results_out = {
            "network_name": pipe.name,
            "mode": "single_pipe",
            "summary": {
                "flow_m3s": flow_rate.value,
                "total_pressure_drop_Pa": total_dp_pa,
                "total_head_m": total_head_m,
                "pump_shaft_power_kW": shaft_power_kw,
                "velocity": v_final,
                "reynolds": final_calc.get("reynolds"),
                "friction_factor": final_calc.get("friction_factor"),
                "calculated_diameter_m": D_final.value,
            },
            "components": [{
                "type": "pipe",
                "name": pipe.name,
                "length": pipe.length,
                "diameter": getattr(pipe, "internal_diameter", getattr(pipe, "diameter", None)),
                "velocity": v_final,
                "reynolds": final_calc.get("reynolds"),
                "friction_factor": final_calc.get("friction_factor"),
                "major_dp": final_calc.get("major_dp"),
                "minor_dp": final_calc.get("minor_dp"),
                "elevation_dp": final_calc.get("elevation_dp"),
                "total_dp": final_calc.get("pressure_drop"),
            }],
        }

        return PipelineResults(results_out)



    
    def _solve_for_diameter_network(self, network, **kwargs):
        """
        Iteratively sizes each pipe in a network based on flow, ΔP, and recommended velocities.
        Each pipe is sized sequentially; fittings and equipment are included in calculations.

        Args:
            network (PipelineNetwork): The network to size.
            **kwargs: Configuration parameters.

        Returns:
            PipelineResults: The simulation results.
        """

        import math
        G = 9.80665

        fluid = kwargs.get("fluid") or self.data.get("fluid")
        if not fluid:
            raise ValueError("Fluid must be provided for network diameter sizing.")

        # Recommended velocity ranges
        RECOMMENDED_VELOCITIES = {
            "carbon_dioxide": (8.0, 15.0),
            "organic_liquids": (1.8, 2.0),
            "water": (1.0, 2.5),
            # Add more fluids as needed
        }
        fluid_type = getattr(fluid, "name", "").strip().lower().replace(" ", "_")
        v_min, v_max = RECOMMENDED_VELOCITIES.get(fluid_type, (0.5, 100.0))
        pump_eff = kwargs.get("pump_efficiency", self.data.get("pump_efficiency", 0.75))

        all_results = []

        # Loop over pipes in the network
        for pipe in getattr(network, "pipes", []):
            flow_rate = self._infer_flowrate(pipe)
            available_dp = kwargs.get("available_dp")  # optional per pipe

            # Initial diameter guess based on average recommended velocity
            v_target = 0.5 * (v_min + v_max)
            D_final = math.sqrt(4 * flow_rate.value / (math.pi * v_target))
            pipe.diameter = Diameter(D_final, "m")

            # Iterative sizing
            max_iterations = 20
            for i in range(max_iterations):
                calc = self._pipe_calculation(pipe, flow_rate)
                total_dp_pa = getattr(calc["pressure_drop"], "value", calc["pressure_drop"])
                v_calc = float(getattr(calc["velocity"], "value", calc["velocity"]))

                # ΔP factor if available
                dp_factor = (total_dp_pa / getattr(available_dp, "value", available_dp) if available_dp else 1.0) ** 0.5

                # Velocity adjustment factor
                vel_factor = 1.0
                if v_calc < v_min:
                    vel_factor = (v_calc / v_min) ** 0.5
                elif v_calc > v_max:
                    vel_factor = (v_calc / v_max) ** 0.5

                adjust_factor = max(dp_factor, vel_factor)
                if abs(adjust_factor - 1.0) < 0.01:
                    break  # converged

                D_final *= adjust_factor
                pipe.diameter = Diameter(D_final, "m")

            # Velocity warning
            if v_calc < v_min or v_calc > v_max:
                print(f"⚠️ Warning: Pipe '{pipe.name}' velocity {v_calc:.2f} m/s outside recommended ({v_min}-{v_max}) m/s")

            # Compute head and pump power
            rho_val = getattr(getattr(fluid, "density", 1000.0), "value", getattr(fluid.density, "value", 1000.0))
            total_head = total_dp_pa / (rho_val * G)
            shaft_power_kw = (total_dp_pa * flow_rate.value) / (1000.0 * pump_eff)

            all_results.append({
                "network_name": pipe.name,
                "mode": "network_pipe",
                "summary": {
                    "flow_m3s": flow_rate.value,
                    "total_pressure_drop_Pa": total_dp_pa,
                    "total_head_m": total_head,
                    "pump_shaft_power_kW": shaft_power_kw,
                    "velocity": v_calc,
                    "reynolds": calc.get("reynolds"),
                    "friction_factor": calc.get("friction_factor"),
                    "calculated_diameter_m": D_final,
                },
                "components": [{
                    "type": "pipe",
                    "name": pipe.name,
                    "length": pipe.length,
                    "diameter": getattr(pipe, "internal_diameter", getattr(pipe, "diameter", None)),
                    "velocity": v_calc,
                    "reynolds": calc.get("reynolds"),
                    "friction_factor": calc.get("friction_factor"),
                    "major_dp": calc.get("major_dp"),
                    "minor_dp": calc.get("minor_dp"),
                    "elevation_dp": calc.get("elevation_dp"),
                    "total_dp": calc.get("pressure_drop"),
                }],
            })

        return PipelineResults({"all_simulation_results": all_results})
