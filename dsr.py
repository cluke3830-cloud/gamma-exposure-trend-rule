"""Deflated Sharpe Ratio (Bailey & Lopez de Prado 2014) — self-contained, no
scipy (runs on EC2 bare py3.9). DSR = P(true Sharpe > 0) after deflating the
observed Sharpe for (a) the number of trials tried and (b) non-normal returns
(skew/kurtosis). A DSR near 1 means the edge survives multiple-testing; near
0.5 means it's indistinguishable from the best of N lucky coin-flips."""
import math

_GAMMA = 0.5772156649015329   # Euler-Mascheroni


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_ppf(p: float) -> float:
    """Inverse normal CDF — Acklam's rational approximation (~1e-9 abs error)."""
    if p <= 0.0:
        return -math.inf
    if p >= 1.0:
        return math.inf
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5]) * q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def _moments(r):
    n = len(r)
    mu = sum(r) / n
    var = sum((x - mu) ** 2 for x in r) / n
    sd = math.sqrt(var) if var > 0 else 0.0
    if sd == 0:
        return mu, sd, 0.0, 3.0
    skew = sum((x - mu) ** 3 for x in r) / (n * sd ** 3)
    kurt = sum((x - mu) ** 4 for x in r) / (n * sd ** 4)   # non-excess (normal=3)
    return mu, sd, skew, kurt


def deflated_sharpe(returns, n_trials: int = 1) -> float:
    """Return DSR in [0,1]. returns = per-observation strategy returns."""
    r = [x for x in returns if x == x]          # drop NaN
    T = len(r)
    if T < 3:
        return 0.0
    mu, sd, skew, kurt = _moments(r)
    if sd == 0:
        return 0.0
    sr = mu / sd                                 # per-observation Sharpe
    # expected-max Sharpe under the null across n_trials (Bailey-Prado);
    # trial-Sharpe variance approximated by the SE^2 of a null Sharpe = 1/T
    N = max(int(n_trials), 1)
    if N == 1:
        sr0 = 0.0
    else:
        v = 1.0 / T
        sr0 = math.sqrt(v) * ((1 - _GAMMA) * norm_ppf(1 - 1.0 / N)
                              + _GAMMA * norm_ppf(1 - 1.0 / (N * math.e)))
    denom = math.sqrt(max(1 - skew * sr + (kurt - 1) / 4.0 * sr ** 2, 1e-12))
    z = (sr - sr0) * math.sqrt(T - 1) / denom
    return norm_cdf(z)
