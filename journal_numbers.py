#!/usr/bin/env python3
"""The six analyses the journal draft marked as not yet run.      python3 journal_numbers.py

Run fetch_inputs.py and paper_numbers.py first. Reads only; writes results/numbers_journal.json,
results/tables_journal.json and, in work/, the arrays the figures need.

  1. concentration        Table 6 without March 2020, and without the rule's five best days
  2. random filters       is the option vote better at choosing days than a random filter with the same day counts?
  3. Sharpe differences   Ledoit and Wolf (2008) studentized circular block bootstrap
  4. day-count check      663 long days in Figure 9 against 662 in Table 5
  5. return accounting    dividends, Treasury bill interest, excess-return Sharpe ratios, borrow fee on shorts
  6. holdout              the rule, unchanged, on the days fixed in HOLDOUT_PREREGISTRATION.md
  +  open-interest timing does the vendor's open interest for day d belong to d or to the session before?
"""
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import ndtr

import paths
from dsr import deflated_sharpe            # the author's validation function, as in Section 6

DATA = paths.WORK
CHAINS = paths.CHAINS
COST, AF = 2e-4, 252
R_F, Q_DIV = 0.04, 0.014
BORROW = 0.005                  # assumed borrow fee on short QQQ, per year
SEED = 20261112
MINUS = "−"
V, T = {}, {}                   # numbers and ready-made tables for the text


# ------------------------------------------------------------------------------------------------ helpers
def neg(s):
    return s.replace("-", MINUS)


def f(x, d=2):
    return neg(f"{x:.{d}f}")


def fs(x, d=2):
    return neg(f"{x:+.{d}f}")


def pct(x, d=1):
    return neg(f"{x * 100:.{d}f}%")


def spct(x, d=1):
    return neg(f"{x * 100:+.{d}f}%")


def n0(x):
    return f"{int(round(x)):,}"


def put(k, s):
    assert isinstance(s, str) and "nan" not in s.lower(), (k, s)
    V[k] = s


def sharpe(x):
    x = pd.Series(x).dropna()
    return float(x.mean() / x.std() * np.sqrt(AF))


def mdd(x):
    e = (1 + pd.Series(x).dropna()).cumprod()
    return float((e / e.cummax() - 1).min())


def growth(x):
    x = pd.Series(x).dropna()
    return float((1 + x).prod() ** (AF / len(x)) - 1)


def wealth(x):
    return float((1 + pd.Series(x).dropna()).prod())


def table(header, rows, align):
    """Pipe table. align: one of l, r, c per column, with a relative width: [("l", 30), ("r", 12), ...]."""
    def sep(a, w):
        body = "-" * (w - (2 if a == "c" else 1))
        return {"l": ":" + body, "r": body + ":", "c": ":" + body + ":"}[a]
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(sep(a, w) for a, w in align) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def pval(draws, actual):
    """One-sided: share of random draws at least as good as the actual value, counting the actual as one draw."""
    return (float((draws >= actual).sum()) + 1) / (len(draws) + 1)


