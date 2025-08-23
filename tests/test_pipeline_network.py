from processpi.pipeline.network import PipelineNetwork
from processpi.pipeline.engine import PipelineEngine

def test_single_line():
    print("\n=== Test: Single Straight Pipeline ===")

    net = PipelineNetwork()
    net.add_pipe("P1", length=50, diameter=None, roughness=0.000045)

    engine = PipelineEngine(network=net)
    engine.fit(
        fluid={"density": 930, "viscosity": 0.91e-3},
        flow_rate=5000/3600,  # 5000 kg/h -> 1.39 kg/s
        inlet_pressure=600_000,
        outlet_pressure=101_325,
        temperature=50
    )
    engine.run()
    engine.summary()


def test_complex_co2_network():
    print("\n=== Test: Complex Pipeline with CO₂ and Fittings ===")

    net = PipelineNetwork()
    net.add_pipe("Main", length=800, diameter=None, roughness=0.000045)
    net.add_fitting("elbow_90", count=8, k_value=0.75)
    net.add_fitting("butterfly_valve", count=1, k_value=2.0)
    net.add_fitting("flow_nozzle", count=1, k_value=1.5)

    engine = PipelineEngine(network=net)
    engine.fit(
        fluid={"density": 1.87, "viscosity": 0.016e-3},
        flow_rate=(1000*1000)/86400,  # 1000 t/day -> ~11.57 kg/s
        inlet_pressure=24000,
        outlet_pressure=101325,
        temperature=60
    )
    engine.run()
    engine.summary()


def test_organic_liquid():
    print("\n=== Test: Organic Liquid Transport ===")

    net = PipelineNetwork()
    net.add_pipe("Line1", length=200, diameter=None, roughness=0.000045)

    engine = PipelineEngine(network=net)
    engine.fit(
        fluid={"density": 850, "viscosity": 0.0012},
        flow_rate=20/3600,  # 20 kg/h -> 0.0056 kg/s
        inlet_pressure=200_000,
        outlet_pressure=101_325,
        temperature=40
    )
    engine.run()
    engine.summary()


def test_carbon_monoxide():
    print("\n=== Test: Carbon Monoxide Pipeline ===")

    net = PipelineNetwork()
    net.add_pipe("CO_Line", length=500, diameter=None, roughness=0.000045)
    net.add_fitting("elbow_90", count=4, k_value=0.75)

    engine = PipelineEngine(network=net)
    engine.fit(
        fluid={"density": 1.25, "viscosity": 0.018e-3},
        flow_rate=(500*1000)/86400,  # 500 t/day -> ~5.78 kg/s
        inlet_pressure=15_000,
        outlet_pressure=101_325,
        temperature=45
    )
    engine.run()
    engine.summary()


if __name__ == "__main__":
    print("Running Extended Pipeline Engine Compatibility Tests")
    test_single_line()
    test_complex_co2_network()
    test_organic_liquid()
    test_carbon_monoxide()
