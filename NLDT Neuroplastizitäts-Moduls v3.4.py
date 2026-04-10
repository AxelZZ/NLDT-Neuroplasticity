#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NLDT Neuroplasticity Module v3.4
================================
Slow Adaptive Consolidation – From acute calcium signaling to therapeutic memory formation

DISCLAIMER:
This model is a scientific simulation tool based on the NLDT framework.
It is NOT a medical device, diagnostic tool, or treatment recommendation.
The results are for research, educational, and exploratory purposes only.
Always consult qualified healthcare professionals for medical advice.

© 2026 Axel Zill-Zheng | Homebase Xiamen NLDT LAB
All rights reserved.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as mgridspec
from matplotlib.widgets import Slider, Button
from matplotlib.animation import FuncAnimation
import datetime
import json
import csv
import tkinter as tk
from tkinter import filedialog

print("=== NLDT Neuroplasticity Module v3.4 – Final Version ===\n")
print("© 2026 Axel Zill-Zheng | Homebase Xiamen NLDT LAB | All rights reserved.\n")

# =====================================================================
# BIOPHYSICAL PARAMETERS
# =====================================================================
THETA_LTD     = 0.35
THETA_LTP     = 0.55
CAMKII_HILL_N = 3
CAMKII_KD     = 0.70
LAM_PHYSICAL  = CAMKII_HILL_N / CAMKII_KD

A_D, A_P      = 0.5, 1.0
N_SYN         = 112

TAU_CA        = 0.050
TAU_FAST      = 0.020
TAU_SLOW      = 0.150
FRAC_FAST     = 0.70
CA_REST       = 0.08

# Validation data
VALIDATION_DATA = [
    (0.10,  0.00,  0.05), (0.25,  0.00,  0.08), (0.38, -0.35,  0.12),
    (0.42, -0.50,  0.15), (0.48, -0.40,  0.13), (0.58,  0.20,  0.18),
    (0.75,  0.65,  0.20), (1.00,  0.85,  0.15), (1.50,  0.90,  0.12),
]
VAL_CA  = np.array([d[0] for d in VALIDATION_DATA])
VAL_OM  = np.array([d[1] for d in VALIDATION_DATA])
VAL_ERR = np.array([d[2] for d in VALIDATION_DATA])

# =====================================================================
# MODEL CLASS
# =====================================================================
class NLDTNeuroModel:
    def __init__(self):
        self.ca_ss      = 0.50
        self.ca_peak    = 0.80
        self.theta_ltd  = THETA_LTD
        self.theta_ltp  = THETA_LTP
        self.alpha      = 0.035
        self.bi_exp     = False
        self.base_res   = 0.0

        rng = np.random.default_rng(42)
        self.theta_ltp_pop = np.clip(rng.normal(THETA_LTP, 0.08, N_SYN), 0.30, 1.20)
        self.theta_ltd_pop = np.clip(rng.normal(THETA_LTD, 0.05, N_SYN), 0.10, 0.70)
        self.kd_pop        = np.clip(rng.normal(CAMKII_KD, 0.10, N_SYN), 0.30, 1.20)
        self.lam_pop       = CAMKII_HILL_N / self.kd_pop

    def nldt_resonance(self, ca):
        return np.tanh(LAM_PHYSICAL * ca)

    def camkii_activation(self, ca):
        ca_n = np.power(np.maximum(ca, 0), CAMKII_HILL_N)
        kd_mean = np.mean(self.kd_pop)
        return ca_n / (kd_mean**CAMKII_HILL_N + ca_n)

    def bcm_omega(self, ca):
        if np.isscalar(ca):
            ltd = -A_D if ca >= self.theta_ltd else 0.0
            ltp = A_P if ca >= self.theta_ltp else 0.0
            return ltd + ltp
        else:
            return (-A_D * (ca >= self.theta_ltd).astype(float) +
                    A_P * (ca >= self.theta_ltp).astype(float))

    def ca_transient(self, t, ca_peak):
        if self.bi_exp:
            decay = FRAC_FAST * np.exp(-t / TAU_FAST) + (1 - FRAC_FAST) * np.exp(-t / TAU_SLOW)
        else:
            decay = np.exp(-t / TAU_CA)
        return CA_REST + (ca_peak - CA_REST) * decay

    def update_consolidation(self, phi_current):
        self.base_res = self.base_res + self.alpha * (phi_current - self.base_res)
        self.base_res = np.clip(self.base_res, 0.0, 1.0)

    def get_synapse_state(self, ca_ss):
        res   = self.nldt_resonance(ca_ss)
        state = np.where(ca_ss >= self.theta_ltp_pop,  1,
                np.where(ca_ss >= self.theta_ltd_pop, -1, 0))
        return res, state


