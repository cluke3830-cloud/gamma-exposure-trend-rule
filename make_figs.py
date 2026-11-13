#!/usr/bin/env python3
"""Drawing functions for the paper's figures. Used by make_journal_figs.py, which is the script to run.

Every figure reads the files paper_numbers.py wrote, so a figure cannot disagree with the text.
Style: one y-axis per panel, thin marks, recessive grid, colour follows the entity in every figure
(Gamma A+C orange, buy-and-hold QQQ blue, trend-only rule aqua), and a blue-to-red scale with a grey
midpoint for anything signed. The three series colours were checked with the palette validator.
"""
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Patch  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

import paths  # noqa: E402

DATA, FIGS = paths.WORK, paths.FIGS
V = json.loads((paths.RESULTS / "numbers.json").read_text())
RAW = json.loads((paths.RESULTS / "numbers_raw.json").read_text())

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
NEUTRAL = "#b9b8b1"
POS_TINT, NEG_TINT, MID_TINT = "#cde2fb", "#f7d2cd", "#f0efec"
POS_DARK, NEG_DARK = "#184f95", "#b3261e"
DIV = LinearSegmentedColormap.from_list("div", [NEG_DARK, "#ef8a7e", MID_TINT, "#6da7ec", POS_DARK])
SEQ = LinearSegmentedColormap.from_list("seq", ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"])
R_F, Q_DIV = 0.04, 0.014
W = 6.5

plt.rcParams.update({
    "figure.facecolor": "#ffffff", "axes.facecolor": "#ffffff", "savefig.facecolor": "#ffffff",
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 8.5, "axes.titlesize": 9.5, "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.labelsize": 8.5,
    "legend.fontsize": 8, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
    "axes.titlecolor": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 1.6, "legend.frameon": False,
    "savefig.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.08,
})


def save(fig, name):
    out = FIGS / f"{name}.png"
    fig.savefig(out)
    plt.close(fig)
    print("wrote", out.name)


def pdf(x):
    return np.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def cdf(x):
    from scipy.special import ndtr
    return ndtr(x)


def bsm(S, K, T, sig, cp=1.0):
    d1 = (np.log(S / K) + (R_F - Q_DIV + 0.5 * sig ** 2) * T) / (sig * np.sqrt(T))
    d2 = d1 - sig * np.sqrt(T)
    price = cp * (S * np.exp(-Q_DIV * T) * cdf(cp * d1) - K * np.exp(-R_F * T) * cdf(cp * d2))
    delta = cp * np.exp(-Q_DIV * T) * cdf(cp * d1)
    gamma = np.exp(-Q_DIV * T) * pdf(d1) / (S * sig * np.sqrt(T))
    return price, delta, gamma


# ------------------------------------------------------------------------------------------------ 1 flow
def fig01_flow():
    fig, ax = plt.subplots(figsize=(W, 5.8))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    def box(x, y, w, h, title, body, tag=None, fc="#ffffff"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.4", fc=fc, ec=AXIS, lw=0.9))
        ax.text(x + w / 2, y + h - 2.4, title, ha="center", va="top", fontsize=8.8, fontweight="bold", color=INK)
        ax.text(x + w / 2, y + h - 7.0, body, ha="center", va="top", fontsize=7.8, color=INK2, linespacing=1.4)
        if tag:
            ax.text(x + w / 2, y + 2.0, tag, ha="center", va="bottom", fontsize=7.8, fontweight="bold", color=INK)

    def arrow(x0, y0, x1, y1):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.0, shrinkA=0, shrinkB=0))

    def caption(y, text):
        ax.text(1, y, text, ha="left", va="center", fontsize=7.4, color=MUTED, fontweight="bold")

    caption(98.2, "THREE QUESTIONS, ASKED JUST BEFORE EVERY MARKET CLOSE")
    box(1, 71, 31, 24.5, "1   Yesterday's options", "Among S&P 500 options that\nexpire in 1 to 8 days, did calls\nor puts hold more gamma?", "CALL-HEAVY  or  PUT-HEAVY")
    box(34.5, 71, 31, 24.5, "2   Today's move", "Did the QQQ fund go up\nor down today?", "UP  or  DOWN")
    box(68, 71, 31, 24.5, "3   The one-month trend", "Is QQQ above or below its\nprice of 20 trading days ago?", "ABOVE  or  BELOW")

    caption(64.3, "TWO VOTES")
    box(1, 43, 64.5, 18.5, "Vote A: the option vote",
        "Call-heavy yesterday:  vote the SAME way as today's move\nPut-heavy yesterday:  vote the OPPOSITE way to today's move")
    box(68, 43, 31, 18.5, "Vote C: the trend vote", "Above:  vote UP\nBelow:  vote DOWN")
    arrow(16.5, 71, 16.5, 61.5)
    arrow(50, 71, 50, 61.5)
    arrow(83.5, 71, 83.5, 61.5)

    ax.plot([33.25, 33.25], [43, 37], color=MUTED, lw=1.0)
    ax.plot([83.5, 83.5], [43, 37], color=MUTED, lw=1.0)
    ax.plot([16.5, 83.5], [37, 37], color=MUTED, lw=1.0)
    ax.text(58.4, 39.2, "compare the two votes", ha="center", va="center", fontsize=7.4, color=MUTED, fontweight="bold")
    for x in (16.5, 50, 83.5):
        arrow(x, 37, x, 30.5)
    caption(33.6, "ONE DECISION")
    box(1, 12, 31, 18.5, "Both vote UP", "LONG\nown QQQ for one day", fc=POS_TINT)
    box(34.5, 12, 31, 18.5, "The votes disagree", "CASH\nown nothing for one day", fc=MID_TINT)
    box(68, 12, 31, 18.5, "Both vote DOWN", "SHORT\nbet on a fall for one day", fc=NEG_TINT)
    ax.text(50, 5.0, "The position lasts from today's close to tomorrow's close. Then the three questions are asked again.",
            ha="center", va="center", fontsize=8.0, color=INK2)
    save(fig, "fig01_flow")


