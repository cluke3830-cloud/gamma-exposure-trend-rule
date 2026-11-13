#!/usr/bin/env python3
"""The main results of the paper: the reading, the rule, and every statistic of Sections 3 to 6.
Run fetch_inputs.py first (it downloads QQQ prices), then:  python3 paper_numbers.py

Nothing in the paper is typed by hand: the text carries {{key}} placeholders, this script writes
results/numbers.json, and build_journal.py stops on a missing key.

  1. QUOTES -> READING   the daily reading (call dollar gamma minus put dollar gamma) from the raw option quotes;
  2. READING -> RULE     the daily positions from the reading and QQQ's closing prices;
  3. RULE -> RESULTS     returns, Sharpe ratios, drawdowns, the deflated Sharpe ratio.

If the author's earlier outputs are available (paths.py, optional entries), each layer is also asserted equal to
them: the reading date by date, the positions row by row, and the headline statistics. Without them those
comparisons are skipped. The script reads data only and writes only inside this repository.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import ndtr, ndtri

import paths

CHAINS = paths.CHAINS            # the raw option quotes (not distributed, see README)
CERT = paths.CERTIFIED           # optional: an earlier, separately produced reading to compare with
OCT = paths.OCTOBER              # optional: an earlier daily frame and headline numbers to compare with
DATA = paths.WORK                # daily series written here are never published

R_F, Q_DIV = 0.04, 0.014            # us_bear_lab.R, Q
DTE_LO, DTE_HI, MONEY = 1, 8, 0.20  # universe
COST = 2e-4                         # 2 basis points per unit of turnover
AF = 252                            # sessions per year used to annualise
MINUS = "−"

V = {}        # key -> text for the paper
RAW = {}      # key -> number, for the figure script


# ----------------------------------------------------------------------------------------------- formatting
def _neg(s):
    return s.replace("-", MINUS)


def f(x, d=2):
    return _neg(f"{x:.{d}f}")


def fs(x, d=2):
    return _neg(f"{x:+.{d}f}")


def pct(x, d=1):
    return _neg(f"{x * 100:.{d}f}%")


def spct(x, d=1):
    return _neg(f"{x * 100:+.{d}f}%")


def n0(x):
    return f"{int(round(x)):,}"


def sci(x, d=2):
    m, e = f"{x:.{d}e}".split("e")
    return _neg(f"{m} × 10^{int(e)}")


def put(key, text, raw=None):
    assert isinstance(text, str) and "nan" not in text.lower(), (key, text)
    V[key] = text
    if raw is not None:
        RAW[key] = float(raw)


# ----------------------------------------------------------------------------------------------- statistics
def sharpe(x):
    x = pd.Series(x).dropna()
    return float(x.mean() / x.std() * np.sqrt(AF))


def mdd(x):
    e = (1 + pd.Series(x).dropna()).cumprod()
    return float((e / e.cummax() - 1).min())


def cagr(x):
    x = pd.Series(x).dropna()
    return float((1 + x).prod() ** (AF / len(x)) - 1)


def total(x):
    return float((1 + pd.Series(x).dropna()).prod() - 1)


def oct_num(s):
    """Parse the October paper's LaTeX-flavoured strings: '$-$22.9\\%' -> -22.9, '2,118' -> 2118."""
    t = s.replace("$", "").replace("\\%", "").replace("{,}", "").replace(",", "").replace("\\times 10^{", "e").replace("}", "")
    return float(t)


# =============================================================================================== 1. RAW -> READING
print("[1/6] raw option chains -> reading", flush=True)
post = pd.read_parquet(CHAINS / "chains_SPX.parquet")
pre = pd.read_parquet(CHAINS / "chains_SPX_pre2022.parquet")
raw = pd.concat([post, pre], ignore_index=True)
put("raw_rows", n0(len(raw)))
put("raw_rows_post", n0(len(post)))
put("raw_rows_pre", n0(len(pre)))
put("raw_dates_post", n0(post["date"].nunique()))
put("raw_dates_pre", n0(pre["date"].nunique()))
put("raw_date_a_pre", str(pre["date"].min()))
put("raw_date_b_pre", str(pre["date"].max()))
put("raw_date_a_post", str(post["date"].min()))
put("raw_date_b_post", str(post["date"].max()))
dups = int(raw.duplicated(["date", "optionSymbol"]).sum())
put("raw_dups", n0(dups))
ch = raw.drop_duplicates(["date", "optionSymbol"]).copy()
ch["date"] = pd.to_datetime(ch["date"])
put("chain_rows", n0(len(ch)))
put("chain_dates", n0(ch["date"].nunique()))
bdays = pd.bdate_range("2018-01-02", "2026-06-12")
put("bdays", n0(len(bdays)))
put("bdays_nodata", n0(len(bdays) - ch["date"].nunique()))
ch["oi"] = pd.to_numeric(ch["openInterest"], errors="coerce")
ch["mid"] = pd.to_numeric(ch["mid"], errors="coerce")
assert float((ch["mid"] - (ch["bid"] + ch["ask"]) / 2).abs().max()) < 1e-9, "vendor mid is not (bid+ask)/2"
put("chain_dte0", n0((ch["dte"] == 0).sum()))