# =====================================================================
# FIGURE SETUP
# =====================================================================
model = NLDTNeuroModel()

fig = plt.figure(figsize=(24, 20), facecolor='#0d1117')

# Überschrift – ganz oben
fig.suptitle(r'NLDT Neuroplasticity v3.4 – $\Phi = \tanh(\lambda \cdot [\mathrm{Ca}^{2+}])$ with Adaptive Consolidation',
             fontsize=12, color='white', y=0.98, fontweight='bold')

gs = mgridspec.GridSpec(3, 5, 
                        height_ratios=[1.55, 1.1, 0.35],
                        width_ratios=[1.02, 1.0, 0.9, 0.82, 0.82],
                        hspace=0.80,
                        wspace=0.40, figure=fig)

# 1. BCM Curve
ax_bcm = fig.add_subplot(gs[0, 0])
ax_bcm.set_facecolor('#0a0e14')
ax_bcm.set_title('Ω([Ca²⁺]) – BCM Rule + Dudek & Bear 1992', color='white', fontsize=10)
ax_bcm.set_xlabel('[Ca²⁺] (µM)', color='white')
ax_bcm.set_ylabel('Ω', color='white')
ax_bcm.grid(True, color='#1a2535', lw=0.5, ls='--')

ca_range = np.linspace(0, 2.5, 500)
ax_bcm.plot(ca_range, model.bcm_omega(ca_range), color='#ffffff', lw=2.2, label='BCM Ω')
ax_bcm.plot(ca_range, model.nldt_resonance(ca_range), color='#ffd700', lw=1.8, ls='--', label='NLDT Φ')
ax_bcm.plot(ca_range, model.camkii_activation(ca_range), color='#ff6688', lw=1.6, ls=':', label='CaMKII')

ax_bcm.errorbar(VAL_CA, VAL_OM, yerr=VAL_ERR, fmt='o', color='#ffaa00', markersize=5, capsize=3, label='Exp. Data')
ax_bcm.axvline(THETA_LTD, color='#4488ff', lw=1.1, ls='--')
ax_bcm.axvline(THETA_LTP, color='#ff4444', lw=1.1, ls='--')
ax_bcm.legend(fontsize=8, loc='lower right', facecolor='#0d1117', labelcolor='white')

# 2. Ca²⁺ Transient
ax_kin = fig.add_subplot(gs[0, 1])
ax_kin.set_facecolor('#0a0e14')
ax_kin.set_title('Ca²⁺ Transient & CaMKII Activation', color='white', fontsize=10)
ax_kin.set_xlabel('Time (ms)', color='white')
ax_kin.set_ylabel('CaMKII Activation', color='#ff6688')
ax_kin.grid(True, color='#1a2535', lw=0.5, ls='--')

t_ms = np.linspace(0, 500, 1000)
t_s  = t_ms / 1000.0

camk_trace_line, = ax_kin.plot([], [], color='#ff6688', lw=2.0)
ax_kin_ca = ax_kin.twinx()
ca_line_mono, = ax_kin_ca.plot([], [], color='#1f77b4', lw=2.0, label='Mono-exp')
ca_line_bi,   = ax_kin_ca.plot([], [], color='#44ddff', lw=1.8, ls='--', alpha=0.0, label='Bi-exp')
ax_kin_ca.set_ylabel('[Ca²⁺] (µM)', color='#1f77b4')

