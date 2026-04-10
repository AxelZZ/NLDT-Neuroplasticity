# NLDT Neuroplasticity v3.4

**Slow adaptive consolidation – From acute calcium signaling to therapeutic memory formation**

© 2026 Axel Zill-Zheng | Homebase Xiamen NLDT LAB

---

## Overview

This interactive model visualizes non-linear synaptic plasticity based on the **Non-Linear Dimensions Theory (NLDT)**. It simulates how calcium signals trigger a phase transition from a linear (blue) to a resonant (gold) state – and how this transition consolidates slowly over time.

**Key innovation:** Instead of binary hysteresis, the model implements **slow adaptive consolidation** – a learning saturation function that mirrors therapeutic memory formation.

---

## Features

| Feature | Description |
|---------|-------------|
| **BCM rule + validation** | Experimental data from Dudek & Bear (1992) |
| **λ from biophysics** | λ = n / K_d ≈ 4.29 µM⁻¹ (Bhalla 1999) |
| **Bi‑exponential Ca²⁺ transient** | Toggle between mono‑ and bi‑exponential kinetics |
| **M112 synapse grid** | 112 nodes – size = acute response, color = consolidated state |
| **Slow consolidation** | `base_res += α · (Φ_current − base_res)` |
| **Interactive controls** | Sliders for Ca²⁺, θ_LTD, θ_LTP, α |
| **Export** | JSON, CSV, PNG |
| **Animation** | Automatic sweep of Ca²⁺ concentration |

---

## Scientific Basis

The model uses the NLDT saturation function:

`Φ = tanh(λ · [Ca²⁺])`

Where `λ = n / K_d` is derived from CaMKII Hill kinetics (Bhalla & Iyengar 1999).

Plasticity follows the BCM/Graupner-Brunel rule:

`Ω = −A_d·H([Ca]−θ_LTD) + A_p·H([Ca]−θ_LTP)`

Validation data points are from Dudek & Bear (1992) – frequency-dependent LTP/LTD in hippocampal CA1.

**Slow consolidation** is implemented as:

`base_res += α · (Φ_current − base_res)`

This replaces binary hysteresis with a **therapeutically relevant memory formation**.

---

## Installation & Usage

### Requirements
- Python 3.9 or higher
- Required packages:
