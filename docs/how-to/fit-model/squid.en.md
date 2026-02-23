---
aliases:
  - "Fitting SQUID Parameters"
tags:
  - diataxis/how-to
  - audience/user
  - sot/true
  - topic/analysis
status: stable
owner: team
audience: user
scope: "How to fit SQUID circuit parameters (Ls, C) from Admittance data"
version: v1.1.0
last_updated: 2026-01-31
updated_by: team
---

# Fitting SQUID Models

This guide explains how to perform **LC-SQUID** model fitting on ingested Admittance data to extract circuit parameters (Series Inductance $L_s$ and Capacitance $C$).

!!! info "Prerequisites"
    - Data has been ingested (see [Ingest HFSS Admittance Data](../ingest-data/hfss-admittance.md)).
    - You know the target Dataset **Name** or **ID**.

---

## Fitting Strategy

Choose the appropriate fitting mode based on your circuit design and data characteristics:

| Mode | Scenario | Flag |
|------|----------|------|
| **Standard (With Ls)** | General case, determine both $L_s$ and $C$ | (Default) |
| **Fixed Capacitance** | Known $C$ from measurement/design, optimize $L_s$ only | `--fixed-c <VAL>` |
| **Ideal LC (No Ls)** | Ignore series inductance (Pure LC resonance) | `--no-ls` |

---

## Steps

=== "CLI"

    The core command is `sc analysis fit lc-squid`.

    ### 1. Standard Fit

    Most common mode, fits both $L_s$ and $C$:

    ```bash
    uv run sc analysis fit lc-squid <DATASET_NAME>
    ```

    !!! tip "Specific Modes"
        To analyze only specific modes, use the `--modes` flag multiple times:
        ```bash
        uv run sc analysis fit lc-squid --modes 1 --modes 2 <DATASET_NAME>
        ```

    ### 2. Fixed Capacitance (Fixed C)

    When $C$ is known (e.g., $C=1.45$ pF), this mode provides more accurate $L_s$ results:

    ```bash
    uv run sc analysis fit lc-squid --fixed-c 1.45 <DATASET_NAME>
    ```

    ### 3. Parameter Bounds

    If results are unphysical (e.g., $L_s < 0$), enforce bounds:

    ```bash
    # Limit Ls <= 0.2 nH
    uv run sc analysis fit lc-squid --ls-max 0.2 <DATASET_NAME>
    ```

=== "UI (TBD)"

    !!! warning "Under Development"
        The Analysis GUI is currently under development.

    1. Navigate to **Analysis** page.
    2. Select **Dataset** from the list.
    3. Choose model (**LC-SQUID**) in "Fit Configuration".
    4. Set Constraints (e.g., check "Fixed C" and enter value).
    5. Click **Run Fit**.

---

## Viewing Results

After fitting, the system generates:

1. **Console Output**: Numerical results and RMSE for each Mode.
2. **HTML Plot**: Saved in `data/results/plots/`.
3. **JSON Metadata**: Saved in `data/results/json/`.

---

## See Also

- [Tutorial: End-to-End Fitting](../../tutorials/end-to-end-fitting.md)
- [CLI Reference: analysis fit](../../reference/cli/sc-fit-squid.md)
