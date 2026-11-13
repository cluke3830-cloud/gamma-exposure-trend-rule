# Holdout test for Gamma A+C: dates and rules fixed before any result is seen

Written 2026-11-12, before any option quote dated after 2026-06-12 was downloaded and before any
holdout return was computed. This file is committed to git on its own so that the timestamp of the
commit precedes the data.

## What is frozen

- **The rule.** Equations (1) to (16) of the paper, exactly as coded in `paper_numbers.py` at commit
  `bfc25b2`: options with 1 to 8 days to expiry, open interest above zero, mid above zero,
  |ln(K/S)| < 0.20; interest rate 0.04 and dividend yield 0.014; 50 Newton steps from 0.25, clipped to
  [0.001, 5]; reading = call dollar gamma minus put dollar gamma; the reading is lagged one quote day;
  option vote with the day's move after a positive reading and against it after a negative one; trend
  vote = sign of QQQ's 20-day log return; position = average of the two votes; cost 2 basis points per
  unit traded.
- **No change** to any parameter, filter, sign or cost will be made for the holdout, whatever it shows.

## The window

- **Quote days to download:** 2026-06-15 to 2026-11-11, the last complete trading day before today.
  Same vendor (marketdata.app), same requests as Appendix A of the paper.
- **Holdout return days:** every NYSE session from 2026-06-15 to 2026-11-11 inclusive (105 sessions).
  The position carried into 2026-06-15 is the one decided on 2026-06-12, inside the original sample.
- **QQQ closes:** FinanceDataReader, the same source as the sample.
- Days with no usable quotes are skipped, as in the sample.
- If the vendor will not supply the whole window, the holdout is the longest unbroken stretch that
  starts on 2026-06-15, and the paper says how far it reached. The start date is not moved.

## What will be reported, whatever the outcome

1. Total return after costs, and the annualized Sharpe ratio before and after costs.
2. The same for buying and holding QQQ and for the trend vote traded long or in cash, on the same days.
3. The number of days long, short and in cash.

## How it will be read

With about 105 days the standard error of an annualized Sharpe ratio is about sqrt(252/105), which is
1.5. A holdout this short cannot confirm or reject the rule by itself. It is reported as a first
out-of-sample observation, not as a test with power.

## What the author already knows about this period

The author is not blind to all of it. A version of the rule ran on a simulated account in July 2026,
with a different configuration (same-day reading, leverage above one), and was stopped on 2026-07-14
after a loss. The rule in its present form has run on a simulated account since early November 2026.
No account results are used in the paper. The window above is set by the data, first day after the
sample and last complete day before today, and not by any of those results.
