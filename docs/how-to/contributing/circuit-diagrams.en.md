# Contributing: Circuit Diagrams

This guide explains how to add or modify circuit diagrams in the project. We use **Schemdraw** (Python) to ensure consistent style and maintainability.

## Workflow Overview

1.  **Write Script**: Create a Python script in `scripts/docs/` to draw the circuit.
2.  **Generate Image**: Run the script to output an SVG to `docs/assets/`.
3.  **Embed in Docs**: Reference the image in Markdown and attach the source code.

## Detailed Steps

### 1. Install Tools
Ensure `schemdraw` is installed:
```bash
uv add schemdraw
```

### 2. Write the Script
Place your script in the `scripts/docs/` directory. Use a descriptive name, e.g., `generate_lc_schematic.py`.

**Template**:
```python
import schemdraw
import schemdraw.elements as elm

# Output path
OUTPUT_PATH = 'docs/assets/my_circuit.svg'

def draw():
    d = schemdraw.Drawing()

    # Draw your circuit here
    d += elm.SourceSin().up().label('Port')
    d += elm.Inductor().right().label('L')
    d += elm.Capacitor().down().label('C')
    d += elm.Ground()

    # Save file
    d.save(OUTPUT_PATH)
    print(f"Saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    draw()
```

### 3. Generate Image
Run the script from the project root:
```bash
uv run scripts/docs/generate_lc_schematic.py
```
Check `docs/assets/` to see if the SVG file works.

### 4. Embed in MkDocs
Use the following format in your Markdown file. We use `??? quote` to create a collapsible block that shows the code without cluttering the layout.

```markdown
![Circuit Name](../assets/my_circuit.svg)

??? quote "Source Code (Schemdraw)"
    ```python
    import schemdraw
    import schemdraw.elements as elm

    d = schemdraw.Drawing()
    d += elm.SourceSin().up().label('Port')
    d += elm.Inductor().right().label('L')
    d += elm.Capacitor().down().label('C')
    d += elm.Ground()
    d.save('my_circuit.svg')
    ```
```

## Why do we do this?

*   **Consistency**: Unified style for all diagrams.
*   **Vector Graphics**: SVGs look crisp at any resolution.
*   **Maintainability**: Future contributors can copy the code to modify the circuit (e.g., changing values) without redrawing from scratch.

---

## Agent Rule { #agent-rule }

```markdown
## Circuit Diagrams
- **Tool**: Schemdraw (Python).
- **Format**: SVG.
- **Location**: Scripts in `scripts/docs/`, Images in `docs/assets/`.
- **Constraint**: All diagrams MUST be generated via code (No manual drawing tools).
```
