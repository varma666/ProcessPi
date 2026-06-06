# Source Inventory Audit

Generated before documentation edits from every `*.py` file under `processpi/`.

## Package inventory

- `processpi.__init__` — 1 module(s)
- `processpi.calculations` — 56 module(s)
- `processpi.cli` — 1 module(s)
- `processpi.components` — 37 module(s)
- `processpi.constants` — 1 module(s)
- `processpi.equipment` — 12 module(s)
- `processpi.integration` — 2 module(s)
- `processpi.pipelines` — 17 module(s)
- `processpi.streams` — 3 module(s)
- `processpi.units` — 25 module(s)

## Module, class, and function inventory

### `processpi.__init__`

- Source: `processpi/__init__.py`
- Public classes/functions: none

### `processpi.calculations.__init__`

- Source: `processpi/calculations/__init__.py`
- Public classes/functions: none

### `processpi.calculations.base`

- Source: `processpi/calculations/base.py`
- Public classes:
  - `CalculationBase`; methods: validate_inputs, calculate, get_inputs, to_dict

### `processpi.calculations.engine`

- Source: `processpi/calculations/engine.py`
- Public classes:
  - `CalculationEngine`; methods: register_calculation, calculate

### `processpi.calculations.fluids.__init__`

- Source: `processpi/calculations/fluids/__init__.py`
- Public classes/functions: none

### `processpi.calculations.fluids.flow_type`

- Source: `processpi/calculations/fluids/flow_type.py`
- Public classes:
  - `TypeOfFlow`; methods: validate_inputs, calculate

### `processpi.calculations.fluids.friction_factor_colebrookwhite`

- Source: `processpi/calculations/fluids/friction_factor_colebrookwhite.py`
- Public classes:
  - `ColebrookWhite`; methods: validate_inputs, calculate

### `processpi.calculations.fluids.optimium_pipe_dia`

- Source: `processpi/calculations/fluids/optimium_pipe_dia.py`
- Public classes:
  - `OptimumPipeDiameter`; methods: validate_inputs, calculate

### `processpi.calculations.fluids.pressure_drop_darcy`

- Source: `processpi/calculations/fluids/pressure_drop_darcy.py`
- Public classes:
  - `PressureDropDarcy`; methods: validate_inputs, calculate

### `processpi.calculations.fluids.pressure_drop_fanning`

- Source: `processpi/calculations/fluids/pressure_drop_fanning.py`
- Public classes:
  - `PressureDropFanning`; methods: validate_inputs, calculate

### `processpi.calculations.fluids.pressure_drop_hazen_williams`

- Source: `processpi/calculations/fluids/pressure_drop_hazen_williams.py`
- Public classes:
  - `PressureDropHazenWilliams`; methods: validate_inputs, calculate

### `processpi.calculations.fluids.pump_power`

- Source: `processpi/calculations/fluids/pump_power.py`
- Public classes:
  - `PumpPower`; methods: validate_inputs, calculate

### `processpi.calculations.fluids.reynolds_number`

- Source: `processpi/calculations/fluids/reynolds_number.py`
- Public classes:
  - `ReynoldsNumber`; methods: validate_inputs, calculate

### `processpi.calculations.fluids.velocity`

- Source: `processpi/calculations/fluids/velocity.py`
- Public classes:
  - `FluidVelocity`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.__init__`

- Source: `processpi/calculations/heat_transfer/__init__.py`
- Public classes/functions: none

### `processpi.calculations.heat_transfer.biot`

- Source: `processpi/calculations/heat_transfer/biot.py`
- Public classes:
  - `BiotNumber`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.boiling_chen`

- Source: `processpi/calculations/heat_transfer/boiling_chen.py`
- Public classes:
  - `ChenBoiling`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.combined_modes`

- Source: `processpi/calculations/heat_transfer/combined_modes.py`
- Public classes:
  - `ConductionConvectionCombined`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.condensation`

- Source: `processpi/calculations/heat_transfer/condensation.py`
- Public classes:
  - `CondensingVapourFilm`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.condensation_dropwise`

- Source: `processpi/calculations/heat_transfer/condensation_dropwise.py`
- Public classes:
  - `DropwiseCondensation`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.condensation_nusselt`

