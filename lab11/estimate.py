"""Part C: estimate a rare probability honestly. TODO 4, 6 and 7."""
from __future__ import annotations

import math

import numpy as np

from avsim import space
from .search import proposal_logpdf


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for k successes in n trials.

    Must behave at k = 0 (lower bound 0, upper bound > 0) where the plain normal interval collapses to [0, 0].
    Return (0, 1) for n = 0.
    """
    if n == 0:
        return (0.0, 1.0)
    p_hat = k / n
    denom = 1 + z ** 2 / n
    center = (p_hat + z ** 2 / (2 * n)) / denom
    margin = z * math.sqrt(p_hat * (1 - p_hat) / n + z ** 2 / (4 * n ** 2)) / denom
    lo = max(0.0, center - margin)
    hi = min(1.0, center + margin)
    return (lo, hi)


def log_weights(Z, Bn, nat: space.Natural, prop: dict, beta: float = 0.2) -> np.ndarray:
    """log p(u) - log q(u) for each row, where q is the DEFENSIVE MIXTURE
    q = (1 - beta) * proposal + beta * natural.

    nat.logpdf(Z, Bn) gives log p; proposal_logpdf(prop, Z, Bn) gives log of the CEM proposal.
    Use np.logaddexp so a weight of 1e-30 does not underflow to 0.
    """
    lp = nat.logpdf(Z, Bn)
    lq_prop = proposal_logpdf(prop, Z, Bn)
    lp_nat = space.Natural().logpdf(Z, Bn)
    # mixture: log((1-beta)*exp(lq_prop) + beta*exp(lp_nat))
    lq_mix = np.logaddexp(np.log(1 - beta) + lq_prop, np.log(beta) + lp_nat)
    return lp - lq_mix


def is_estimate(logw: np.ndarray, y: np.ndarray, z: float = 1.96) -> dict:
    """Importance-sampling estimate of P(y = 1) under the natural distribution.

    w = exp(logw); p = mean(w * y)  (NOT normalised by sum(w): that version is biased for small n);
    se = std(w * y, ddof=1) / sqrt(n); CI = [max(0, p - z se), p + z se];
    Kish effective sample size ess = (sum w)^2 / sum(w^2).
    Return dict(p=, lo=, hi=, se=, ess=, n=).
    """
    w = np.exp(logw)
    p = np.mean(w * y)
    n = len(logw)
    se = np.std(w * y, ddof=1) / math.sqrt(n)
    ess = (np.sum(w) ** 2) / np.sum(w ** 2) if np.sum(w ** 2) > 0 else 0.0
    return dict(p=float(p), lo=max(0.0, p - z * se), hi=p + z * se, se=float(se), ess=float(ess), n=n)


def rule_of_three(n_eff: float) -> float:
    """Given: 95% upper bound on a probability when 0 events were seen in n_eff independent tries."""
    return 3.0 / max(n_eff, 1.0)
