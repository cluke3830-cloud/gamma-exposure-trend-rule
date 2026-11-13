#!/usr/bin/env python3
"""Downloads the inputs that are not the main sample's option quotes.      python3 fetch_inputs.py [--no-chains]

1. QQQ daily prices with the dividend-adjusted close, through today (FinanceDataReader, same source as the sample).
2. The 3-month Treasury bill rate, daily (FRED series DTB3, public).
3. Holdout option quotes for the window fixed in HOLDOUT_PREREGISTRATION.md. Same vendor, same chain request as
   Appendix A. The vendor's free tier allows 100 requests a day, so this step is resumable: it starts at the first
   session not yet saved, stops when the day's requests are nearly used up, and can be run again after the reset.
   Before the first holdout day it re-downloads one in-sample day and checks it against the saved sample.

The access key is read from the environment or from a local file (paths.py) and is never printed. Everything is
written to work/, which git ignores: the vendor's terms do not allow its quotes to be redistributed.
"""
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

import paths

DATA = paths.WORK
HOLD_A, HOLD_B = "2026-06-15", "2026-11-11"          # fixed in HOLDOUT_PREREGISTRATION.md
PARITY_DAY = "2026-06-12"                             # last day of the original sample
KEEP = ["optionSymbol", "expiration", "side", "strike", "dte", "bid", "ask", "mid", "last", "openInterest", "volume", "underlyingPrice"]
B = "https://api.marketdata.app/v1/options"
RESERVE = 1                                           # requests left untouched each day


def qqq():
    import FinanceDataReader as fdr
    q = fdr.DataReader("QQQ", "2014-06-01", None)
    q.index = pd.to_datetime(q.index).normalize()
    cols = [c for c in ("Open", "Close", "Adj Close") if c in q.columns]
    assert "Adj Close" in cols, f"no dividend-adjusted close in {list(q.columns)}"
    q[cols].to_parquet(paths.QQQ)
    print(f"QQQ: {len(q):,} days {q.index[0].date()} to {q.index[-1].date()}, columns {cols}")


def tbill():
    import FinanceDataReader as fdr
    df = fdr.DataReader("FRED:DTB3", "2017-12-01")          # FRED series DTB3 through the library's FRED reader
    df.index = pd.to_datetime(df.index).normalize()
    df.index.name = "date"
    df.to_csv(paths.TBILL)
    ok = df["DTB3"].dropna()
    print(f"DTB3: {len(ok):,} daily values {ok.index[0].date()} to {ok.index[-1].date()}, range {ok.min():.2f}% to {ok.max():.2f}%")


class Vendor:
    def __init__(self):
        self._tok = paths.token()
        self.remaining = None
        self.used = 0

    def get(self, url, retries=4):
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {self._tok}"})
        for a in range(retries):
            try:
                with urllib.request.urlopen(req, timeout=45) as r:
                    rem = r.headers.get("x-api-ratelimit-remaining")
                    self.remaining = int(rem) if rem is not None else self.remaining
                    self.used += 1
                    return json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                rem = e.headers.get("x-api-ratelimit-remaining")
                self.remaining = int(rem) if rem is not None else self.remaining
                if e.code == 429:
                    self.remaining = 0
                    return None
                if e.code in (402, 404):
                    return {"s": "no_data", "code": e.code}
                time.sleep(1 + a)
            except Exception:
                time.sleep(1 + a)
        return None

    def chain(self, day, expiry):
        b = self.get(f"{B}/chain/SPX/?date={day}&expiration={expiry}&strikeLimit=100")
        if not b or b.get("s") != "ok":
            return None
        n = len(b.get("optionSymbol", []))
        df = pd.DataFrame({k: b.get(k, [None] * n) for k in KEEP})
        df.insert(0, "date", day)
        df.insert(1, "root", "SPX")
        return df


def expiries_for(day, sessions):
    """Sessions 1 to 8 calendar days after `day`. SPX options expire on every session, so this is the same set the
    vendor's expirations list gives for days to expiry 1 to 8. Same-day expiries are not requested: the filter
    drops them."""
    d0 = pd.Timestamp(day)
    return [s.strftime("%Y-%m-%d") for s in sessions if 1 <= (s - d0).days <= 8]


def chains():
    import exchange_calendars as xc
    cal = xc.get_calendar("XNYS")
    sessions = [pd.Timestamp(s.date()) for s in cal.sessions_in_range("2026-06-01", "2026-11-30")]
    out = paths.HOLDOUT_CHAINS
    have = pd.read_parquet(out) if out.exists() else pd.DataFrame()
    done = set(have["date"].unique()) if len(have) else set()
    v = Vendor()

    if PARITY_DAY not in done:                         # one in-sample day, to prove the holdout request matches the sample
        rows = [c for c in (v.chain(PARITY_DAY, e) for e in expiries_for(PARITY_DAY, sessions)) if c is not None]
        if not rows:
            print("vendor returned nothing for the parity day; requests left:", v.remaining)
            return
        new = pd.concat(rows, ignore_index=True)
        old = pd.read_parquet(paths.CHAINS / "chains_SPX.parquet")
        old = old[(old["date"] == PARITY_DAY) & (old["dte"].between(1, 8))]
        m = old.merge(new, on="optionSymbol", suffixes=("_old", "_new"))
        same = {c: bool((m[c + "_old"].fillna(-1) == m[c + "_new"].fillna(-1)).all()) for c in ("mid", "openInterest", "underlyingPrice", "strike", "dte")}
        print(f"parity {PARITY_DAY}: saved {len(old)} rows, new {len(new)} rows, matched {len(m)}; identical columns: {same}")
        pd.DataFrame([dict(day=PARITY_DAY, saved=len(old), new=len(new), matched=len(m), **same)]).to_csv(DATA / "holdout_parity.csv", index=False)
        have = pd.concat([have, new], ignore_index=True)
        have.to_parquet(out, index=False)
        done.add(PARITY_DAY)

    todo = [s.strftime("%Y-%m-%d") for s in sessions if HOLD_A <= s.strftime("%Y-%m-%d") <= HOLD_B and s.strftime("%Y-%m-%d") not in done]
    got = 0
    for day in todo:                                   # strictly in date order: the holdout is an unbroken stretch from the start
        exps = expiries_for(day, sessions)
        if v.remaining is not None and v.remaining - RESERVE < len(exps):
            break
        rows = [v.chain(day, e) for e in exps]
        if any(r is None for r in rows) and v.remaining == 0:
            break
        rows = [r for r in rows if r is not None]
        if rows:
            have = pd.concat([have] + rows, ignore_index=True)
            have.to_parquet(out, index=False)
        got += 1
        time.sleep(0.08)
    hold = sorted(d for d in have["date"].unique() if d >= HOLD_A)
    print(f"holdout quotes: {got} new sessions this run; {len(hold)} of {len([s for s in sessions if HOLD_A <= s.strftime('%Y-%m-%d') <= HOLD_B])} "
          f"sessions saved ({hold[0] if hold else '-'} to {hold[-1] if hold else '-'}); requests used {v.used}, left today {v.remaining}")


if __name__ == "__main__":
    qqq()
    tbill()
    if "--no-chains" not in sys.argv:
        chains()
