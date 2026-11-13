#!/usr/bin/env python3
"""The paper's figures.      python3 make_journal_figs.py      (after paper_numbers.py and journal_numbers.py)

Twelve figures are drawn by the functions in make_figs.py. Here their in-image titles are removed (the caption does
that job) and the panels of a multi-panel figure are labelled (a), (b), ... The thirteenth, the random-filter
benchmark of Section 5.2, is drawn here.
"""
import json
import math
import sys
from pathlib import Path

import paths  # noqa: E402
import make_figs as mf  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

FIGS = paths.FIGS
J = json.loads((paths.RESULTS / "numbers_journal.json").read_text())


def save(fig, name):
    titled = [ax for ax in fig.axes if ax.get_title() or ax.get_title(loc="left")]
    many = len(titled) >= 2
    for i, ax in enumerate(titled):
        ax.set_title("")
        ax.set_title(f"({chr(97 + i)})" if many else "", loc="left", fontsize=9.5, fontweight="bold")
    for t in list(fig.texts):
        t.remove()
    out = FIGS / f"{name}.png"
    if any(ax.name == "3d" for ax in fig.axes):
        # the tight box leaves out the vertical-axis label of a 3-D plot unless it is named; make_figs trims the border afterwards
        fig.canvas.draw()
        fig.savefig(out, bbox_inches="tight", pad_inches=0.35, bbox_extra_artists=[lab for ax in fig.axes for lab in (ax.xaxis.label, ax.yaxis.label, ax.zaxis.label)])
    else:
        fig.savefig(out)
    plt.close(fig)
    print("wrote", out.name)


mf.save = save


def fig_random_filters():
    z = np.load(paths.WORK / "random_filters.npz")
    act = z["actual"]
    panels = [("iid_gross", act[0], "Sharpe ratio before costs", 2), ("iid_net", act[1], "Sharpe ratio after costs", 2),
              ("iid_long", act[3], "Long side: mean next-day return (basis points)", 1), ("iid_short", act[4], "Short side: mean next-day gain (basis points)", 1)]
    fig, axs = plt.subplots(2, 2, figsize=(mf.W, 4.9), gridspec_kw=dict(hspace=0.5, wspace=0.24))
    for i, (ax, (key, a, lab, d)) in enumerate(zip(axs.ravel(), panels)):
        x = z[key]
        lo, hi = min(x.min(), a), max(x.max(), a)
        pad = (hi - lo) * 0.06
        ax.hist(x, bins=np.linspace(lo - pad, hi + pad, 56), color="#9ec5f4", edgecolor="#ffffff", linewidth=0.3)
        ax.axvline(x.mean(), color=mf.POS_DARK, lw=1.3)
        ax.axvline(a, color=mf.ORANGE, lw=1.7)
        top = ax.get_ylim()[1]
        ax.set_ylim(0, top * 1.34)
        p = (float((x >= a).sum()) + 1) / (len(x) + 1)
        ptxt = "p < 0.001" if p < 0.001 else f"p = {p:.3f}"
        right = a >= x.mean()                       # the rule's label sits left of its line; the mean's label moves to whichever side is free
        ax.text(a - pad * 0.5, top * 1.29, f"rule: {a:.{d}f}\n{ptxt}".replace("-", "\u2212"), fontsize=7.8, color=mf.INK, va="top", ha="right")
        ax.text(x.mean() + (-pad * 0.5 if right else pad * 0.5), top * 1.29, f"random\nmean: {x.mean():.{d}f}".replace("-", "\u2212"), fontsize=7.8, color=mf.INK2,
                va="top", ha="right" if right else "left")
        ax.set_xlabel(lab)
        ax.set_title(f"({chr(97 + i)})", loc="left", fontsize=9.5, fontweight="bold")
        ax.grid(axis="x", visible=False)
        if i % 2 == 0:
            ax.set_ylabel(f"Count, of {J['rf_draws']} random filters")
    out = FIGS / "fig_random_filters.png"
    fig.savefig(out)
    plt.close(fig)
    print("wrote", out.name)


if __name__ == "__main__":
    for fn in (mf.fig01_flow, mf.fig02_coverage, mf.fig04_surface, mf.fig05_chain, mf.fig06_reading, mf.fig08_states, mf.fig09_equity,
               mf.fig10_years, mf.fig11_months, mf.fig12_sharpes, mf.fig13_luck, mf.fig14_dsr):
        fn()
    fig_random_filters()
