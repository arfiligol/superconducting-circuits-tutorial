from __future__ import annotations

import math
from pprint import pformat

from core.shared.persistence import get_unit_of_work
from core.shared.persistence.models import CircuitRecord

PHI0_REDUCED = 2.0678338484619295e-15 / (2 * math.pi)


def ictolj(ic_amp: float) -> float:
    return PHI0_REDUCED / ic_amp


def schema_name(title: str) -> str:
    return f"JosephsonCircuits Examples: {title}"


def make_definition(name: str, parameters: dict[str, dict], topology: list[tuple]) -> str:
    component_rows: list[dict[str, object]] = []
    normalized_topology: list[tuple[str, str, str, str | int]] = []
    seen_component_names: set[str] = set()

    for elem_name, node1, node2, value_ref in topology:
        elem_name_text = str(elem_name)
        if elem_name_text.lower().startswith("p"):
            normalized_topology.append((elem_name_text, str(node1), str(node2), int(value_ref)))
            continue

        if elem_name_text in seen_component_names:
            normalized_topology.append((elem_name_text, str(node1), str(node2), elem_name_text))
            continue

        parameter_key = str(value_ref)
        if parameter_key not in parameters:
            raise KeyError(
                "Topology element "
                f"'{elem_name_text}' references undefined parameter '{parameter_key}'."
            )

        parameter = parameters[parameter_key]
        component_rows.append(
            {
                "name": elem_name_text,
                "default": float(parameter["default"]),
                "unit": str(parameter["unit"]),
            }
        )
        seen_component_names.add(elem_name_text)
        normalized_topology.append((elem_name_text, str(node1), str(node2), elem_name_text))

    payload = {
        "name": name,
        "components": component_rows,
        "topology": normalized_topology,
    }
    return pformat(payload, width=100, sort_dicts=False)


def _format_payload(payload: dict[str, object]) -> str:
    return pformat(payload, width=100, sort_dicts=False)


def jpa_core_schema(title: str) -> tuple[str, str]:
    parameters = {
        "R": {"default": 50.0, "unit": "Ohm"},
        "Cc": {"default": 100.0e-15, "unit": "F"},
        "Cj": {"default": 1000.0e-15, "unit": "F"},
        "Lj": {"default": 1000.0e-12, "unit": "H"},
    }
    topology = [
        ("P1", "1", "0", 1),
        ("R1", "1", "0", "R"),
        ("C1", "1", "2", "Cc"),
        ("Lj1", "2", "0", "Lj"),
        ("C2", "2", "0", "Cj"),
    ]
    name = schema_name(title)
    return name, make_definition(name, parameters, topology)


def flux_pumped_jpa_schema() -> tuple[str, str]:
    parameters = {
        "R": {"default": 50.0, "unit": "Ohm"},
        "Cc": {"default": 16.0e-15, "unit": "F"},
        "Cj": {"default": 10.0e-15, "unit": "F"},
        "Lj": {"default": 219.63e-12, "unit": "H"},
        "Cr": {"default": 0.4e-12, "unit": "F"},
        "Lr": {"default": 0.4264e-9, "unit": "H"},
        "Ll": {"default": 34.0e-12, "unit": "H"},
        "Ldc": {"default": 0.74e-12, "unit": "H"},
        "K": {"default": 0.999, "unit": "H"},
        "Lg": {"default": 100.0e-9, "unit": "H"},
        "R_bias": {"default": 1000.0, "unit": "Ohm"},
    }
    topology = [
        ("P1", "1", "0", 1),
        ("R1", "1", "0", "R"),
        ("L0", "1", "0", "Lg"),
        ("C1", "1", "2", "Cc"),
        ("L1", "2", "3", "Lr"),
        ("C2", "2", "0", "Cr"),
        ("Lj1", "3", "0", "Lj"),
        ("Cj1", "3", "0", "Cj"),
        ("L2", "3", "4", "Ll"),
        ("Lj2", "4", "0", "Lj"),
        ("Cj2", "4", "0", "Cj"),
        ("L3", "5", "0", "Ldc"),
        ("K1", "L2", "L3", "K"),
        ("P2", "5", "0", 2),
        ("R2", "5", "0", "R_bias"),
    ]
    name = schema_name("Flux-pumped Josephson Parametric Amplifier (JPA)")
    return name, make_definition(name, parameters, topology)


