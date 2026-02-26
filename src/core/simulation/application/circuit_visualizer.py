"""
Circuit Visualizer using Schemdraw.

This module provides functionality to convert a CircuitDefinition
into an SVG string using the Schemdraw library.
"""

import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

from core.simulation.domain.circuit import CircuitDefinition

# Configure Matplotlib fonts to cleanly render CJK characters (Bopomofo) if used in schematics
plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "PingFang HK", "Heiti TC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def generate_circuit_svg(circuit: CircuitDefinition) -> str:
    """
    Generate an SVG string representation of a CircuitDefinition.

    This uses a simple layout heuristic to draw the components.

    Args:
        circuit: The circuit definition to visualize.

    Returns:
        A string containing the raw SVG data.
    """
    d = schemdraw.Drawing(show=False)

    x_pos = 0.0
    dx = 3.0
    gap = 1.5

    node_latest_x: dict[str, float] = {}
    tip_node_top = None
    route_level = 4.5

    def wire_node(node_str: str, target_x: float, target_y: float):
        nonlocal route_level, d
        if node_str in node_latest_x:
            prev_x = node_latest_x[node_str]
            dist = abs(target_x - prev_x)
            if dist > 2.0:
                # Route OVER components to avoid slicing through them
                d += elm.Line().at((prev_x, target_y)).to((prev_x, route_level))
                d += elm.Line().at((prev_x, route_level)).to((target_x, route_level))
                d += elm.Line().at((target_x, route_level)).to((target_x, target_y))
                route_level += 0.5  # increment so multiple routes don't overlap
            elif dist > 0.1:
                # Route STRAIGHT (adjacent)
                d += elm.Line().at((prev_x, target_y)).to((target_x, target_y))

        node_latest_x[node_str] = max(node_latest_x.get(node_str, 0.0), target_x)

    # Track ground coordinates separately for bottom-rail routing
    last_ground_x = None
    ground_drawn = False

    def wire_ground(target_x: float):
        nonlocal last_ground_x, d, ground_drawn

        if not ground_drawn:
            d += elm.Ground().at((target_x, 0.0))
            ground_drawn = True

        if last_ground_x is not None:
            dist = abs(target_x - last_ground_x)
            if dist > 0.1:
                # Draw a solid ground rail at y=0 connecting the previous ground to this one
                d += elm.Line().at((last_ground_x, 0.0)).to((target_x, 0.0))
        last_ground_x = target_x

    for comp_name, node1_raw, node2_raw, _ in circuit.topology:
        name_lower = comp_name.lower()
        node1_str = str(node1_raw)
        node2_str = str(node2_raw)

        # Determine element type based on prefix
        element = None
        if name_lower.startswith("p"):
            element = elm.SourceSin().label(comp_name)
        elif name_lower.startswith("c"):
            element = elm.Capacitor().label(comp_name)
        elif name_lower.startswith("l") and not name_lower.startswith("lj"):
            element = elm.Inductor().label(comp_name)
        elif name_lower.startswith("r"):
            element = elm.Resistor().label(comp_name)
        elif name_lower.startswith("lj"):
            element = elm.Josephson().label(comp_name)
        elif name_lower.startswith("k"):
            element = elm.Dot(open=True).label(f"K({comp_name})")
        else:
            element = elm.Dot(open=True).label(f"? {comp_name}")

        if element is None:
            continue

        is_gnd1 = node1_str.lower() in ["0", "gnd", "gnd"]
        is_gnd2 = node2_str.lower() in ["0", "gnd", "gnd"]

        y1 = 0.0 if is_gnd1 else 3.0
        y2 = 0.0 if is_gnd2 else 3.0

        is_shunt = y1 != y2

        if is_shunt:
            signal_node = node1_str if not is_gnd1 else node2_str

            if tip_node_top is not None and tip_node_top != signal_node:
                x_pos += gap

            x = x_pos

            if isinstance(element, elm.Dot):
                d += element.at((x, 1.5))
            else:
                d += element.at((x, 0.0)).to((x, 3.0))

            wire_ground(x)  # Connect this ground to the previous ground rail

            loc1 = "top" if y1 > y2 else "bottom"
            loc2 = "bottom" if y1 > y2 else "top"
            d += elm.Label().at((x, y1)).label(node1_str, loc=loc1, color="gray")
            d += elm.Label().at((x, y2)).label(node2_str, loc=loc2, color="gray")

            wire_node(signal_node, x, 3.0)

            tip_node_top = signal_node
            x_pos = x + gap

        else:
            if is_gnd1 and is_gnd2:
                # Two grounds, draw a wire connecting them via ground rail
                if tip_node_top is not None:
                    x_pos += gap
                x1 = x_pos
                x2 = x_pos + dx
                wire_ground(x1)
                wire_ground(x2)
                x_pos = x2
                continue

            if tip_node_top is not None and tip_node_top != node1_str:
                x_pos += gap

            x1 = x_pos
            x2 = x_pos + dx

            if isinstance(element, elm.Dot):
                d += element.at(((x1 + x2) / 2, 3.0))
            else:
                d += element.at((x1, 3.0)).to((x2, 3.0))

            loc1 = "left" if x1 < x2 else "right"
            loc2 = "right" if x1 < x2 else "left"
            d += elm.Label().at((x1, 3.0)).label(node1_str, loc=loc1, color="gray")
            d += elm.Label().at((x2, 3.0)).label(node2_str, loc=loc2, color="gray")

            wire_node(node1_str, x1, 3.0)
            wire_node(node2_str, x2, 3.0)

            tip_node_top = node2_str
            x_pos = x2

    # Return the raw SVG string
    svg_bytes = d.get_imagedata("svg")
    return svg_bytes.decode("utf-8")