def fp(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def pt(p):
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


def ab(s):
    """Drop the sign of a formatted number, for sentences that already say 'lost' or 'below'."""
    return s.replace(MINUS, "").replace("+", "")


# ------------------------------------------------------------------------------------------------ the sample
fr = pd.read_parquet(DATA / "frame.parquet")                      # the daily frame written by paper_numbers.py
ser = pd.read_parquet(DATA / "series.parquet")
base = json.loads((paths.RESULTS / "numbers.json").read_text())
h, r, fwd, C, g = fr["h"], fr["r"], fr["fwd"], fr["C"], fr["g"]


def net_log(pos, cost=COST):
    return (pos.shift(1) * r - cost * pos.diff().abs()).dropna()


def net_simple(pos, cost=COST):
    return (pos.shift(1) * np.expm1(r) - cost * pos.diff().abs()).dropna()


Cl = C.where(C > 0, 0.0)                                           # trend vote, long or cash
ac_log, ac_s = net_log(h), net_simple(h)
tl_log, tl_s = net_log(Cl), net_simple(Cl)
ts_log, ts_s = net_log(C), net_simple(C)
qq_log = r.reindex(ac_log.index)
qq_s = np.expm1(qq_log)
assert np.allclose(ac_s.values, ser["net_s"].values) and np.allclose(tl_s.values, ser["trend_s"].values) and np.allclose(qq_s.values, ser["hold_s"].values)
for key, val in (("net_sharpe", sharpe(ac_log)), ("trend_sharpe", sharpe(tl_log)), ("c_only_sharpe", sharpe(ts_log)), ("hold_sharpe", sharpe(qq_log)), ("gross_sharpe", sharpe(h * fwd))):
    assert f(val) == base[key], (key, f(val), base[key])
idx = ac_log.index
n = len(idx)
print(f"sample: {len(fr):,} decision days, {n:,} after-cost returns; baseline Sharpe ratios reproduced")

# ================================================================================================ 1. CONCENTRATION
print("[1] concentration")
march = (idx.year == 2020) & (idx.month == 3)
top5 = ac_s.sort_values(ascending=False).index[:5]
masks = {"full": np.ones(n, bool), "exmar": ~march, "extop": ~idx.isin(top5)}
labels = {"full": "Full sample", "exmar": "Without March 2020", "extop": "Without the rule's five best days"}
cols = {"ac": (ac_log, ac_s), "tl": (tl_log, tl_s), "qq": (qq_log, qq_s)}
rows = []
for mk, m in masks.items():
    for ck, (lg, sm) in cols.items():
        put(f"conc_{mk}_{ck}_sh", f(sharpe(lg[m])))
        put(f"conc_{mk}_{ck}_gr", pct(growth(sm[m])))
        put(f"conc_{mk}_{ck}_w", f(wealth(sm[m])))
        put(f"conc_{mk}_{ck}_dd", pct(mdd(sm[m])))
    put(f"conc_{mk}_n", n0(m.sum()))
    rows.append([labels[mk], n0(m.sum())] + [x for ck in ("ac", "tl", "qq") for x in (V[f"conc_{mk}_{ck}_sh"], "\\$" + V[f"conc_{mk}_{ck}_w"])])
T["conc"] = table(["Sample", "Days", "Gamma A+C: Sharpe", "Gamma A+C: value of \\$1", "Trend, long or cash: Sharpe", "Trend, long or cash: value of \\$1", "QQQ: Sharpe", "QQQ: value of \\$1"],
                  rows, [("l", 26), ("r", 8), ("r", 11), ("r", 11), ("r", 11), ("r", 11), ("r", 11), ("r", 11)])
tot = float(ac_log.sum())
put("conc_march_days", n0(march.sum()))
put("conc_march_share", pct(float(ac_log[march].sum()) / tot, 0))
put("conc_march_ret", spct(float(np.prod(1 + ac_s[march]) - 1)))
put("conc_march_qqq", spct(float(np.prod(1 + qq_s[march]) - 1)))
put("conc_top5_share", pct(float(ac_log[idx.isin(top5)].sum()) / tot, 0))
put("conc_top5_list", "; ".join(f"{d.date()} ({spct(ac_s[d])})" for d in sorted(top5)))
put("conc_top5_in_march", n0(sum(1 for d in top5 if d.year == 2020 and d.month == 3)))
put("conc_top5_short", n0(int((h.shift(1).reindex(top5) < 0).sum())))
put("conc_sh_drop_mar", f(sharpe(ac_log) - sharpe(ac_log[masks["exmar"]])))
put("conc_sh_drop_top", f(sharpe(ac_log) - sharpe(ac_log[masks["extop"]])))
put("conc_w_share_mar", pct(1 - math.log(wealth(ac_s[masks["exmar"]])) / math.log(wealth(ac_s)), 0))
put("conc_w_share_top", pct(1 - math.log(wealth(ac_s[masks["extop"]])) / math.log(wealth(ac_s)), 0))
for mk in ("exmar", "extop"):
    put(f"conc_{mk}_rank", "above" if sharpe(ac_log[masks[mk]]) > sharpe(qq_log[masks[mk]]) else "below")

# ================================================================================================ 4. DAY-COUNT CHECK
print("[4] day count")
call_long = (g > 0) & (h > 0)
case1 = (g > 0) & (r > 0) & (fr["M"] > 0)
extra = fr.index[call_long & ~case1]
assert int(call_long.sum()) == 663 and int(case1.sum()) == 662 and len(extra) == 1 and str(extra[0].date()) == "2021-07-13" and h[extra[0]] == 0.5
put("count_fig", n0(call_long.sum()))
put("count_tab", n0(case1.sum()))
put("count_extra_day", str(extra[0].date()))

# ================================================================================================ 2. RANDOM FILTERS
print("[2] random filters")
rng = np.random.default_rng(SEED)
DRAWS = 10000
hv, rv, fv = h.values, r.values, fwd.values
up = np.where((C.values > 0) & (rv != 0))[0]
dn = np.where((C.values < 0) & (rv != 0))[0]
special = np.where(rv == 0)[0]
k_up, k_dn = int((hv[up] == 1).sum()), int((hv[dn] == -1).sum())
assert (len(up), k_up, len(dn), k_dn, len(special)) == (1399, 750, 718, 372, 1)
f_up, f_dn = (hv[up] == 1).astype(float), (hv[dn] == -1).astype(float)


def assemble(sel_up, sel_dn):
    """Positions for a batch of filters. sel_*: (batch, group size) arrays of 0/1."""
    pos = np.zeros((sel_up.shape[0], len(hv)))
    pos[:, up] = sel_up
    pos[:, dn] = -sel_dn
    pos[:, special] = hv[special]
    return pos


def stats(pos):
    gross = pos * fv
    sg = gross.mean(1) / gross.std(1, ddof=1) * math.sqrt(AF)
    d = np.abs(np.diff(pos, axis=1))
    net = pos[:, :-1] * rv[1:] - COST * d
    sn = net.mean(1) / net.std(1, ddof=1) * math.sqrt(AF)
    changes = (d > 0).sum(1)
    lng = (np.clip(pos, 0, 1) * fv).sum(1) / np.clip(pos, 0, 1).sum(1) * 1e4          # mean next-day return on long days, bp
    sht = (np.clip(-pos, 0, 1) * -fv).sum(1) / np.clip(-pos, 0, 1).sum(1) * 1e4       # mean gain on short days, bp
    return sg, sn, changes, lng, sht


actual = [float(x[0]) for x in stats(hv[None, :])]
assert f(actual[0]) == base["gross_sharpe"] and f(actual[1]) == base["net_sharpe"] and int(actual[2]) == 1108


def iid_batch(b):
    su = np.zeros((b, len(up)))
    sd = np.zeros((b, len(dn)))
    for i in range(b):
        su[i, rng.choice(len(up), k_up, replace=False)] = 1
        sd[i, rng.choice(len(dn), k_dn, replace=False)] = 1
    return su, sd


def block_perm(seq, L, b):
    blocks = [seq[i:i + L] for i in range(0, len(seq), L)]
    out = np.empty((b, len(seq)))
    for i in range(b):
        out[i] = np.concatenate([blocks[j] for j in rng.permutation(len(blocks))])
    return out


def run(kind, L=None):
    res = [[] for _ in range(5)]
    for _ in range(DRAWS // 1000):
        su, sd = iid_batch(1000) if kind == "iid" else (block_perm(f_up, L, 1000), block_perm(f_dn, L, 1000))
        for a, x in zip(res, stats(assemble(su, sd))):
            a.append(x)
    return [np.concatenate(a) for a in res]


iid = run("iid")
# block length: the shortest whose random filters change position about as often as the rule (within 2%); set on turnover alone
chosen = None
trial = {}
for L in (2, 3, 5, 8, 10, 15, 20, 30, 40, 60):
    su, sd = block_perm(f_up, L, 400), block_perm(f_dn, L, 400)
    trial[L] = float(stats(assemble(su, sd))[2].mean())
    if chosen is None and abs(trial[L] / actual[2] - 1) <= 0.02:
        chosen = L
assert chosen is not None, trial
blk = run("block", chosen)
np.savez_compressed(DATA / "random_filters.npz", iid_gross=iid[0], iid_net=iid[1], iid_long=iid[3], iid_short=iid[4],
                    blk_gross=blk[0], blk_net=blk[1], blk_long=blk[3], blk_short=blk[4], actual=np.array(actual))
put("rf_draws", n0(DRAWS))
put("rf_block", n0(chosen))
put("rf_changes_actual", n0(actual[2]))
put("rf_changes_iid", n0(iid[2].mean()))
put("rf_changes_blk", n0(blk[2].mean()))
put("rf_up_n", n0(len(up)))
put("rf_up_k", n0(k_up))
put("rf_dn_n", n0(len(dn)))
put("rf_dn_k", n0(k_dn))
put("rf_up_all_bp", fs(float(fv[up].mean() * 1e4), 1))
put("rf_dn_all_bp", fs(float(fv[dn].mean() * 1e4), 1))
put("rf_dn_all_abs", f(abs(float(fv[dn].mean() * 1e4)), 1))
assert fv[dn].mean() > 0, "the text says QQQ rose on an average trend-down day"
names = [("gross", "Sharpe ratio before costs", 0, 2), ("net", "Sharpe ratio after costs", 1, 2), ("long", "Long side: mean next-day return, basis points", 3, 1),
         ("short", "Short side: mean next-day gain, basis points", 4, 1)]
for key, lab, j, d in names:
    put(f"rf_{key}_actual", f(actual[j], d))
    for tag, res in (("iid", iid), ("blk", blk)):
        x = res[j]
        p = pval(x, actual[j])
        put(f"rf_{key}_{tag}_mean", f(float(x.mean()), d))
        put(f"rf_{key}_{tag}_p05", f(float(np.percentile(x, 5)), d))
        put(f"rf_{key}_{tag}_p95", f(float(np.percentile(x, 95)), d))
        put(f"rf_{key}_{tag}_pct", pct(float((x < actual[j]).mean()), 1))
        put(f"rf_{key}_{tag}_p", fp(p))
        put(f"rf_{key}_{tag}_pt", pt(p))
        if key in ("gross", "net"):
            assert 2 * p < 0.01, "the text says the doubled p-values stay below 0.01"
rows = []
for tag, title in (("iid", "**Independent draws**"), ("blk", f"**Block draws, blocks of {chosen} days**")):
    rows.append([title, "", "", "", ""])
    for key, lab, j, d in names:
        rows.append([lab, V[f"rf_{key}_actual"], V[f"rf_{key}_{tag}_mean"], f"{V[f'rf_{key}_{tag}_p05']} to {V[f'rf_{key}_{tag}_p95']}", V[f"rf_{key}_{tag}_p"]])
put("rf_short_iid_mean_abs", ab(V["rf_short_iid_mean"]))
assert V["rf_short_iid_mean"].startswith(MINUS), "the text says a random choice of trend-down days loses"
T["rf"] = table(["Statistic", "Rule", "Random filters: mean", "Random filters: 5% to 95%", "p"], rows, [("l", 40), ("r", 11), ("r", 17), ("r", 20), ("r", 12)])
print(f"    position changes: rule {actual[2]:.0f}, independent {iid[2].mean():.0f}, blocks of {chosen}: {blk[2].mean():.0f}")
# the same test with March 2020 left out of the scoring: is the day selection one episode?
ret_day = list(fr.index[1:]) + [fr.index[-1] + pd.Timedelta(days=3)]
keep_g = np.array([not (d.year == 2020 and d.month == 3) for d in ret_day])        # decision days whose return falls outside March 2020
keep_n = ~march                                                                      # return days outside March 2020


def stats_ex(pos):
    gross = (pos * fv)[:, keep_g]
    sg = gross.mean(1) / gross.std(1, ddof=1) * math.sqrt(AF)
    net = (pos[:, :-1] * rv[1:] - COST * np.abs(np.diff(pos, axis=1)))[:, keep_n]
    sn = net.mean(1) / net.std(1, ddof=1) * math.sqrt(AF)
    w = np.clip(-pos, 0, 1)[:, keep_g]
    sht = (w * -fv[keep_g]).sum(1) / w.sum(1) * 1e4
    return sg, sn, sht


act_ex = [float(x[0]) for x in stats_ex(hv[None, :])]
ex = [[], [], []]
for _ in range(DRAWS // 1000):
    for a, x in zip(ex, stats_ex(assemble(*iid_batch(1000)))):
        a.append(x)
ex = [np.concatenate(a) for a in ex]
for key, j, d in (("gross", 0, 2), ("net", 1, 2), ("short", 2, 1)):
    put(f"rfx_{key}_actual", f(act_ex[j], d))
    put(f"rfx_{key}_mean", f(float(ex[j].mean()), d))
    put(f"rfx_{key}_p", fp(pval(ex[j], act_ex[j])))
    put(f"rfx_{key}_pt", pt(pval(ex[j], act_ex[j])))
print(f"    without March 2020: Sharpe before costs {act_ex[0]:.2f} (p {V['rfx_gross_p']}), after costs {act_ex[1]:.2f} (p {V['rfx_net_p']}), short side {act_ex[2]:.1f} bp (p {V['rfx_short_p']})")

# ------------------------------------------------------------------------------------------------ 2b. is it the reading?
# The option vote uses two things, the reading and the day's move. Shuffle the readings across days and keep everything else.
print("[2b] shuffled readings")
sgn_g, sgn_r, Cv = np.sign(g.values), np.sign(rv), C.values


def rule_pos(sg_):
    return np.where(sg_ == 0, 0.0, (sg_ * sgn_r + Cv) / 2)


assert (rule_pos(sgn_g) == hv).all()


def shuffled(kind, L=20):
    out = np.empty((DRAWS, 2))
    for i in range(DRAWS):
        if kind == "iid":
            sg_ = rng.permutation(sgn_g)
        else:
            bl = [sgn_g[j:j + L] for j in range(0, len(sgn_g), L)]
            sg_ = np.concatenate([bl[j] for j in rng.permutation(len(bl))])
        st = stats(rule_pos(sg_)[None, :])
        out[i] = st[0][0], st[1][0]
    return out


sh_iid, sh_blk = shuffled("iid"), shuffled("block")
np.savez_compressed(DATA / "shuffled_readings.npz", iid=sh_iid, blk=sh_blk)
put("sh_stay", pct(float((sgn_g[1:] == sgn_g[:-1]).mean()), 1))
put("sh_block", "20")
for tag, arr in (("iid", sh_iid), ("blk", sh_blk)):
    for j, key in ((0, "gross"), (1, "net")):
        put(f"sh_{key}_{tag}_mean", f(float(arr[:, j].mean())))
        put(f"sh_{key}_{tag}_p95", f(float(np.percentile(arr[:, j], 95))))
        put(f"sh_{key}_{tag}_p", fp(pval(arr[:, j], actual[j])))
        put(f"sh_{key}_{tag}_pt", pt(pval(arr[:, j], actual[j])))
fade = pd.Series(rule_pos(-np.ones_like(sgn_g)), index=fr.index)          # as if every reading were put-heavy: act only after a move against the trend
follow = pd.Series(rule_pos(np.ones_like(sgn_g)), index=fr.index)        # as if every reading were call-heavy: act only after a move with the trend
fade_log, follow_log = net_log(fade), net_log(follow)
fade_s, follow_s = net_simple(fade), net_simple(follow)
for key, pos_, lg_, sm_ in (("fade", fade, fade_log, fade_s), ("follow", follow, follow_log, follow_s)):
    put(f"{key}_gross", f(sharpe(pos_ * fwd)))
    put(f"{key}_net", f(sharpe(lg_)))
    put(f"{key}_gr", pct(growth(sm_)))
    put(f"{key}_dd", pct(mdd(sm_)))
    put(f"{key}_in", pct(float((pos_ != 0).mean())))
put("fade_corr", f(float(np.corrcoef(fade_log.values, ac_log.values)[0, 1])))
put("fade_dd_abs", ab(V["fade_dd"]))
same_days = (np.sign(hv) == np.sign(fade.values)) & (hv != 0)
put("fade_overlap", pct(float(same_days.sum() / (hv != 0).sum()), 0))
dn_cash = (Cv < 0) & (hv == 0) & (rv != 0)
put("dn_cash_n", n0(int(dn_cash.sum())))
put("dn_cash_bp", fs(float(fv[dn_cash].mean() * 1e4), 1))
print(f"    shuffled readings: mean Sharpe after costs {V['sh_net_iid_mean']} (p {V['sh_net_iid_p']}; blocks {V['sh_net_blk_p']}); always fade {V['fade_net']}, always follow {V['follow_net']}")

# ================================================================================================ 3. SHARPE DIFFERENCES
print("[3] Ledoit-Wolf")


def sr_diff(a, b):
    m1, m2, g1, g2 = a.mean(), b.mean(), (a ** 2).mean(), (b ** 2).mean()
    s1, s2 = math.sqrt(g1 - m1 ** 2), math.sqrt(g2 - m2 ** 2)
    grad = np.array([g1 / s1 ** 3, -g2 / s2 ** 3, -0.5 * m1 / s1 ** 3, 0.5 * m2 / s2 ** 3])
    return m1 / s1 - m2 / s2, grad, np.column_stack([a - m1, b - m2, a ** 2 - g1, b ** 2 - g2])


def qs(x):
    x = np.asarray(x, float)
    out = np.ones_like(x)
    nz = x != 0
    z = 6 * math.pi * x[nz] / 5
    out[nz] = 25 / (12 * math.pi ** 2 * x[nz] ** 2) * (np.sin(z) / z - np.cos(z))
    return out


def hac_prewhitened_qs(Vm):
    """Andrews and Monahan (1992): VAR(1) prewhitening, quadratic spectral kernel, Andrews (1991) automatic bandwidth."""
    Tn = len(Vm)
    Y, X = Vm[1:], Vm[:-1]
    A = np.linalg.lstsq(X, Y, rcond=None)[0].T
    E = Y - X @ A.T
    num = den = 0.0
    for i in range(E.shape[1]):
        e = E[:, i]
        rho = float(e[1:] @ e[:-1] / (e[:-1] @ e[:-1]))
        s2 = float(((e[1:] - rho * e[:-1]) ** 2).mean())
        num += 4 * rho ** 2 * s2 ** 2 / (1 - rho) ** 8
        den += s2 ** 2 / (1 - rho) ** 4
    bw = 1.3221 * (num / den * len(E)) ** 0.2
    n_e = len(E)
    psi = E.T @ E / n_e
    lags = np.arange(1, n_e)
    w = qs(lags / bw)
    for j in lags[np.abs(w) > 1e-8][:400]:
        Gj = E[j:].T @ E[:-j] / n_e
        psi += w[j - 1] * (Gj + Gj.T)
    psi *= n_e / (n_e - E.shape[1])
    D = np.linalg.inv(np.eye(A.shape[0]) - A)
    return D @ psi @ D.T


def lw_test(a, b, block, M, gen):
    a, b = np.asarray(a, float), np.asarray(b, float)
    Tn = len(a)
    d0, grad, Vm = sr_diff(a, b)
    se0 = math.sqrt(float(grad @ hac_prewhitened_qs(Vm) @ grad) / Tn)
    stat0 = abs(d0) / se0
    nb = Tn // block
    hits = 0
    for start in range(0, M, 500):
        m = min(500, M - start)
        s0 = gen.integers(0, Tn, size=(m, nb))
        ix = (s0[:, :, None] + np.arange(block)[None, None, :]) % Tn          # circular blocks
        A_, B_ = a[ix], b[ix]                                                 # (m, nb, block)
        m1, m2 = A_.mean((1, 2)), B_.mean((1, 2))
        g1, g2 = (A_ ** 2).mean((1, 2)), (B_ ** 2).mean((1, 2))
        s1, s2 = np.sqrt(g1 - m1 ** 2), np.sqrt(g2 - m2 ** 2)
        d = m1 / s1 - m2 / s2
        gr = np.stack([g1 / s1 ** 3, -g2 / s2 ** 3, -0.5 * m1 / s1 ** 3, 0.5 * m2 / s2 ** 3], axis=1)
        Y = np.stack([A_ - m1[:, None, None], B_ - m2[:, None, None], A_ ** 2 - g1[:, None, None], B_ ** 2 - g2[:, None, None]], axis=3)
        zeta = Y.sum(2) / math.sqrt(block)                                    # (m, nb, 4)
        psi = np.einsum("mji,mjk->mik", zeta, zeta) / nb
        se = np.sqrt(np.einsum("mi,mik,mk->m", gr, psi, gr) / (nb * block))
        hits += int((np.abs(d - d0) / se >= stat0).sum())
    return d0 * math.sqrt(AF), se0 * math.sqrt(AF), (hits + 1) / (M + 1)


def memmel_z(a, b):
    Tn = len(a)
    s1, s2, rho = a.mean() / a.std(ddof=1), b.mean() / b.std(ddof=1), np.corrcoef(a, b)[0, 1]
    var = (2 * (1 - rho) + 0.5 * (s1 ** 2 + s2 ** 2 - 2 * s1 * s2 * rho ** 2)) / Tn
    return (s1 - s2) / math.sqrt(var)


gen = np.random.default_rng(SEED + 1)
# size check under the null: two correlated series with the same true Sharpe ratio, fat tails, same length as the sample
rej = 0
SIMS = 300
for _ in range(SIMS):
    z = gen.standard_t(5, size=(n, 2)) * 0.01
    a2 = z[:, 0] + 0.0005                                             # same mean and same variance: equal true Sharpe ratios
    b2 = 0.4 * z[:, 0] + math.sqrt(0.84) * z[:, 1] + 0.0005
    rej += lw_test(a2, b2, 5, 499, gen)[2] < 0.05
put("lw_size", pct(rej / SIMS, 1))
put("lw_size_sims", n0(SIMS))
print(f"    size check: rejects a true null at the 5% level in {rej / SIMS:.1%} of {SIMS} simulations")
pairs = [("tl", "Trend vote, long or cash", tl_log), ("ts", "Trend vote, long or short", ts_log), ("qq", "Buy and hold QQQ", qq_log),
         ("fade", "Trend position after a move against the trend, no option data", fade_log)]
MB = 4999
rows = []
for key, lab, other in pairs:
    res = {b: lw_test(ac_log.values, other.values, b, MB, gen) for b in (5, 10, 20)}
    d_ann, se_ann = res[5][0], res[5][1]
    put(f"lw_{key}_diff", fs(d_ann))
    put(f"lw_{key}_diff_abs", f(abs(d_ann)))
    put(f"lw_{key}_se", f(se_ann))
    put(f"lw_{key}_t", fs(d_ann / se_ann))
    put(f"lw_{key}_z", fs(memmel_z(ac_log.values, other.values)))
    put(f"lw_{key}_rho", f(float(np.corrcoef(ac_log.values, other.values)[0, 1])))
    for b in (5, 10, 20):
        put(f"lw_{key}_p{b}", fp(res[b][2]))
    put(f"lw_{key}_pmin", fp(min(res[b][2] for b in (5, 10, 20))))
    put(f"lw_{key}_pmax", fp(max(res[b][2] for b in (5, 10, 20))))
    rows.append([lab, f(sharpe(other)), V[f"lw_{key}_diff"], V[f"lw_{key}_se"], V[f"lw_{key}_p5"], V[f"lw_{key}_p10"], V[f"lw_{key}_p20"]])
    print(f"    A+C minus {lab}: {d_ann:+.2f} (se {se_ann:.2f}); p = {res[5][2]:.3f}, {res[10][2]:.3f}, {res[20][2]:.3f}; Memmel z {memmel_z(ac_log.values, other.values):+.2f}")
T["lw"] = table(["Benchmark", "Its Sharpe ratio", "Gamma A+C minus benchmark", "Standard error", "p, blocks of 5", "p, blocks of 10", "p, blocks of 20"],
                rows, [("l", 26), ("r", 11), ("r", 14), ("r", 11), ("r", 11), ("r", 11), ("r", 11)])
put("lw_boot", n0(MB))
T["nofilter"] = table(["Rule", "Uses the option reading", "Sharpe before costs", "Sharpe after costs", "p against Gamma A+C"],
                      [["Gamma A+C", "yes", V["rf_gross_actual"], V["rf_net_actual"], ""],
                       [f"Readings shuffled across days, mean of {V['rf_draws']}", "shuffled", V["sh_gross_iid_mean"], V["sh_net_iid_mean"], V["sh_net_iid_p"]],
                       ["Trend position only after a move against the trend", "no", V["fade_gross"], V["fade_net"], V["lw_fade_p5"]],
                       ["Trend position only after a move with the trend", "no", V["follow_gross"], V["follow_net"], ""]],
                      [("l", 40), ("l", 14), ("r", 12), ("r", 12), ("r", 12)])

# ================================================================================================ 5. RETURN ACCOUNTING
print("[5] return accounting")
q = pd.read_parquet(paths.QQQ)
if paths.OCTOBER is not None:                            # the closes must not have been revised since the sample was first built
    old = pd.read_parquet(paths.OCTOBER / "gamma_qqq_ohlc.parquet")
    common = old.index.intersection(q.index)
    assert len(common) == len(old) and np.allclose(q.loc[common, "Close"], old.loc[common, "Close"], rtol=1e-9), "QQQ closes changed since the sample was built"
tr = (q["Adj Close"] / q["Adj Close"].shift(1) - 1).reindex(idx)             # total return, dividends reinvested
pr = (q["Close"] / q["Close"].shift(1) - 1).reindex(idx)
assert np.allclose(pr.values, qq_s.values, atol=1e-12)
tb = pd.read_csv(paths.TBILL, index_col=0, parse_dates=True)["DTB3"].dropna() / 100
cal = pd.Series(q.index, index=q.index)
gap = (cal - cal.shift(1)).dt.days.reindex(idx)                              # calendar days since the previous session
rate_prev = tb.reindex(q.index.union(tb.index)).ffill().shift(1).reindex(idx)   # the bill rate known the session before
rf = rate_prev * gap / 360                                                   # bank-discount convention, simple
fee = BORROW * gap / 360
put("acct_div_yield", pct(float((1 + tr).prod() ** (AF / n) - (1 + pr).prod() ** (AF / n)), 2))
put("acct_rf_mean", pct(float((1 + rf).prod() ** (AF / n) - 1), 2))
put("acct_rf_min", pct(float(rate_prev.min()), 2))
put("acct_rf_max", pct(float(rate_prev.max()), 2))
put("acct_borrow", pct(BORROW, 1))
put("acct_tb_last", str(tb.index[-1].date()))


def full(pos, cost=COST, rebate=False, borrow=BORROW):
    """Simple daily return of one unit of capital: QQQ total return when long, the bill return on idle capital, and on
    short days the bill return on own capital less QQQ's total return (so dividends are paid) less the borrow fee."""
    p = pos.shift(1).reindex(idx)
    lng, sht = p.clip(lower=0), (-p).clip(lower=0)
    R = lng * tr + (1 - lng) * rf - sht * tr - sht * (borrow * gap / 360) + (sht * rf if rebate else 0.0) - cost * pos.diff().abs().reindex(idx)
    return R


def ex_sharpe(R):
    return sharpe(np.log1p(R) - np.log1p(rf))


one = pd.Series(1.0, index=fr.index)
rules = {"ac": ("Gamma A+C", h), "tl": ("Trend vote, long or cash", Cl), "ts": ("Trend vote, long or short", C), "qq": ("Buy and hold QQQ", one)}
base_s = {"ac": ac_s, "tl": tl_s, "ts": ts_s, "qq": qq_s}
base_l = {"ac": ac_log, "tl": tl_log, "ts": ts_log, "qq": qq_log}
fullR = {k: full(p, cost=0.0 if k == "qq" else COST) for k, (_, p) in rules.items()}
rows = []
for k, (lab, _) in rules.items():
    put(f"acct_{k}_sh0", f(sharpe(base_l[k])))
    put(f"acct_{k}_sh1", f(ex_sharpe(fullR[k])))
    put(f"acct_{k}_gr0", pct(growth(base_s[k])))
    put(f"acct_{k}_gr1", pct(growth(fullR[k])))
    put(f"acct_{k}_dd0", pct(mdd(base_s[k])))
    put(f"acct_{k}_dd1", pct(mdd(fullR[k])))
    put(f"acct_{k}_w1", f(wealth(fullR[k])))
    put(f"acct_{k}_vol1", pct(float(fullR[k].std() * math.sqrt(AF))))
    rows.append([lab, V[f"acct_{k}_sh0"], V[f"acct_{k}_sh1"], V[f"acct_{k}_gr0"], V[f"acct_{k}_gr1"], V[f"acct_{k}_dd0"], V[f"acct_{k}_dd1"]])
T["acct"] = table(["Rule", "Sharpe: baseline", "Sharpe: full, excess", "Growth: baseline", "Growth: full", "Worst fall: baseline", "Worst fall: full"],
                  rows, [("l", 26), ("r", 11), ("r", 12), ("r", 11), ("r", 11), ("r", 12), ("r", 12)])
put("acct_ac_sh_rebate", f(ex_sharpe(full(h, rebate=True))))
put("acct_ac_sh_fee1", f(ex_sharpe(full(h, borrow=0.01))))
put("acct_ac_gross", f(ex_sharpe(full(h, cost=0.0))))
put("acct_ac_x2", f(ex_sharpe(full(h, cost=2 * COST))))
# one extra day of delay, before costs: the position decided two sessions earlier
p2 = h.shift(2).reindex(idx)
R_late = p2.clip(lower=0) * tr + (1 - p2.clip(lower=0)) * rf - (-p2).clip(lower=0) * (tr + fee)
put("acct_ac_late", f(ex_sharpe(R_late.dropna())))
half = idx[n // 2]
put("acct_ac_h1", f(sharpe((np.log1p(fullR["ac"]) - np.log1p(rf))[idx < half])))
put("acct_ac_h2", f(sharpe((np.log1p(fullR["ac"]) - np.log1p(rf))[idx >= half])))
# appendix tables: Table 6, 7 and 9 again under full accounting
T["acct6"] = table(["", "Gamma A+C, after costs", "Trend vote, long or cash, after costs", "Buy and hold QQQ"],
                   [["Value of \\$1 at the end"] + ["\\$" + V[f"acct_{k}_w1"] for k in ("ac", "tl", "qq")],
                    ["Growth rate a year"] + [V[f"acct_{k}_gr1"] for k in ("ac", "tl", "qq")],
                    ["Volatility a year"] + [V[f"acct_{k}_vol1"] for k in ("ac", "tl", "qq")],
                    ["Sharpe ratio, excess of bills"] + [V[f"acct_{k}_sh1"] for k in ("ac", "tl", "qq")],
                    ["Worst fall"] + [V[f"acct_{k}_dd1"] for k in ("ac", "tl", "qq")]],
                   [("l", 34), ("r", 22), ("r", 22), ("r", 22)])
yr = pd.DataFrame({"ac": fullR["ac"].groupby(idx.year).apply(lambda x: float((1 + x).prod() - 1)), "qq": fullR["qq"].groupby(idx.year).apply(lambda x: float((1 + x).prod() - 1)),
                   "sh": (np.log1p(fullR["ac"]) - np.log1p(rf)).groupby(idx.year).apply(sharpe)})
yr0 = pd.DataFrame({"ac": ac_s.groupby(idx.year).apply(lambda x: float((1 + x).prod() - 1)), "qq": qq_s.groupby(idx.year).apply(lambda x: float((1 + x).prod() - 1))})
years = [str(y) for y in yr.index]
T["acct7"] = table([""] + years, [["Gamma A+C, after costs"] + [spct(v) for v in yr["ac"]], ["Buy and hold QQQ"] + [spct(v) for v in yr["qq"]],
                                  ["Gamma A+C Sharpe ratio, excess of bills"] + [f(v) for v in yr["sh"]]], [("l", 19)] + [("r", 9)] * len(years))
STRESS = [("Late 2018 sell-off", "2018-10-01", "2018-12-31"), ("COVID crash and rebound", "2020-02-15", "2020-04-30"), ("2022 bear market", "2022-01-01", "2022-12-31"),
          ("March 2023 bank failures", "2023-03-01", "2023-03-31")]
srow, flips = [], []
for lab, a, b in STRESS:
    a1, q1 = float((1 + fullR["ac"].loc[a:b]).prod() - 1), float((1 + fullR["qq"].loc[a:b]).prod() - 1)
    a0, q0 = float((1 + ac_s.loc[a:b]).prod() - 1), float((1 + qq_s.loc[a:b]).prod() - 1)
    srow.append([lab, f"{a} to {b}", n0(len(ac_s.loc[a:b])), spct(a1), spct(q1)])
    if np.sign(a1) != np.sign(a0) or np.sign(a1 - q1) != np.sign(a0 - q0):
        flips.append(lab)
T["acct9"] = table(["Period", "Dates", "Days", "Gamma A+C, after costs", "Buy and hold QQQ"], srow, [("l", 28), ("l", 30), ("r", 8), ("r", 18), ("r", 16)])
for y in yr.index:
    if np.sign(yr.loc[y, "ac"]) != np.sign(yr0.loc[y, "ac"]):
        flips.append(f"the sign of the rule's return in {y}")
    if np.sign(yr.loc[y, "ac"] - yr.loc[y, "qq"]) != np.sign(yr0.loc[y, "ac"] - yr0.loc[y, "qq"]):
        flips.append(f"which of the rule and QQQ did better in {y}")
order0 = sorted(rules, key=lambda k: -sharpe(base_l[k]))
order1 = sorted(rules, key=lambda k: -ex_sharpe(fullR[k]))
if order0 != order1:
    flips.append("the ranking of the four rules by Sharpe ratio")
for a_, b_ in (("ac", "qq"), ("ac", "tl"), ("ac", "ts")):
    for nm, fn0, fn1 in (("growth", lambda k: growth(base_s[k]), lambda k: growth(fullR[k])), ("worst fall", lambda k: mdd(base_s[k]), lambda k: mdd(fullR[k]))):
        if np.sign(fn0(a_) - fn0(b_)) != np.sign(fn1(a_) - fn1(b_)):
            flips.append(f"{nm} of Gamma A+C against {rules[b_][0]}")
ex_net = (np.log1p(fullR["ac"]) - np.log1p(rf)).tolist()
assert f(deflated_sharpe(ac_log.tolist(), n_trials=12), 3) == base["dsr_net_12"]
put("acct_dsr12", f(deflated_sharpe(ex_net, n_trials=12), 3))
put("acct_dsr1", f(deflated_sharpe(ex_net, n_trials=1), 3))
assert flips == ["the sign of the rule's return in 2018"], flips          # Section 5.5 names this as the one change of sign
put("acct_y2018", spct(float(yr.loc[2018, "ac"])))
put("acct_borrow_dec", f"{BORROW:.3f}")
put("acct_flips_n", n0(len(flips)))
put("acct_flips", "; ".join(flips) if flips else "none")
put("acct_years_pos", n0(int((yr["ac"] > 0).sum())))
put("acct_years_beat", n0(int((yr["ac"] > yr["qq"]).sum())))
put("acct_order", ", ".join(rules[k][0] for k in order1))
print(f"    excess-return Sharpe: A+C {V['acct_ac_sh1']}, trend long/cash {V['acct_tl_sh1']}, trend long/short {V['acct_ts_sh1']}, QQQ {V['acct_qq_sh1']}; sign changes: {V['acct_flips']}")

# ================================================================================================ open-interest timing
print("[+] open-interest timing")
ch = pd.concat([pd.read_parquet(CHAINS / "chains_SPX.parquet"), pd.read_parquet(CHAINS / "chains_SPX_pre2022.parquet")], ignore_index=True)
ch = ch.drop_duplicates(["date", "optionSymbol"])
ch = ch[ch["dte"] >= 1][["date", "optionSymbol", "openInterest", "volume"]].sort_values(["optionSymbol", "date"])
days = sorted(ch["date"].unique())
nxt = dict(zip(days[:-1], days[1:]))
ch["next_date"] = ch["date"].map(nxt)
m = ch.merge(ch, left_on=["optionSymbol", "next_date"], right_on=["optionSymbol", "date"], suffixes=("_a", "_b"))
d_oi = (m["openInterest_b"] - m["openInterest_a"]).abs()
moved = d_oi > 0
ok_prev = float((d_oi[moved] <= m.loc[moved, "volume_a"]).mean())     # the change is within the EARLIER day's volume
ok_same = float((d_oi[moved] <= m.loc[moved, "volume_b"]).mean())     # the change is within the LATER day's volume
put("oi_pairs", n0(int(moved.sum())))
put("oi_fit_prev", pct(ok_prev, 1))
put("oi_fit_same", pct(ok_same, 1))
put("oi_corr_prev", f(float(np.corrcoef(d_oi[moved], m.loc[moved, "volume_a"])[0, 1])))
put("oi_corr_same", f(float(np.corrcoef(d_oi[moved], m.loc[moved, "volume_b"])[0, 1])))
print(f"    change in open interest fits within the earlier day's volume on {ok_prev:.1%} of {moved.sum():,} contract-days, within the same day's on {ok_same:.1%}")

# ================================================================================================ 6. HOLDOUT
print("[6] holdout")


def pdf(x):
    return np.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def reading(df):
    df = df.copy()
    df["oi"] = pd.to_numeric(df["openInterest"], errors="coerce")
    df["mid"] = pd.to_numeric(df["mid"], errors="coerce")
    df = df[(df["dte"].between(1, 8)) & (df["oi"] > 0) & (df["mid"] > 0)]
    S, K = df["underlyingPrice"].values.astype(float), df["strike"].values.astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        df = df[np.abs(np.log(K / S)) < 0.20]
    S, K = df["underlyingPrice"].values.astype(float), df["strike"].values.astype(float)
    Tm = df["dte"].values.astype(float) / 365.0
    cp = np.where(df["side"].values == "call", 1.0, -1.0)
    price = df["mid"].values.astype(float)
    sig = np.full(price.shape, 0.25)
    for _ in range(50):
        d1 = (np.log(S / K) + (R_F - Q_DIV + 0.5 * sig ** 2) * Tm) / (sig * np.sqrt(Tm))
        d2 = d1 - sig * np.sqrt(Tm)
        model = cp * (S * np.exp(-Q_DIV * Tm) * ndtr(cp * d1) - K * np.exp(-R_F * Tm) * ndtr(cp * d2))
        vega = S * np.exp(-Q_DIV * Tm) * pdf(d1) * np.sqrt(Tm)
        sig = np.clip(sig - (model - price) / np.maximum(vega, 1e-8), 1e-3, 5.0)
    d1 = (np.log(S / K) + (R_F - Q_DIV + 0.5 * sig ** 2) * Tm) / (sig * np.sqrt(Tm))
    gam = np.exp(-Q_DIV * Tm) * pdf(d1) / (S * sig * np.sqrt(Tm))
    df["signed"] = cp * gam * df["oi"].values * S ** 2 * 0.01
    return df.groupby("date")["signed"].sum(), df.groupby("date").size()


hc = pd.read_parquet(paths.HOLDOUT_CHAINS).drop_duplicates(["date", "optionSymbol"])
gex_new, n_contracts = reading(hc)
gex_new.index = pd.to_datetime(gex_new.index)
cert = pd.read_csv(paths.READING, index_col=0, parse_dates=True)["gex"]     # the sample's reading, written by paper_numbers.py
cert.index = pd.to_datetime(cert.index).normalize()
last_in = pd.Timestamp("2026-06-12")
par = pd.read_csv(DATA / "holdout_parity.csv").iloc[0]
assert abs(gex_new[last_in] / cert[last_in] - 1) < 1e-9, "the re-downloaded sample day does not reproduce the sample's reading"
put("ho_parity_rows", n0(par["matched"]))
put("ho_parity_day", str(last_in.date()))
gex_all = pd.concat([cert, gex_new[gex_new.index > last_in]]).sort_index()
hold_quotes = gex_new.index[gex_new.index > last_in]
# unbroken stretch from the first holdout session
import exchange_calendars as xc
sess = [pd.Timestamp(s.date()) for s in xc.get_calendar("XNYS").sessions_in_range("2026-06-15", "2026-11-12")]
stretch = []
for s in sess:
    if s in hold_quotes:
        stretch.append(s)
    else:
        break
close = q["Close"]
ret_all = np.log(close / close.shift(1))
hf = pd.DataFrame(index=gex_all.index.intersection(close.index).sort_values())
hf["g"] = gex_all.shift(1).reindex(hf.index)
hf["r"] = ret_all.reindex(hf.index)
hf["M"] = ret_all.rolling(20).sum().reindex(hf.index)
hf = hf.dropna()
A_ = np.where(hf["g"] > 0, np.sign(hf["r"]), -np.sign(hf["r"]))
hf["C"] = np.sign(hf["M"])
hf["h"] = np.where(hf["g"] == 0, 0.0, (A_ + hf["C"]) / 2)
assert (hf["h"].reindex(fr.index) == fr["h"]).all(), "holdout code does not reproduce the sample's positions"
# return days are the frame's own days, built exactly as in the sample: days that have a reading of their own
hh = hf["h"]
x_net = (hh.shift(1) * hf["r"] - COST * hh.diff().abs())
x_gross = hh.shift(1) * hf["r"]
ho = hf.index[(hf.index >= pd.Timestamp("2026-06-15"))]
Clh = hf["C"].where(hf["C"] > 0, 0.0)
t_net = (Clh.shift(1) * hf["r"] - COST * Clh.diff().abs())
put("ho_planned", n0(105))
put("ho_days", n0(len(ho)))
put("ho_a", str(ho[0].date()))
put("ho_b", str(ho[-1].date()))
put("ho_quote_b", str(stretch[-1].date()))
put("ho_quote_days", n0(len(stretch)))
put("ho_contracts", n0(float(n_contracts[n_contracts.index > "2026-06-12"].median())))
pos_carried = hh.shift(1).reindex(ho)
put("ho_long", n0(int((pos_carried > 0).sum())))
put("ho_short", n0(int((pos_carried < 0).sum())))
put("ho_cash", n0(int((pos_carried == 0).sum())))
for key, ser_ in (("ac", x_net.reindex(ho)), ("acg", x_gross.reindex(ho)), ("tl", t_net.reindex(ho)), ("qq", hf["r"].reindex(ho))):
    put(f"ho_{key}_ret", spct(float(np.expm1(ser_.sum()))))
    put(f"ho_{key}_sh", f(sharpe(ser_)) if ser_.std() > 0 else "0.00")
put("ho_se", f(math.sqrt(AF / len(ho)), 1))
for key in ("ac", "tl", "qq"):
    put(f"ho_{key}_ret_abs", ab(V[f"ho_{key}_ret"]))
put("ho_remaining", n0(105 - len(stretch)))
put("ho_big", n0(int((np.abs(np.expm1(hf["r"].reindex(ho))) > 0.01).sum())))
put("ho_long_losses", n0(int(((pos_carried > 0) & (x_net.reindex(ho) < 0)).sum())))
put("ho_short_losses", n0(int(((pos_carried < 0) & (x_net.reindex(ho) < 0)).sum())))
assert V["ho_ac_ret"].startswith(MINUS) and V["ho_qq_ret"].startswith("+") and V["ho_tl_ret"].startswith(MINUS), "Section 5.6 is written for a loss while QQQ gained"
assert (V["ho_long"], V["ho_long_losses"], V["ho_short"], V["ho_short_losses"]) == ("2", "2", "4", "2"), "Section 5.6 describes these counts in words"
put("ho_putheavy", n0(int((hf["g"].reindex(ho) < 0).sum())))
T["ho"] = table(["", "Holdout: Gamma A+C, after costs", "Holdout: trend vote, long or cash", "Holdout: buy and hold QQQ", "Sample: Gamma A+C, after costs"],
                [["Days", V["ho_days"], V["ho_days"], V["ho_days"], n0(n)],
                 ["Total return", V["ho_ac_ret"], V["ho_tl_ret"], V["ho_qq_ret"], spct(wealth(ac_s) - 1, 0)],
                 ["Sharpe ratio, annualized", V["ho_ac_sh"], V["ho_tl_sh"], V["ho_qq_sh"], f(sharpe(ac_log))],
                 ["Days long / short / in cash", f"{V['ho_long']} / {V['ho_short']} / {V['ho_cash']}", "", "", f"{base['n_long']} / {base['n_short']} / {base['n_flat']}"]],
                [("l", 24), ("r", 19), ("r", 19), ("r", 19), ("r", 19)])
pd.DataFrame({"h_carried": pos_carried, "r": hf["r"].reindex(ho), "net": x_net.reindex(ho), "g": hf["g"].reindex(ho)}).to_csv(DATA / "holdout_daily.csv")
print(f"    {len(ho)} return days {ho[0].date()} to {ho[-1].date()}: A+C {V['ho_ac_ret']} (Sharpe {V['ho_ac_sh']}), trend {V['ho_tl_ret']}, QQQ {V['ho_qq_ret']}; long/short/cash {V['ho_long']}/{V['ho_short']}/{V['ho_cash']}")

(paths.RESULTS / "numbers_journal.json").write_text(json.dumps(V, indent=1, sort_keys=True, ensure_ascii=False))
(paths.RESULTS / "tables_journal.json").write_text(json.dumps(T, indent=1, ensure_ascii=False))
print(f"wrote {len(V)} values and {len(T)} tables")
