---
title: "Does option gamma exposure add anything to a trend rule? A daily test on QQQ, 2018 to 2026"
author: "Taeheon Cha"
date: "Working paper, November 2026"
abstract: |
  Practitioners use gamma exposure measures built from index option open interest as indicators of dealer hedging flows. I test whether the sign of such a measure adds anything to a simple trend rule. Each day I compute the dollar gamma of calls minus that of puts from end-of-day quotes on S&P 500 index options with 1 to 8 days to expiry (1.77 million contract-days after filtering), and combine its sign with the day's return and the 20-day return of the Nasdaq-100 fund QQQ in a rule that is long, short or in cash until the next close. Over {{n_days}} trading days from January 2018 to June 2026 the rule earns an annualized Sharpe ratio of {{net_sharpe}} after costs, against {{hold_sharpe}} for buying and holding QQQ and {{trend_sharpe}} for the trend signal traded long or in cash. Neither difference is statistically significant. The option signal never sets the direction of a position. It selects the days on which the trend position is held, and it selects them better than random filters with the same day counts ({{rf_net_iid_pt}}), with all of the selection on the short side. But a rule that uses no option data and takes the trend position only after a day that moved against the trend earns {{fade_net}}, and the difference from the full rule is not significant either. With dividends, interest on cash, a borrow fee and returns measured in excess of Treasury bills, the rule's Sharpe ratio is {{acct_ac_sh1}} and no ranking changes. The deflated Sharpe ratio is {{dsr_12}} with twelve documented trials, below the 0.95 threshold, and in the first {{ho_days}} days of a preregistered {{ho_planned}}-day holdout the rule lost {{ho_ac_ret_abs}}. I conclude that the rule remains a hypothesis awaiting out-of-sample evidence.

  **Keywords:** gamma exposure, dealer hedging, trend following, backtest overfitting, deflated Sharpe ratio, QQQ
---

# 1 Introduction

Option dealers who hedge their books trade the underlying index, and the amount they trade depends on the gamma of the options they hold. SqueezeMetrics (2017) proposed a daily gamma exposure (GEX) index that estimates this hedging demand for the S&P 500 from public open interest, and argued that dealer hedging dampens market moves when the measure is positive and amplifies them when it is negative. Academic work has since tied hedging demand to return patterns within the day. Baltussen, Da, Lammers and Martens (2021) find that the return in the last 30 minutes of trading is predicted by the return earlier in the day, that for the S&P 500 this intraday momentum appears when their measure of net gamma exposure is negative, and that it reverts over the following days.

This paper asks a narrower question. Does the sign of a simple gamma exposure reading, of the kind that can be computed from end-of-day data, improve a daily trading rule once the rule is compared with plain trend following?

I compute a daily reading from 1,766,188 end-of-day quotes on S&P 500 index options with 1 to 8 days to expiry, on 2,119 days between January 2018 and June 2026. The reading is the dollar gamma of calls minus that of puts. Its sign is combined with two facts about the Nasdaq-100 fund QQQ, the day's return and the return over the past 20 trading days, in a rule that is long, short or in cash from one close to the next. I call the rule Gamma A+C. The letters come from my research notebook, where three candidate signals were labeled A, B and C. The rule keeps A, the option vote, and C, the trend vote. The test covers 2,118 trading days and includes the market declines of late 2018, 2020 and 2022.

The paper has five main findings. First, after costs the rule has a higher Sharpe ratio than buying and holding QQQ ({{net_sharpe}} against {{hold_sharpe}}) and a smaller maximum drawdown ({{net_dd_abs}} against {{hold_dd_abs}}), but lower growth ({{net_cagr}} a year against {{hold_cagr}}), and the difference in Sharpe ratios is not statistically significant (p = {{lw_qq_p5}}). Second, the option vote never sets the direction of a position. Section 4.3 shows that the position always has the sign of the 20-day return and that the option vote only decides whether the position is taken, so the rule is a filtered trend rule and should be judged against unfiltered ones. That comparison depends on the benchmark. The trend vote traded long or short every day earns a Sharpe ratio of {{c_only_sharpe}}, below the combined rule, while the trend vote traded long or in cash earns {{trend_sharpe}}, above it, and neither difference is significant. Third, the option vote does select days better than chance. Random filters that hold the trend position on the same number of days earn a mean Sharpe ratio of {{rf_net_iid_mean}} after costs, far below the rule's {{net_sharpe}} ({{rf_net_iid_pt}}). All of that selection is on the short side: the rule's long positions earn about the unconditional mean return, and its short positions fall on days that differ sharply from the other trend-down days. Fourth, the option reading may not be what does the selecting. A rule that ignores the option data and takes the trend position only after a day that moved against the trend earns {{fade_net}}, and the {{lw_fade_diff_abs}} that the reading adds is not significant (p = {{lw_fade_p5}}). Fifth, the result is fragile in the usual ways. Executing one day late cuts the Sharpe ratio before costs from {{gross_sharpe}} to {{lag2_sharpe}}, one month supplies {{conc_march_share}} of the total return, the deflated Sharpe ratio of Bailey and López de Prado (2014) is {{dsr_12}} when the twelve documented trials are counted, below the 0.95 threshold, and the first {{ho_days}} days of a preregistered holdout were a loss.

The direction in which the option vote is used needs a caveat of its own. Read literally, the white paper's argument implies betting against a move after a positive reading. That version lost money in my tests, and the rule studied here uses the opposite direction. I therefore treat the direction as a choice made in sample. The sign flip is also a trial that the count of twelve in Section 6 does not include, which is one reason that count is a lower bound.

The contribution is a fully specified and reproducible test of a gamma exposure signal that can be built from end-of-day quotes, a decomposition showing that in this rule the signal can act only as a filter on trend, benchmarks that separate the option reading from the other inputs of the filter, and a complete account of the multiple-testing arithmetic, including the places where the rule fails. On this evidence the rule remains a hypothesis. Section 5.6 reports the start of a preregistered holdout and Section 7 lists what is still missing.

Section 2 reviews related work. Section 3 describes the data and Section 4 the method. Section 5 reports the results, Section 6 the multiple-testing analysis and Section 7 the limitations. Section 8 concludes.

# 2 Related work

SqueezeMetrics (2017) builds a daily gamma exposure index for the S&P 500 from open interest, on the assumption that dealers are long calls and short puts. The white paper's evidence concerns the size of market moves: it reports that the S&P 500's typical one-day move was 0.55% after the highest readings and 0.85% after the next-highest group. It does not test whether a day's move continues or reverses, which is what a directional trading rule depends on.

The academic evidence is mostly intraday. Gao, Han, Li and Zhou (2018) show that the first half-hour return of the S&P 500 ETF predicts its last half-hour return. Baltussen, Da, Lammers and Martens (2021) extend the pattern to more than 60 futures between 1974 and 2020, with the return in the last 30 minutes predicted by the return over the rest of the day, and link it to gamma hedging by option market makers and leveraged ETFs. For the S&P 500 they find intraday momentum when their proxy for net gamma exposure is negative, stronger as it becomes more negative, and they find that the effect reverts over the following days. Barbon and Buraschi (2020) report a similar pattern for individual stocks, with negative aggregate gamma imbalance associated with intraday momentum and positive imbalance with reversal, more strongly in the least liquid names. Dim, Eraker and Vilkov (2024) study options that expire on the day they are traded and find no evidence that their open-interest gamma propagates or raises index volatility.

The rule tested here differs from that literature in horizon and in construction. It trades from one close to the next, while the academic evidence concerns returns within the day, and it uses the sign of a raw open-interest measure, while Baltussen et al. (2021) and Barbon and Buraschi (2020) build proxies for the dealers' net position. One leg of the rule can be read in their terms. After a put-heavy (negative) reading the option vote bets against the day's move, which is consistent with a next-day reversal of hedging-driven momentum. The other leg, continuation after a call-heavy reading, has no counterpart in their results.

The second input to the rule is a 20-day trend filter. Moskowitz, Ooi and Pedersen (2012) document time series momentum in 58 futures and forward contracts using the past 12 months of returns. The 20-day window used here is much shorter. It is a setting inherited from my code, I did not test other lengths, and doing so would add to the trial count.

Because the rule was selected after several variants had been tried, its Sharpe ratio is biased upward. Bailey, Borwein, López de Prado and Zhu (2014) derive the expected maximum Sharpe ratio among unskilled trials, and Bailey and López de Prado (2014) use it to define the deflated Sharpe ratio applied in Section 6. Harvey, Liu and Zhu (2016) make the same argument for factor research and conclude that a new factor should clear a t-statistic of 3.0. For comparing two Sharpe ratios measured on the same days, the appropriate test is that of Ledoit and Wolf (2008), which allows for fat tails and serial correlation. Standard errors of mean returns in this paper follow Newey and West (1987).

# 3 Data

## 3.1 Sources

The study uses two datasets (Table [@tab:t1]): end-of-day quotes on S&P 500 index options, from which the reading is computed, and daily prices of QQQ, the instrument that is traded. The signal therefore comes from one index and the position is taken in another. The two indexes share many large constituents and usually move together, but the mismatch is a design choice that Section 7 returns to.

