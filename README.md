markdown
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
pip install numpy matplotlib


### Run the model
python nldt_neuro_v3.4.py


The interactive window opens with all controls.

### Controls

| Slider | Function |
|--------|----------|
| `Ca²⁺ SS (µM)` | Steady‑state calcium concentration |
| `Ca²⁺ Peak (µM)` | Peak amplitude after stimulation |
| `θ_LTD (µM)` | LTD threshold (Calcineurin) |
| `θ_LTP (µM)` | LTP threshold (CaMKII T286) |
| `α` | Consolidation rate (memory speed) |

| Button | Function |
|--------|----------|
| `▶ Animation` | Automatic Ca²⁺ sweep |
| `⇄ Bi-Exp` | Toggle mono‑/bi‑exponential transient |
| `JSON Save / Load` | Save/load full model state |
| `CSV Export` | Export sweep data |
| `Save PNG` | Screenshot |
| `Reset θ` | Reset thresholds to literature values |
| `? Help` | Cycle through help topics |

---

## Interpretation

- **Blue phase** – linear response, no consolidation
- **Gold phase** – resonant state, S ≥ 0.68
- **Φ_base** – consolidated therapeutic memory (slowly increases with each Ca²⁺ peak)

The model shows that therapeutic breakthroughs are not binary switches – they **consolidate** over time. The parameter `α` controls how fast this consolidation happens.

---

## References

- Bhalla, U. S. & Iyengar, R. (1999). *Science*, 283(5400), 381–387.
- Chang, J. Y. et al. (2017). *PNAS*, 114(29), E5999–E6007.
- Dudek, S. M. & Bear, M. F. (1992). *PNAS*, 89(10), 4363–4367.
- Graupner, M. & Brunel, N. (2012). *PNAS*, 109(10), 3991–3996.
- Mulkey, R. M. et al. (1993). *Science*, 261(5124), 1051–1055.
- Oertner, T. G. et al. (2002). *Nat. Neurosci.*, 5(7), 657–665.

---
## Disclaimer

This model is a scientific simulation tool based on the NLDT framework. It is **not** a medical device, diagnostic tool, or treatment recommendation. The results are for research, educational, and exploratory purposes only. Always consult qualified healthcare professionals for medical advice.

## License

MIT License

Copyright (c) 2026 Axel Zill-Zheng

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Author

**Axel Zill-Zheng** | Homebase Xiamen NLDT LAB  
© 2026 Axel Zill-Zheng