s1 = ch[ch["dte"].between(DTE_LO, DTE_HI)]
s2 = s1[s1["oi"] > 0]
s3 = s2[s2["mid"] > 0]
S_, K_ = s3["underlyingPrice"].values.astype(float), s3["strike"].values.astype(float)
u = s3[np.abs(np.log(K_ / S_)) < MONEY].copy()
put("f_dte", n0(len(s1)))
put("f_oi", n0(len(s2)))
put("f_mid", n0(len(s3)))
put("f_money", n0(len(u)))
put("f_drop_dte", n0(len(ch) - len(s1)))
put("f_drop_oi", n0(len(s1) - len(s2)))
put("f_drop_mid", n0(len(s2) - len(s3)))
put("f_drop_money", n0(len(s3) - len(u)))
put("u_calls", n0((u["side"] == "call").sum()))
put("u_puts", n0((u["side"] == "put").sum()))
put("u_dates", n0(u["date"].nunique()))
sym_root = u["optionSymbol"].str.extract(r"^([A-Z]+)")[0]
put("u_spxw", n0((sym_root == "SPXW").sum()))
put("u_spx", n0((sym_root == "SPX").sum()))
per = u.groupby("date").size()
nexp = u.groupby("date")["expiration"].nunique()
pd.DataFrame({"contracts": per, "expiries": nexp}).to_csv(DATA / "chain_counts.csv")
for y, v in per.groupby(per.index.year).median().items():
    put(f"med_contracts_{y}", n0(v))
put("med_contracts_1821", n0(per[per.index.year <= 2021].median()))
put("med_contracts_2326", n0(per[per.index.year >= 2023].median()))
put("med_exp_1821", n0(nexp[nexp.index.year <= 2021].median()))
put("med_exp_2326", n0(nexp[nexp.index.year >= 2023].median()))


def bsm_d1(S, K, T, sig):
    return (np.log(S / K) + (R_F - Q_DIV + 0.5 * sig ** 2) * T) / (sig * np.sqrt(T))


def pdf(x):
    return np.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def bsm_price(S, K, T, sig, cp):
    d1 = bsm_d1(S, K, T, sig)
    d2 = d1 - sig * np.sqrt(T)
    return cp * (S * np.exp(-Q_DIV * T) * ndtr(cp * d1) - K * np.exp(-R_F * T) * ndtr(cp * d2))


def implied_vol(price, S, K, T, cp, n=50, trace=None):
    sig = np.full(np.shape(price), 0.25)
    for k in range(n):
        d1 = bsm_d1(S, K, T, sig)
        vega = S * np.exp(-Q_DIV * T) * pdf(d1) * np.sqrt(T)
        model = bsm_price(S, K, T, sig, cp)
        if trace is not None:
            trace.append((k, float(np.ravel(sig)[0]), float(np.ravel(model)[0]), float(np.ravel(vega)[0])))
        sig = np.clip(sig - (model - price) / np.maximum(vega, 1e-8), 1e-3, 5.0)
    return sig


S = u["underlyingPrice"].values.astype(float)
K = u["strike"].values.astype(float)
T = u["dte"].values.astype(float) / 365.0
cp = np.where(u["side"].values == "call", 1.0, -1.0)
iv = implied_vol(u["mid"].values.astype(float), S, K, T, cp)
d1 = bsm_d1(S, K, T, iv)
gam = np.exp(-Q_DIV * T) * pdf(d1) / (S * iv * np.sqrt(T))
G = gam * u["oi"].values * S ** 2 * 0.01
u["iv"], u["d1"], u["gamma"], u["G"], u["cp"] = iv, d1, gam, G, cp
u["signed"] = cp * G
gex_mine = u.groupby("date")["signed"].sum()

gex_mine.index = pd.to_datetime(gex_mine.index).normalize()
if CERT is not None:                                   # compare with the earlier reading, date by date
    earlier = pd.read_parquet(CERT)["gex_std"]
    earlier.index = pd.to_datetime(earlier.index).normalize()
    assert gex_mine.index.equals(earlier.index), "reading dates differ from the earlier series"
    rel = float(((gex_mine - earlier).abs() / earlier.abs()).max())
    assert (np.sign(gex_mine) == np.sign(earlier)).all() and rel < 1e-9, rel
    put("recheck_dates", n0(len(earlier)))
    put("recheck_rel", "no difference at all" if rel == 0 else f"a largest relative difference of {sci(rel, 1)}")
else:
    rel = float("nan")
cert = gex_mine.copy()                                 # the reading used from here on
cert.rename("gex").to_csv(paths.READING)
bad_S = int((~(s3["underlyingPrice"] > 0)).sum())
put("f_missing_S", n0(bad_S))
put("f_drop_far", n0(len(s3) - len(u) - bad_S))
put("gex_pos_all", n0((cert > 0).sum()))
put("gex_neg_all", n0((cert < 0).sum()))
clip_lo = iv <= 1e-3 + 1e-12
put("clip_n", n0(clip_lo.sum()))
put("clip_pct", pct(clip_lo.mean()))
put("clip_share", sci(float(G[clip_lo].sum() / G.sum()), 1))
put("clip_hi_n", n0((iv >= 5.0 - 1e-12).sum()))
print(f"      reading computed on {len(cert):,} dates" + (f", largest relative gap to the earlier series {rel:.1e}" if CERT is not None else ""), flush=True)