# ------------------------------------------------------------------------------------------------ 2 data coverage
def fig02_coverage():
    c = pd.read_csv(DATA / "chain_counts.csv", index_col=0, parse_dates=True)
    fig, ax = plt.subplots(figsize=(W, 2.9))
    ax.scatter(c.index, c["contracts"], s=2.2, color="#9ec5f4", linewidths=0, label="One trading day", rasterized=True)
    med = c["contracts"].rolling(21, min_periods=10).median()
    ax.plot(c.index, med, color=POS_DARK, lw=1.5, label="Median of the last 21 trading days")
    ax.set_ylim(0, None)
    ax.set_ylabel("Option contracts used that day")
    ax.set_title("How many option contracts went into each day's reading")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_ylim(0, 1650)
    ax.text(pd.Timestamp("2018-02-01"), 1590, f"2018 to 2021: typically {V['med_contracts_1821']} contracts a day,\nfrom {V['med_exp_1821']} expiry dates", fontsize=7.8, color=INK2, va="top")
    ax.text(pd.Timestamp("2022-07-01"), 1590, f"2023 to 2026: typically {V['med_contracts_2326']} contracts a day,\nfrom {V['med_exp_2326']} expiry dates", fontsize=7.8, color=INK2, va="top")
    ax.legend(loc="upper center", markerscale=3, bbox_to_anchor=(0.5, -0.11), ncol=2)
    save(fig, "fig02_coverage")


# ------------------------------------------------------------------------------------------------ 3 option basics
def fig03_basics():
    K, sig, T = 6800.0, 0.20, 5 / 365
    S = np.linspace(6400, 7200, 401)
    price, delta, gamma = bsm(S, K, T, sig)
    fig, axs = plt.subplots(3, 1, figsize=(W, 6.0), sharex=True, gridspec_kw=dict(hspace=0.28))
    a = axs[0]
    a.plot(S, np.maximum(S - K, 0), color=NEUTRAL, lw=1.4, label="Value on the expiry day")
    a.plot(S, price, color=BLUE, label="Value 5 days before expiry")
    a.set_ylabel("Call value (index points)")
    a.set_title("A call option's value bends as the index moves")
    a.legend(loc="upper left")
    a.text(K + 8, 395, "strike price 6,800", fontsize=7.8, color=INK2, va="top", ha="left")
    b = axs[1]
    b.plot(S, delta, color=BLUE)
    b.set_ylabel("Delta")
    b.set_ylim(-0.03, 1.03)
    b.set_title("Delta: the slope of that curve (the hedge the dealer must hold)")
    c = axs[2]
    c.plot(S, gamma * 0.01 * S, color=BLUE)
    c.set_ylabel("Change in delta\nfor a 1% index move")
    c.set_title("Gamma: how fast delta changes (largest when the index is near the strike)")
    c.set_xlabel("S&P 500 index level")
    c.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    for ax in axs:
        ax.axvline(K, color=AXIS, lw=0.8, zorder=0)
    save(fig, "fig03_basics")


