# Does option gamma exposure add anything to a trend rule?

Code and paper for *Does option gamma exposure add anything to a trend rule? A daily test on QQQ, 2018 to 2026*
by Taeheon Cha (working paper, November 2026).

The paper is in [`paper/Gamma_AC_Journal_Paper.pdf`](paper/Gamma_AC_Journal_Paper.pdf).

## What the paper does

It tests a daily trading rule on the Nasdaq-100 fund QQQ. The rule combines two votes: the sign of a gamma exposure
reading built from S&P 500 index options with 1 to 8 days to expiry, and the sign of QQQ's 20-day return. It is long,
short or in cash from one close to the next. The question is whether the option reading adds anything to the trend.

## What it finds

Sample: 2,118 trading days, January 2018 to June 2026. Sharpe ratios are annualized and after costs of 2 basis points
per unit traded.

| | Sharpe ratio | Growth a year | Maximum drawdown |
|---|---:|---:|---:|
| The rule (Gamma A+C) | 0.88 | 13.7% | 22.9% |
| Trend vote alone, long or cash | 1.02 | 16.2% | 20.2% |
| Buy and hold QQQ | 0.74 | 19.4% | 35.6% |
| Trend position only after a day against the trend (no option data) | 0.70 | 10.4% | 17.2% |

- No difference in Sharpe ratio between the rule and any benchmark is statistically significant (Ledoit and Wolf test).
- The option vote selects days better than random filters with the same day counts (p = 0.004), entirely on the short side.
- A rule with no option data reaches most of the same result.
- With dividends, Treasury bill interest, a borrow fee and excess returns, the rule's Sharpe ratio is 0.73 and no ranking changes.
- The deflated Sharpe ratio is 0.932 with twelve documented trials, below the 0.95 threshold.
- **Holdout, in progress.** The plan was fixed in [`HOLDOUT_PREREGISTRATION.md`](HOLDOUT_PREREGISTRATION.md) before any
  post-sample data were downloaded: 105 sessions, 2026-06-15 to 2026-11-11. The first 17 are in: the rule lost 5.3%
  while QQQ gained 0.3%. Seventeen days cannot confirm or reject anything.

The paper's conclusion is that the rule remains a hypothesis and that the evidence does not show the option signal
adds to a trend rule.

## What is in this repository

| Path | Contents |
|---|---|
| `paper/` | The paper, as PDF and Word |
| `paper_journal.md` | The paper's source text. Numbers are placeholders filled in by the scripts |
| `figs/` | The paper's figures |
| `results/` | Every number and table the paper prints, as written by the scripts |
| `paper_numbers.py` | The reading, the rule and the main results (Sections 3 to 6) |
| `journal_numbers.py` | Concentration, random filters, Sharpe ratio differences, return accounting, holdout (Section 5) |
| `fetch_inputs.py` | Downloads QQQ prices, the Treasury bill rate and the holdout quotes |
| `fetch_sample_quotes.py` | Downloads the main sample's option quotes (Appendix A) |
| `make_journal_figs.py`, `make_figs.py` | The figures |
| `build_journal.py`, `build.py` | Fill the numbers into the text and write the Word file |
| `dsr.py` | The deflated Sharpe ratio |
| `paths.py` | Every file location, in one place |
| `HOLDOUT_PREREGISTRATION.md` | The holdout plan |
| `declarations.json` | The author's declarations as printed in the paper |

## Data

**The option quotes are not here, and neither is any day-by-day series computed from them.** They come from
[Market Data](https://www.marketdata.app) under an individual subscription, and its terms do not allow the quotes, or
data files built from them, to be redistributed. The figures and summary statistics in `figs/` and `results/` are the
author's calculations from Market Data quotes. Source: Market Data (https://www.marketdata.app).

To run the code you need your own subscription. `fetch_sample_quotes.py` downloads the sample with the requests listed
in Appendix A of the paper. QQQ prices (FinanceDataReader) and the 3-month Treasury bill rate (FRED series DTB3) are
public and are downloaded by `fetch_inputs.py`.

## Reproducing the paper

Python 3.11 or later, [pandoc](https://pandoc.org) 3.x, and the packages in `requirements.txt`.

```
pip install -r requirements.txt
export MARKETDATA_TOKEN=...            # your own access key
export GAMMA_CHAINS_DIR=/where/the/quotes/go

python3 fetch_sample_quotes.py         # the main sample's option quotes (needs history access; about 15,000 requests)
python3 fetch_inputs.py                # QQQ, Treasury bills, holdout quotes (resumable; see the note below)
python3 paper_numbers.py               # results/numbers.json
python3 journal_numbers.py             # results/numbers_journal.json, results/tables_journal.json
python3 make_journal_figs.py           # figs/
python3 build_journal.py               # paper/Gamma_AC_Journal_Paper.docx
```

Everything computed day by day is written to `work/`, which git ignores. The PDF is exported from the Word file.

Notes:

- Results depend on the vendor's data and on QQQ prices as downloaded on the day. The scripts print the numbers they
  compute; `results/` holds the ones in the paper.
- `fetch_inputs.py` downloads the holdout quotes in date order and stops when the day's request allowance is used up.
  Run it again after the allowance resets. The holdout is always the unbroken stretch from 2026-06-15.
- `journal_numbers.py` checks that the wording of Section 5.6 still matches the holdout numbers and stops if it does not.
- Random draws are seeded, so the tests of Section 5.2 give the same numbers on every run.

## License and citation

The code is released under the MIT License (`LICENSE`). The paper and its figures are © 2026 Taeheon Cha, all rights
reserved (`NOTICE.md`). To cite the paper or the code, see `CITATION.cff`.

The analysis code and figures were written with the assistance of Claude, an AI model made by Anthropic, which was also
used to draft and edit the text. The author takes responsibility for the content.

This is research on historical data. Nothing here is a recommendation to buy or sell anything.
