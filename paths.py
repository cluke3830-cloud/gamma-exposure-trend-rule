"""Every location the scripts use, in one place.

Published with the repository
    figs/       the paper's figures
    results/    summary numbers and tables that the paper prints
    paper/      the paper itself

Never published (git-ignored)
    work/       daily series and everything else computed day by day from the option quotes
    the option quotes themselves, wherever they are kept

To run the pipeline you need your own copy of the option quotes (README, "Data"). Tell the scripts where they are with
the environment variable GAMMA_CHAINS_DIR, or with a file `local_config.json` next to this one:

    {"chains_dir": "/folder/holding/chains_SPX.parquet and chains_SPX_pre2022.parquet",
     "env_file": "/file/with/a/line/MARKETDATA_TOKEN=..."}

The access key can also be given in the environment variable MARKETDATA_TOKEN. It is only needed by fetch_inputs.py.

Three optional entries let the author compare a run with earlier, separately produced outputs. Without them those
comparisons are skipped and nothing else changes:
    "certified_reading"   a parquet of the daily reading from an earlier run
    "october_dir"         a folder with an earlier daily frame and its headline numbers
    "received_draft"      the Word draft whose equations build_journal.py checks the rebuilt paper against
"""
import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent
_cfg_file = REPO / "local_config.json"
_cfg = json.loads(_cfg_file.read_text()) if _cfg_file.exists() else {}

WORK = REPO / "work"
RESULTS = REPO / "results"
FIGS = REPO / "figs"
PAPER = REPO / "paper"
BUILD = WORK / "build"
for _d in (WORK, RESULTS, FIGS, PAPER, BUILD):
    _d.mkdir(exist_ok=True)

CHAINS = Path(os.environ.get("GAMMA_CHAINS_DIR") or _cfg.get("chains_dir") or REPO / "vendor_data")
ENV_FILE = Path(_cfg["env_file"]) if _cfg.get("env_file") else REPO / ".env"


def _optional(key):
    p = _cfg.get(key)
    return Path(p) if p and Path(p).exists() else None


CERTIFIED = _optional("certified_reading")
OCTOBER = _optional("october_dir")
RECEIVED = _optional("received_draft")

QQQ = WORK / "qqq_daily.parquet"                    # written by fetch_inputs.py
TBILL = WORK / "dtb3.csv"                           # written by fetch_inputs.py
HOLDOUT_CHAINS = WORK / "holdout_chains_SPX.parquet"  # written by fetch_inputs.py
READING = WORK / "reading.csv"                      # the daily reading, written by paper_numbers.py


def token():
    """The data vendor's access key. Never printed."""
    if os.environ.get("MARKETDATA_TOKEN"):
        return os.environ["MARKETDATA_TOKEN"].strip()
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if line.startswith("MARKETDATA_TOKEN="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("No access key: set MARKETDATA_TOKEN or point local_config.json at a file that holds it.")