- Source: `processpi/calculations/heat_transfer/condensation_nusselt.py`
- Public classes:
  - `NusseltCondensation`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.conduction_heat_loss`

- Source: `processpi/calculations/heat_transfer/conduction_heat_loss.py`
- Public classes:
  - `ConductionHeatLoss`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.convection_heat_loss`

- Source: `processpi/calculations/heat_transfer/convection_heat_loss.py`
- Public classes:
  - `ConvectionHeatLoss`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.crossflow_tube`

- Source: `processpi/calculations/heat_transfer/crossflow_tube.py`
- Public classes:
  - `CrossFlowSingleTube`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.fourier`

- Source: `processpi/calculations/heat_transfer/fourier.py`
- Public classes:
  - `FourierNumber`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.fourierlaw`

- Source: `processpi/calculations/heat_transfer/fourierlaw.py`
- Public classes:
  - `FourierLaw`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.grashof`

- Source: `processpi/calculations/heat_transfer/grashof.py`
- Public classes:
  - `GrashofNumber`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.heat_exchanger`

- Source: `processpi/calculations/heat_transfer/heat_exchanger.py`
- Public classes:
  - `SensibleHeatDuty`; methods: validate_inputs, calculate
  - `LatentHeatDuty`; methods: validate_inputs, calculate
  - `KernNusselt`; methods: validate_inputs, calculate
  - `ConvectiveCoefficient`; methods: validate_inputs, calculate
  - `DarcyPressureDrop`; methods: validate_inputs, calculate
  - `ReynoldsFromProperties`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.heat_exchanger_area`

- Source: `processpi/calculations/heat_transfer/heat_exchanger_area.py`
- Public classes:
  - `HeatExchangerArea`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.hx_kern`

- Source: `processpi/calculations/heat_transfer/hx_kern.py`
- Public classes:
  - `SensibleDuty`; methods: validate_inputs, calculate
  - `LatentDuty`; methods: validate_inputs, calculate
  - `Reynolds`; methods: validate_inputs, calculate
  - `DittusBoelter`; methods: validate_inputs, calculate
  - `KernShellNu`; methods: validate_inputs, calculate
  - `ConvectiveH`; methods: validate_inputs, calculate
  - `TubeCountFromArea`; methods: validate_inputs, calculate
  - `ShellDiameterEstimate`; methods: validate_inputs, calculate
  - `DarcyDrop`; methods: validate_inputs, calculate
  - `CondensationHTC`; methods: validate_inputs, calculate
  - `BoilingHTC`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.lmtd`

- Source: `processpi/calculations/heat_transfer/lmtd.py`
- Public classes:
  - `LMTD`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.newton_cooling`

- Source: `processpi/calculations/heat_transfer/newton_cooling.py`
- Public classes:
  - `NewtonCooling`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.ntu`

- Source: `processpi/calculations/heat_transfer/ntu.py`
- Public classes:
  - `NTUHeatExchanger`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.nusselt`

- Source: `processpi/calculations/heat_transfer/nusselt.py`
- Public classes:
  - `NusseltNumber`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.overall_u`

- Source: `processpi/calculations/heat_transfer/overall_u.py`
- Public classes:
  - `OverallHeatTransferCoefficient`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.peclet`

- Source: `processpi/calculations/heat_transfer/peclet.py`
- Public classes:
  - `PecletNumber`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.prandtl`

- Source: `processpi/calculations/heat_transfer/prandtl.py`
- Public classes:
  - `PrandtlNumber`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.radial_cylinder`

- Source: `processpi/calculations/heat_transfer/radial_cylinder.py`
- Public classes:
  - `RadialHeatFlowCylinder`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.radiation_blackbody`

- Source: `processpi/calculations/heat_transfer/radiation_blackbody.py`
- Public classes:
  - `BlackbodyRadiation`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.radiation_exchange`

- Source: `processpi/calculations/heat_transfer/radiation_exchange.py`
- Public classes:
  - `RadiationExchange`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.radiation_greybody`