# 3. Synapse Grid
ax_grid = fig.add_subplot(gs[0, 2])
ax_grid.set_facecolor('#0a0e14')
ax_grid.set_title('M112 Synapse Grid\nSize = acute | Color = consolidated', 
                  color='white', fontsize=9.8, pad=8)
ax_grid.axis('off')

th_sp = np.linspace(0, 12*np.pi, N_SYN)
r_sp  = np.linspace(0.3, 3.8, N_SYN)
xg = r_sp * np.cos(th_sp)
yg = r_sp * np.sin(th_sp) * 0.35
scatter_syn = ax_grid.scatter(xg, yg, s=50, c='#333333', edgecolors='#444', lw=0.8)

# 4. Circular Progress Ring – kompakt, weit rechts
ax_circle = fig.add_axes([0.62, 0.645, 0.09, 0.09])

ax_circle.set_facecolor('#0a0e14')
ax_circle.axis('off')
ax_circle.set_aspect('equal')

# Hintergrund-Ring
theta_bg = np.linspace(0, 2*np.pi, 200)
ax_circle.plot(np.cos(theta_bg), np.sin(theta_bg), color='#333333', lw=10, alpha=0.6)

# Fortschritts-Ring
progress_line, = ax_circle.plot([], [], color='#ffd700', lw=8, solid_capstyle='round')

progress_text = ax_circle.text(0, 0, '0.0%', ha='center', va='center', 
                               fontsize=10, fontweight='bold', color='white')

def update_circular_progress():
    prog = model.base_res
    if prog < 0.001:
        progress_line.set_data([], [])
    else:
        theta_fill = np.linspace(-np.pi/2, -np.pi/2 - 2*np.pi * prog, 180)
        x = np.cos(theta_fill)
        y = np.sin(theta_fill)
        progress_line.set_data(x, y)
    
    progress_text.set_text(f'{prog*100:.1f}%')
    progress_line.set_color(plt.cm.plasma(0.3 + 0.7*prog))

# 5. λ Derivation
ax_lam = fig.add_subplot(gs[0, 3])
ax_lam.set_facecolor('#0a0e1a')
ax_lam.axis('off')
ax_lam.set_title('λ Derivation', color='#ffd700', fontsize=9, pad=4)
ax_lam.text(0.05, 0.92, r'$\Phi = \tanh(\lambda \cdot [\mathrm{Ca}^{2+}])$', 
            transform=ax_lam.transAxes, color='#ffd700', fontsize=10)
ax_lam.text(0.05, 0.78, r'$\lambda = n / K_d \approx 4.29\,\mu\mathrm{M}^{-1}$', 
            transform=ax_lam.transAxes, color='white', fontsize=8)
ax_lam.text(0.05, 0.65, "n=3 (Hill) | K_d=0.70µM (Bhalla 1999)", 
            transform=ax_lam.transAxes, color='#aaaaaa', fontsize=7)

# 6. Help Panel
ax_help = fig.add_subplot(gs[0, 4])
ax_help.set_facecolor('#0a1010')
ax_help.axis('off')
ax_help.set_title('Help', color='#ffd700', fontsize=9, pad=4)
help_body = ax_help.text(0.05, 0.88, "", transform=ax_help.transAxes, color='white', fontsize=7.5, va='top', wrap=True)

help_texts = {
    "BCM Model": "Ω = −A_d·H([Ca]−θ_LTD) + A_p·H([Ca]−θ_LTP)\nA_d=0.5, A_p=1.0 (Graupner & Brunel 2012)",
    "λ Derivation": "λ = n / K_d ≈ 4.29 µM⁻¹\nApproximation of Hill equation for low [Ca]",
    "Consolidation": "base_res += α · (Φ_current − base_res)\nSlow memory formation (therapeutically relevant)",
    "Synapse Population": "N=112 synapses with heterogeneity\nSize = acute response | Color = long-term consolidation"
}
current_help = ["BCM Model"]