# ------------------------------------------------------------------------------------------------ 4 gamma surface
def fig04_surface():
    S0, sig = 6800.0, 0.20
    m = np.linspace(0.94, 1.06, 161)
    d = np.linspace(1, 8, 113)
    MM, DD = np.meshgrid(m, d)
    _, _, gamma = bsm(S0, MM * S0, DD / 365.0, sig)
    Z = gamma * 0.01 * S0
    fig = plt.figure(figsize=(W, 4.7))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(MM * 100, DD, Z, cmap=SEQ, linewidth=0, antialiased=True, rcount=113, ccount=161, vmin=0, vmax=float(Z.max()))
    ax.set_xlabel("Strike price, % of the index level", labelpad=6)
    ax.set_ylabel("Days to expiry", labelpad=4)
    ax.set_zlabel("Change in delta for a 1% index move", labelpad=6)
    ax.set_yticks(range(1, 9))
    ax.view_init(elev=27, azim=-56)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.set_pane_color((1, 1, 1, 1))
        axis._axinfo["grid"]["color"] = GRID
        axis._axinfo["grid"]["linewidth"] = 0.5
    ax.tick_params(labelsize=7.5, pad=1)
    ax.set_box_aspect((1.25, 1.0, 0.72), zoom=0.92)
    fig.subplots_adjust(left=-0.02, right=0.98, bottom=-0.02, top=1.04)
    fig.text(0.07, 0.93, "The gamma surface: highest where the strike equals the index level and expiry is one day away",
             fontsize=9.3, fontweight="bold", color=INK, ha="left", va="center")
    save(fig, "fig04_gamma_surface")
    from PIL import Image, ImageChops        # the 3-D axes box is larger than what it draws: trim the empty white border
    im = Image.open(FIGS / "fig04_gamma_surface.png").convert("RGB")
    box = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    pad = 14
    im.crop((max(box[0] - pad, 0), max(box[1] - pad, 0), min(box[2] + pad, im.width), min(box[3] + pad, im.height))).save(FIGS / "fig04_gamma_surface.png", dpi=(200, 200))


# ------------------------------------------------------------------------------------------------ 5 real chain heat map
def fig05_chain():
    ex = pd.read_csv(DATA / "example_chain.csv")
    S0 = float(V["ex_S"].replace(",", ""))
    ex = ex[ex["money"].abs() <= 0.04].copy()
    ex["band"] = (np.floor(ex["strike"] / 25.0) * 25).astype(int)
    pv = ex.pivot_table(index=["dte", "exp_date"], columns="band", values="signed", aggfunc="sum").sort_index()
    vals = pv.values / 1e6
    vmax = float(np.nanpercentile(np.abs(vals), 98))
    fig, ax = plt.subplots(figsize=(W, 3.3))
    im = ax.imshow(vals, aspect="auto", cmap=DIV, norm=TwoSlopeNorm(vcenter=0, vmin=-vmax, vmax=vmax), interpolation="nearest")
    ax.grid(False)
    bands = list(pv.columns)
    step = 4
    ax.set_xticks(range(0, len(bands), step))
    ax.set_xticklabels([f"{b:,}" for b in bands[::step]], rotation=0)
    ax.set_yticks(range(len(pv.index)))
    ax.set_yticklabels([f"{dte} day{'s' if dte != 1 else ''}  ({pd.Timestamp(e).strftime('%d %b')})" for dte, e in pv.index])
    ax.set_xlabel("Strike price, in 25-point bands")
    ax.set_ylabel("Time left to expiry")
    xpos = (S0 - bands[0]) / 25.0 - 0.5
    ax.axvline(xpos, color=INK, lw=1.0)
    ax.text(xpos + 0.3, -0.62, f"index level {S0:,.0f}", fontsize=7.8, color=INK, va="bottom", ha="left")
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks(np.arange(-0.5, len(bands), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(pv.index), 1), minor=True)
    ax.grid(which="minor", color="#ffffff", linewidth=1.2)
    ax.tick_params(which="minor", length=0)
    cb = fig.colorbar(im, ax=ax, pad=0.02, aspect=16)
    cb.outline.set_visible(False)
    cb.set_label("Call gamma minus put gamma\n(millions of reading units)", fontsize=7.8)
    cb.ax.tick_params(labelsize=7.5)
    ax.set_title(f"One real reading ({pd.Timestamp(V['ex_read']).strftime('%d %B %Y')}): call gamma in blue, put gamma in red", pad=16, fontsize=9.2)
    save(fig, "fig05_chain_heatmap")


