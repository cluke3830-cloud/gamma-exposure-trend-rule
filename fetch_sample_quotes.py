#!/usr/bin/env python3
"""Download the main sample's option quotes, as described in Appendix A of the paper.

    python3 fetch_sample_quotes.py --dry-run     # list what would be requested for the first few days, no requests made
    python3 fetch_sample_quotes.py               # the whole sample
    python3 fetch_sample_quotes.py --append      # continue an interrupted download (an existing file is otherwise left alone)

For each weekday from 2018-01-02 to 2026-06-12 it
  1. asks the vendor which S&P 500 (SPX) expiry dates were listed that day,
  2. keeps the expiries from 0 to 8 calendar days ahead,
  3. downloads the option chain for each, with the 100 strikes nearest the index level.
The result is two files in the folder paths.CHAINS, the ones paper_numbers.py reads:
    chains_SPX_pre2022.parquet    2018-01-02 to 2022-04-29
    chains_SPX.parquet            2022-05-02 to 2026-06-12
One row per contract per day, with the fields of Table 2.

You need your own subscription to Market Data (https://www.marketdata.app) with access to history before the last
year, and roughly 15,000 requests. The quotes may not be redistributed, so this folder is never part of the repository.

This is a tidied version of the script that made the original download in June 2026. Since tidying it has been run
only in --dry-run mode. The request code it shares with fetch_inputs.py is the code that downloaded the holdout quotes.
"""
import sys
import time

import pandas as pd

import paths
from fetch_inputs import B, KEEP, Vendor  # noqa: F401  (KEEP documents the fields that are saved)

DTE_MAX = 8
FILES = [("chains_SPX_pre2022.parquet", "2018-01-02", "2022-04-29"), ("chains_SPX.parquet", "2022-05-02", "2026-06-12")]
FLUSH_EVERY = 40          # days between writes to disk


def expiries(v, day):
    b = v.get(f"{B}/expirations/SPX/?date={day}")
    if not b or b.get("s") != "ok":
        return []
    d0 = pd.Timestamp(day)
    return [e for e in b.get("expirations", []) if 0 <= (pd.Timestamp(e) - d0).days <= DTE_MAX]


def main():
    dry = "--dry-run" in sys.argv
    paths.CHAINS.mkdir(parents=True, exist_ok=True)
    v = None if dry else Vendor()
    for name, start, end in FILES:
        out = paths.CHAINS / name
        days = [d.strftime("%Y-%m-%d") for d in pd.bdate_range(start, end)]
        done = set(pd.read_parquet(out, columns=["date"])["date"].unique()) if out.exists() else set()
        todo = [d for d in days if d not in done]
        print(f"{name}: {len(done):,} days saved, {len(todo):,} to download ({start} to {end})", flush=True)
        if out.exists() and not dry and "--append" not in sys.argv:
            print(f"   {name} already exists and is left untouched. Use --append to add the missing days to it.")
            continue
        if dry:
            for d in todo[:3]:
                print(f"   would request {B}/expirations/SPX/?date={d}, then one chain per expiry within {DTE_MAX} days (strikeLimit=100)")
            continue
        buf = []
        for i, day in enumerate(todo):
            for e in expiries(v, day):
                c = v.chain(day, e)
                if c is not None:
                    buf.append(c)
                time.sleep(0.08)
            if v.remaining == 0:
                print("   the day's requests are used up; run again after the reset", flush=True)
                break
            if buf and (len(buf) >= FLUSH_EVERY * 6 or i == len(todo) - 1):
                new = pd.concat(buf, ignore_index=True)
                if out.exists():
                    new = pd.concat([pd.read_parquet(out), new], ignore_index=True)
                new.to_parquet(out, index=False)
                buf = []
            if (i + 1) % 25 == 0:
                print(f"   {i + 1:,} of {len(todo):,} ({day})", flush=True)
        if buf:
            new = pd.concat(buf, ignore_index=True)
            if out.exists():
                new = pd.concat([pd.read_parquet(out), new], ignore_index=True)
            new.to_parquet(out, index=False)


if __name__ == "__main__":
    main()