def update_help():
    topic = current_help[0]
    help_body.set_text(help_texts.get(topic, ""))
    fig.canvas.draw_idle()

# Table
ax_table = fig.add_subplot(gs[1, :4])
ax_table.axis('off')

# Parameters
ax_param = fig.add_subplot(gs[1, 4])
ax_param.set_facecolor('#0a0e1a')
ax_param.axis('off')
ax_param.set_title('Parameters', color='white', fontsize=9, pad=4)

# =====================================================================
# SLIDERS & BUTTONS (weiter nach unten)
# =====================================================================
ax_sl_ca    = fig.add_axes([0.08, 0.115, 0.38, 0.020])
ax_sl_peak  = fig.add_axes([0.08, 0.088, 0.38, 0.020])
ax_sl_ltd   = fig.add_axes([0.08, 0.061, 0.38, 0.020])
ax_sl_ltp   = fig.add_axes([0.08, 0.034, 0.38, 0.020])
ax_sl_alpha = fig.add_axes([0.08, 0.007, 0.38, 0.020])

slider_ca    = Slider(ax_sl_ca,   'Ca²⁺ SS (µM)', 0.0, 2.5, valinit=0.50, color='#1f77b4')
slider_peak  = Slider(ax_sl_peak, 'Ca²⁺ Peak (µM)', 0.0, 2.5, valinit=0.80, color='#44aaff')
slider_ltd   = Slider(ax_sl_ltd,  'θ_LTD (µM)', 0.1, 1.0, valinit=THETA_LTD, color='#4488ff')
slider_ltp   = Slider(ax_sl_ltp,  'θ_LTP (µM)', 0.1, 1.5, valinit=THETA_LTP, color='#ff4444')
slider_alpha = Slider(ax_sl_alpha, 'α (Consolidation Rate)', 0.001, 0.15, valinit=0.035, color='#ffaa88')

for sl in [slider_ca, slider_peak, slider_ltd, slider_ltp, slider_alpha]:
    sl.label.set_color('white')
    sl.valtext.set_color('white')

def _btn(rect, label, bg='#21262d'):
    ax = fig.add_axes(rect)
    b = Button(ax, label, color=bg, hovercolor='#30363d')
    b.label.set_color('white')
    return b

btn_anim  = _btn([0.63, 0.095, 0.082, 0.025], '▶ Animation')
btn_bi    = _btn([0.63, 0.067, 0.082, 0.025], '⇄ Bi-Exp')
btn_json  = _btn([0.72, 0.095, 0.082, 0.025], 'JSON Save')
btn_load  = _btn([0.72, 0.067, 0.082, 0.025], 'JSON Load')
btn_csv   = _btn([0.81, 0.095, 0.082, 0.025], 'CSV Export')
btn_save  = _btn([0.81, 0.067, 0.082, 0.025], 'Save PNG')
btn_reset = _btn([0.90, 0.095, 0.082, 0.025], 'Reset θ')
btn_help  = _btn([0.90, 0.067, 0.082, 0.025], '? Help')

# =====================================================================
# UPDATE & EVENT HANDLERS
# =====================================================================
_anim_obj = [None]

def update_bcm():
    ax_bcm.lines[0].set_ydata(model.bcm_omega(ca_range))
    ax_bcm.lines[1].set_ydata(model.nldt_resonance(ca_range))
    ax_bcm.lines[2].set_ydata(model.camkii_activation(ca_range))