# =============================================================================================== 2. READING -> RULE
print("[2/6] reading -> rule", flush=True)
q = pd.read_parquet(paths.QQQ)[["Open", "Close"]]
close, opn = q["Close"], q["Open"]
ret = np.log(close / close.shift(1))
put("qqq_a", str(q.index.min().date()))
put("qqq_b", str(q.index.max().date()))
put("qqq_rows", n0(len(q)))
df = pd.DataFrame(index=cert.index.intersection(close.index).sort_values())
df["g"] = cert.shift(1).reindex(df.index)                 # previous chain date's reading
df["g_same"] = cert.reindex(df.index)
df["r"] = ret.reindex(df.index)
df["M"] = ret.rolling(20).sum().reindex(df.index)
df["fwd"] = ret.shift(-1).reindex(df.index)
df["oc_next"] = np.log(close.shift(-1) / opn.shift(-1)).reindex(df.index)
df["co_next"] = np.log(opn.shift(-1) / close).reindex(df.index)
df["P"] = close.reindex(df.index)
df = df.dropna()


def rule(g, r, M):
    gamma_sign = np.sign(-g)
    if gamma_sign == 0:
        return 0.0, float(np.sign(M)), 0.0
    A = -np.sign(r) if gamma_sign > 0 else np.sign(r)
    C = np.sign(M)
    return float(A), float(C), float((A + C) / 2.0)


acp = [rule(g, r, M) for g, r, M in zip(df["g"], df["r"], df["M"])]
df["A"], df["C"], df["h"] = [x[0] for x in acp], [x[1] for x in acp], [x[2] for x in acp]
if OCT is not None:                                     # compare with the earlier frame, row by row
    octf = pd.read_parquet(OCT / "gamma_daily.parquet")
    assert df.index.equals(octf.index), "frame dates differ from the earlier frame"
    assert (df["h"].values == octf["pos"].values).all() and (df["A"].values == octf["A"].values).all() and (df["C"].values == octf["C"].values).all()
    assert np.allclose(df["g"].values, octf["gex_prev"].values, rtol=1e-12) and np.allclose(df["r"].values, octf["ret_t"].values, atol=1e-15)
closed = np.sign(df["M"]) * (np.sign(df["g"] * df["r"]) == np.sign(df["M"]))
nz = df["r"] != 0
assert (closed[nz] == df["h"][nz]).all(), "closed form differs from the rule"
put("n_days", n0(len(df)), len(df))
put("date_a", str(df.index[0].date()))
put("date_b", str(df.index[-1].date()))
sess = close.loc[df.index[0]:df.index[-1]].index
missing = sess.difference(df.index)
put("n_sessions", n0(len(sess)))
put("n_missing", n0(len(missing)))
put("missing_dates", ", ".join(str(d.date()) for d in missing))
put("closed_match", n0(int((closed[nz] == df["h"][nz]).sum())))
put("n_r0", n0(int((~nz).sum())))

h, fwd, r = df["h"], df["fwd"], df["r"]
gross = h * fwd                                                     # log return, decided at close t, earned t -> t+1
net = (h.shift(1) * r - COST * h.diff().abs()).dropna()             # log return, indexed on the day it is earned
net_s = (h.shift(1) * np.expm1(r) - COST * h.diff().abs()).dropna() # same, simple returns (for compounding)
hold_log = r.reindex(net.index)                                     # QQQ on the same earning days
hold_s = np.expm1(hold_log)
Cl = df["C"].where(df["C"] > 0, 0.0)                                # long-or-flat 20-session rule
trend_log = (Cl.shift(1) * r - COST * Cl.diff().abs()).dropna()
trend_s = (Cl.shift(1) * np.expm1(r) - COST * Cl.diff().abs()).dropna()
A_log = (df["A"].shift(1) * r - COST * df["A"].diff().abs()).dropna()
C_log = (df["C"].shift(1) * r - COST * df["C"].diff().abs()).dropna()
net2 = (h.shift(1) * r - 2 * COST * h.diff().abs()).dropna()
lag2 = (h.shift(1) * fwd).dropna()                                  # one extra session of delay, no cost

# =============================================================================================== 3. RULE -> RESULTS
print("[3/6] rule -> results", flush=True)
octn = json.loads((OCT / "numbers_gamma.json").read_text()) if OCT is not None else {}
octg = json.loads((OCT / "numbers_gate.json").read_text()) if OCT is not None else {}


def same(key, value, d):
    """Assert that a statistic equals the one in the earlier run. Skipped when that run is not available."""
    if key not in octn:
        return
    want = oct_num(octn[key])
    got = round(value, d)
    assert abs(got - want) < 10 ** (-d) / 2 + 1e-12, (key, got, want)


turn = float(h.diff().abs().sum() / (len(h) / AF))
checks = [("gross_sharpe", sharpe(gross), 2), ("net_sharpe", sharpe(net), 2), ("netsim_sharpe", sharpe(net_s), 2),
          ("x2_sharpe", sharpe(net2), 2), ("lag_gross", sharpe(lag2), 2), ("c_long_only", sharpe(trend_log), 2),
          ("a_only", sharpe(A_log), 2), ("c_only", sharpe(C_log), 2), ("net_cagr", cagr(net_s) * 100, 1),
          ("net_dd", mdd(net_s) * 100, 1), ("net_vol", net_s.std() * np.sqrt(AF) * 100, 1), ("c_long_dd", mdd(trend_s) * 100, 1),
          ("turnover", turn, 0), ("cost_drag", COST * turn * 100, 1), ("is_sharpe", sharpe(gross[gross.index.year < 2022]), 2),
          ("oos_sharpe", sharpe(gross[gross.index.year >= 2022]), 2), ("corr_qqq", net.corr(hold_log), 2),
          ("beta_qqq", net.cov(hold_log) / hold_log.var(), 2), ("corr_c_long", trend_log.corr(net), 2)]
for key, val, d in checks:
    same(key, val, d)