def snail_schema() -> tuple[str, str]:
    alpha = 0.29
    parameters = {
        "R": {"default": 50.0, "unit": "Ohm"},
        "Cc": {"default": 0.048e-12, "unit": "F"},
        "Cj": {"default": 10.0e-15, "unit": "F"},
        "Cj_div_alpha": {"default": (10.0e-15) / alpha, "unit": "F"},
        "Lj": {"default": 60e-12, "unit": "H"},
        "Lj_div_alpha": {"default": (60e-12) / alpha, "unit": "H"},
        "Cr": {"default": 0.4e-12 * 1.25, "unit": "F"},
        "Lr": {"default": 0.4264e-9 * 1.25, "unit": "H"},
        "Ll": {"default": 34e-12, "unit": "H"},
        "Ldc": {"default": 0.74e-12, "unit": "H"},
        "K": {"default": 0.999, "unit": "H"},
        "Lg": {"default": 100e-9, "unit": "H"},
        "R_bias": {"default": 1000.0, "unit": "Ohm"},
    }
    topology = [
        ("P1", "1", "0", 1),
        ("R1", "1", "0", "R"),
        ("L0", "1", "0", "Lg"),
        ("C1", "1", "2", "Cc"),
        ("L1", "2", "3", "Lr"),
        ("C2", "2", "0", "Cr"),
        ("Lj1", "3", "0", "Lj_div_alpha"),
        ("Cj1", "3", "0", "Cj_div_alpha"),
        ("L2", "3", "4", "Ll"),
        ("Lj2", "4", "5", "Lj"),
        ("Cj2", "4", "5", "Cj"),
        ("Lj3", "5", "6", "Lj"),
        ("Cj3", "5", "6", "Cj"),
        ("Lj4", "6", "0", "Lj"),
        ("Cj4", "6", "0", "Cj"),
        ("L3", "7", "0", "Ldc"),
        ("K1", "L2", "L3", "K"),
        ("P2", "7", "0", 2),
        ("R2", "7", "0", "R_bias"),
    ]
    name = schema_name("SNAIL Parametric Amplifier")
    return name, make_definition(name, parameters, topology)