def update_transient():
    ca_mono = model.ca_transient(t_s, model.ca_peak)
    ca_bi   = model.ca_transient(t_s, model.ca_peak) if model.bi_exp else ca_mono
    ca_line_mono.set_data(t_ms, ca_mono)
    ca_line_bi.set_data(t_ms, ca_bi)
    ca_line_bi.set_alpha(0.75 if model.bi_exp else 0.0)
    camk_t = model.camkii_activation(ca_mono if not model.bi_exp else ca_bi)
    camk_trace_line.set_data(t_ms, camk_t)

def update_grid():
    res, _ = model.get_synapse_state(model.ca_ss)
    sizes = (20 + res * 65).ravel()
    scatter_syn.set_sizes(sizes)
    colors = plt.cm.plasma(model.base_res)
    scatter_syn.set_color(colors)

def update_table():
    ax_table.clear()
    ax_table.axis('off')
    headers = ["Parameter", "Value", "Unit", "Reference"]
    rows = [
        ["Ca²⁺ SS", f"{model.ca_ss:.3f}", "µM", "Slider"],
        ["Ca²⁺ Peak", f"{model.ca_peak:.3f}", "µM", "Slider"],
        ["θ_LTD", f"{model.theta_ltd:.3f}", "µM", "Mulkey 1993"],
        ["θ_LTP", f"{model.theta_ltp:.3f}", "µM", "Chang 2017"],
        ["λ", f"{LAM_PHYSICAL:.3f}", "µM⁻¹", "Bhalla 1999"],
        ["Φ (current)", f"{model.nldt_resonance(model.ca_ss):.4f}", "–", "NLDT"],
        ["Φ_base (consol.)", f"{model.base_res:.4f}", "–", f"α={model.alpha:.4f}"],
        ["CaMKII", f"{model.camkii_activation(model.ca_ss):.4f}", "–", "Bhalla 1999"],
        ["Ω BCM", f"{model.bcm_omega(model.ca_ss):+.2f}", "–", "Graupner 2012"],
        ["Regime", "LTP" if model.ca_ss >= model.theta_ltp else "LTD" if model.ca_ss >= model.theta_ltd else "none", "–", "BCM"],
        ["LTP/LTD/inactive", f"{int(np.sum(model.get_synapse_state(model.ca_ss)[1]==1))}/{int(np.sum(model.get_synapse_state(model.ca_ss)[1]==-1))}/{int(np.sum(model.get_synapse_state(model.ca_ss)[1]==0))}", f"/{N_SYN}", "Oertner 2002"],
    ]
    tbl = ax_table.table(cellText=rows, colLabels=headers, loc='center', cellLoc='center', colWidths=[0.28, 0.16, 0.09, 0.34])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_height(0.052)
        cell.set_facecolor('#0d1117' if row % 2 == 0 else '#111820')
        cell.set_text_props(color='white')
        cell.set_edgecolor('#1f2a3a')

def update(val=None):
    model.ca_ss     = slider_ca.val
    model.ca_peak   = slider_peak.val
    model.theta_ltd = slider_ltd.val
    model.theta_ltp = slider_ltp.val
    model.alpha     = slider_alpha.val

    phi_current = model.nldt_resonance(model.ca_ss)
    model.update_consolidation(phi_current)

    update_bcm()
    update_transient()
    update_grid()
    update_circular_progress()
    update_table()

    fig.canvas.draw_idle()

def toggle_bi_exp(event):
    model.bi_exp = not model.bi_exp
    btn_bi.label.set_text('⇄ Bi-Exp ✓' if model.bi_exp else '⇄ Bi-Exp')
    update()

def toggle_animation(event):
    global _anim_obj
    if _anim_obj[0] is not None:
        try:
            _anim_obj[0].event_source.stop()
        except:
            pass
        _anim_obj[0] = None
        btn_anim.label.set_text('▶ Animation')
        fig.canvas.draw_idle()
        return

    def anim_step(frame):
        new_ca = min(slider_ca.val + 0.012, 2.5)
        slider_ca.set_val(new_ca)
        update()
        return []

    _anim_obj[0] = FuncAnimation(fig, anim_step, interval=90, blit=False, cache_frame_data=False, repeat=True)
    btn_anim.label.set_text('❚❚ Pause')
    fig.canvas.draw_idle()