- Source: `processpi/calculations/heat_transfer/radiation_greybody.py`
- Public classes:
  - `GreybodyRadiation`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.radiation_viewfactor`

- Source: `processpi/calculations/heat_transfer/radiation_viewfactor.py`
- Public classes:
  - `RadiationWithViewFactor`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.resistance`

- Source: `processpi/calculations/heat_transfer/resistance.py`
- Public classes:
  - `ThermalResistanceSeries`; methods: validate_inputs, calculate
  - `ThermalResistanceParallel`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.reyleigh`

- Source: `processpi/calculations/heat_transfer/reyleigh.py`
- Public classes:
  - `RayleighNumber`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.rohsenow_boiling`

- Source: `processpi/calculations/heat_transfer/rohsenow_boiling.py`
- Public classes:
  - `RohsenowBoiling`; methods: validate_inputs, calculate

### `processpi.calculations.heat_transfer.stefan_boltzmann`

- Source: `processpi/calculations/heat_transfer/stefan_boltzmann.py`
- Public classes:
  - `StefanBoltzmann`; methods: validate_inputs, calculate

### `processpi.calculations.mass_transfer.__init__`

- Source: `processpi/calculations/mass_transfer/__init__.py`
- Public classes/functions: none

### `processpi.calculations.mass_transfer.distillation_stage_count`

- Source: `processpi/calculations/mass_transfer/distillation_stage_count.py`
- Public classes:
  - `DistillationStageCount`; methods: validate_inputs, calculate

### `processpi.calculations.mass_transfer.drying_rate`

- Source: `processpi/calculations/mass_transfer/drying_rate.py`
- Public classes:
  - `DryingRate`; methods: validate_inputs, calculate

### `processpi.calculations.reaction_engineering.__init__`

- Source: `processpi/calculations/reaction_engineering/__init__.py`
- Public classes/functions: none

### `processpi.calculations.reaction_engineering.catalyst_activity`

- Source: `processpi/calculations/reaction_engineering/catalyst_activity.py`
- Public classes:
  - `CatalystActivity`; methods: validate_inputs, calculate

### `processpi.calculations.reaction_engineering.reaction_rate`

- Source: `processpi/calculations/reaction_engineering/reaction_rate.py`
- Public classes:
  - `ReactionRate`; methods: validate_inputs, calculate

### `processpi.calculations.reaction_engineering.residence_time`

- Source: `processpi/calculations/reaction_engineering/residence_time.py`
- Public classes:
  - `ResidenceTime`; methods: validate_inputs, calculate

### `processpi.calculations.thermodynamics.__init__`

- Source: `processpi/calculations/thermodynamics/__init__.py`
- Public classes/functions: none

### `processpi.calculations.thermodynamics.enthalpy_change`

- Source: `processpi/calculations/thermodynamics/enthalpy_change.py`
- Public classes:
  - `EnthalpyChange`; methods: validate_inputs, calculate

### `processpi.calculations.thermodynamics.entropy_change`

- Source: `processpi/calculations/thermodynamics/entropy_change.py`
- Public classes:
  - `EntropyChange`; methods: validate_inputs, calculate

### `processpi.calculations.thermodynamics.heat_of_vaporization`

- Source: `processpi/calculations/thermodynamics/heat_of_vaporization.py`
- Public classes:
  - `HeatOfVaporization`; methods: validate_inputs, calculate

### `processpi.cli`

- Source: `processpi/cli.py`
- Public functions:
  - `build_parser()`
  - `main(argv: list[str] | None=None)`

### `processpi.components.__init__`

- Source: `processpi/components/__init__.py`
- Public classes/functions: none

### `processpi.components.aceticacid`

- Source: `processpi/components/aceticacid.py`
- Public classes:
  - `AceticAcid`; methods: none

### `processpi.components.acetone`

- Source: `processpi/components/acetone.py`
- Public classes:
  - `Acetone`; methods: none

### `processpi.components.acrylicacid`

- Source: `processpi/components/acrylicacid.py`
- Public classes:
  - `AcrylicAcid`; methods: none

### `processpi.components.air`

- Source: `processpi/components/air.py`
- Public classes:
  - `Air`; methods: none

### `processpi.components.ammonia`

- Source: `processpi/components/ammonia.py`
- Public classes:
  - `Ammonia`; methods: specific_heat