# ------------------------------------------------------------------------------------------------ 6 the reading through time
def fig06_reading():
    fr = pd.read_parquet(DATA / "frame.parquet")
    g = fr["g_same"] / 1e8
    cap = float(np.percentile(np.abs(g), 99.5))
    gc = g.clip(-cap, cap)
    sh = pd.read_csv(DATA / "putheavy_by_year.csv", index_col=0)["put_heavy_share"] * 100
    fig, axs = plt.subplots(2, 1, figsize=(W, 5.0), gridspec_kw=dict(hspace=0.42, height_ratios=[1.25, 1]))
    a = axs[0]
    a.vlines(gc.index[gc > 0], 0, gc[gc > 0], color="#3987e5", lw=0.45, rasterized=True)
    a.vlines(gc.index[gc < 0], 0, gc[gc < 0], color="#d9584f", lw=0.45, rasterized=True)
    a.axhline(0, color=AXIS, lw=0.8)
    a.set_ylabel("Reading (hundreds of millions)")
    a.set_title("The daily reading: above zero is call-heavy, below zero is put-heavy")
    a.xaxis.set_major_locator(mdates.YearLocator())
    a.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    a.set_ylim(-cap * 1.05, cap * 1.38)
    a.legend(handles=[Line2D([0], [0], color="#3987e5", lw=2, label=f"Call-heavy day ({int((g > 0).sum()):,} days)"),
                      Line2D([0], [0], color="#d9584f", lw=2, label=f"Put-heavy day ({int((g < 0).sum()):,} days)")], loc="upper left", ncol=2)
    b = axs[1]
    bars = b.bar(sh.index.astype(str), sh.values, color="#d9584f", width=0.62, edgecolor="#ffffff", linewidth=1.5)
    for r_, v in zip(bars, sh.values):
        b.text(r_.get_x() + r_.get_width() / 2, v + 1.2, f"{v:.0f}%", ha="center", va="bottom", fontsize=7.8, color=INK2)
    b.set_ylim(0, 75)
    b.set_ylabel("Share of trading days")
    b.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    b.set_title("Share of days each year on which the previous reading was put-heavy")
    b.grid(axis="x", visible=False)
    save(fig, "fig06_reading_history")


# ------------------------------------------------------------------------------------------------ 7 a window of positions
def fig07_window():
    fr = pd.read_parquet(DATA / "frame.parquet")
    a_, b_ = pd.Timestamp(V["wk_a"]), pd.Timestamp(V["wk_b"])
    i0, i1 = fr.index.get_loc(a_) - 27, fr.index.get_loc(b_) + 16
    w = fr.iloc[i0:i1 + 1]
    fig, ax = plt.subplots(figsize=(W, 3.2))
    for k in range(len(w) - 1):
        h = w["h"].iloc[k]
        if h != 0:
            ax.axvspan(w.index[k], w.index[k + 1], color=POS_TINT if h > 0 else NEG_TINT, lw=0)
    ax.plot(w.index, w["P"], color=INK, lw=1.3, marker="o", ms=2.4)
    ax.set_ylabel("QQQ closing price (US dollars)")
    ax.set_title("What the rule held, day by day, over three months")
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    y0, y1 = ax.get_ylim()
    ax.set_ylim(y0, y1 + (y1 - y0) * 0.26)
    ytop = y1 + (y1 - y0) * 0.07
    end_ = fr.index[fr.index.get_loc(b_) + 1]
    ax.plot([a_, end_], [ytop, ytop], color=INK2, lw=1.0, solid_capstyle="butt")
    for x_ in (a_, end_):
        ax.plot([x_, x_], [ytop - (y1 - y0) * 0.025, ytop + (y1 - y0) * 0.025], color=INK2, lw=1.0)
    ax.text(a_ + (end_ - a_) / 2, ytop + (y1 - y0) * 0.05, "the six decisions in the worked example", ha="center", va="bottom", fontsize=7.8, color=INK2)
    ax.legend(handles=[Patch(fc=POS_TINT, label="Long (owned QQQ)"), Patch(fc=NEG_TINT, label="Short (bet on a fall)"),
                       Patch(fc="#ffffff", ec=AXIS, label="Cash (no position)")], loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)
    save(fig, "fig07_positions_window")