def export_json(event):
    data = {
        "ca_ss": model.ca_ss, "ca_peak": model.ca_peak,
        "theta_ltd": model.theta_ltd, "theta_ltp": model.theta_ltp,
        "alpha": model.alpha, "bi_exp": model.bi_exp,
        "base_res": model.base_res,
        "timestamp": datetime.datetime.now().isoformat(),
        "model": "NLDT Neuro v3.4"
    }
    fname = f"nldt_neuro_v3.4_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(fname, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"✅ JSON saved: {fname}")

def load_json(event):
    try:
        root = tk.Tk(); root.withdraw()
        fname = filedialog.askopenfilename(title="Load JSON", filetypes=[("JSON", "*.json")])
        root.destroy()
        if not fname: return
        with open(fname, "r", encoding='utf-8') as f:
            data = json.load(f)
        if "ca_ss" in data: slider_ca.set_val(data["ca_ss"])
        if "ca_peak" in data: slider_peak.set_val(data["ca_peak"])
        if "theta_ltd" in data: slider_ltd.set_val(data["theta_ltd"])
        if "theta_ltp" in data: slider_ltp.set_val(data["theta_ltp"])
        if "alpha" in data: slider_alpha.set_val(data["alpha"])
        if "bi_exp" in data:
            model.bi_exp = data["bi_exp"]
            btn_bi.label.set_text('⇄ Bi-Exp ✓' if model.bi_exp else '⇄ Bi-Exp')
        if "base_res" in data:
            model.base_res = data["base_res"]
        update()
        print(f"✅ JSON loaded: {fname}")
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")

def export_csv(event):
    fname = f"nldt_neuro_v3.4_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    ca_sweep = np.linspace(0, 2.5, 250)
    with open(fname, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["ca_um", "phi", "camkii", "omega_bcm", "regime", "base_res", "alpha"])
        for ca in ca_sweep:
            phi = float(model.nldt_resonance(ca))
            camk = float(model.camkii_activation(ca))
            om = float(model.bcm_omega(ca))
            regime = "LTP" if ca >= model.theta_ltp else "LTD" if ca >= model.theta_ltd else "none"
            writer.writerow([round(ca,4), round(phi,5), round(camk,5), round(om,3), regime, round(model.base_res,4), model.alpha])
    print(f"✅ CSV exported: {fname}")

def save_png(event):
    fname = f"NLDT_Neuro_v3.4_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    fig.savefig(fname, dpi=350, bbox_inches='tight', facecolor='#0d1117')
    print(f"✅ PNG saved: {fname}")

def reset_thresholds(event):
    slider_ltd.set_val(THETA_LTD)
    slider_ltp.set_val(THETA_LTP)
    update()

def cycle_help(event):
    topics = list(help_texts.keys())
    idx = topics.index(current_help[0])
    current_help[0] = topics[(idx + 1) % len(topics)]
    update_help()

# Bindings
btn_bi.on_clicked(toggle_bi_exp)
btn_anim.on_clicked(toggle_animation)
btn_json.on_clicked(export_json)
btn_load.on_clicked(load_json)
btn_csv.on_clicked(export_csv)
btn_save.on_clicked(save_png)
btn_reset.on_clicked(reset_thresholds)
btn_help.on_clicked(cycle_help)

for sl in (slider_ca, slider_peak, slider_ltd, slider_ltp, slider_alpha):
    sl.on_changed(update)

# =====================================================================
# START
# =====================================================================
update_help()
update()

# Alles nach unten schieben, nur Überschrift bleibt oben
plt.subplots_adjust(left=0.05, right=0.95, top=0.94, bottom=0.08)

_anim_obj[0] = None
fig.canvas.draw_idle()

print("NLDT Neuroplasticity v3.4 started – Click ▶ Animation to start")
plt.show()