### `processpi.components.base`

- Source: `processpi/components/base.py`
- Public classes:
  - `PropertyMethod`; methods: none
  - `Component`; methods: name, formula, molecular_weight, phase, density, specific_heat, viscosity, thermal_conductivity, vapor_pressure, enthalpy

### `processpi.components.benzene`

- Source: `processpi/components/benzene.py`
- Public classes:
  - `Benzene`; methods: specific_heat, hx_data, httype

### `processpi.components.benzoicacid`

- Source: `processpi/components/benzoicacid.py`
- Public classes:
  - `BenzoicAcid`; methods: none

### `processpi.components.bromine`

- Source: `processpi/components/bromine.py`
- Public classes:
  - `Bromine`; methods: none

### `processpi.components.butane`

- Source: `processpi/components/butane.py`
- Public classes:
  - `Butane`; methods: none

### `processpi.components.carbondioxide`

- Source: `processpi/components/carbondioxide.py`
- Public classes:
  - `Carbondioxide`; methods: none

### `processpi.components.carbonmonoxide`

- Source: `processpi/components/carbonmonoxide.py`
- Public classes:
  - `CarbonMonoxide`; methods: specific_heat

### `processpi.components.carbontetrachloride`

- Source: `processpi/components/carbontetrachloride.py`
- Public classes:
  - `CarbonTetrachloride`; methods: none

### `processpi.components.chlorine`

- Source: `processpi/components/chlorine.py`
- Public classes:
  - `Chlorine`; methods: none

### `processpi.components.chlorobenzene`

- Source: `processpi/components/chlorobenzene.py`
- Public classes:
  - `ChloroBenzene`; methods: none

### `processpi.components.chloroform`

- Source: `processpi/components/chloroform.py`
- Public classes:
  - `Chloroform`; methods: none

### `processpi.components.chloromethane`

- Source: `processpi/components/chloromethane.py`
- Public classes:
  - `ChloroMethane`; methods: none

### `processpi.components.constants`

- Source: `processpi/components/constants.py`
- Public classes/functions: none

### `processpi.components.cyanogen`

- Source: `processpi/components/cyanogen.py`
- Public classes:
  - `Cyanogen`; methods: none

### `processpi.components.cyclohexene`

- Source: `processpi/components/cyclohexene.py`
- Public classes:
  - `Cyclohexane`; methods: none

### `processpi.components.ethane`

- Source: `processpi/components/ethane.py`
- Public classes:
  - `Ethane`; methods: specific_heat

### `processpi.components.ethanol`

- Source: `processpi/components/ethanol.py`
- Public classes:
  - `Ethanol`; methods: none

### `processpi.components.ethylacetate`

- Source: `processpi/components/ethylacetate.py`
- Public classes:
  - `EthlylAcetate`; methods: none

### `processpi.components.ethylene`

- Source: `processpi/components/ethylene.py`
- Public classes:
  - `Ethlylene`; methods: none

### `processpi.components.fluorine`

- Source: `processpi/components/fluorine.py`
- Public classes:
  - `Fluorine`; methods: none

### `processpi.components.fluorobenzene`

- Source: `processpi/components/fluorobenzene.py`
- Public classes:
  - `FluoroBenzene`; methods: none

### `processpi.components.formicacid`

- Source: `processpi/components/formicacid.py`
- Public classes:
  - `FormicAcid`; methods: none

### `processpi.components.gas`

- Source: `processpi/components/gas.py`
- Public classes:
  - `Gas`; methods: density

### `processpi.components.inorganic_liquid`

- Source: `processpi/components/inorganic_liquid.py`
- Public classes:
  - `InorganicLiquid`; methods: none

### `processpi.components.methanol`

- Source: `processpi/components/methanol.py`
- Public classes:
  - `Methanol`; methods: none

### `processpi.components.oil`

- Source: `processpi/components/oil.py`
- Public classes:
  - `Oil`; methods: hx_data, httype

### `processpi.components.organic_liquid`

- Source: `processpi/components/organic_liquid.py`
- Public classes:
  - `OrganicLiquid`; methods: hx_data, httype

### `processpi.components.steam`