# ------------------------------------------------------------------------------------------------ 8 state heat map
def fig08_states():
    st = pd.read_csv(DATA / "states.csv").set_index("cell")
    grid = np.array([[st.loc[k, "bp"] for k in ("cl", "cf", "cs")], [st.loc[k, "bp"] for k in ("pl", "pf", "ps")]])
    keys = [["cl", "cf", "cs"], ["pl", "pf", "ps"]]
    fig, ax = plt.subplots(figsize=(W, 2.95))
    ax.imshow(grid, cmap=DIV, norm=TwoSlopeNorm(vcenter=0, vmin=-32, vmax=32), aspect="auto")
    ax.grid(False)
    for i in range(2):
        for j in range(3):
            k = keys[i][j]
            dark = abs(grid[i, j]) > 22
            ax.text(j, i - 0.13, f"{grid[i, j]:+.1f} bp".replace("-", "−"), ha="center", va="center", fontsize=12, fontweight="bold", color="#ffffff" if dark else INK)
            ax.text(j, i + 0.24, f"{int(st.loc[k, 'n']):,} days,  t = {st.loc[k, 't']:+.2f}".replace("-", "−"), ha="center", va="center", fontsize=7.8,
                    color="#ffffff" if dark else INK2)
    ax.set_xticks(range(3))
    ax.set_xticklabels(["Rule was LONG", "Rule was in CASH", "Rule was SHORT"], fontsize=8.5, color=INK)
    ax.xaxis.tick_top()
    ax.set_title("Average QQQ return on the following day, in basis points (1 bp = 0.01%)", pad=24)
    ax.set_yticks(range(2))
    ax.set_yticklabels([f"Call-heavy book\n({V['n_callheavy']} days)", f"Put-heavy book\n({V['n_putheavy']} days)"], fontsize=8.3, color=INK)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks(np.arange(-0.5, 3, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, 2, 1), minor=True)
    ax.grid(which="minor", color="#ffffff", linewidth=2.5)
    ax.tick_params(which="minor", length=0)
    save(fig, "fig08_state_heatmap")


# ------------------------------------------------------------------------------------------------ 9 backtest
STRESS = [("2018-10-01", "2018-12-31", "late 2018"), ("2020-02-15", "2020-04-30", "COVID crash"), ("2022-01-01", "2022-12-31", "2022 bear market"),
          ("2023-03-01", "2023-03-31", "Mar 2023")]


