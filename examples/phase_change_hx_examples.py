"""ProcessPI v0.3.0 phase-change heat-exchanger examples.

Includes design/rate scenarios for condenser, evaporator, and reboiler
with horizontal and vertical orientation variants.
"""

from processpi.equipment.heatexchangers import HeatExchangerEngine


def condenser_design(hot_in, cold_in):
    return (
        HeatExchangerEngine(method="kern")
        .fit(
            hot_in=hot_in,
            cold_in=cold_in,
            hx_type="condenser",
            mode="design",
            orientation="horizontal",
            condensation_mode="total",
            condensing_side="shell",
            latent_heat=2.1e6,
        )
        .run()
    )


def condenser_rate(hot_in, cold_in):
    return (
        HeatExchangerEngine(method="kern")
        .fit(
            hot_in=hot_in,
            cold_in=cold_in,
            hx_type="condenser",
            mode="rate",
            orientation="vertical",
            condensation_mode="partial",
            vapor_fraction_condensed=0.7,
            latent_heat=2.1e6,
            tube_od=0.01905,
            tube_id=0.016,
            tube_length=6.0,
            area=120.0,
        )
        .run()
    )


def evaporator_design(hot_in, cold_in):
    return (
        HeatExchangerEngine(method="kern")
        .fit(
            hot_in=hot_in,
            cold_in=cold_in,
            hx_type="evaporator",
            mode="design",
            orientation="vertical",
            boiling_side="shell",
            latent_heat=2.25e6,
        )
        .run()
    )


def reboiler_design(hot_in, cold_in):
    return (
        HeatExchangerEngine(method="kern")
        .fit(
            hot_in=hot_in,
            cold_in=cold_in,
            hx_type="reboiler",
            mode="design",
            reboiler_type="vertical_thermosyphon",
            orientation="vertical",
            boiling_side="shell",
            latent_heat=2.3e6,
        )
        .run()
    )