- Source: `processpi/components/steam.py`
- Public classes:
  - `Steam`; methods: density, specific_heat, viscosity, thermal_conductivity, vapor_pressure, enthalpy

### `processpi.components.toluene`

- Source: `processpi/components/toluene.py`
- Public classes:
  - `Toluene`; methods: hx_data, httype

### `processpi.components.vapor`

- Source: `processpi/components/vapor.py`
- Public classes:
  - `Vapor`; methods: none

### `processpi.components.water`

- Source: `processpi/components/water.py`
- Public classes:
  - `Water`; methods: density, hx_data, httype

### `processpi.constants`

- Source: `processpi/constants.py`
- Public classes/functions: none

### `processpi.equipment.__init__`

- Source: `processpi/equipment/__init__.py`
- Public classes/functions: none

### `processpi.equipment.base`

- Source: `processpi/equipment/base.py`
- Public classes:
  - `PortMap`; methods: add_port, has_port, values_ordered
  - `Equipment`; methods: connect_inlet, connect_outlet, attach_stream

### `processpi.equipment.heatexchangers.__init__`

- Source: `processpi/equipment/heatexchangers/__init__.py`
- Public classes/functions: none

### `processpi.equipment.heatexchangers.base`

- Source: `processpi/equipment/heatexchangers/base.py`
- Public classes:
  - `HeatExchangerBaseMixin`; methods: none
  - `HeatExchanger`; methods: heat_duty, lmtd, area, overall_u, design

### `processpi.equipment.heatexchangers.bell_delaware`

- Source: `processpi/equipment/heatexchangers/bell_delaware.py`
- Public classes:
  - `BellDelawareHX`; methods: design

### `processpi.equipment.heatexchangers.condenser`

- Source: `processpi/equipment/heatexchangers/condenser.py`
- Public classes:
  - `CondenserHX`; methods: design, rate

### `processpi.equipment.heatexchangers.double_pipe`

- Source: `processpi/equipment/heatexchangers/double_pipe.py`
- Public classes:
  - `DoublePipeHX`; methods: design, rate

### `processpi.equipment.heatexchangers.engine`

- Source: `processpi/equipment/heatexchangers/engine.py`
- Public classes:
  - `HeatExchangerResults`; methods: summary, detailed_summary, trace, debug_summary
  - `HeatExchangerEngine`; methods: fit, run, summary, results

### `processpi.equipment.heatexchangers.evaporator`

- Source: `processpi/equipment/heatexchangers/evaporator.py`
- Public classes:
  - `EvaporatorHX`; methods: design, rate

### `processpi.equipment.heatexchangers.reboiler`

- Source: `processpi/equipment/heatexchangers/reboiler.py`
- Public classes:
  - `ReboilerHX`; methods: design, rate

### `processpi.equipment.heatexchangers.shell_and_tube`

- Source: `processpi/equipment/heatexchangers/shell_and_tube.py`
- Public classes:
  - `ShellAndTubeHX`; methods: rate, design

### `processpi.equipment.heatexchangers.standards`

- Source: `processpi/equipment/heatexchangers/standards.py`
- Public functions:
  - `get_u_range(hx_type: str, service_type: str, hot_type: str, cold_type: str)`
  - `get_velocity_range(component)`
  - `select_tube_configuration(area_required, hot, cold)`
  - `tube_length_select(tube_length, ld)`
  - `get_fouling_factor(fluid_key: str, velocity: float | None=None, temperature: float | None=None, database: dict | None=None, debug: bool=True)`

### `processpi.integration.__init__`

- Source: `processpi/integration/__init__.py`
- Public classes/functions: none

### `processpi.integration.flowsheet`

- Source: `processpi/integration/flowsheet.py`
- Public classes:
  - `Flowsheet`; methods: add_equipment, add_material_stream, add_energy_stream, connect, run, solve_sequential, summary

### `processpi.pipelines.__init__`

- Source: `processpi/pipelines/__init__.py`
- Public classes/functions: none

### `processpi.pipelines.base`

- Source: `processpi/pipelines/base.py`
- Public classes:
  - `PipelineBase`; methods: calculate, get_param, validate_required

### `processpi.pipelines.design_rules`

