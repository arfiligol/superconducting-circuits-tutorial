import asyncio

from nicegui import run

from core.simulation.application.run_simulation import run_simulation
from core.simulation.domain.circuit import CircuitDefinition, ComponentValue, FrequencyRange

circuit = CircuitDefinition(
    name="Test",
    components=[
        ComponentValue(name="L", value=10.0, unit="nH"),
        ComponentValue(name="C", value=1.0, unit="pF"),
        ComponentValue(name="R50", value=50.0, unit="Ohm"),
    ],
    topology=[
        ("P1", "1", "0", 1),
        ("R50", "1", "0", "R50"),
        ("L", "1", "2", "L"),
        ("C", "2", "0", "C"),
    ],
)
freq_range = FrequencyRange(start_ghz=1.0, stop_ghz=10.0, points=10)


async def main():
    print("Testing cpu_bound simulation...")
    result = await run.cpu_bound(run_simulation, circuit, freq_range)
    print("Result size:", len(result.frequencies_ghz))
    print("Success")


if __name__ == "__main__":
    asyncio.run(main())