print(f"      {len(checks)} headline figures " + ("equal the earlier run's" if octn else "computed (no earlier run to compare with)"), flush=True)

put("gross_sharpe", f(sharpe(gross)), sharpe(gross))
put("net_sharpe", f(sharpe(net)), sharpe(net))
put("net_sharpe_simple", f(sharpe(net_s)))
put("net2_sharpe", f(sharpe(net2)), sharpe(net2))
put("lag2_sharpe", f(sharpe(lag2)), sharpe(lag2))
put("trend_sharpe", f(sharpe(trend_log)), sharpe(trend_log))
put("a_only_sharpe", f(sharpe(A_log)), sharpe(A_log))
put("c_only_sharpe", f(sharpe(C_log)), sharpe(C_log))
put("hold_sharpe", f(sharpe(hold_log)), sharpe(hold_log))
put("net_cagr", pct(cagr(net_s)), cagr(net_s))
put("net_vol", pct(net_s.std() * np.sqrt(AF)))
put("net_dd", pct(mdd(net_s)), mdd(net_s))
put("net_total", spct(total(net_s), 0))
put("net_growth", f(1 + total(net_s)))
put("hold_cagr", pct(cagr(hold_s)), cagr(hold_s))
put("hold_vol", pct(hold_s.std() * np.sqrt(AF)))
put("hold_dd", pct(mdd(hold_s)), mdd(hold_s))
put("hold_total", spct(total(hold_s), 0))
put("hold_growth", f(1 + total(hold_s)))
put("trend_cagr", pct(cagr(trend_s)), cagr(trend_s))
put("trend_vol", pct(trend_s.std() * np.sqrt(AF)))
put("trend_dd", pct(mdd(trend_s)), mdd(trend_s))
put("trend_growth", f(1 + total(trend_s)))
put("trend_in", pct(float((Cl > 0).mean())))
put("n_net", n0(len(net)))
put("net_a", str(net.index[0].date()))
put("net_b", str(net.index[-1].date()))
put("years", f(len(net) / AF, 1))
put("turnover", f(turn, 0), turn)
put("cost_drag", pct(COST * turn))
put("n_changes", n0(int((h.diff().abs() > 0).sum())))
put("n_flips", n0(int((h.diff().abs() == 2).sum())))
put("is_sharpe", f(sharpe(gross[gross.index.year < 2022])))
put("oos_sharpe", f(sharpe(gross[gross.index.year >= 2022])))
half = net.index[len(net) // 2]
put("half_date", str(half.date()))
put("h1_sharpe", f(sharpe(net[net.index < half])))
put("h2_sharpe", f(sharpe(net[net.index >= half])))
put("corr_qqq", f(net.corr(hold_log)))
put("beta_qqq", f(net.cov(hold_log) / hold_log.var()))
put("corr_trend", f(trend_log.corr(net)))
put("mean_day_bp", fs(net_s.mean() * 1e4, 1))
put("sd_day_pct", pct(net_s.std(), 2))
put("best_day", spct(net_s.max()))
put("best_day_date", str(net_s.idxmax().date()))
put("worst_day", spct(net_s.min()))
put("worst_day_date", str(net_s.idxmin().date()))
inpos = h.shift(1).reindex(net.index) != 0
put("hit_all", pct(float((net_s[inpos] > 0).mean())))
put("n_inpos", n0(int(inpos.sum())))
put("pct_inpos", pct(float(inpos.mean())))
for name, m in (("long", h > 0), ("short", h < 0), ("flat", h == 0)):
    put(f"n_{name}", n0(int(m.sum())))
    put(f"pct_{name}", pct(float(m.mean())))
put("n_half", n0(int(h.abs().eq(0.5).sum())))
put("half_dates", ", ".join(str(d.date()) for d in h.index[h.abs().eq(0.5)]) or "none")
put("n_full_long", n0(int((h == 1).sum())))
put("n_full_short", n0(int((h == -1).sum())))
put("n_callheavy", n0(int((df["g"] > 0).sum())))
put("n_putheavy", n0(int((df["g"] < 0).sum())))
put("pct_callheavy", pct(float((df["g"] > 0).mean())))
put("pct_putheavy", pct(float((df["g"] < 0).mean())))
put("sum_long", fs(float(gross[h > 0].sum()), 3))
put("sum_short", fs(float(gross[h < 0].sum()), 3))
put("hit_long", pct(float((gross[h > 0] > 0).mean())))
put("hit_short", pct(float((gross[h < 0] > 0).mean())))
runs = (h != h.shift()).cumsum()
runlen = h[h != 0].groupby(runs[h != 0]).size()
put("n_runs", n0(len(runlen)))
put("run_mean", f(float(runlen.mean()), 1))
put("run_max", n0(int(runlen.max())))

# how often each of the eight combinations of the three questions occurred
k = 0
tot8 = 0
for gs_ in (1, -1):
    for rs_ in (1, -1):
        for ms_ in (1, -1):
            k += 1
            m8 = (np.sign(df["g"]) == gs_) & (np.sign(df["r"]) == rs_) & (np.sign(df["M"]) == ms_)
            put(f"case{k}_n", n0(int(m8.sum())))
            tot8 += int(m8.sum())
            want = float(ms_) if gs_ * rs_ == ms_ else 0.0
            assert (h[m8] == want).all(), k
put("case_total", n0(tot8))
put("case_other", n0(len(df) - tot8))

# worked arithmetic for the statistics section
put("ex_mean_bp", f(net.mean() * 1e4, 2))
put("ex_sd_pct", pct(net.std(), 3))
put("ex_ratio", f(net.mean() / net.std(), 4))
put("ex_sqrt252", f(math.sqrt(AF), 3))
put("ex_years", f(len(net_s) / AF, 2))
put("ex_mean_ann", pct(net.mean() * AF))
put("ex_sd_ann", pct(net.std() * math.sqrt(AF)))
for name, ser in (("net", net_s), ("hold", hold_s), ("trend", trend_s)):
    e = (1 + ser).cumprod()
    trough = (e / e.cummax() - 1).idxmin()
    peak = e.loc[:trough].idxmax()
    after = e.loc[trough:]
    rec = after[after >= e.loc[peak]]
    put(f"dd_{name}_peak", str(peak.date()))
    put(f"dd_{name}_trough", str(trough.date()))
    put(f"dd_{name}_peak_val", f(float(e.loc[peak]), 2))
    put(f"dd_{name}_trough_val", f(float(e.loc[trough]), 2))
    put(f"dd_{name}_recover", str(rec.index[0].date()) if len(rec) else "not recovered by the end of the test")
# position changes filled at the next morning's open instead of this close (no cost), as the project's fill check does
changed = h.ne(h.shift(1).fillna(0.0))
alt = fwd.copy()
alt[changed & h.ne(0)] = df.loc[changed & h.ne(0), "oc_next"]
alt[changed & h.eq(0)] = df.loc[changed & h.eq(0), "co_next"]
same("alt_sharpe", sharpe(h * alt), 2)
put("open_sharpe", f(sharpe(h * alt)))
# which sessions have no reading, and why
all_sess = close.loc["2018-01-02":"2026-06-12"].index
have_rows = pd.DatetimeIndex(sorted(ch["date"].unique()))
put("sess_all", n0(len(all_sess)))
put("sess_holidays", n0(len(bdays) - len(all_sess)))
no_rows = all_sess.difference(have_rows)
no_qual = all_sess.intersection(have_rows).difference(cert.index)
put("sess_no_rows", n0(len(no_rows)))
put("sess_no_rows_dates", ", ".join(str(d.date()) for d in no_rows) or "none")
put("sess_no_qual", n0(len(no_qual)))
put("sess_no_qual_dates", ", ".join(str(d.date()) for d in no_qual) or "none")
put("rows_not_session", n0(len(have_rows.difference(all_sess))))

# sized as deployed on the paper account
ALLOC = 0.611
sized = ALLOC * net_s
put("alloc", "0.611")
put("sized_cagr", pct(cagr(sized)))
put("sized_vol", pct(sized.std() * np.sqrt(AF)))
put("sized_dd", pct(mdd(sized)))
put("sized_dd_abs", pct(abs(mdd(sized))))
put("net_dd_abs", pct(abs(mdd(net_s))))
put("hold_dd_abs", pct(abs(mdd(hold_s))))
put("trend_dd_abs", pct(abs(mdd(trend_s))))

# calendar years and months
yr = pd.DataFrame({"strategy": net_s.groupby(net_s.index.year).apply(total), "qqq": hold_s.groupby(hold_s.index.year).apply(total),
                   "trend": trend_s.groupby(trend_s.index.year).apply(total),
                   "sharpe": net.groupby(net.index.year).apply(sharpe), "days": net_s.groupby(net_s.index.year).size()})
yr.to_csv(DATA / "yearly.csv")
for y, row in yr.iterrows():
    same(f"y{y}", row["strategy"] * 100, 1)
    put(f"y{y}", spct(row["strategy"]))
    put(f"yq{y}", spct(row["qqq"]))
    put(f"ysh{y}", f(row["sharpe"]))
put("years_pos", n0(int((yr["strategy"] > 0).sum())))
put("years_n", n0(len(yr)))
put("years_beat", n0(int((yr["strategy"] > yr["qqq"]).sum())))
mo = net_s.groupby([net_s.index.year, net_s.index.month]).apply(total).unstack()
mo.to_csv(DATA / "monthly.csv")
mflat = mo.stack()
put("months_n", n0(len(mflat)))
put("months_pos", n0(int((mflat > 0).sum())))
put("months_pos_pct", pct(float((mflat > 0).mean()), 0))
put("month_best", spct(float(mflat.max())))
put("month_best_when", f"{mflat.idxmax()[0]}-{mflat.idxmax()[1]:02d}")
put("month_worst", spct(float(mflat.min())))
put("month_worst_when", f"{mflat.idxmin()[0]}-{mflat.idxmin()[1]:02d}")

# stress windows named in the project's rules
STRESS = {"fed": ("2018-10-01", "2018-12-31"), "covid": ("2020-02-15", "2020-04-30"), "tech": ("2022-01-01", "2022-12-31"), "svb": ("2023-03-01", "2023-03-31")}
for k, (a, b) in STRESS.items():
    same(f"{k}_sh", sharpe(gross.loc[a:b]), 2)
    put(f"{k}_sh", f(sharpe(gross.loc[a:b])))
    put(f"{k}_ret", spct(total(net_s.loc[a:b])))
    put(f"{k}_qqq", spct(total(hold_s.loc[a:b])))
    put(f"{k}_days", n0(len(net_s.loc[a:b])))

# mean next-day QQQ return by state, Newey-West t with 5 lags
import statsmodels.api as sm


def hac(x):
    x = pd.Series(x).dropna()
    res = sm.OLS(x.values, np.ones(len(x))).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
    return float(res.params[0]), float(res.tvalues[0]), float(res.bse[0])


cells = {"cl": (df["g"] > 0) & (h > 0), "cf": (df["g"] > 0) & (h == 0), "cs": (df["g"] > 0) & (h < 0),
         "pl": (df["g"] < 0) & (h > 0), "pf": (df["g"] < 0) & (h == 0), "ps": (df["g"] < 0) & (h < 0)}
rows = []
for k, m in cells.items():
    a, t, se = hac(fwd[m])
    put(f"st_{k}_n", n0(int(m.sum())))
    put(f"st_{k}_bp", fs(a * 1e4, 1))
    put(f"st_{k}_t", fs(t, 2))
    rows.append(dict(cell=k, n=int(m.sum()), bp=a * 1e4, t=t, se_bp=se * 1e4))
pd.DataFrame(rows).to_csv(DATA / "states.csv", index=False)
a, t, se = hac(fwd)
put("st_all_bp", fs(a * 1e4, 1), a * 1e4)
put("st_all_t", fs(t, 2))
put("st_all_se", f(se * 1e4, 2))
put("st_all_mean_pct", pct(a, 3))
same("st_all_t", t, 2)
same("st_ls_bp", rows[2]["bp"], 1)
same("st_pf_bp", rows[4]["bp"], 1)

# =============================================================================================== 4. DEFLATED SHARPE
print("[4/6] deflated Sharpe ratio", flush=True)
from dsr import deflated_sharpe  # the author's validation function; the step-by-step calculation below must agree with it

x = gross.values
Tn = len(x)
mu = x.sum() / Tn
sd = math.sqrt(((x - mu) ** 2).sum() / Tn)
skew = ((x - mu) ** 3).sum() / (Tn * sd ** 3)
kurt = ((x - mu) ** 4).sum() / (Tn * sd ** 4)
sr = mu / sd
EULER = 0.5772156649015329


def sr0_of(N):
    if N <= 1:
        return 0.0
    return math.sqrt(1.0 / Tn) * ((1 - EULER) * ndtri(1 - 1.0 / N) + EULER * ndtri(1 - 1.0 / (N * math.e)))


denom = math.sqrt(1 - skew * sr + (kurt - 1) / 4.0 * sr ** 2)


def dsr_of(N):
    return float(ndtr((sr - sr0_of(N)) * math.sqrt(Tn - 1) / denom))


put("dsr_T", n0(Tn), Tn)
put("dsr_mu", f(mu, 6), mu)
put("dsr_mu_bp", f(mu * 1e4, 2))
put("dsr_sd", f(sd, 6), sd)
put("dsr_sd_pct", pct(sd, 3))
put("dsr_skew", fs(skew, 3), skew)
put("dsr_kurt", f(kurt, 2), kurt)
put("dsr_sr", f(sr, 5), sr)
put("dsr_sr_ann", f(sr * math.sqrt(AF), 2))
put("dsr_denom", f(denom, 4), denom)
put("dsr_term_skew", f(skew * sr, 4))
put("dsr_term_kurt", f((kurt - 1) / 4.0 * sr ** 2, 4))
put("dsr_kurt_q", f((kurt - 1) / 4.0, 4))
put("dsr_sr2", f(sr ** 2, 6))
put("dsr_radicand", f(1 - skew * sr + (kurt - 1) / 4.0 * sr ** 2, 4))
put("dsr_num_12", f((sr - sr0_of(12)) * math.sqrt(Tn - 1), 4))
put("dsr_se", f(denom / math.sqrt(Tn - 1), 5), denom / math.sqrt(Tn - 1))
put("dsr_se_ann", f(denom / math.sqrt(Tn - 1) * math.sqrt(AF), 3), denom / math.sqrt(Tn - 1) * math.sqrt(AF))
put("dsr_sqrtT", f(math.sqrt(Tn - 1), 2))
put("dsr_varT", sci(1.0 / Tn, 2))
put("dsr_sdT", f(math.sqrt(1.0 / Tn), 5))
for N in (1, 2, 5, 12, 50, 90, 670):
    mine, gate = dsr_of(N), deflated_sharpe(list(x), n_trials=N)
    assert abs(mine - gate) < 1e-7, (N, mine, gate)
    if f"gate_gm_dsr{N}" in octg:
        assert abs(round(mine, 3) - oct_num(octg[f"gate_gm_dsr{N}"])) < 5e-4 + 1e-12, N
    put(f"dsr_{N}", f(mine, 3), mine)
    put(f"sr0_{N}", f(sr0_of(N), 5), sr0_of(N))
    put(f"sr0_{N}_ann", f(sr0_of(N) * math.sqrt(AF), 2), sr0_of(N) * math.sqrt(AF))
    put(f"z_{N}", f((sr - sr0_of(N)) * math.sqrt(Tn - 1) / denom, 3))
put("dsr_12_pct", pct(dsr_of(12)))
put("dsr_12_rest", pct(1 - dsr_of(12)))
put("dsr_net_12", f(deflated_sharpe(list(net.values), n_trials=12), 3))
put("dsr_net_1", f(deflated_sharpe(list(net.values), n_trials=1), 3))
put("q1_12", f(float(ndtri(1 - 1 / 12)), 4))
put("q2_12", f(float(ndtri(1 - 1 / (12 * math.e))), 4))
put("p1_12", f(1 - 1 / 12, 5))
put("p2_12", f(1 - 1 / (12 * math.e), 5))
put("bracket_12", f((1 - EULER) * float(ndtri(1 - 1 / 12)) + EULER * float(ndtri(1 - 1 / (12 * math.e))), 4))
put("gap_12", f(sr - sr0_of(12), 5))
Ns = np.unique(np.round(np.logspace(0, 3, 400)).astype(int))
pd.DataFrame({"N": Ns, "dsr": [dsr_of(int(n)) for n in Ns], "sr0_ann": [sr0_of(int(n)) * math.sqrt(AF) for n in Ns]}).to_csv(DATA / "dsr_curve.csv", index=False)
n_pass = max(int(n) for n in range(1, 2000) if dsr_of(n) >= 0.95)
put("dsr_maxN_pass", n0(n_pass))
put("dsr_at_pass", f(dsr_of(n_pass), 3))
put("dsr_after_pass", f(dsr_of(n_pass + 1), 3))

# where the luck bar comes from: best of N strategies with no skill, simulated
rng = np.random.default_rng(20261112)
REPS = 20000
sim = {}
for N in (12, 50, 670):
    tvals = rng.standard_t(Tn - 1, size=(REPS, N))
    best = (tvals / math.sqrt(Tn - 1)).max(axis=1)      # mean / population-sd of T normal draws equals t_{T-1} / sqrt(T-1)
    sim[N] = best * math.sqrt(AF)
    put(f"sim_mean_{N}", f(float(sim[N].mean()), 2), float(sim[N].mean()))
np.save(DATA / "luck_best12.npy", sim[12])
put("sim_reps", n0(REPS))
put("sim_seed", "20261112")

# =============================================================================================== 5. WORKED EXAMPLES
print("[5/6] worked examples", flush=True)
hv = df["h"].values
win = None
gv, rv, fv = df["g"].values, df["r"].values, df["fwd"].values
for i in range(len(df) - 6, 0, -1):     # most recent 6 sessions with all three positions, both kinds of option book, and real moves
    w = hv[i:i + 6]
    if ((w == 1).any() and (w == -1).any() and (w == 0).any() and (gv[i:i + 6] > 0).any() and (gv[i:i + 6] < 0).any()
            and (np.abs(np.expm1(rv[i:i + 6])) >= 0.002).all() and (np.abs(np.expm1(fv[i:i + 6])) >= 0.002).all()):
        win = df.iloc[i:i + 6]
        break
assert win is not None, "no example week found"
wk = win[["g", "r", "M", "A", "C", "h", "fwd", "P"]].copy()
wk["strategy_next"] = wk["h"] * np.expm1(wk["fwd"])
wk["qqq_next"] = np.expm1(wk["fwd"])
wk["r_pct"] = np.expm1(wk["r"])
wk["M_pct"] = np.expm1(wk["M"])
wk.to_csv(DATA / "week_example.csv")
put("wk_a", str(wk.index[0].date()))
put("wk_b", str(wk.index[-1].date()))
put("wk_sum", spct(float(np.prod(1 + wk["strategy_next"]) - 1), 2))
put("wk_qqq_sum", spct(float(np.prod(1 + wk["qqq_next"]) - 1), 2))
put("wk_sum_abs", pct(abs(float(np.prod(1 + wk["strategy_next"]) - 1)), 2))
put("wk_qqq_sum_abs", pct(abs(float(np.prod(1 + wk["qqq_next"]) - 1)), 2))
# the paper's prose describes this week in words (rose, fell, long, short); stop if the data no longer matches the words
w1, w5 = wk.iloc[0], wk.iloc[4]
assert str(wk.index[0].date()) == "2026-01-28", "the worked week changed: rewrite the prose in section 4.2"
assert w1["g"] > 0 and w1["r"] > 0 and w1["M"] > 0 and w1["h"] == 1 and w1["fwd"] < 0
assert w5["g"] > 0 and w5["r"] < 0 and w5["M"] < 0 and w5["h"] == -1 and w5["fwd"] < 0
assert (wk["h"].iloc[[1, 2, 3, 5]] == 0).all() and np.prod(1 + wk["strategy_next"]) > 1 > np.prod(1 + wk["qqq_next"])
word = {1.0: "Long", 0.0: "Cash", -1.0: "Short"}
arrow = {1.0: "up", -1.0: "down", 0.0: "flat"}
for j, (d, row) in enumerate(wk.iterrows(), 1):
    put(f"wk{j}_date", str(d.date()))
    put(f"wk{j}_book", "call-heavy" if row["g"] > 0 else "put-heavy")
    put(f"wk{j}_r", spct(row["r_pct"], 2))
    put(f"wk{j}_M", spct(row["M_pct"], 1))
    put(f"wk{j}_A", arrow[row["A"]])
    put(f"wk{j}_C", arrow[row["C"]])
    put(f"wk{j}_h", word[row["h"]])
    put(f"wk{j}_next", spct(row["qqq_next"], 2))
    put(f"wk{j}_pnl", spct(row["strategy_next"], 2) if row["h"] != 0 else "0.00%")
    put(f"wk{j}_P", f(row["P"], 2))
    put(f"wk{j}_r_abs", pct(abs(row["r_pct"]), 2))
    put(f"wk{j}_M_abs", pct(abs(row["M_pct"]), 1))
    put(f"wk{j}_next_abs", pct(abs(row["qqq_next"]), 2))
    put(f"wk{j}_pnl_abs", pct(abs(row["strategy_next"]), 2))

# one reading built from its contracts: the reading used by the first day of that week
ex_day = wk.index[0]
ex_read = cert.index[cert.index.get_loc(ex_day) - 1]      # the previous chain date
ex = u[u["date"] == ex_read].copy()
assert abs(ex["signed"].sum() - cert.loc[ex_read]) / abs(cert.loc[ex_read]) < 1e-9
put("ex_read", str(ex_read.date()))
put("ex_day", str(ex_day.date()))
put("ex_n", n0(len(ex)))
put("ex_ncall", n0((ex["cp"] > 0).sum()))
put("ex_nput", n0((ex["cp"] < 0).sum()))
put("ex_nexp", n0(ex["expiration"].nunique()))
put("ex_S", f(float(ex["underlyingPrice"].median()), 2))
put("ex_call_G", sci(float(ex.loc[ex["cp"] > 0, "G"].sum()), 3))
put("ex_put_G", sci(float(ex.loc[ex["cp"] < 0, "G"].sum()), 3))
put("ex_gex", _neg(sci(float(ex["signed"].sum()), 3)))
put("ex_gex_sign", "positive (call-heavy)" if ex["signed"].sum() > 0 else "negative (put-heavy)")
top = ex.sort_values("G", ascending=False).iloc[0]
tr = []
cpv = 1.0 if top["side"] == "call" else -1.0
iv_top = implied_vol(np.array([float(top["mid"])]), np.array([float(top["underlyingPrice"])]), np.array([float(top["strike"])]),
                     np.array([float(top["dte"]) / 365.0]), np.array([cpv]), trace=tr)[0]
assert abs(iv_top - top["iv"]) < 1e-12
St, Kt, Tt = float(top["underlyingPrice"]), float(top["strike"]), float(top["dte"]) / 365.0
d1t = float(bsm_d1(St, Kt, Tt, iv_top))
put("c_symbol", str(top["optionSymbol"]))
put("c_side", str(top["side"]))
put("c_S", f(St, 2))
put("c_K", n0(Kt))
put("c_dte", n0(top["dte"]))
put("c_tau", f(Tt, 5))
put("c_bid", f(float(top["bid"]), 2))
put("c_ask", f(float(top["ask"]), 2))
put("c_mid", f(float(top["mid"]), 2))
put("c_oi", n0(top["oi"]))
put("c_iv", f(iv_top, 4))
put("c_iv_pct", pct(iv_top, 2))
put("c_d1", fs(d1t, 4))
put("c_pdf", f(float(pdf(d1t)), 4))
put("c_disc", f(math.exp(-Q_DIV * Tt), 6))
put("c_sqrt_tau", f(math.sqrt(Tt), 5))
put("c_gamma", f(float(top["gamma"]), 6))
put("c_delta_1pct", f(float(top["gamma"]) * 0.01 * St, 4))
put("c_G", sci(float(top["G"]), 3))
put("c_share", pct(float(top["G"] / ex["G"].sum())))
put("c_model", f(float(bsm_price(St, Kt, Tt, iv_top, cpv)), 2))
put("c_exp", pd.to_datetime(int(top["expiration"]), unit="s").strftime("%Y-%m-%d"))
put("c_disc_r", f(math.exp(-R_F * Tt), 6))
put("c_onepct", n0(0.01 * St))
for k in (0, 1, 2, 3):
    put(f"nr{k}_sig", f(tr[k][1], 4))
    put(f"nr{k}_model", f(tr[k][2], 2))
    put(f"nr{k}_vega", f(tr[k][3], 1))
conv = next(k for k in range(1, 50) if abs(tr[k][1] - iv_top) < 5e-7)
put("nr_conv", n0(conv))
# the example day's heat map: net dollar gamma by strike band and expiry
exh = ex.copy()
exh["exp_date"] = pd.to_datetime(exh["expiration"], unit="s").dt.strftime("%Y-%m-%d")
exh["money"] = exh["strike"] / exh["underlyingPrice"] - 1
exh[["exp_date", "dte", "strike", "money", "side", "oi", "iv", "gamma", "G", "signed"]].to_csv(DATA / "example_chain.csv", index=False)

# =============================================================================================== 6. SERIES FOR FIGURES
print("[6/6] series for the figures", flush=True)
out = pd.DataFrame({"net_s": net_s, "hold_s": hold_s, "trend_s": trend_s, "net_log": net, "hold_log": hold_log})
out["h_prev"] = h.shift(1).reindex(out.index)
out.to_parquet(DATA / "series.parquet")
df[["g", "g_same", "r", "M", "A", "C", "h", "fwd", "P"]].to_parquet(DATA / "frame.parquet")
share = (df["g"] < 0).groupby(df.index.year).mean()
share.rename("put_heavy_share").to_csv(DATA / "putheavy_by_year.csv")
for y, v in share.items():
    put(f"puthv{y}", pct(v, 0))

(paths.RESULTS / "numbers.json").write_text(json.dumps(V, indent=1, sort_keys=True, ensure_ascii=False))
(paths.RESULTS / "numbers_raw.json").write_text(json.dumps(RAW, indent=1, sort_keys=True))
print(f"wrote {len(V)} values -> results/numbers.json")
for k in ("n_days", "gross_sharpe", "net_sharpe", "hold_sharpe", "trend_sharpe", "net_cagr", "hold_cagr", "net_dd", "hold_dd", "trend_dd",
          "dsr_12", "sr0_12_ann", "sim_mean_12", "dsr_maxN_pass", "wk_a", "wk_b", "ex_read", "c_symbol", "c_iv", "c_gamma", "nr_conv"):
    print(f"   {k:16s} {V[k]}")