- Source: `processpi/pipelines/design_rules.py`
- Public classes:
  - `DesignRuleError`; methods: none
  - `DesignRules`; methods: validate_step_name, validate_inputs_outputs, validate_parameters, validate_callable, validate_pipeline_consistency, summary

### `processpi.pipelines.engine`

- Source: `processpi/pipelines/engine.py`
- Public classes:
  - `ElementReport`; methods: as_dict
  - `PipelineEngine`; methods: fit, run, summary

### `processpi.pipelines.equipment`

- Source: `processpi/pipelines/equipment.py`
- Public classes:
  - `Equipment`; methods: add_inlet, add_outlet

### `processpi.pipelines.fittings`

- Source: `processpi/pipelines/fittings.py`
- Public classes:
  - `Fitting`; methods: equivalent_length, k_factor, calculate

### `processpi.pipelines.insulation`

- Source: `processpi/pipelines/insulation.py`
- Public classes/functions: none

### `processpi.pipelines.materials`

- Source: `processpi/pipelines/materials.py`
- Public functions:
  - `get_material_property(material: str, prop: str)`
  - `get_material_data(material: str)`

### `processpi.pipelines.network`

- Source: `processpi/pipelines/network.py`
- Public classes:
  - `Node`; methods: none
  - `PipelineNetwork`; methods: series, parallel, add, add_series, add_parallel, add_node, get_node, add_edge, add_fitting, add_subnetwork, validate, describe, schematic, get_all_pipes, visualize_network

### `processpi.pipelines.nozzle`

- Source: `processpi/pipelines/nozzle.py`
- Public classes:
  - `Nozzle`; methods: pressure_drop_at_flow

### `processpi.pipelines.pipelineresults`

- Source: `processpi/pipelines/pipelineresults.py`
- Public classes:
  - `PipelineResults`; methods: pipe_diameter, summary, detailed_summary

### `processpi.pipelines.pipes`

- Source: `processpi/pipelines/pipes.py`
- Public classes:
  - `Pipe`; methods: cross_sectional_area, surface_area, pressure_difference, to_dict, calculate

### `processpi.pipelines.piping_costs`

- Source: `processpi/pipelines/piping_costs.py`
- Public classes:
  - `PipeCostModel`; methods: default_steel_model, get_pipe_cost, calculate_network_cost

### `processpi.pipelines.pumps`

- Source: `processpi/pipelines/pumps.py`
- Public classes:
  - `Pump`; methods: hydraulic_power, brake_power, to_dict, calculate

### `processpi.pipelines.selection`

- Source: `processpi/pipelines/selection.py`
- Public classes:
  - `MaterialSelector`; methods: filter_materials, recommend_material

### `processpi.pipelines.standards`

- Source: `processpi/pipelines/standards.py`
- Public functions:
  - `get_internal_diameter(nominal_diameter: Diameter, schedule: str='STD')`
  - `get_thickness(nominal_diameter: Diameter, schedule: str='STD')`
  - `get_roughness(material: str)`
  - `get_recommended_velocity(service: str)`
  - `get_nearest_diameter(calculated_diameter: Diameter)`
  - `get_standard_pipe_data(nominal_diameter: Diameter, schedule: str='STD')`
  - `get_k_factor(fitting_type: str)`
  - `list_available_pipe_diameters()`
  - `get_next_standard_nominal(diameter_m: float)`
  - `get_previous_standard_nominal(nominal_diameter: Diameter)`
  - `get_next_next_standard_nominal(nominal_diameter: Diameter)`
  - `get_standard_diameters_list()`
  - `get_equivalent_length(fitting_type: str)`
  - `get_k_factor(fitting_type: str, reynolds_number: Optional[float]=None, relative_roughness: Optional[float]=None, diameter: Optional[float]=None)`
  - `get_nominal_dia_from_internal_dia(internal_diameter: Diameter, schedule: str='STD')`

### `processpi.pipelines.vessel`

- Source: `processpi/pipelines/vessel.py`
- Public classes:
  - `Vessel`; methods: add_inlet, add_outlet

### `processpi.streams.__init__`

- Source: `processpi/streams/__init__.py`
- Public classes/functions: none