def fig09_equity():
    s = pd.read_parquet(DATA / "series.parquet")
    start = pd.read_parquet(DATA / "frame.parquet").index[0]
    eq = (1 + s[["net_s", "hold_s", "trend_s"]]).cumprod()
    eq.loc[start] = 1.0
    eq = eq.sort_index()
    dd = eq / eq.cummax() - 1
    fig, axs = plt.subplots(2, 1, figsize=(W, 5.6), sharex=True, gridspec_kw=dict(hspace=0.16, height_ratios=[2.1, 1]))
    a = axs[0]
    for x0, x1, lab in STRESS:
        for ax in axs:
            ax.axvspan(pd.Timestamp(x0), pd.Timestamp(x1), color="#f0efec", lw=0, zorder=0)
    a.plot(eq.index, eq["hold_s"], color=BLUE, lw=1.4, label="Buy and hold QQQ")
    a.plot(eq.index, eq["trend_s"], color=AQUA, lw=1.4, label="Trend vote only (long or cash), after costs")
    a.plot(eq.index, eq["net_s"], color=ORANGE, lw=1.8, label="Gamma A+C, after costs")
    a.set_yscale("log")
    a.set_yticks([0.75, 1, 1.5, 2, 3, 4, 5])
    a.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:g}"))
    a.yaxis.set_minor_formatter(FuncFormatter(lambda v, _: ""))
    a.set_ylabel("Value of $1 invested (log scale)")
    a.set_title("Growth of $1, 3 January 2018 to 12 June 2026")
    a.legend(loc="lower right", bbox_to_anchor=(0.9, 0.02))
    end = eq.index[-1]
    xr = end + pd.Timedelta(days=45)
    a.set_xlim(eq.index[0] - pd.Timedelta(days=40), end + pd.Timedelta(days=330))
    for col, lab in (("hold_s", "QQQ"), ("trend_s", "Trend only"), ("net_s", "Gamma A+C")):
        a.text(xr, eq[col].iloc[-1], f"{lab}  ${eq[col].iloc[-1]:.2f}", fontsize=7.8, color=INK2, va="center", ha="left")
    ytxt = 5.3
    a.set_ylim(0.72, 5.9)
    for x0, x1, lab in STRESS:
        if lab == "Mar 2023":
            a.text(pd.Timestamp(x1) + pd.Timedelta(days=12), 4.55, lab, fontsize=7.2, color=INK2, ha="left", va="center")
        else:
            a.text(pd.Timestamp(x0) + (pd.Timestamp(x1) - pd.Timestamp(x0)) / 2, ytxt, lab, fontsize=7.2, color=INK2, ha="center", va="center")
    b = axs[1]
    b.plot(dd.index, dd["hold_s"] * 100, color=BLUE, lw=1.2, label="Buy and hold QQQ")
    b.plot(dd.index, dd["net_s"] * 100, color=ORANGE, lw=1.4, label="Gamma A+C, after costs")
    b.set_ylabel("Fall from the\nprevious high")
    b.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%".replace("-", "−")))
    b.set_title("Drawdown: how far each was below its own earlier peak")
    b.xaxis.set_major_locator(mdates.YearLocator())
    b.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    b.text(xr, dd["hold_s"].min() * 100, f"QQQ worst {dd['hold_s'].min() * 100:.1f}%".replace("-", "−"), fontsize=7.6, color=INK2, va="center")
    b.text(xr, dd["net_s"].min() * 100, f"A+C worst {dd['net_s'].min() * 100:.1f}%".replace("-", "−"), fontsize=7.6, color=INK2, va="center")
    save(fig, "fig09_equity")


# ------------------------------------------------------------------------------------------------ 10 calendar years
def fig10_years():
    y = pd.read_csv(DATA / "yearly.csv", index_col=0)
    x = np.arange(len(y))
    fig, ax = plt.subplots(figsize=(W, 3.1))
    ax.bar(x - 0.2, y["strategy"] * 100, width=0.38, color=ORANGE, edgecolor="#ffffff", linewidth=1.5, label="Gamma A+C, after costs")
    ax.bar(x + 0.2, y["qqq"] * 100, width=0.38, color=BLUE, edgecolor="#ffffff", linewidth=1.5, label="Buy and hold QQQ")
    ax.axhline(0, color=AXIS, lw=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{i}*" if i in (2018, 2026) else str(i) for i in y.index])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:+.0f}%".replace("-", "−")))
    ax.set_ylabel("Return in the calendar year")
    ax.set_title("Year by year: the rule against simply holding QQQ")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left", ncol=2)
    ax.set_ylim(-42, 72)
    save(fig, "fig10_yearly")