|  | **Option quotes** | **QQQ prices** |
|:------------|:-----------------------------|:-----------------------------|
| What it is | For each day, every listed S&P 500 index option that expires within 8 days: its strike, expiry, bid, ask and open interest, and the index level | QQQ's opening and closing price each trading day |
| Source | Market Data (<https://www.marketdata.app>), a commercial data service, through its API | The open-source Python library FinanceDataReader |
| Period downloaded | 2018-01-02 to 2026-06-12 | {{qqq_a}} to {{qqq_b}} |
| Size | 2,338,267 quotes on 2,121 days, after removing duplicates | {{qqq_rows}} days |
| Used for | The option reading behind Vote A | Today's move, the 20-day trend, and every profit and loss |

: **Table [#tab:t1].** The two datasets.

## 3.2 Option quotes

Option quotes come from Market Data (<https://www.marketdata.app>), a commercial data service, through its API. For each weekday from 2018-01-02 to 2026-06-12 I requested the list of S&P 500 (SPX) expiry dates listed on that day, kept those from 0 to 8 calendar days ahead, and downloaded the option chain for each with the 100 strikes nearest the index level. Appendix A gives the requests. The download returned 2,353,021 rows. Removing 14,754 exact duplicates of the same contract on the same day leaves 2,338,267 rows on 2,121 days. Of the 2,204 weekdays in the period, 81 were market holidays, and on 2 trading days (2024-10-09 and 2025-12-12) the service returned no data.

Table [@tab:t2] lists the fields that are saved. The service does not supply delta or gamma for past dates, so gamma is computed from the quotes (Section 4.2). Two contract roots appear in the data. `SPXW` options expire at the close on their expiry day, and one is now listed for every weekday. `SPX` options are the older monthly contracts, which stop trading the day before expiry and settle at the next morning's opening prices.

| **Field** | **What it holds** | **Example** |
|:---------------|:------------------------------------|:------------------|
| `date` | The day of the quote | 2026-01-27 |
| `optionSymbol` | The contract's official code: root, expiry date, C for call or P for put, and strike | SPXW260130C06950000 |
| `expiration` | The expiry date | 2026-01-30 |
| `side` | call or put | call |
| `strike` | Strike price, in index points | 6,950 |
| `dte` | Days to expiry: calendar days from the quote day to the expiry date | 3 |
| `bid`, `ask` | The best price a buyer was offering and the best price a seller was asking, at the end of the day | 56.60, 56.80 |
| `mid` | The average of bid and ask | 56.70 |
| `openInterest` | Number of contracts in existence | 18,166 |
| `underlyingPrice` | The S&P 500 index level on that row | 6978.60 |
| `last`, `volume` | Last traded price and number traded that day. Saved but not used |  |

: **Table [#tab:t2].** Fields saved for each option contract. The example is one real contract, used again in Appendix B. Source: Market Data (<https://www.marketdata.app>).

## 3.3 Filters

Four filters are applied in the order shown in Table [@tab:t3].

| **Step** | **Rule** | **Why** | **Rows removed** | **Rows left** |
|:-----|:-----------------|-----------------------------|----------|---------:|
| 0 | All quotes |  |  | 2,338,267 |
| 1 | Days to expiry from 1 to 8 | Options expiring the same day have almost no time left, and the formula for gamma divides by time | 354,499 | 1,983,768 |
| 2 | Open interest above zero | If no contracts exist, no one has anything to hedge | 211,260 | 1,772,508 |
| 3 | Mid price above zero | A price of zero cannot be turned into a volatility | 180 | 1,772,328 |
| 4 | Strike within about 20% of the index level | Options far from the index level have almost no gamma. Rows with no index level also fail this test | 6,140 | 1,766,188 |

: **Table [#tab:t3].** Filters applied to the option quotes. Step 4 is stated exactly in Equation [@eq:e1].

Of the 6,140 rows removed at step 4, 5,117 were too far from the index level and 1,023 had a missing or zero index level. Nearly all of the second group fall on 2020-07-10 and 2020-07-31, when the service supplied no index level, so those two days have quotes but no reading. The 1,766,188 rows that remain are 888,945 calls and 877,243 puts on 2,119 days. Of these, 1,655,263 are `SPXW` contracts and 110,925 are `SPX` contracts.

![**Figure [#fig:f1].** Number of option contracts that pass the filters on each day. Each dot is one day and the line is the median of the previous 21 days. The count roughly doubles in 2022, when options for more weekdays were listed. Source: author's calculations from Market Data (<https://www.marketdata.app>) quotes.](figs/fig02_coverage.png){width=6.1in}

The composition of the sample changes over time (Figure [@fig:f1]). The reading is built from about 587 contracts a day before 2022 and about 1,087 a day from 2023, because the exchange listed options for more weekdays and a typical day went from 4 expiry dates to 6. The reading before and after 2022 is therefore not built from quite the same set of instruments.

## 3.4 QQQ prices

QQQ prices come from the open-source FinanceDataReader library for Python. I keep the daily opening and closing prices from {{qqq_a}} to {{qqq_b}}, {{qqq_rows}} trading days. The series starts before the test so that the 20-day return can be computed from the first test day, and it runs past the end of the sample so that the holdout of Section 5.6 can be scored. The prices are adjusted for share splits but not for dividends, so QQQ's cash dividends are left out of the main results, for the rule and for buy and hold alike. Section 5.5 adds them back, using the dividend-adjusted closing price from the same library and the 3-month Treasury bill rate (series DTB3 of the Federal Reserve Bank of St. Louis).

## 3.5 Sample

For each trading day $t$ the test needs the reading from the previous quote day and QQQ's prices on day $t$. The first usable day is 2018-01-03, because 2018-01-02 has no earlier reading, and the last is 2026-06-12. QQQ traded on 2,122 days between those dates. The 4 days with no option reading (2020-07-10, 2020-07-31, 2024-10-09 and 2025-12-12) are excluded, which leaves 2,118 trading days, about 8.4 years.

## 3.6 Verification and known weaknesses

I checked the data pipeline in three ways. A separate program recomputed the reading for all 2,119 days from the saved quotes and reproduced the stored series with no difference. Positions recomputed for this paper match the earlier record on all 2,118 days. The headline results were also recomputed and match an earlier run from October 2026.

Four weaknesses remain that these checks cannot remove. The first concerns the timing of open interest. Open interest for a day is published the following morning, so a vendor's figure dated $d$ could be the count at that day's close or the one before. The data point to the second. A contract's open interest cannot change by more than the volume traded in it. On the {{oi_pairs}} contract-days on which open interest changed from one quote day to the next, the change is no larger than the earlier day's volume in {{oi_fit_prev}} of cases and no larger than the later day's volume in only {{oi_fit_same}}, and its correlation with volume is {{oi_corr_prev}} for the earlier day against {{oi_corr_same}} for the later. The figure dated $d$ therefore appears to be the count at the close of the session before. The reading the rule uses on day $t$ is then built from open interest that is two sessions old and quotes that are one session old. This makes the one-day lag (Section 4.2) more conservative than it needs to be. It does not open a route for look-ahead. Second, the bid and ask are the last quotes of the day and may be stale for contracts that rarely trade. Third, the gamma calculation uses an interest rate of 4% and a dividend yield of 1.4% for every day in the sample, although actual rates ranged from near zero to above 5%. Section 4.2 explains why this matters little for options that expire within 8 days. Fourth, the quotes come from one vendor and have not been compared with a second source over the full history.

# 4 Method

## 4.1 The gamma exposure hypothesis

A dealer who has bought or sold an option hedges by trading the index itself, in practice index futures, so that small moves in the index leave the value of the book unchanged. The size of the hedge is the option's delta, and gamma is the rate at which delta changes as the index moves. A book with high gamma has to be re-hedged heavily after each move.

SqueezeMetrics (2017) argues that the sign of dealers' aggregate gamma determines the direction of that re-hedging. If dealers, added together, hold options in a way that makes them buy when the index falls and sell when it rises, their hedging pushes against every move. If they hold the opposite way, they sell into falls and buy into rises, and their hedging makes every move larger. The white paper calls the first case positive gamma exposure and the second negative.

Dealer positions are not public. Open interest gives the number of contracts in existence and says nothing about who holds them. The white paper therefore assumes that every option has a dealer on one side, that the public sells calls and buys puts, so that dealers own calls and have sold puts, and that dealers hedge exactly. Under those assumptions calls count as positive and puts as negative, and the total is one number per day. I call that number the reading. A positive reading is a call-heavy day and a negative reading is a put-heavy day. I adopt the white paper's sign convention without testing the assumptions behind it, which is a limitation (Section 7).

Gamma A+C uses the reading, computed from options with 1 to 8 days to expiry, to decide whether the day's move in QQQ is more likely to continue or to reverse on the next day. After a call-heavy reading the option vote sides with the day's move, and after a put-heavy reading it sides against it. This is the opposite of what the white paper's argument implies, since a positive reading should dampen moves and so favor betting against them. My research notes record that the literal version lost money when it was tested and that the direction was then reversed. The notes suggest a reason, that in very short-dated options the public may now be buying where the white paper assumed it was selling. That explanation has not been tested, and it would not by itself explain a reading that changes sign from day to day. The direction of the option vote is therefore an empirical choice, made on the same data that are used to evaluate it.

## 4.2 The daily reading

Table [@tab:t4] lists the notation. Throughout, $\ln$ is the natural logarithm and $\operatorname{sgn}(a)$ is the sign function, equal to $+ 1$, $- 1$ or $0$ when $a$ is positive, negative or zero.

| **Symbol** | **Name** | **Meaning** | **Unit or value** |
|:-------|:-------------|:-----------------------------------|:--------------|
| $d$ | quote day | A day with option quotes | date |
| $t$ | trading day | A day in the test | date |
| $t^{-}$ | previous day | The trading day in the test just before $t$ | date |
| $c$ | contract | One option on one day: one row of data |  |
| $S$ | index level | The S&P 500 level on that row | index points |
| $K$ | strike | The contract's strike price | index points |
| $\tau$ | time to expiry | Days to expiry divided by 365 | years |
| $m$ | mid price | Average of bid and ask | index points |
| $\mathrm{OI}$ | open interest | Contracts in existence | contracts |
| $\chi$ | call or put flag | $+ 1$ for a call, $- 1$ for a put |  |
| $r_{f}$ | interest rate | Yearly rate used in the formula | 0.04 |
| $q$ | dividend yield | Yearly dividend rate of the index | 0.014 |
| $\sigma$ | volatility | How much the index is expected to move, per year | e.g. 0.16 = 16% |
| $\widehat{\sigma}$ | implied volatility | The $\sigma$ that makes the formula match the market price |  |
| $\Phi$, $\varphi$ | normal curve | $\Phi(z)$ is the share of a standard bell curve to the left of $z$. $\varphi(z)$ is the height of that curve at $z$ |  |
| $V$ | model value | The option's value given by the formula | index points |
| $\nu$ | vega | How much $V$ changes when $\sigma$ changes |  |
| $\Gamma$ | gamma | Change in delta per one-point move in the index | per point |
| $G$ | dollar gamma | A contract's gamma scaled by open interest and index level | reading units |
| $\mathrm{GEX}_{d}$ | the reading | Call dollar gamma minus put dollar gamma on day $d$ | reading units |
| $g_{t}$ | lagged reading | The reading from the quote day before $t$ | reading units |
| $P_{t}$ | QQQ price | QQQ's closing price on day $t$ | US dollars |
| $r_{t}$ | today's return | QQQ's log return on day $t$ |  |
| $M_{t}$ | 20-day return | QQQ's log return over the last 20 trading days |  |
| $A_{t}$, $C_{t}$ | the votes | $+ 1$ for up, $- 1$ for down |  |
| $h_{t}$ | position | $+ 1$ long, $0$ cash, $- 1$ short | units of QQQ |
| $\kappa$ | cost rate | Trading cost per unit traded | 0.0002 |
| $x_{t}$, $R_{t}$ | net return | The rule's return on day $t$ after costs |  |

: **Table [#tab:t4].** Notation used in Section 4.

On quote day $d$, contract $c$ is used if all four of the following conditions hold:

$$1 \leq \mathrm{dte}_{c} \leq 8,\quad\quad\mathrm{OI}_{c} > 0,\quad\quad m_{c} > 0,\quad\quad\left| \ln\left( \frac{K_{c}}{S_{c}} \right) \right| < 0.20\EQ{e1}$$

where $\mathrm{dte}_{c}$ is the contract's days to expiry. The last condition keeps strikes within about 20% of the index level. It rarely removes anything, because the download returns only the 100 strikes nearest the index. Time to expiry in years is $\tau_{c} = \mathrm{dte}_{c}/365$.

Each contract's implied volatility is found by inverting the formula of Black and Scholes (1973) and Merton (1973) with a continuous dividend yield. The two auxiliary terms are

$$d_{1} = \frac{\ln(S/K) + \left( r_{f} - q + \frac{1}{2}\sigma^{2} \right)\tau}{\sigma\sqrt{\tau}},\quad\quad d_{2} = d_{1} - \sigma\sqrt{\tau}\EQ{e2}$$

and the model value is

$$V(\sigma) = \chi\left\lbrack \, S\, e^{- q\tau}\,\Phi(\chi\, d_{1})\; - \; K\, e^{- r_{f}\tau}\,\Phi(\chi\, d_{2})\, \right\rbrack\EQ{e3}$$

where $\chi$ is $+ 1$ for a call and $- 1$ for a put, $r_{f}$ is 0.04 and $q$ is 0.014. For an option with 3 days to expiry the discount factors $e^{- q\tau}$ and $e^{- r_{f}\tau}$ are 0.999885 and 0.999671, which is why holding the two rates fixed over the whole sample does little harm.

The implied volatility $\widehat{\sigma}$ is the value of $\sigma$ at which the model value equals the mid quote $m$. It has no closed form and is found by Newton's method, starting from 0.25 and using the option's vega,

$$\nu(\sigma) = S\, e^{- q\tau}\,\varphi(d_{1})\,\sqrt{\tau}\EQ{e4}$$

in 50 iterations of

$$\sigma_{k + 1} = \operatorname{clip}\left( \sigma_{k} - \frac{V(\sigma_{k}) - m}{\max\{\nu(\sigma_{k}),\; 10^{- 8}\}},\;\; 0.001,\;\; 5 \right),\quad\quad\sigma_{0} = 0.25,\quad k = 0,1,\ldots,49\EQ{e5}$$

with $\widehat{\sigma} = \sigma_{50}$. The bounds keep the iterate between 0.1% and 500%, and the floor on vega prevents division by zero.

For 178,566 rows, 10.1% of the total, no volatility reproduces the quote. These are options deep in the money whose mid quote is slightly below the lowest value the formula can produce, and the iteration ends at the lower bound of 0.001. Such options have almost no gamma. Together they carry 6.9 × 10^−7^ of the total dollar gamma, so their treatment does not affect the reading. Another 122 rows end at the upper bound of 5.

Given $\widehat{\sigma}$, the option's gamma is

$$\Gamma = \frac{e^{- q\tau}\,\varphi(d_{1})}{S\,\widehat{\sigma}\,\sqrt{\tau}}\EQ{e6}$$

where $d_{1}$ is computed from Equation [@eq:e2] with $\sigma = \widehat{\sigma}$. Gamma is the same for a call and a put with the same strike and expiry, it is largest when the strike is near the index level, and it grows as expiry approaches. Figure [@fig:f2] plots Equation [@eq:e6] across strikes and expiries. Per contract, gamma is concentrated in options near the index level with a day or two left, which is the motivation for the window of 1 to 8 days.

![**Figure [#fig:f2].** Gamma per contract by strike and days to expiry. For each strike, shown as a percentage of the index level, and each number of days to expiry from 1 to 8, the height is the change in delta for a 1% move in the index, from Equation [@eq:e6] at a fixed volatility of 20% with the index at 6,800.](figs/fig04_gamma_surface.png){width=5.7in}

Each contract's gamma is then scaled by open interest and by the index level,

$$G_{c} = \Gamma_{c} \times \mathrm{OI}_{c} \times S_{c}^{\, 2} \times 0.01\EQ{e7}$$

so that $G_{c}$ measures how much index, in index points, the holders of contract $c$ would have to trade to stay hedged after a 1% move. One S&P 500 option contract covers 100 times the index. The code leaves that multiplier out, which changes the size of the number and not its sign, and only the sign is used. The reading for the day is the dollar gamma of calls minus that of puts:

$$\mathrm{GEX}_{d} = \sum_{\text{calls }c\text{ on day }d}^{}G_{c}\;\; - \sum_{\text{puts }c\text{ on day }d}^{}G_{c}\EQ{e8}$$

The rule uses the reading with a lag,

$$g_{t} = \mathrm{GEX}_{d^{-}(t)}\EQ{e9}$$

where $d^{-}(t)$ is the last day with a reading before trading day $t$. Usually that is the previous trading day. On the day after one of the four days with no reading it is two days back. The lag is part of the rule as specified. It was introduced because open interest for a day is published the next morning, so that a same-day reading might have used a number not yet known at the close. Section 3.6 suggests the vendor's figure is already a session old, in which case the lag is stricter than necessary.

Figure [@fig:f3] shows the reading over the sample. It was call-heavy on 62.0% of days and put-heavy on 38.0%. Put-heavy days are more common in falling markets. They were 63% of days in 2022 and 26% in 2019. Appendix B works through the whole calculation for one contract and one day.

![**Figure [#fig:f3].** (a) The reading on each day. The few largest values are cut off at the edge of the chart. (b) The share of trading days in each year on which the previous day's reading was put-heavy. Source: author's calculations from Market Data (<https://www.marketdata.app>) quotes.](figs/fig06_reading_history.png){width=5.7in}

## 4.3 The trading rule

The rule uses the signs of two QQQ returns computed from closing prices $P_{t}$, the day's log return and the log return over 20 trading days:

$$r_{t} = \ln\left( \frac{P_{t}}{P_{t - 1}} \right),\quad\quad M_{t} = \ln\left( \frac{P_{t}}{P_{t - 20}} \right) = \sum_{k = 0}^{19}r_{t - k}\EQ{e10}$$

The option vote and the trend vote are

$$A_{t} = \begin{cases}
 + \operatorname{sgn}(r_{t}) & \text{if }g_{t} > 0\quad\text{(call-heavy: vote with today’s move)} \\
 - \operatorname{sgn}(r_{t}) & \text{if }g_{t} < 0\quad\text{(put-heavy: vote against today’s move)}
\end{cases} \EQ{e11}$$

$$C_{t} = \operatorname{sgn}(M_{t})\EQ{e12}$$

and the position, held from the close of day $t$ to the next close, is their average:

$$h_{t} = \frac{A_{t} + C_{t}}{2}\EQ{e13}$$

The rule is long one unit of QQQ when both votes are up, short one unit when both are down, and in cash when they disagree. If the reading is exactly zero the code sets $h_{t} = 0$, which never happened in the test. Figure [@fig:f4] shows the rule as a flow chart.

![**Figure [#fig:f4].** The rule as a flow chart. Three questions give two votes, and the two votes give one position that is held until the next day's close. The chart describes the questions as asked just before the close; the backtest evaluates them at the closing price (Section 7).](figs/fig01_flow.png){width=5.6in}

The rule can be written in one line. When $g_{t}$, $r_{t}$ and $M_{t}$ are all non-zero, the option vote is $A_{t} = \operatorname{sgn}(g_{t} \times r_{t})$, because multiplying by a positive $g_{t}$ keeps the sign of $r_{t}$ and multiplying by a negative $g_{t}$ flips it. The position is then

$$h_{t} = \begin{cases}
\operatorname{sgn}(M_{t}) & \text{if }\operatorname{sgn}(g_{t} \times r_{t}) = \operatorname{sgn}(M_{t}) \\
0 & \text{otherwise}
\end{cases} \EQ{e14}$$

Equation [@eq:e14] shows that whenever the rule holds a position, its direction is $\operatorname{sgn}(M_{t})$, the direction of the 20-day trend. The option reading never picks the direction and only decides whether the trend position is taken. Equation [@eq:e14] matches the rule's recorded positions on all 2,117 days on which QQQ moved.

Table [@tab:t5] lists the eight possible cases and how often each occurred. Over the test the rule was long on 35.5% of days, short on 17.6% and in cash on 47.0%. It changed position 1,108 times in 2,118 days. A typical spell in one position lasted 2.0 trading days and the longest lasted 11.

| **Case** | **Yesterday's options** | **QQQ today** | **QQQ against 20 days ago** | **Vote A** | **Vote C** | **Position** | **Days** |
|:----:|:-------------|:-------|:--------------|:------|:------|:--------|-------:|
| 1 | Call-heavy | Up | Above | Up | Up | **Long** | 662 |
| 2 | Call-heavy | Up | Below | Up | Down | Cash | 79 |
| 3 | Call-heavy | Down | Above | Down | Up | Cash | 463 |
| 4 | Call-heavy | Down | Below | Down | Down | **Short** | 109 |
| 5 | Put-heavy | Up | Above | Down | Up | Cash | 186 |
| 6 | Put-heavy | Up | Below | Down | Down | **Short** | 263 |
| 7 | Put-heavy | Down | Above | Up | Up | **Long** | 88 |
| 8 | Put-heavy | Down | Below | Up | Down | Cash | 267 |

: **Table [#tab:t5].** The eight cases of the rule and the number of days on which each occurred. The cases cover 2,117 of the 2,118 days. On the remaining day (2021-07-13) QQQ closed exactly unchanged, the option vote had nothing to vote on, and the rule held half a position.

This structure decides what the rule should be compared with. Because the option vote acts as a filter on the trend position, the natural benchmarks are rules that take the trend position without the filter, and the natural null hypothesis is that the filter selects days no better than chance. Section 5.2 takes up both.

## 4.4 Returns and costs

The position taken at the close of day $t^{-}$, the previous day in the test, earns the next day's return, and each change of position has a cost. The rule's log return on day $t$ is

$$x_{t} = h_{t^{-}}\, r_{t}\; - \;\kappa\left| h_{t} - h_{t^{-}} \right|,\quad\quad\kappa = 0.0002\EQ{e15}$$

where $\left| h_{t} - h_{t^{-}} \right|$ is the amount traded at the close of day $t$, 1 unit when moving between cash and a position and 2 units when moving between long and short. The cost rate $\kappa$ of 0.0002, or 2 basis points per unit traded, is an assumption meant to cover fees and the gap between buying and selling prices. It is not a measured cost. Equation [@eq:e15] is used for Sharpe ratios. To follow wealth over time the same rule is written with simple returns,

$$R_{t} = h_{t^{-}}\left( e^{\, r_{t}} - 1 \right)\; - \;\kappa\left| h_{t} - h_{t^{-}} \right|\EQ{e16}$$

so that a dollar invested at the start is worth $(1 + R_{1})(1 + R_{2})\cdots(1 + R_{n})$ after $n$ days. Results before costs use $y_{t} = h_{t} \times r_{t + 1}$, the position decided on day $t$ times QQQ's log return on the next trading day, and have 2,118 daily values. Results after costs use Equations [@eq:e15] and [@eq:e16] and have 2,117, because the first day has no position carried in. The two series handle the four days without a reading slightly differently, and the effect on any figure reported here is negligible.

## 4.5 Performance measures

The Sharpe ratio is the mean daily log return divided by its standard deviation and scaled to a year, $\mathrm{SR} = \frac{\bar{x}}{s} \times \sqrt{252}$. Following my code, I do not subtract the interest rate on cash before dividing, so the Sharpe ratios in the main results are slightly higher than the conventional excess-return figure, for the rule and for QQQ alike. Section 5.5 reports Sharpe ratios on returns in excess of Treasury bills. Volatility is $s \times \sqrt{252}$. Growth is the annualized compound rate of the simple returns, $\left\lbrack (1 + R_{1})\cdots(1 + R_{n}) \right\rbrack^{252/n} - 1$, and maximum drawdown is the largest fall in compounded wealth from a high to a later low. Standard errors of mean returns are computed with the Newey and West (1987) estimator and five lags.

# 5 Results

## 5.1 Performance

Figure [@fig:f5] and Table [@tab:t6] give the main results after costs, next to buying and holding QQQ and a trend-only rule that is long when $C_{t}$ is $+ 1$ and in cash otherwise.

![**Figure [#fig:f5].** (a) The value of \$1 from 2018-01-03 to 2026-06-12 on a logarithmic scale. (b) Drawdown, the percentage each line is below its own earlier high. Grey bands mark the four stress periods of Table [@tab:t9].](figs/fig09_equity.png){width=6.3in}

|  | **Gamma A+C, after costs** | **Trend vote only, after costs** | **Buy and hold QQQ** |
|:-----------------------|---------------:|---------------:|---------------:|
| Value of \$1 at the end | \$2.93 | \$3.52 | \$4.45 |
| Growth rate a year | 13.7% | 16.2% | 19.4% |
| Volatility a year | 16.3% | 14.7% | 23.9% |
| Sharpe ratio | 0.88 | 1.02 | 0.74 |
| Worst fall | −22.9% | −20.2% | −35.6% |
| Share of days invested | 53.0% | 66.1% | 100% |

: **Table [#tab:t6].** Performance over 2,117 daily returns, 2018-01-04 to 2026-06-12. All three columns are measured on the same days.

One dollar became \$2.93 under Gamma A+C, \$3.52 under the trend-only rule and \$4.45 in QQQ. This was a strong period for QQQ, and a rule that is in cash on 47.0% of days gives up much of the rise. After costs the rule's mean daily log return is 5.75 basis points and its daily standard deviation 1.037%, which gives the Sharpe ratio of 0.88. That is higher than QQQ's 0.74 because the rule's volatility is lower, 16.3% a year against 23.9%. Its maximum drawdown was 22.9%, from \$1.79 on 2020-09-02 to \$1.38 on 2022-04-19. QQQ's was 35.6%, from 2021-11-19 to 2022-12-28, and QQQ did not regain its earlier high until 2023-12-15.

The rule's path differs from QQQ's. Its large gains came in early 2020, in 2022 and in spring 2025, all periods when QQQ fell sharply and the rule was often short. Between them it moved sideways for long stretches, including most of 2023 and 2024, while QQQ rose. Its daily returns have a correlation of −0.19 with QQQ's. By calendar year (Figure [@fig:f6] and Table [@tab:t7]) the rule made money in 6 of 9 years and beat QQQ in 4 of them, which include every year in which QQQ fell.

![**Figure [#fig:f6].** Return in each calendar year. The years marked with a star are incomplete: 2018 starts on 4 January and 2026 ends on 12 June.](figs/fig10_yearly.png){width=5.9in}

|  | **2018** | **2019** | **2020** | **2021** | **2022** | **2023** | **2024** | **2025** | **2026** |
|:------------|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| Gamma A+C, after costs | −1.0% | +9.9% | +53.3% | −6.7% | +25.1% | −5.7% | +4.3% | +42.5% | +7.5% |
| Buy and hold QQQ | −3.6% | +37.8% | +44.0% | +26.8% | −33.1% | +53.8% | +23.9% | +22.5% | +17.4% |
| Gamma A+C Sharpe ratio | 0.04 | 0.90 | 1.92 | −0.41 | 1.18 | −0.40 | 0.39 | 2.39 | 1.26 |

: **Table [#tab:t7].** Calendar-year returns and the rule's Sharpe ratio. 2018 and 2026 are part-years.

The returns are concentrated in a few months (Figure [@fig:f7]). Of 102 months, 56 (55%) were gains. The best was +32.2% in 2020-03, the month of the COVID crash, and the worst was −10.4% in 2020-09. The best day was +12.0% on 2020-03-16, when the rule was short, and the worst was −5.2% on 2020-03-02. On days when it held a position the rule gained on 54.2% of them, so the result comes from gains being a little larger than losses over many days. Daily returns before costs have skewness of +1.356 and kurtosis of 19.11, far above the 3 of a normal distribution, because of a few very large days in March 2020.

![**Figure [#fig:f7].** The rule's return in each month, after costs, in percent. Blue is a gain and red a loss. The color scale stops at 12%, so the largest months are shown at full color. The right-hand column is the year's total.](figs/fig11_monthly_heatmap.png){width=5.5in}

Table [@tab:conc] measures that concentration. March 2020 has {{conc_march_days}} trading days. In them the rule returned {{conc_march_ret}} while QQQ returned {{conc_march_qqq}}, and they supply {{conc_march_share}} of the rule's total log return over the sample. Without that month the rule's Sharpe ratio falls from {{net_sharpe}} to {{conc_exmar_ac_sh}} and a dollar grows to \${{conc_exmar_ac_w}} instead of \${{net_growth}}. QQQ's Sharpe ratio rises to {{conc_exmar_qq_sh}} when the same days are removed, so the rule's advantage over buy and hold on this measure depends on that month. The rule's five best days ({{conc_top5_list}}) were all days on which it was short. Only one of them is in March 2020, and together they supply {{conc_top5_share}} of the total log return. Without them the Sharpe ratio is {{conc_extop_ac_sh}} and the final value \${{conc_extop_ac_w}}. The last row is not a fair race with QQQ, because the rule's best days are among QQQ's worst and removing them raises QQQ's figures mechanically. The trend-only rule is hardly affected by either exclusion, because it was in cash on almost all of those days.

[[table:conc]]

: **Table [#tab:conc].** Concentration of the result. Sharpe ratio and final value of \$1 after costs, for the full sample and with the named days removed from all three series.

## 5.2 Comparison with simpler rules

Figure [@fig:f8] compares the rule with simpler alternatives over the same days. Traded alone and always invested, long when the vote is up and short when it is down, the option vote earns a Sharpe ratio of 0.69 after costs and the trend vote earns 0.51. The combined rule's 0.88 is higher than both. A trend rule that is long when the trend vote is up and in cash otherwise earns 1.02, with growth of 16.2% a year and a maximum drawdown of 20.2%, and so does better than Gamma A+C on each of those measures. Its returns have a correlation of 0.41 with those of Gamma A+C.

![**Figure [#fig:f8].** Annualized Sharpe ratios over the same sample. The top group is Gamma A+C under different assumptions about costs and timing. The bottom group is simpler alternatives.](figs/fig12_sharpe_bars.png){width=6.3in}

The two trend benchmarks sit on either side of the combined rule, and the difference between them is whether the trend signal is traded on the short side. Adding a short position on every trend-down day lowers the Sharpe ratio of the trend rule from 1.02 to 0.51, in a sample in which QQQ more than quadrupled. Gamma A+C is short on about half of the trend-down days (372 of 718), and its short positions made money in total (Section 5.3). The Sharpe ratios in Figure [@fig:f8] cannot say whether the option vote chose those days with skill or by chance. Two further tests are needed.

**Random filters.** By Equation [@eq:e14] the option vote is a filter on the trend position. On the {{rf_up_n}} trend-up days the rule was long on {{rf_up_k}}, and on the {{rf_dn_n}} trend-down days it was short on {{rf_dn_k}} (Table [@tab:t5]). To test whether the option vote chose those days better than chance, I drew {{rf_draws}} random filters. Each takes the trend position on the same number of days in each group, chosen uniformly at random, holds cash on the other days, and is scored exactly as the rule is. The p-value is the share of random filters that do at least as well as the rule.

[[table:rf]]

: **Table [#tab:rf].** The rule against {{rf_draws}} random filters that hold the trend position on the same number of trend-up and trend-down days. Independent draws choose the days uniformly at random. Block draws permute the rule's own sequence of entries in blocks of {{rf_block}} days. The p-value is the share of random filters at least as good as the rule.

![**Figure [#fig:rf].** The rule against random filters with the same day counts (independent draws). The histogram is the distribution across {{rf_draws}} random filters, the dark line its mean and the orange line the rule. (a) Sharpe ratio before costs. (b) Sharpe ratio after costs. (c) Mean next-day QQQ return on long days. (d) Mean next-day gain on short days, which is minus QQQ's return.](figs/fig_random_filters.png){width=6.0in}

The random filters earn a mean Sharpe ratio of {{rf_gross_iid_mean}} before costs and {{rf_net_iid_mean}} after costs (Table [@tab:rf] and Figure [@fig:rf]). The rule's {{rf_gross_actual}} and {{rf_net_actual}} lie far in the right tail of both distributions ({{rf_gross_iid_pt}} and {{rf_net_iid_pt}}). The option vote therefore selected days better than chance in this sample. The two sides differ sharply. On its long days the rule earned a mean next-day return of {{rf_long_actual}} basis points, below the {{rf_long_iid_mean}} earned by a random choice of trend-up days ({{rf_long_iid_pt}}). On its short days it gained {{rf_short_actual}} basis points a day, while a random choice of trend-down days loses {{rf_short_iid_mean_abs}}, because QQQ rose by {{rf_dn_all_abs}} basis points on an average trend-down day ({{rf_short_iid_pt}}). All of the selection is on the short side. Seen from the other side, the {{dn_cash_n}} trend-down days on which the rule held cash had a mean next-day return of {{dn_cash_bp}} basis points.

Two checks leave this unchanged. Random filters drawn independently change position {{rf_changes_iid}} times on average, about as often as the rule's {{rf_changes_actual}}, so they bear the same costs, and drawing the skipped days in blocks gives the same answers (Table [@tab:rf]). Scoring every filter without March 2020 lowers the rule's Sharpe ratios to {{rfx_gross_actual}} before costs and {{rfx_net_actual}} after costs, with p-values of {{rfx_gross_p}} and {{rfx_net_p}}, and the short side remains far from the random filters ({{rfx_short_actual}} basis points against {{rfx_short_mean}}, {{rfx_short_pt}}).

These p-values overstate the evidence in one respect. The direction in which the option vote uses the reading was chosen in sample (Section 4.1), and with the other direction the same test would have been run on the mirror-image filter. Doubling the p-values allows for that choice and leaves the main ones below 0.01.

**Is it the option reading?** The option vote has two inputs, the reading and the day's move, and the random filters do not say which of them does the selecting. Two further benchmarks separate them (Table [@tab:nofilter]). The first keeps the rule and the day's moves and shuffles the readings across days, so that any link between the reading and the next day's return is broken. The {{rf_draws}} shuffled rules earn a mean Sharpe ratio of {{sh_net_iid_mean}} after costs, against the rule's {{net_sharpe}} ({{sh_net_iid_pt}}). Shuffling in blocks of {{sh_block}} days, which keeps the persistence of the reading (its sign is unchanged from one day to the next {{sh_stay}} of the time), gives the same result. The timing of the reading therefore matters to a rule of this form.

The second benchmark uses no option data at all. Equation [@eq:e11] votes with the day's move after a call-heavy reading and against it after a put-heavy one. A rule that always votes against the day's move takes the trend position only after a day that moved against the trend, buying dips in an uptrend and selling rallies in a downtrend. It earns a Sharpe ratio of {{fade_net}} after costs, with growth of {{fade_gr}} a year and a maximum drawdown of {{fade_dd_abs}}. The opposite rule, which takes the trend position only after a day that moved with the trend, earns {{follow_net}}. The shuffled rules do badly because they follow the day's move on randomly chosen days, and following is the losing half of the rule. The reading tells the rule when following is safe, but a rule that never follows does almost as well without it.

[[table:nofilter]]

: **Table [#tab:nofilter].** Gamma A+C against rules that use the day's move without the option reading. The p-value in the second row is the share of shuffled rules at least as good as Gamma A+C after costs. The p-value in the third row is from the test of Table [@tab:lw].

**Differences between Sharpe ratios.** Table [@tab:lw] tests whether the rule's Sharpe ratio differs from that of each benchmark, using the studentized bootstrap of Ledoit and Wolf (2008). For two return series measured on the same days, the statistic is

$$\widehat{\Delta} = \widehat{\mathrm{SR}}_{1} - \widehat{\mathrm{SR}}_{2},\quad\quad d = \frac{\left| \widehat{\Delta} \right|}{s(\widehat{\Delta})} \EQ{lw}$$

where $s(\widehat{\Delta})$ is a standard error that allows for fat tails and serial correlation. The p-value is the share of {{lw_boot}} circular block bootstrap resamples in which the same statistic, centered on $\widehat{\Delta}$ and studentized within the resample, is at least $d$. I report three block lengths. As a check on my implementation, I applied it to {{lw_size_sims}} simulated pairs of fat-tailed series with equal true Sharpe ratios and the length of this sample, and it rejected at the 5% level in {{lw_size}} of them.

[[table:lw]]

: **Table [#tab:lw].** Differences in annualized Sharpe ratio between Gamma A+C ({{net_sharpe}} after costs) and four benchmarks, with standard errors and the p-values of the Ledoit and Wolf (2008) test for three block lengths. All series are after costs and cover the same {{n_net}} days.

None of the differences is significant. The rule's Sharpe ratio is {{lw_tl_diff_abs}} below that of the trend vote traded long or in cash, with a standard error of {{lw_tl_se}} (p = {{lw_tl_p5}}), and {{lw_ts_diff_abs}} above that of the trend vote traded long or short (p = {{lw_ts_p5}}). Its advantage of {{lw_qq_diff_abs}} over buying and holding QQQ has a standard error of {{lw_qq_se}} (p = {{lw_qq_p5}}), and its advantage of {{lw_fade_diff_abs}} over the rule that uses no option data has a standard error of {{lw_fade_se}} (p = {{lw_fade_p5}}). Eight years of daily returns cannot separate Sharpe ratios that differ by a few tenths.

Taken together, the tests of this section say three things. The option vote selects days better than chance, and only on the short side. The timing of the reading matters to that selection. And the evidence does not show that the reading improves on a rule that reaches most of the same result from the day's move and the trend alone. The reading-free benchmarks were chosen after the results were known, so they add to the number of comparisons made on this sample.

## 5.3 Where the returns come from

Figure [@fig:f9] sorts every day by the sign of the previous reading and by what the rule did, and shows QQQ's mean log return on the following day. Across all 2,118 days that mean was +7.3 basis points, with a standard error of 2.96 and a t-statistic of 2.47.

![**Figure [#fig:f9].** QQQ's mean return on the day after each kind of decision, in basis points, by the previous reading (rows) and the rule's position (columns). Under each mean is the number of days and a Newey-West t-statistic. On the days the rule was short, a negative QQQ return is a gain for the rule. The call-heavy long cell has {{count_fig}} days against {{count_tab}} in Table [@tab:t5] because it includes {{count_extra_day}}, the one day on which the rule held half a position.](figs/fig08_state_heatmap.png){width=6.0in}

When the rule was long, QQQ's mean next-day return was +7.4 basis points after call-heavy readings and +9.2 after put-heavy readings, close to the +7.3 of an average day. The long side shows no ability to pick days. When the rule was short, QQQ's mean was −25.1 and −24.2 basis points in the two groups. Added up over the test, short positions contributed +0.910 in log return and long positions +0.568. Neither short cell reaches a t-statistic of 2 (−1.73 and −1.63), so even the short side is not firmly established.

The rule also sat out its best days. On days in cash, QQQ's mean next-day return was +10.4 basis points after call-heavy readings (t-statistic of 1.93) and +29.3 after put-heavy readings (t-statistic of 3.79), the strongest cell in the figure. Weighted by the number of days in each cell, QQQ returned about +19 basis points a day on the 995 days the rule held cash, more than twice its return on the days the rule was long.

A rule that earns most of its return from short positions, in a period when the market mostly rose, depends on there being sharp falls. This sample had three. A sample with fewer would look different.

## 5.4 Sensitivity to costs, timing and sample period

Table [@tab:t8] lists the ways a backtest can mislead and the test applied to each. The Sharpe ratio is 1.07 before costs and 0.88 after costs of 2 basis points per unit traded. At twice that cost it is 0.71. The rule trades 136 units a year, so at the assumed rate costs take 2.7% a year.

| Threat | Description | Test | Result |
|:----------------|:-------------------------|:-----------------------------|:-----------------------------|
| Look-ahead | The test uses a number that was not yet known at the moment of the decision | Use the previous day's reading, then delay everything by one more day and see what is left | Sharpe falls from {{gross_sharpe}} to {{lag2_sharpe}}. It survives, but halves |
| Transaction costs | Every trade costs a little, and this rule trades often | Charge 0.02% per unit traded, then double it | {{gross_sharpe}} becomes {{net_sharpe}}, then {{net2_sharpe}} |
| Fill price | The test assumes trading exactly at the closing price | Assume position changes happen at the next morning's opening price instead | {{gross_sharpe}} becomes {{open_sharpe}}, before costs |
| Period dependence | A rule can look good only because of one unusual stretch | Split the test in two; look at each year and at named crises; remove the best month and the best days | Both halves positive. One crisis month negative. Without March 2020 the Sharpe ratio is {{conc_exmar_ac_sh}} (Sections 5.1 and 5.4) |
| Weak benchmark | A rule should beat simpler alternatives as well as zero | Compare with buy and hold, with each vote alone, with random filters and with a rule that uses no option data | Beats random filters ({{rf_net_iid_pt}}). No difference in Sharpe ratio from any benchmark is significant (Section 5.2) |
| Incomplete accounting | Dividends, interest and borrowing costs change what a position earns | Add all three and measure Sharpe ratios in excess of Treasury bills | {{net_sharpe}} becomes {{acct_ac_sh1}}. No ranking changes (Section 5.5) |
| Multiple testing | Try enough rules and one will look good by chance | The deflated Sharpe ratio | {{dsr_12}}, below the 0.95 pass mark (Section 6) |
| No out-of-sample test | The rule was developed on the whole sample | A holdout fixed in advance | {{ho_days}} of {{ho_planned}} days so far: a loss of {{ho_ac_ret_abs}} (Section 5.6) |

: **Table [#tab:t8].** Threats to the validity of the backtest, the test applied to each, and the outcome.

Timing matters more than costs. Acting one day late cuts the Sharpe ratio before costs from 1.07 to 0.52, and executing position changes at the next morning's opening price gives 0.81 before costs. The information in the signal fades within a day or two. This makes the result sensitive to the assumption, discussed in Section 7, that the closing price is known when the trade is made.

Split at 2022-03-22, the Sharpe ratio after costs was 0.58 in the first half of the sample and 1.20 in the second. Before costs, the years 2018 to 2021 gave 0.97 and 2022 to 2026 gave 1.16. Both halves are positive, but the second half is not a fresh test, because the rule's details were settled after the whole period had been seen.

Table [@tab:t9] reports returns in four stress periods that my research protocol requires every strategy to be shown in. The rule gained in the three long declines and lost 5.5% in March 2023, when markets swung sharply around the failure of several US banks and QQQ ended the month 9.3% higher. A rule that follows a 20-day trend is badly placed for sharp reversals.

| **Period** | **Dates** | **Days** | **Gamma A+C, after costs** | **Buy and hold QQQ** |
|:-------------------|:--------------------|------:|------------:|-----------:|
| Late 2018 sell-off | 2018-10-01 to 2018-12-31 | 63 | +10.4% | −17.0% |
| COVID crash and rebound | 2020-02-15 to 2020-04-30 | 52 | +44.6% | −6.7% |
| 2022 bear market | 2022-01-01 to 2022-12-31 | 251 | +25.1% | −33.1% |
| March 2023 bank failures | 2023-03-01 to 2023-03-31 | 23 | −5.5% | +9.3% |

: **Table [#tab:t9].** Total return in four stress periods.

## 5.5 Return accounting

The results so far follow my original code, which leaves out four things: QQQ's dividends, interest on idle cash, the cost of borrowing shares to sell short, and the subtraction of a risk-free rate before computing a Sharpe ratio. This section adds all four. The positions are unchanged, and only the returns earned on them are measured differently.

Let $\rho_{t}$ be QQQ's total return on day $t$, computed from the dividend-adjusted closing price, $b_{t}$ the return on a Treasury bill for that day and $\phi_{t}$ the borrow fee for that day. With $h = h_{t^{-}}$ the position carried into day $t$, the return on one unit of capital is

$$R_{t}^{F} = \begin{cases} h\,\rho_{t} + (1 - h)\, b_{t} & \text{if } h \geq 0 \\ b_{t} + h\,\rho_{t} - \left| h \right| \phi_{t} & \text{if } h < 0 \end{cases}\;\; - \;\kappa\left| h_{t} - h_{t^{-}} \right| \EQ{full}$$

A long position earns QQQ's total return. Idle capital earns the bill return. A short position leaves the capital in bills, loses QQQ's total return, which includes any dividend owed to the lender of the shares, and pays the borrow fee. No interest is credited on the proceeds of the short sale, which is the cautious assumption for a small account. The bill return is $b_{t} = B_{t^{-}} \times n_{t}/360$, where $B_{t^{-}}$ is the 3-month Treasury bill discount rate on the previous day and $n_{t}$ is the number of calendar days since the previous session. The borrow fee is $\phi_{t} = {{m:acct_borrow_dec}} \times n_{t}/360$, an assumed {{acct_borrow}} a year. QQQ is easy to borrow, but I have no record of the actual fee, so this figure is an assumption in the same sense as the cost rate $\kappa$. Sharpe ratios are computed on the excess log return, $\ln(1 + R_{t}^{F}) - \ln(1 + b_{t})$.

Over the sample QQQ's dividends added {{acct_div_yield}} a year to its return, and the bill rate averaged {{acct_rf_mean}} a year, ranging from {{acct_rf_min}} to {{acct_rf_max}}.

[[table:acct]]

: **Table [#tab:acct].** Baseline and full return accounting, after costs. The baseline is the accounting of Sections 5.1 to 5.4. Full accounting adds dividends, Treasury bill interest on idle capital and a borrow fee of {{acct_borrow}} a year on short positions, and its Sharpe ratio is computed on returns in excess of Treasury bills.

Table [@tab:acct] gives the result. Growth rises for every rule, because dividends and interest are now counted, and every Sharpe ratio falls, because the bill return is subtracted. Gamma A+C falls from {{acct_ac_sh0}} to {{acct_ac_sh1}}, the trend vote traded long or in cash from {{acct_tl_sh0}} to {{acct_tl_sh1}}, the trend vote traded long or short from {{acct_ts_sh0}} to {{acct_ts_sh1}}, and QQQ from {{acct_qq_sh0}} to {{acct_qq_sh1}}. The rule that is short most often loses most, since it pays dividends and the fee and gives up the excess return on its capital. The ranking of the four rules is unchanged. Appendix C repeats Tables [@tab:t6], [@tab:t7] and [@tab:t9] under full accounting. Across those tables one comparison changes sign: the rule's return in 2018 moves from {{y2018}} to {{acct_y2018}}, so that it gains in {{acct_years_pos}} of 9 years instead of {{years_pos}}. It still beats QQQ in {{acct_years_beat}} of them, and the four stress periods keep their signs.

The sensitivity results of Section 5.4 keep their shape. Under full accounting the rule's Sharpe ratio is {{acct_ac_gross}} before costs, {{acct_ac_sh1}} after costs and {{acct_ac_x2}} at twice the cost. Acting one day late gives {{acct_ac_late}} before costs. The two halves of the sample give {{acct_ac_h1}} and {{acct_ac_h2}}. Crediting bill interest on short-sale proceeds would raise the rule's figure to {{acct_ac_sh_rebate}}, and a borrow fee of 1% a year would lower it to {{acct_ac_sh_fee1}}.

## 5.6 Holdout

Every result above comes from the sample on which the rule was developed. Before downloading any later data I fixed a holdout in writing (Appendix D): the rule exactly as specified in Section 4, on every trading day from {{ho_a}} to 2026-11-11, {{ho_planned}} sessions, with the outcomes to be reported named in advance.

The holdout is incomplete. The data vendor limits the number of requests in a day, and by the time of writing the quotes for the first {{ho_quote_days}} sessions had been downloaded, {{ho_a}} to {{ho_quote_b}}. The preregistration provides for this case: the holdout is the longest unbroken stretch from the first day, and the start date is not moved. As a check on the new download, I requested the last day of the original sample again. All {{ho_parity_rows}} rows matched the saved data, and the reading recomputed from them equals the stored one.

[[table:ho]]

: **Table [#tab:ho].** The first {{ho_days}} days of the preregistered holdout, {{ho_a}} to {{ho_b}}, next to the sample. All holdout columns cover the same days.

Table [@tab:ho] reports the result. Over the {{ho_days}} days the rule lost {{ho_ac_ret_abs}} after costs, while QQQ gained {{ho_qq_ret_abs}} and the trend vote traded long or in cash lost {{ho_tl_ret_abs}}. The rule was long on {{ho_long}} days, short on {{ho_short}} and in cash on {{ho_cash}}. It lost on both of its long days and on two of its four short days, in a stretch in which QQQ moved by more than 1% on {{ho_big}} of the {{ho_days}} days.

A sample of {{ho_days}} days says little by itself. The standard error of an annualized Sharpe ratio over {{ho_days}} days is about {{ho_se}}, so the holdout figure of {{ho_ac_sh}} is not statistically distinguishable from the sample's {{net_sharpe}}, or from zero. The result is reported because it was promised in advance, and because it is the only evidence in this paper that the rule's development could not have influenced. It is a first observation and an unfavorable one. The remaining {{ho_remaining}} sessions will be added as the data arrive.

# 6 Multiple testing

## 6.1 The deflated Sharpe ratio

The rule studied here was chosen after other versions had been tried. Even if none of the versions had any skill, the best of them would show a good Sharpe ratio by luck, and the more versions are tried, the better the luckiest one looks. The deflated Sharpe ratio (DSR) of Bailey and López de Prado (2014) corrects for this. It is the probability that the true Sharpe ratio exceeds the value that the best of $N$ unskilled trials would be expected to show. I compute it on the rule's daily returns before costs, $y_{t}$, of which there are $T = 2,118$, to match my existing validation code, and report the value after costs at the end of Section 6.2. Table [@tab:t10] lists the inputs.

| **Symbol** | **Name** | **Meaning** | **Value here** |
|:-------|:--------------|:------------------------------------|:------------|
| $T$ | sample size | Number of daily returns | 2,118 |
| $y_{t}$ | daily return | The rule's return on day $t$, before costs |  |
| $\bar{y}$ | mean | Average daily return | 0.000698 |
| $s_{T}$ | standard deviation | Typical distance of a daily return from the average | 0.010350 |
| $\mathrm{SR}$ | Sharpe ratio per day | $\bar{y}$ divided by $s_{T}$, not scaled to a year | 0.06743 |
| $b_{3}$ | skewness | Whether large gains or large losses are more common. Zero for a symmetric bell curve | +1.356 |
| $b_{4}$ | kurtosis | How often extreme days happen. 3 for a bell curve | 19.11 |
| $N$ | number of trials | How many versions of the strategy were tried | 12 or more |
| $v$ | variance of trial Sharpe ratios | How much the Sharpe ratios of skill-less strategies vary. Set to $1/T$ | 4.72 × 10^−4^ |
| $\gamma_{E}$ | Euler-Mascheroni constant | A fixed number from mathematics, like $\pi$ | 0.5772... |
| $e$ | Euler's number | A fixed number from mathematics | 2.71828... |
| $\Phi$ | normal curve | $\Phi(z)$ is the share of a standard bell curve to the left of $z$ |  |
| $\Phi^{- 1}$ | its inverse | $\Phi^{- 1}(p)$ is the $z$ that has share $p$ to its left |  |
| $\mathrm{SR}_{0}$ | the luck bar | Expected best Sharpe ratio among $N$ skill-less strategies | depends on $N$ |
| $\mathrm{DSR}$ | deflated Sharpe ratio | Confidence that the true Sharpe ratio exceeds $\mathrm{SR}_{0}$ | depends on $N$ |

: **Table [#tab:t10].** Inputs to the deflated Sharpe ratio.

The sample moments of the daily returns are

$$\bar{y} = \frac{1}{T}\sum_{t = 1}^{T}y_{t},\quad\quad s_{T} = \sqrt{\frac{1}{T}\sum_{t = 1}^{T}\left( y_{t} - \bar{y} \right)^{2}}\EQ{e17}$$

$$b_{3} = \frac{1}{T}\sum_{t = 1}^{T}\left( \frac{y_{t} - \bar{y}}{s_{T}} \right)^{3},\quad\quad b_{4} = \frac{1}{T}\sum_{t = 1}^{T}\left( \frac{y_{t} - \bar{y}}{s_{T}} \right)^{4}\EQ{e18}$$

Here the standard deviation divides by $T$, while the Sharpe ratios in Section 5 use the sample formula that divides by $n - 1$. With more than two thousand days the difference is negligible. The mean is 6.98 basis points a day and the standard deviation 1.035%. The daily Sharpe ratio is

$$\mathrm{SR} = \frac{\bar{y}}{s_{T}} = \frac{0.000698}{0.010350} = 0.06743\EQ{e19}$$

which is 1.07 when multiplied by $\sqrt{252}$. Bailey, Borwein, López de Prado and Zhu (2014) give the expected maximum Sharpe ratio among $N$ unskilled trials as

$$\mathrm{SR}_{0} = \sqrt{v}\,\left\lbrack \,(1 - \gamma_{E})\;\Phi^{- 1}\left( 1 - \frac{1}{N} \right)\; + \;\gamma_{E}\;\Phi^{- 1}\left( 1 - \frac{1}{N\, e} \right) \right\rbrack,\quad\quad v = \frac{1}{T}\EQ{e20}$$

where $\gamma_{E}$ is the Euler-Mascheroni constant and $v$ is the variance of the Sharpe ratios across trials. I call this expected maximum the luck bar, the label used in the figures and in Table [@tab:t11]. The deflated Sharpe ratio is

$$\mathrm{DSR} = \Phi\left( \frac{\left( \mathrm{SR} - \mathrm{SR}_{0} \right)\sqrt{T - 1}}{\sqrt{\, 1\; - \; b_{3}\, \mathrm{SR}\; + \;\frac{b_{4} - 1}{4}\,\mathrm{SR}^{2}\,}} \right)\EQ{e21}$$

The numerator is the distance of the measured Sharpe ratio above the luck bar, scaled by the length of the sample. The denominator corrects for returns that are not normal through the skewness $b_{3}$ and kurtosis $b_{4}$.

![**Figure [#fig:f10].** The two steps of the deflated Sharpe ratio with 12 trials. (a) The best Sharpe ratio in each of 20,000 simulated sets of 12 strategies with no skill, each as long as this test. (b) The sampling distribution of the true Sharpe ratio given the measured 1.07. The share of its area to the right of the luck bar is the deflated Sharpe ratio.](figs/fig13_luck_confidence.png){width=6.2in}

## 6.2 Result and sensitivity to the number of trials

For $N = 12$,

$$\Phi^{- 1}\left( 1 - \frac{1}{12} \right) = \Phi^{- 1}(0.91667) = 1.3830,\quad\quad\Phi^{- 1}\left( 1 - \frac{1}{12e} \right) = \Phi^{- 1}(0.96934) = 1.8712$$

$$\mathrm{SR}_{0} = 0.02173 \times \lbrack\, 0.4228 \times 1.3830 + 0.5772 \times 1.8712\,\rbrack = 0.02173 \times 1.6648 = 0.03617$$

which is 0.57 when scaled to a year. A simulation agrees: 12 strategies with zero true skill were created 20,000 times, and the mean of the best Sharpe ratio across those sets was 0.56 (Figure [@fig:f10]). The numerator of Equation [@eq:e21] is

$$(0.06743 - 0.03617) \times \sqrt{2,118 - 1} = 0.03126 \times 46.01 = 1.4383$$

and the denominator is

$$\sqrt{\, 1 - ( + 1.356)(0.06743) + 4.5286 \times 0.004547\,} = \sqrt{\, 1 - 0.0914 + 0.0206\,} = \sqrt{0.9291} = 0.9639$$

so

$$\mathrm{DSR} = \Phi\left( \frac{1.4383}{0.9639} \right) = \Phi(1.492) = 0.932$$

The measured Sharpe ratio is about one and a half standard errors above the luck bar, which leaves a 6.8% probability that the true value is below it. The positive skewness helps a little, since it makes the denominator smaller than 1. The threshold my research protocol applies to every strategy is 0.95, so with 12 trials the rule falls just short.

The result depends heavily on $N$ (Table [@tab:t11] and Figure [@fig:f11]). The rule passes only if no more than 8 versions were tried. I can document 12: the signal in three forms (the option vote alone, the trend vote alone, and both), on two funds, with and without the one-day lag, which is $3 \times 2 \times 2 = 12$. No complete record of every version tried was kept, so 12 is a minimum and the true DSR is below 0.932. If the count were 50 it would be 0.805. The value of 670 in the table is the count recorded for a different strategy in the same research program and is included to show how far the figure can fall.

| **Versions tried,** $N$       | **1** | **2** | **5** | **12** | **50** | **90** | **670** |
|:---------------------------|------:|------:|------:|------:|------:|------:|------:|
| Luck bar, yearly Sharpe ratio |  0.00 |  0.18 |  0.41 |   0.57 |   0.79 |   0.86 |    1.08 |
| Deflated Sharpe ratio         | 0.999 | 0.996 | 0.976 |  0.932 |  0.805 |  0.737 |   0.485 |
| Passes 0.95?                  |   yes |   yes |   yes |     no |     no |     no |      no |

: **Table [#tab:t11].** The deflated Sharpe ratio for different numbers of trials.

![**Figure [#fig:f11].** The deflated Sharpe ratio against the number of versions tried. The result clears the 0.95 threshold only if 8 or fewer versions were tried.](figs/fig14_dsr_curve.png){width=5.9in}

Two features of the calculation should be kept in mind. In the published method $v$ is measured from the Sharpe ratios of all the versions that were tried. No such record exists here, so the code uses $v = 1/T$, the variation that pure noise would produce in a sample of this length. The calculation above also uses returns before costs. On returns after costs, where the Sharpe ratio is {{net_sharpe}}, the same calculation with $N = 12$ gives {{dsr_net_12}}. On excess returns after costs under the full accounting of Section 5.5, where it is {{acct_ac_sh1}}, it gives {{acct_dsr12}}.

# 7 Limitations

The test assumes that the day's closing price is known when the decision is made and that the trade is filled at that same close. In practice the decision has to be made a little before the close, on a price that is not final. The delay and next-open results in Section 5.4 suggest the outcome is sensitive to this. A test that forms the signal from prices a few minutes before the close would answer the question, and it needs intraday prices, which this study does not use.

The construction of the signal has several weaknesses. The direction in which the option vote uses the reading was chosen because it worked (Section 4.1). The sign convention rests on the white paper's assumptions about who holds calls and puts, which I have not checked against data on dealer positions. The reading is built from S&P 500 options and the position is taken in QQQ, and the test does not show whether this is better or worse than reading and trading the same index. Options that expire on the quote day are excluded, because the gamma formula divides by time to expiry (Table [@tab:t3]). These are the contracts studied by Dim, Eraker and Vilkov (2024), and a reading that includes them might behave differently. Finally, the reading is built from about twice as many contracts after 2022 as before (Figure [@fig:f1]), and the rule is treated as one rule across both periods.

The main results leave out dividends, interest and borrowing costs. Section 5.5 adds them and finds lower Sharpe ratios for every rule and no change in their ranking. Two inputs to that section are assumptions: the borrow fee of {{acct_borrow}} a year, and the treatment of short-sale proceeds as earning no interest.

The sample is one market period. From 2018 to mid-2026 QQQ more than quadrupled. A rule that is often in cash or short will look worse in such a period and might look better in a flat or falling one, and one period cannot settle which. The result is also concentrated: one month supplies {{conc_march_share}} of the rule's total return and five days supply {{conc_top5_share}} (Section 5.1). The trend window of 20 days was not varied, and the trial count in Section 6 is a lower bound. The benchmarks of Section 5.2 that use no option data were constructed after the results were known, and they add to the number of comparisons made on this sample.

The holdout of Section 5.6 covers only the first {{ho_days}} of its {{ho_planned}} preregistered days, too few to support any conclusion. Part of the holdout window was not unknown to me when it was fixed: a version of the rule with a different configuration ran on a simulated account in July 2026 and was stopped after a loss (Appendix D). The rule currently runs on a simulated account only, and no results from that account are used in this paper.

# 8 Conclusion

The sign of a short-dated S&P 500 gamma exposure reading, used as a filter on a 20-day trend position in QQQ, produced a profitable backtest from 2018 to 2026. The combined rule has a higher Sharpe ratio than buy and hold and than either vote traded alone, long or short every day, a smaller drawdown than buy and hold, and a result that stays positive after transaction costs, after a one-day delay and under full return accounting. Its option filter selects days better than random filters do, and better than the same filter with the readings shuffled. Against that, none of its Sharpe ratio differences from the benchmarks is statistically significant. It does not beat a trend rule that simply stays out of the market when the trend is down. Its long positions earn no more than the average day. Its selection is confined to short positions, {{conc_march_share}} of its return comes from one month, and a rule with no option data reaches most of the same result. It fails the deflated Sharpe ratio test at the smallest trial count that can be documented, and the first {{ho_days}} days of its holdout were a loss.

I conclude that the evidence does not show that the option signal adds to the trend rule, and that Gamma A+C is best described as a hypothesis that has not been ruled out. Three kinds of new evidence would move that verdict in either direction: the rest of the preregistered holdout, a complete record of every version tried from now on so that $N$ is known and not estimated, and the same test on a different period or market chosen in advance.

# Declarations

**Data availability.** The option quotes were obtained from Market Data (<https://www.marketdata.app>) under an individual subscription. Its terms do not allow the quotes, or data files built from them, to be redistributed, so the code repository contains no quotes and no daily series computed from them. The quotes can be obtained from the same service with the requests in Appendix A. The QQQ prices and the Treasury bill rate are public.

**Code availability.** Every number, table and figure in this paper is produced by five programs. `paper_numbers.py` and `make_figs.py` produce the main results and their figures. `fetch_inputs.py`, `journal_numbers.py` and `make_journal_figs.py` produce the tests of Section 5.2 and the results of Sections 5.5 and 5.6. {{decl_code}} Calculations use Python with the NumPy, pandas, SciPy and statsmodels libraries, and the figures use Matplotlib.

**Preregistration.** The holdout of Section 5.6 was fixed in a dated note that was committed to the author's version-control repository before any data after the end of the sample were downloaded. Appendix D reproduces it, and the note itself is in the code repository.

**Funding.** {{decl_funding}}

**Competing interests.** {{decl_interests}}

**Use of AI tools.** The analysis code and the figures were written with the assistance of Claude, an AI model made by Anthropic, which was also used to draft and edit the text. The author takes responsibility for the content of the paper.

This paper reports a test on historical data. Nothing in it is a recommendation to buy or sell anything.

# References

::: {custom-style="Reference"}
Bailey, D. H., Borwein, J. M., López de Prado, M. and Zhu, Q. J. (2014). Pseudo-mathematics and financial charlatanism: the effects of backtest overfitting on out-of-sample performance. *Notices of the American Mathematical Society*, 61(5), 458-471. <https://www.ams.org/notices/201405/rnoti-p458.pdf>
:::

::: {custom-style="Reference"}
Bailey, D. H. and López de Prado, M. (2014). The deflated Sharpe ratio: correcting for selection bias, backtest overfitting and non-normality. *Journal of Portfolio Management*, 40(5), 94-107. <https://papers.ssrn.com/abstract=2460551>
:::

::: {custom-style="Reference"}
Baltussen, G., Da, Z., Lammers, S. and Martens, M. (2021). Hedging demand and market intraday momentum. *Journal of Financial Economics*, 142(1), 377-403. <https://doi.org/10.1016/j.jfineco.2021.04.029>
:::

::: {custom-style="Reference"}
Barbon, A. and Buraschi, A. (2020). Gamma fragility. Working paper, School of Finance, University of St. Gallen. <https://www.alexandria.unisg.ch/261487>
:::

::: {custom-style="Reference"}
Black, F. and Scholes, M. (1973). The pricing of options and corporate liabilities. *Journal of Political Economy*, 81(3), 637-654. <https://www.jstor.org/stable/1831029>
:::

::: {custom-style="Reference"}
Dim, C., Eraker, B. and Vilkov, G. (2024). 0DTEs: trading, gamma risk and volatility propagation. Working paper. <https://ssrn.com/abstract=4692190>
:::

::: {custom-style="Reference"}
Gao, L., Han, Y., Li, S. Z. and Zhou, G. (2018). Market intraday momentum. *Journal of Financial Economics*, 129(2), 394-414. <https://doi.org/10.1016/j.jfineco.2018.05.009>
:::

::: {custom-style="Reference"}
Harvey, C. R., Liu, Y. and Zhu, H. (2016). \... and the cross-section of expected returns. *Review of Financial Studies*, 29(1), 5-68. <https://doi.org/10.1093/rfs/hhv059>
:::

::: {custom-style="Reference"}
Ledoit, O. and Wolf, M. (2008). Robust performance hypothesis testing with the Sharpe ratio. *Journal of Empirical Finance*, 15(5), 850-859. <https://doi.org/10.1016/j.jempfin.2008.03.002>
:::

::: {custom-style="Reference"}
Merton, R. C. (1973). Theory of rational option pricing. *Bell Journal of Economics and Management Science*, 4(1), 141-183. <https://www.jstor.org/stable/3003143>
:::

::: {custom-style="Reference"}
Moskowitz, T. J., Ooi, Y. H. and Pedersen, L. H. (2012). Time series momentum. *Journal of Financial Economics*, 104(2), 228-250. <https://doi.org/10.1016/j.jfineco.2011.11.003>
:::

::: {custom-style="Reference"}
Newey, W. K. and West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. *Econometrica*, 55(3), 703-708.
:::

::: {custom-style="Reference"}
SqueezeMetrics (2017). *Gamma Exposure (GEX): Quantifying hedge rebalancing in SPX options.* White paper, March 2016, revised December 2017. Not peer-reviewed. <https://squeezemetrics.com/monitor/download/pdf/white_paper.pdf>
:::

# Appendix A. Data collection

The option quotes were downloaded by a short program that is run once for each weekday. For a given day it takes three steps.

1.  It asks which expiry dates existed that day, with the request `https://api.marketdata.app/v1/options/expirations/SPX/?date=D`, where `D` is the day in the form YYYY-MM-DD. The service answers with the expiry dates that were listed on day `D`.
2.  It keeps only the expiry dates from 0 to 8 calendar days after `D`.
3.  For each one it sends `https://api.marketdata.app/v1/options/chain/SPX/?date=D&expiration=E&strikeLimit=100`, where `E` is the expiry date. The setting `strikeLimit=100` asks for the 100 strike prices nearest the index level. The answer is one row per option contract.

Each request carries a private access key. The program pauses 0.08 seconds between requests, retries a failed request up to four times with a longer wait each time, skips a day for which the service reports no data, and saves finished days to disk so that an interrupted run can resume.

The download was made in two runs. The first covered 2022-05-02 to 2026-06-12 and returned 1,404,196 rows on 1,031 days. The second went back from 2018-01-02 to 2022-04-29 and returned 948,825 rows on 1,090 days. It was added so that the test would include the market declines of late 2018 and early 2020. QQQ prices come from a single call to the FinanceDataReader library, `DataReader("QQQ", "2014-06-01")`, and the Treasury bill rate from `DataReader("FRED:DTB3", "2017-12-01")`.

# Appendix B. Worked example for one contract

This appendix follows the contract of Table [@tab:t2] through the calculation of Section 4.2. The quote is from Market Data (<https://www.marketdata.app>). It is the call SPXW260130C06950000 on 2026-01-27, with $S = 6978.60$, $K = 6,950$, 3 days to expiry so that $\tau = 3/365 = 0.00822$, and a mid quote of $m = 56.70$. Table B1 shows the first steps of Newton's method.

| **Step** $k$ | **Guess** $\sigma_{k}$ | **Model value** $V(\sigma_{k})$ | **Market price** $m$ | **Vega** $\nu(\sigma_{k})$ | **Next guess** |
|:---------:|------------:|------------:|------------:|------------:|------------:|
| 0 | 0.2500 | 79.14 | 56.70 | 247.3 | 0.1593 |
| 1 | 0.1593 | 56.93 | 56.70 | 240.8 | 0.1583 |
| 2 | 0.1583 | 56.70 | 56.70 | 240.7 | 0.1583 |

: **Table B1.** Newton's method for the example contract. After two steps the model value equals the mid quote to the cent.

At the first step the starting guess of 25% gives a model value of 79.14, well above the quoted 56.70, so the guess is lowered by $(79.14 - 56.70)/247.3$ to 0.1593. One more step gives $\widehat{\sigma} = 0.1583$, or 15.83% a year, and the remaining 47 steps change nothing. With $d_{1} = + 0.3082$, $\varphi(d_{1}) = 0.3804$ and $\sqrt{\tau} = 0.09066$, gamma is

$$\Gamma = \frac{0.999885 \times 0.3804}{6978.60 \times 0.1583 \times 0.09066} = 0.003798$$

If the index rises one point, this option's delta rises by 0.003798, and a 1% move in the index, about 70 points, changes its delta by about 0.2650. With 18,166 contracts in existence, the contract's dollar gamma is

$$G = 0.003798 \times 18,166 \times {6978.60}^{2} \times 0.01 = 3.360 \times 10^{7}$$

On that day 1,071 contracts passed the filters, 544 calls and 527 puts across 6 expiry dates. The calls added up to 5.303 × 10^8^ and the puts to 2.696 × 10^8^, so

$$\mathrm{GEX}_{d} = 5.303 \times 10^{8} - 2.696 \times 10^{8} = 2.607 \times 10^{8}$$

The reading is positive and the day was call-heavy. The example contract supplied 4.2% of the day's total dollar gamma, more than any other. Figure B1 shows where the rest of it sat.

![**Figure B1.** The reading for 2026-01-27 by strike and expiry. Each cell is a band of strikes 25 index points wide, for one expiry date. Blue means calls carried more dollar gamma than puts in that cell and red means puts carried more. Adding every cell gives the day's reading. The color scale stops at the 98th percentile, so the few largest cells are shown at full color. Source: author's calculations from Market Data (<https://www.marketdata.app>) quotes.](figs/fig05_chain_heatmap.png){width=6.1in}

# Appendix C. Results under full return accounting

This appendix repeats Tables [@tab:t6], [@tab:t7] and [@tab:t9] with the accounting of Section 5.5: QQQ's total return including dividends, the Treasury bill return on idle capital, a borrow fee of {{acct_borrow}} a year on short positions, and Sharpe ratios on returns in excess of Treasury bills. Positions and transaction costs are unchanged.

[[table:acct6]]

: **Table C1.** Table [@tab:t6] under full return accounting. Performance over {{n_net}} daily returns.

[[table:acct7]]

: **Table C2.** Table [@tab:t7] under full return accounting. Calendar-year returns and the rule's Sharpe ratio. 2018 and 2026 are part-years.

[[table:acct9]]

: **Table C3.** Table [@tab:t9] under full return accounting. Total return in four stress periods.

# Appendix D. Holdout preregistration

The note below was written on 2026-11-12 and committed to the author's private version-control repository at 21:35 Eastern time (commit `f2f6acb`), before any option quote dated after 2026-06-12 was requested. It is reproduced in substance, and the note itself is in the code repository.

**What is frozen.** The rule of Equations [@eq:e1] to [@eq:e16], exactly as coded for the sample: options with 1 to 8 days to expiry, open interest above zero, mid quote above zero and a strike within 20% of the index level; an interest rate of 0.04 and a dividend yield of 0.014; 50 Newton steps from 0.25, bounded between 0.001 and 5; the reading lagged one quote day; the option vote with the day's move after a positive reading and against it after a negative one; the trend vote equal to the sign of QQQ's 20-day log return; the position equal to the average of the two votes; and a cost of 2 basis points per unit traded. No parameter, filter, sign or cost is to be changed for the holdout, whatever it shows.

**The window.** Quote days from 2026-06-15 to 2026-11-11, the last complete trading day before the note was written, from the same vendor with the same requests. The holdout return days are every session in that window, {{ho_planned}} in all. The position carried into the first day is the one decided on the last day of the sample. Days with no usable quotes are skipped, as in the sample. If the vendor does not supply the whole window, the holdout is the longest unbroken stretch that starts on 2026-06-15, and the start date is not moved.

**What is reported, whatever the outcome.** The total return after costs and the annualized Sharpe ratio; the same for buying and holding QQQ and for the trend vote traded long or in cash on the same days; and the number of days long, short and in cash.

**How it is to be read.** With about {{ho_planned}} days the standard error of an annualized Sharpe ratio is about 1.5, so a holdout of this length cannot confirm or reject the rule by itself. It is a first out-of-sample observation.

**What the author already knew.** A version of the rule with a different configuration, using the same-day reading and leverage above one, ran on a simulated account in July 2026 and was stopped on 2026-07-14 after a loss. The rule in its present form has run on a simulated account since early November 2026. No account results are used in this paper. The window is set by the data, from the first day after the sample to the last complete day before the note, and not by those results.