### `processpi.streams.energy`

- Source: `processpi/streams/energy.py`
- Public classes:
  - `EnergyStream`; methods: bind_equipment, record, total_duty

### `processpi.streams.material`

- Source: `processpi/streams/material.py`
- Public classes:
  - `MaterialStream`; methods: set_composition, mass_flow, molar_flow, avg_mw, copy

### `processpi.units.__init__`

- Source: `processpi/units/__init__.py`
- Public classes/functions: none

### `processpi.units.area`

- Source: `processpi/units/area.py`
- Public classes:
  - `Area`; methods: to

### `processpi.units.base`

- Source: `processpi/units/base.py`
- Public classes:
  - `Variable`; methods: to, to_base, from_base

### `processpi.units.density`

- Source: `processpi/units/density.py`
- Public classes:
  - `Density`; methods: to

### `processpi.units.diameter`

- Source: `processpi/units/diameter.py`
- Public classes:
  - `Diameter`; methods: to_base, to

### `processpi.units.dimensionless`

- Source: `processpi/units/dimensionless.py`
- Public classes:
  - `Dimensionless`; methods: to

### `processpi.units.heat_flow`

- Source: `processpi/units/heat_flow.py`
- Public classes:
  - `HeatFlow`; methods: to

### `processpi.units.heat_flux`

- Source: `processpi/units/heat_flux.py`
- Public classes:
  - `HeatFlux`; methods: to

### `processpi.units.heat_of_vaporization`

- Source: `processpi/units/heat_of_vaporization.py`
- Public classes:
  - `HeatOfVaporization`; methods: to

### `processpi.units.heat_transfer_coefficient`

- Source: `processpi/units/heat_transfer_coefficient.py`
- Public classes:
  - `HeatTransferCoefficient`; methods: to

### `processpi.units.length`

- Source: `processpi/units/length.py`
- Public classes:
  - `Length`; methods: to

### `processpi.units.mass`

- Source: `processpi/units/mass.py`
- Public classes:
  - `Mass`; methods: to

### `processpi.units.mass_flowrate`

- Source: `processpi/units/mass_flowrate.py`
- Public classes:
  - `MassFlowRate`; methods: to

### `processpi.units.molar_flowrate`

- Source: `processpi/units/molar_flowrate.py`
- Public classes:
  - `MolarFlowRate`; methods: to

### `processpi.units.power`

- Source: `processpi/units/power.py`
- Public classes:
  - `Power`; methods: to

### `processpi.units.pressure`

- Source: `processpi/units/pressure.py`
- Public classes:
  - `Pressure`; methods: to_base, from_base, to

### `processpi.units.specific_heat`

- Source: `processpi/units/specific_heat.py`
- Public classes:
  - `SpecificHeat`; methods: to

### `processpi.units.strings`

- Source: `processpi/units/strings.py`
- Public classes:
  - `StringUnit`; methods: to

### `processpi.units.temperature`

- Source: `processpi/units/temperature.py`
- Public classes:
  - `Temperature`; methods: to

### `processpi.units.thermal_conductivity`

- Source: `processpi/units/thermal_conductivity.py`
- Public classes:
  - `ThermalConductivity`; methods: to

### `processpi.units.thermal_resistance`

- Source: `processpi/units/thermal_resistance.py`
- Public classes:
  - `ThermalResistance`; methods: to

### `processpi.units.velocity`

- Source: `processpi/units/velocity.py`
- Public classes:
  - `Velocity`; methods: to_base, from_base, to

### `processpi.units.viscosity`

- Source: `processpi/units/viscosity.py`
- Public classes:
  - `Viscosity`; methods: to

### `processpi.units.volume`

- Source: `processpi/units/volume.py`
- Public classes:
  - `Volume`; methods: to

### `processpi.units.volumetric_flowrate`

- Source: `processpi/units/volumetric_flowrate.py`
- Public classes:
  - `VolumetricFlowRate`; methods: to, from_mass_flow

## CLI inventory

- Packaging advertises the console script `processpi=processpi.cli:main` in `setup.py`.
- A root-level `cli.py` existed with `main()` that printed a startup message; the package module `processpi.cli` is now documented as the supported import path.