# ------------------------------------------------------------------------------------------------ 11 monthly heat map
def fig11_months():
    m = pd.read_csv(DATA / "monthly.csv", index_col=0) * 100
    y = pd.read_csv(DATA / "yearly.csv", index_col=0)["strategy"] * 100
    fig, ax = plt.subplots(figsize=(W, 3.7))
    ax.imshow(m.values, cmap=DIV, norm=TwoSlopeNorm(vcenter=0, vmin=-12, vmax=12), aspect="auto")
    ax.grid(False)
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            v = m.values[i, j]
            if np.isnan(v):
                continue
            lab = "0.0" if abs(v) < 0.05 else f"{v:+.1f}".replace("-", "−")
            ax.text(j, i, lab, ha="center", va="center", fontsize=7.2, color="#ffffff" if abs(v) > 8.5 else INK)
        ax.text(12.15, i, f"{y.iloc[i]:+.1f}%".replace("-", "−"), ha="center", va="center", fontsize=7.6, color=INK, fontweight="bold")
    ax.text(12.15, -0.95, "Year", ha="center", va="center", fontsize=8, color=INK2)
    ax.set_xticks(range(12))
    ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    ax.xaxis.tick_top()
    ax.set_yticks(range(m.shape[0]))
    ax.set_yticklabels(m.index.astype(str))
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks(np.arange(-0.5, 12, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, m.shape[0], 1), minor=True)
    ax.grid(which="minor", color="#ffffff", linewidth=1.6)
    ax.tick_params(which="minor", length=0)
    ax.set_xlim(-0.5, 12.75)
    save(fig, "fig11_monthly_heatmap")


# ------------------------------------------------------------------------------------------------ 12 Sharpe comparison
def fig12_sharpes():
    rows = [("Gamma A+C, before any trading cost", RAW["gross_sharpe"], ORANGE),
            ("Gamma A+C, after costs (0.02% per trade unit)", RAW["net_sharpe"], ORANGE),
            ("Gamma A+C, after double costs (0.04%)", RAW["net2_sharpe"], ORANGE),
            ("Gamma A+C, acting one day late, before costs", RAW["lag2_sharpe"], ORANGE),
            None,
            ("Trend vote only: long or cash, after costs", RAW["trend_sharpe"], AQUA),
            ("Buy and hold QQQ", RAW["hold_sharpe"], BLUE),
            ("Vote A only: long or short every day, after costs", RAW["a_only_sharpe"], NEUTRAL),
            ("Vote C only: long or short every day, after costs", RAW["c_only_sharpe"], NEUTRAL)]
    fig, ax = plt.subplots(figsize=(W, 3.5))
    ypos, labels = [], []
    y = 0.0
    for r_ in rows:
        if r_ is None:
            y += 0.55
            continue
        lab, v, col = r_
        ax.barh(y, v, height=0.62, color=col, edgecolor="#ffffff", linewidth=1.2)
        ax.text(v + 0.015, y, f"{v:.2f}", va="center", ha="left", fontsize=8.2, color=INK)
        ypos.append(y)
        labels.append(lab)
        y += 1.0
    ax.set_yticks(ypos)
    ax.set_yticklabels(labels, fontsize=8.2, color=INK)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.25)
    ax.set_xlabel("Sharpe ratio (average yearly return divided by yearly volatility; higher is better)")
    ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", length=0)
    ax.set_title("The same test, measured eight ways")
    save(fig, "fig12_sharpe_bars")