def jtwp_uniform_topology(nj: int, pmrpitch: int) -> list[tuple[str, str, str, str | int]]:
    topology: list[tuple[str, str, str, str | int]] = []
    topology.append(("P1_0", "1", "0", 1))
    topology.append(("R1_0", "1", "0", "Rleft"))
    topology.append(("C1_0", "1", "0", "Cg_half"))
    topology.append(("Lj1_2", "1", "2", "Lj"))
    topology.append(("C1_2", "1", "2", "Cj"))

    j = 2
    for i in range(2, nj):
        if i % pmrpitch == (pmrpitch // 2):
            topology.append((f"C{j}_0", str(j), "0", "Cg_minus_Cc"))
            topology.append((f"Lj{j}_{j + 2}", str(j), str(j + 2), "Lj"))
            topology.append((f"C{j}_{j + 2}", str(j), str(j + 2), "Cj"))
            topology.append((f"C{j}_{j + 1}", str(j), str(j + 1), "Cc"))
            topology.append((f"C{j + 1}_0", str(j + 1), "0", "Cr"))
            topology.append((f"L{j + 1}_0", str(j + 1), "0", "Lr"))
            j += 1
        else:
            topology.append((f"C{j}_0", str(j), "0", "Cg"))
            topology.append((f"Lj{j}_{j + 1}", str(j), str(j + 1), "Lj"))
            topology.append((f"C{j}_{j + 1}", str(j), str(j + 1), "Cj"))
        j += 1

    topology.append((f"C{j}_0", str(j), "0", "Cg_half"))
    topology.append((f"R{j}_0", str(j), "0", "Rright"))
    topology.append((f"P{j}_0", str(j), "0", 2))
    return topology


def jtwp_schema(title: str, *, nj: int, pmrpitch: int, floquet: bool) -> tuple[str, str]:
    if floquet:
        parameters = {
            "Rleft": {"default": 50.0, "unit": "Ohm"},
            "Rright": {"default": 50.0, "unit": "Ohm"},
            "Lj": {"default": ictolj(1.75e-6), "unit": "H"},
            "Cg": {"default": 76.6e-15, "unit": "F"},
            "Cg_half": {"default": 76.6e-15 / 2, "unit": "F"},
            "Cc": {"default": 40.0e-15, "unit": "F"},
            "Cg_minus_Cc": {"default": 76.6e-15 - 40.0e-15, "unit": "F"},
            "Cr": {"default": 1.533e-12, "unit": "F"},
            "Lr": {"default": 2.47e-10, "unit": "H"},
            "Cj": {"default": 40e-15, "unit": "F"},
        }
    else:
        parameters = {
            "Rleft": {"default": 50.0, "unit": "Ohm"},
            "Rright": {"default": 50.0, "unit": "Ohm"},
            "Lj": {"default": ictolj(3.4e-6), "unit": "H"},
            "Cg": {"default": 45.0e-15, "unit": "F"},
            "Cg_half": {"default": 45.0e-15 / 2, "unit": "F"},
            "Cc": {"default": 30.0e-15, "unit": "F"},
            "Cg_minus_Cc": {"default": 45.0e-15 - 30.0e-15, "unit": "F"},
            "Cr": {"default": 2.8153e-12, "unit": "F"},
            "Lr": {"default": 1.70e-10, "unit": "H"},
            "Cj": {"default": 55e-15, "unit": "F"},
        }

    name = schema_name(title)
    values = {key: float(spec["default"]) for key, spec in parameters.items()}
    units = {key: str(spec["unit"]) for key, spec in parameters.items()}
    floquet_weight_width = 745.0
    component_items: list[dict[str, object]] = []
    topology_items: list[tuple[str, str, str, str | int] | dict[str, object]] = []

    def floquet_weight(position: float) -> float:
        if not floquet:
            return 1.0
        return math.exp(-(((position - (nj / 2)) ** 2) / (floquet_weight_width**2)))

    def add_component_value(component_name: str, default_value: float, unit_name: str) -> None:
        component_items.append(
            {
                "name": component_name,
                "default": default_value,
                "unit": unit_name,
            }
        )

    def add_component(component_name: str, parameter_name: str) -> None:
        add_component_value(component_name, values[parameter_name], units[parameter_name])

    def add_topology_row(
        element_name: str,
        node1: int | str,
        node2: int | str,
        value_ref: str | int,
    ) -> None:
        topology_items.append((element_name, str(node1), str(node2), value_ref))

    def add_simple_segment(start_node: int, logical_start: int, count: int) -> None:
        if count <= 0:
            return
        if floquet:
            for offset in range(count):
                logical_cell = logical_start + offset
                node = start_node + offset
                next_node = node + 1
                shunt_weight = floquet_weight(logical_cell - 0.5)
                junction_weight = floquet_weight(float(logical_cell))
                add_component_value(f"C{node}_0", values["Cg"] * shunt_weight, units["Cg"])
                add_component_value(
                    f"Lj{node}_{next_node}",
                    values["Lj"] * junction_weight,
                    units["Lj"],
                )
                add_component_value(
                    f"C{node}_{next_node}",
                    values["Cj"] / junction_weight,
                    units["Cj"],
                )
        else:
            component_items.append(
                {
                    "repeat": {
                        "count": count,
                        "index": "cell",
                        "symbols": {
                            "n": {"base": start_node, "step": 1},
                            "n2": {"base": start_node + 1, "step": 1},
                        },
                        "emit": [
                            {"name": "C${n}_0", "default": values["Cg"], "unit": units["Cg"]},
                            {"name": "Lj${n}_${n2}", "default": values["Lj"], "unit": units["Lj"]},
                            {"name": "C${n}_${n2}", "default": values["Cj"], "unit": units["Cj"]},
                        ],
                    }
                }
            )
        topology_items.append(
            {
                "repeat": {
                    "count": count,
                    "index": "cell",
                    "symbols": {
                        "n": {"base": start_node, "step": 1},
                        "n2": {"base": start_node + 1, "step": 1},
                    },
                    "emit": [
                        ("C${n}_0", "${n}", "0", "C${n}_0"),
                        ("Lj${n}_${n2}", "${n}", "${n2}", "Lj${n}_${n2}"),
                        ("C${n}_${n2}", "${n}", "${n2}", "C${n}_${n2}"),
                    ],
                }
            }
        )

    def add_resonator_stage(start_node: int, logical_cell: int) -> None:
        if floquet:
            shunt_weight = floquet_weight(logical_cell - 0.5)
            junction_weight = floquet_weight(float(logical_cell))
            add_component_value(
                f"C{start_node}_0",
                values["Cg_minus_Cc"] * shunt_weight,
                units["Cg_minus_Cc"],
            )
            add_component_value(
                f"Lj{start_node}_{start_node + 2}",
                values["Lj"] * junction_weight,
                units["Lj"],
            )
            add_component_value(
                f"C{start_node}_{start_node + 2}",
                values["Cj"] / junction_weight,
                units["Cj"],
            )
            add_component_value(
                f"C{start_node}_{start_node + 1}",
                values["Cc"] * shunt_weight,
                units["Cc"],
            )
        else:
            add_component(f"C{start_node}_0", "Cg_minus_Cc")
            add_component(f"Lj{start_node}_{start_node + 2}", "Lj")
            add_component(f"C{start_node}_{start_node + 2}", "Cj")
            add_component(f"C{start_node}_{start_node + 1}", "Cc")
        add_component(f"C{start_node + 1}_0", "Cr")
        add_component(f"L{start_node + 1}_0", "Lr")
        add_topology_row(f"C{start_node}_0", start_node, 0, f"C{start_node}_0")
        add_topology_row(
            f"Lj{start_node}_{start_node + 2}",
            start_node,
            start_node + 2,
            f"Lj{start_node}_{start_node + 2}",
        )
        add_topology_row(
            f"C{start_node}_{start_node + 2}",
            start_node,
            start_node + 2,
            f"C{start_node}_{start_node + 2}",
        )
        add_topology_row(
            f"C{start_node}_{start_node + 1}",
            start_node,
            start_node + 1,
            f"C{start_node}_{start_node + 1}",
        )
        add_topology_row(f"C{start_node + 1}_0", start_node + 1, 0, f"C{start_node + 1}_0")
        add_topology_row(f"L{start_node + 1}_0", start_node + 1, 0, f"L{start_node + 1}_0")

    add_topology_row("P1_0", 1, 0, 1)
    add_component("R1_0", "Rleft")
    if floquet:
        add_component_value("C1_0", values["Cg_half"] * floquet_weight(0.5), units["Cg_half"])
        add_component_value("Lj1_2", values["Lj"] * floquet_weight(1.0), units["Lj"])
        add_component_value("C1_2", values["Cj"] / floquet_weight(1.0), units["Cj"])
    else:
        add_component("C1_0", "Cg_half")
        add_component("Lj1_2", "Lj")
        add_component("C1_2", "Cj")
    add_topology_row("R1_0", 1, 0, "R1_0")
    add_topology_row("C1_0", 1, 0, "C1_0")
    add_topology_row("Lj1_2", 1, 2, "Lj1_2")
    add_topology_row("C1_2", 1, 2, "C1_2")

    current_node = 2
    pending_simple_start_node: int | None = None
    pending_simple_start_logical: int | None = None
    pending_simple_count = 0

    for logical_cell in range(2, nj):
        is_resonator = logical_cell % pmrpitch == (pmrpitch // 2)
        if is_resonator:
            if pending_simple_start_node is not None and pending_simple_start_logical is not None:
                add_simple_segment(
                    pending_simple_start_node,
                    pending_simple_start_logical,
                    pending_simple_count,
                )
                pending_simple_start_node = None
                pending_simple_start_logical = None
                pending_simple_count = 0
            add_resonator_stage(current_node, logical_cell)
            current_node += 2
            continue

        if pending_simple_start_node is None:
            pending_simple_start_node = current_node
            pending_simple_start_logical = logical_cell
        pending_simple_count += 1
        current_node += 1

    if pending_simple_start_node is not None and pending_simple_start_logical is not None:
        add_simple_segment(
            pending_simple_start_node,
            pending_simple_start_logical,
            pending_simple_count,
        )

    if floquet:
        add_component_value(
            f"C{current_node}_0",
            values["Cg_half"] * floquet_weight(nj - 0.5),
            units["Cg_half"],
        )
    else:
        add_component(f"C{current_node}_0", "Cg_half")
    add_component(f"R{current_node}_0", "Rright")
    add_topology_row(f"C{current_node}_0", current_node, 0, f"C{current_node}_0")
    add_topology_row(f"R{current_node}_0", current_node, 0, f"R{current_node}_0")
    add_topology_row(f"P{current_node}_0", current_node, 0, 2)

    payload = {
        "name": name,
        "components": component_items,
        "topology": topology_items,
    }
    return name, _format_payload(payload)


def flux_driven_jtwp_schema(nr_cells: int = 24) -> tuple[str, str]:
    cutoff_frequency = 46e9
    z0 = 50.0
    capacitance = 1 / (2 * math.pi * cutoff_frequency * z0)
    lj = z0 / (2 * math.pi * cutoff_frequency)
    coupling = 0.02
    mutual = coupling * lj
    lsmall = (mutual**2) / lj
    lpump = 1.1 * lj
    critical_current = PHI0_REDUCED / lj
    jj_area = critical_current / 3e6
    jj_cap_density = 50e-15 / (1e-6) ** 2
    c_j = jj_cap_density * jj_area

    parameters = {
        "Rport": {"default": 50.0, "unit": "Ohm"},
        "C": {"default": capacitance, "unit": "F"},
        "C_half": {"default": capacitance / 2, "unit": "F"},
        "Cj": {"default": c_j, "unit": "F"},
        "Lj": {"default": lj, "unit": "H"},
        "Lpump": {"default": lpump, "unit": "H"},
        "Cpump": {"default": lpump / (z0**2), "unit": "F"},
        "Cpump_half": {"default": (lpump / (z0**2)) / 2, "unit": "F"},
        "kappa": {"default": 0.999, "unit": "H"},
        "Lg": {"default": 20.0e-9, "unit": "H"},
        "Lsmall": {"default": lsmall, "unit": "H"},
    }

    name = schema_name("Flux-Driven Josephson Traveling-Wave Parametric Amplifier (JTWPA)")
    values = {key: float(spec["default"]) for key, spec in parameters.items()}
    units = {key: str(spec["unit"]) for key, spec in parameters.items()}
    component_items: list[dict[str, object]] = []
    topology_items: list[tuple[str, str, str, str | int] | dict[str, object]] = []

    def add_component(component_name: str, parameter_name: str) -> None:
        component_items.append(
            {
                "name": component_name,
                "default": values[parameter_name],
                "unit": units[parameter_name],
            }
        )

    def add_topology_row(
        element_name: str,
        node1: int | str,
        node2: int | str,
        value_ref: str | int,
    ) -> None:
        topology_items.append((element_name, str(node1), str(node2), value_ref))

    add_topology_row("P1_0", 1, 0, 1)
    add_component("R1_0", "Rport")
    add_topology_row("R1_0", 1, 0, "R1_0")

    add_topology_row("P2_0", 2, 0, 3)
    add_component("R2_0", "Rport")
    add_topology_row("R2_0", 2, 0, "R2_0")

    add_component("C1_0", "C_half")
    add_component("Lj_a1_4", "Lj")
    add_component("Cj_a1_4", "Cj")
    add_component("L1_3", "Lsmall")
    add_component("Lj_b3_4", "Lj")
    add_component("Cj_b3_4", "Cj")
    add_component("L2_5", "Lpump")
    add_component("C2_0", "Cpump_half")
    add_component("K1", "kappa")
    add_topology_row("C1_0", 1, 0, "C1_0")
    add_topology_row("Lj_a1_4", 1, 4, "Lj_a1_4")
    add_topology_row("Cj_a1_4", 1, 4, "Cj_a1_4")
    add_topology_row("L1_3", 1, 3, "L1_3")
    add_topology_row("Lj_b3_4", 3, 4, "Lj_b3_4")
    add_topology_row("Cj_b3_4", 3, 4, "Cj_b3_4")
    add_topology_row("L2_5", 2, 5, "L2_5")
    add_topology_row("C2_0", 2, 0, "C2_0")
    add_topology_row("K1", "L1_3", "L2_5", "K1")

    if nr_cells > 1:
        component_items.append(
            {
                "repeat": {
                    "count": nr_cells - 1,
                    "index": "cell",
                    "symbols": {
                        "s": {"base": 4, "step": 3},
                        "p": {"base": 5, "step": 3},
                        "m": {"base": 6, "step": 3},
                        "e": {"base": 7, "step": 3},
                        "pe": {"base": 8, "step": 3},
                    },
                    "emit": [
                        {"name": "C${s}_0", "default": values["C"], "unit": units["C"]},
                        {"name": "Lj_a${s}_${e}", "default": values["Lj"], "unit": units["Lj"]},
                        {"name": "Cj_a${s}_${e}", "default": values["Cj"], "unit": units["Cj"]},
                        {
                            "name": "L${s}_${m}",
                            "default": values["Lsmall"],
                            "unit": units["Lsmall"],
                        },
                        {"name": "Lj_b${m}_${e}", "default": values["Lj"], "unit": units["Lj"]},
                        {"name": "Cj_b${m}_${e}", "default": values["Cj"], "unit": units["Cj"]},
                        {"name": "L${p}_${pe}", "default": values["Lpump"], "unit": units["Lpump"]},
                        {"name": "C${p}_0", "default": values["Cpump"], "unit": units["Cpump"]},
                        {"name": "K${s}", "default": values["kappa"], "unit": units["kappa"]},
                    ],
                }
            }
        )
        topology_items.append(
            {
                "repeat": {
                    "count": nr_cells - 1,
                    "index": "cell",
                    "symbols": {
                        "s": {"base": 4, "step": 3},
                        "p": {"base": 5, "step": 3},
                        "m": {"base": 6, "step": 3},
                        "e": {"base": 7, "step": 3},
                        "pe": {"base": 8, "step": 3},
                    },
                    "emit": [
                        ("C${s}_0", "${s}", "0", "C${s}_0"),
                        ("Lj_a${s}_${e}", "${s}", "${e}", "Lj_a${s}_${e}"),
                        ("Cj_a${s}_${e}", "${s}", "${e}", "Cj_a${s}_${e}"),
                        ("L${s}_${m}", "${s}", "${m}", "L${s}_${m}"),
                        ("Lj_b${m}_${e}", "${m}", "${e}", "Lj_b${m}_${e}"),
                        ("Cj_b${m}_${e}", "${m}", "${e}", "Cj_b${m}_${e}"),
                        ("L${p}_${pe}", "${p}", "${pe}", "L${p}_${pe}"),
                        ("C${p}_0", "${p}", "0", "C${p}_0"),
                        ("K${s}", "L${s}_${m}", "L${p}_${pe}", "K${s}"),
                    ],
                }
            }
        )

    final_signal_node = 1 + (3 * nr_cells)
    final_pump_node = final_signal_node + 1
    add_component(f"C{final_signal_node}_0", "C_half")
    add_component(f"R{final_signal_node}_0", "Rport")
    add_component(f"C{final_pump_node}_0", "Cpump_half")
    add_component(f"R{final_pump_node}_0", "Rport")
    add_component(f"L{final_pump_node}_0", "Lg")
    add_topology_row(f"C{final_signal_node}_0", final_signal_node, 0, f"C{final_signal_node}_0")
    add_topology_row(f"P{final_signal_node}_0", final_signal_node, 0, 2)
    add_topology_row(f"R{final_signal_node}_0", final_signal_node, 0, f"R{final_signal_node}_0")
    add_topology_row(f"C{final_pump_node}_0", final_pump_node, 0, f"C{final_pump_node}_0")
    add_topology_row(f"P{final_pump_node}_0", final_pump_node, 0, 4)
    add_topology_row(f"R{final_pump_node}_0", final_pump_node, 0, f"R{final_pump_node}_0")
    add_topology_row(f"L{final_pump_node}_0", final_pump_node, 0, f"L{final_pump_node}_0")

    payload = {
        "name": name,
        "components": component_items,
        "topology": topology_items,
    }
    return name, _format_payload(payload)


def lesa_schema(nstages_snake: int = 10) -> tuple[str, str]:
    parameters = {
        "Lj": {"default": ictolj(16e-6), "unit": "H"},
        "L1": {"default": 2.6e-12, "unit": "H"},
        "L2": {"default": 8.0e-12, "unit": "H"},
        "L3": {"default": 5.0e-12, "unit": "H"},
        "Lg": {"default": 100.0e-9, "unit": "H"},
        "L22": {"default": 1.320e-9, "unit": "H"},
        "C1": {"default": 6.607e-12, "unit": "F"},
        "C6": {"default": 0.743e-12, "unit": "F"},
        "C7": {"default": 0.265e-12, "unit": "F"},
        "PLCC": {"default": 0.654e-12, "unit": "F"},
        "PLCL": {"default": 0.650e-9, "unit": "H"},
        "R": {"default": 50.0, "unit": "Ohm"},
        "Lb": {"default": 60e-12, "unit": "H"},
        "K": {"default": 0.5 * 50 / math.sqrt(60 * 60), "unit": "H"},
    }
    topology: list[tuple[str, str, str, str | int]] = []

    def push(name: str, n1: int | str, n2: int | str, value_ref: str | int) -> None:
        topology.append((name, str(n1), str(n2), value_ref))

    def add_snake(start_node: int, skip_nodes: int) -> tuple[int, int]:
        j = start_node + skip_nodes
        push(f"L{start_node}_{j + 1}", start_node, j + 1, "L1")
        push(f"L{j + 2}_{j + 3}", j + 2, j + 3, "L1")
        push(f"Lj{start_node}_{j + 2}", start_node, j + 2, "Lj")
        push(f"L{j + 1}_{j + 3}", j + 1, j + 3, "L2")
        j += 2
        for i in range(2, nstages_snake + 1):
            push(f"L{j + 2}_{j + 3}", j + 2, j + 3, "L1")
            if i % 2 == 1:
                push(f"Lj{j}_{j + 2}", j, j + 2, "Lj")
                push(f"L{j + 1}_{j + 3}", j + 1, j + 3, "L2")
            else:
                push(f"L{j}_{j + 2}", j, j + 2, "L2")
                push(f"Lj{j + 1}_{j + 3}", j + 1, j + 3, "Lj")
            j += 2
        return j + 1, 0

    def add_snake_squid(start_node: int, skip_nodes: int) -> tuple[int, int]:
        end_node, skip_nodes = add_snake(start_node, skip_nodes)
        j = end_node

        push(f"L{j}_{j + 1}", j, j + 1, "L3")
        j += 1

        end_node, skip_nodes = add_snake(j, 0)
        j = end_node

        push(f"L{j}_0", j, 0, "Lb")
        push("Kb1", f"L{j}_0", "Lb1", "K")
        j += 1

        end_node, skip_nodes = add_snake(1, j - 2)
        j = end_node

        push(f"L{j}_{j + 1}", j, j + 1, "L3")
        j += 1

        end_node, skip_nodes = add_snake(j, 0)
        j = end_node

        push(f"L{j}_0", j, 0, "Lb")
        push("Kb2", f"L{j}_0", "Lb2", "K")
        j += 1

        push("P2", j, 0, 2)
        push(f"R{j}_0", j, 0, "R")

        push("Lb1", j, j + 1, "Lb")
        push("Lb2", j + 1, 0, "Lb")

        return j + 1, 0

    def add_tline(
        start_node: int, theta: float, w0: float, wc: float, z0: float
    ) -> tuple[int, int]:
        n_cells = math.ceil(theta * wc / (2 * w0))
        wc_eff = n_cells * 2 * w0 / theta
        l_cell = 2 * z0 / wc_eff
        c_cell = 2 / (wc_eff * z0)

        j = start_node
        for i in range(1, n_cells + 1):
            if i == 1:
                key_l_half_a = f"TL_Lhalf_{j}_a"
                parameters[key_l_half_a] = {"default": l_cell / 2, "unit": "H"}
                push(f"L{j}_{j + 1}", j, j + 1, key_l_half_a)
                j += 1

            key_c = f"TL_C_{j}"
            parameters[key_c] = {"default": c_cell, "unit": "F"}
            push(f"C{j}_0", j, 0, key_c)

            if i == n_cells:
                key_l_half_b = f"TL_Lhalf_{j}_b"
                parameters[key_l_half_b] = {"default": l_cell / 2, "unit": "H"}
                push(f"L{j}_{j + 1}", j, j + 1, key_l_half_b)
            else:
                key_l = f"TL_L_{j}"
                parameters[key_l] = {"default": l_cell, "unit": "H"}
                push(f"L{j}_{j + 1}", j, j + 1, key_l)
            j += 1

        return j, 0

    end_node, _ = add_snake_squid(1, 0)
    j = end_node
    start_node = 1
    push(f"C{start_node}_0", start_node, 0, "C1")
    push(f"C{start_node}_{j + 1}", start_node, j + 1, "C6")
    j += 1

    push(f"C{j}_0", j, 0, "PLCC")
    push(f"L{j}_0", j, 0, "PLCL")
    push(f"C{j}_{j + 1}", j, j + 1, "C7")
    j += 1

    theta = 32.6 * math.pi / 180
    w0 = 2 * math.pi * 4.9e9
    wc = 2 * math.pi * 150e9
    j, _ = add_tline(j, theta, w0, wc, 50.0)

    push(f"L{j}_0", j, 0, "L22")
    push("P1", j, 0, 1)
    push("R1", j, 0, "R")

    name = schema_name("Impedance-engineered JPA")
    return name, make_definition(name, parameters, topology)


def build_all() -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    records.append(jpa_core_schema("Josephson Parametric Amplifier (JPA)"))
    records.append(jpa_core_schema("Double-pumped Josephson Parametric Amplifier (JPA)"))
    records.append(flux_pumped_jpa_schema())
    records.append(snail_schema())
    records.append(
        jtwp_schema(
            "Josephson Traveling Wave Parametric Amplifier (JTWPA)",
            nj=64,
            pmrpitch=4,
            floquet=False,
        )
    )
    records.append(
        jtwp_schema(
            "Floquet JTWPA",
            nj=64,
            pmrpitch=8,
            floquet=True,
        )
    )
    records.append(
        jtwp_schema(
            "Floquet JTWPA with Dissipation",
            nj=64,
            pmrpitch=8,
            floquet=True,
        )
    )
    records.append(flux_driven_jtwp_schema(nr_cells=24))
    records.append(lesa_schema(nstages_snake=10))
    return records


def upsert_records(records: list[tuple[str, str]]) -> tuple[list[str], list[str]]:
    created: list[str] = []
    updated: list[str] = []
    with get_unit_of_work() as uow:
        for name, definition in records:
            existing = uow.circuits.get_by_name(name)
            if existing is None:
                uow.circuits.add(CircuitRecord(name=name, definition_json=definition))
                created.append(name)
            else:
                existing.definition_json = definition
                uow.circuits.update(existing)
                updated.append(name)
        uow.commit()
    return created, updated


if __name__ == "__main__":
    all_records = build_all()
    created, updated = upsert_records(all_records)
    print(f"created={len(created)}")
    for n in created:
        print(f"  + {n}")
    print(f"updated={len(updated)}")
    for n in updated:
        print(f"  ~ {n}")