# ------------------------------------------------------------------------------------------------ 13 luck bar and confidence
def fig13_luck():
    best = np.load(DATA / "luck_best12.npy")
    sr, se = RAW["gross_sharpe"], RAW["dsr_se_ann"]
    bar12, bar50, bar670 = RAW["sr0_12_ann"], RAW["sr0_50_ann"], RAW["sr0_670_ann"]
    fig, axs = plt.subplots(1, 2, figsize=(W, 3.2), gridspec_kw=dict(wspace=0.26))
    a = axs[0]
    a.hist(best, bins=np.linspace(-0.2, 1.8, 61), color="#9ec5f4", edgecolor="#ffffff", linewidth=0.3)
    a.axvline(best.mean(), color=POS_DARK, lw=1.4)
    a.axvline(sr, color=ORANGE, lw=1.6)
    ymax = a.get_ylim()[1]
    a.set_ylim(0, ymax * 1.5)
    a.text(best.mean() - 0.04, ymax * 1.45, f"average best\nof 12: {best.mean():.2f}\n(formula: {bar12:.2f})", fontsize=7.6, color=INK2, va="top", ha="right")
    a.text(sr + 0.04, ymax * 1.45, f"what we\nmeasured:\n{sr:.2f}", fontsize=7.6, color=INK2, va="top", ha="left")
    a.set_xlabel("Best Sharpe ratio among 12 no-skill strategies")
    a.set_ylabel(f"Count, out of {V['sim_reps']} simulated sets")
    a.set_title("Step 1: how good does pure luck look?", fontsize=9)
    a.set_xlim(-0.2, 1.8)
    b = axs[1]
    x = np.linspace(sr - 3.6 * se, sr + 3.6 * se, 600)
    yv = np.exp(-0.5 * ((x - sr) / se) ** 2) / (se * math.sqrt(2 * math.pi))
    b.plot(x, yv, color=ORANGE, lw=1.6)
    b.fill_between(x, 0, yv, where=x >= bar12, color="#f6c1ab", lw=0)
    b.fill_between(x, 0, yv, where=x < bar12, color="#e4e3df", lw=0)
    b.axvline(bar12, color=POS_DARK, lw=1.4)
    top = yv.max()
    b.set_ylim(0, top * 1.42)
    b.text(bar12 - 0.04, top * 1.36, f"luck bar,\n12 tries: {bar12:.2f}", fontsize=7.6, color=INK2, va="top", ha="right")
    b.text(sr + 0.12, top * 0.42, f"{RAW['dsr_12'] * 100:.1f}%\nof the area", fontsize=8.6, color=INK, ha="center", va="center", fontweight="bold")
    b.annotate(f"{(1 - RAW['dsr_12']) * 100:.1f}%\nof the area", xy=(bar12 - 0.1, top * 0.07), xytext=(sr - 3.62 * se, top * 0.5), fontsize=8, color=INK2, ha="left", va="center",
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    for v_, lab in ((bar50, "50 tries"), (bar670, "670 tries")):
        b.plot([v_, v_], [0, top * 1.07], color=MUTED, lw=0.9)
        b.text(v_ + 0.02, top * 1.09, f"{lab}: {v_:.2f}", fontsize=7.2, color=INK2, va="bottom", ha="left", rotation=28)
    b.set_xlabel("Sharpe ratio (yearly)")
    b.set_yticks([])
    b.set_ylabel("How plausible each true value is")
    b.set_title("Step 2: is our Sharpe clear of the luck bar?", fontsize=9)
    b.grid(axis="y", visible=False)
    save(fig, "fig13_luck_confidence")


# ------------------------------------------------------------------------------------------------ 14 DSR against the number of tries
def fig14_dsr():
    c = pd.read_csv(DATA / "dsr_curve.csv")
    npass = int(V["dsr_maxN_pass"])
    fig, ax = plt.subplots(figsize=(W, 3.1))
    ax.axvspan(1, npass, color="#e3f1e3", lw=0, zorder=0)
    ax.plot(c["N"], c["dsr"], color=ORANGE, lw=1.8)
    ax.axhline(0.95, color=INK2, lw=1.0)
    ax.text(980, 0.958, "pass bar 0.95", ha="right", va="bottom", fontsize=7.8, color=INK2)
    pts = [(1, "1 try", (7, 5)), (12, "12 tries (the declared minimum)", (8, 10)), (50, "50 tries", (9, 5)), (670, "670 tries", (-9, -12))]
    for N, lab, off in pts:
        v = RAW[f"dsr_{N}"]
        ax.plot([N], [v], marker="o", ms=5.5, color=ORANGE, mec="#ffffff", mew=1.5, zorder=5)
        ax.annotate(f"{lab}: {v:.3f}", xy=(N, v), xytext=off, textcoords="offset points", fontsize=7.8, color=INK, ha="left" if off[0] > 0 else "right")
    ax.text(math.sqrt(npass) * 1.0, 0.44, f"passes only if\nat most {npass} versions\nwere tried", fontsize=7.8, color=INK2, ha="center", va="bottom")
    ax.set_xscale("log")
    ax.set_xlim(1, 1000)
    ax.set_ylim(0.4, 1.07)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.set_xlabel("Number of strategy versions tried, N (log scale)")
    ax.set_ylabel("Deflated Sharpe ratio")
    ax.set_title("The more versions were tried, the less the result can be trusted")
    save(fig, "fig14_dsr_curve")


ALL = [fig01_flow, fig02_coverage, fig03_basics, fig04_surface, fig05_chain, fig06_reading, fig07_window, fig08_states,
       fig09_equity, fig10_years, fig11_months, fig12_sharpes, fig13_luck, fig14_dsr]

if __name__ == "__main__":
    sys.exit("Run make_journal_figs.py. This module holds the drawing functions it uses.")
