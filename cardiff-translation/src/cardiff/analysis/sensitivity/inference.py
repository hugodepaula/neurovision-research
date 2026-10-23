"""Inference conditional on exchangeable questionnaire items, not general text."""

from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd
from scipy.stats import norm, rankdata


def bootstrap_indices(n: int, resamples: int, seed: int, groups=None) -> np.ndarray:
    rng = np.random.default_rng(seed)
    if groups is None:
        return rng.integers(0, n, size=(resamples, n))
    labels = np.asarray(groups)
    if len(labels) != n:
        raise ValueError("Stratum labels must match the item axis")
    return np.concatenate(
        [
            rng.choice(
                np.flatnonzero(labels == g),
                size=(resamples, np.sum(labels == g)),
                replace=True,
            )
            for g in sorted(set(labels))
        ],
        axis=1,
    )


def mean_interval(x, indices: np.ndarray, confidence: float = 0.95) -> dict:
    x = np.asarray(x, dtype=float)
    if x.ndim != 1 or len(x) < 2 or not np.isfinite(x).all():
        raise ValueError("Need at least two finite, paired item scores")
    if not 0 < confidence < 1:
        raise ValueError("Confidence must be between zero and one")
    estimate = float(x.mean())
    draws = x[indices].mean(axis=1)
    alpha = (1 - confidence) / 2
    low, high = np.quantile(draws, [alpha, 1 - alpha])
    result = dict(
        mean=estimate,
        percentile_low=float(low),
        percentile_high=float(high),
        bca_low=np.nan,
        bca_high=np.nan,
        bca_status="ok",
        n_items=len(x),
    )
    centered = x - estimate  # Proportional to mean jackknife influence.
    denominator = 6 * np.sum(centered**2) ** 1.5
    if denominator == 0:
        result["bca_status"] = "constant_sample_not_estimable"
        return result
    acceleration = np.sum(centered**3) / denominator
    # Mid-rank correction for ties, matching scipy.stats.bootstrap.
    p = (np.sum(draws < estimate) + np.sum(draws <= estimate)) / (2 * len(draws))
    if not 0 < p < 1:
        result["bca_status"] = "extreme_bias_correction_not_estimable"
        return result
    z0 = norm.ppf(p)
    z = norm.ppf([alpha, 1 - alpha])
    transformed = norm.cdf(z0 + (z0 + z) / (1 - acceleration * (z0 + z)))
    if not np.isfinite(transformed).all() or transformed[0] >= transformed[1]:
        result["bca_status"] = "invalid_acceleration_not_estimable"
        return result
    if transformed.min() < 1 / len(draws) or transformed.max() > 1 - 1 / len(draws):
        result["bca_status"] = "unstable_tail_resolution"
    result["bca_low"], result["bca_high"] = map(float, np.quantile(draws, transformed))
    return result


def holm(p_values) -> np.ndarray:
    p = np.asarray(p_values, dtype=float)
    order = np.argsort(p)
    adjusted = np.empty(len(p))
    adjusted[order] = np.minimum(
        1, np.maximum.accumulate(p[order] * np.arange(len(p), 0, -1))
    )
    return adjusted


def pairwise_inference(
    matrix: pd.DataFrame,
    indices: np.ndarray,
    seed: int,
    permutations: int = 10000,
    margin: float = 0.01,
) -> pd.DataFrame:
    """Two-sided paired sign randomization; Holm family = all pairs per metric.

    Validity requires within-item label exchangeability. The margin is an
    exploratory raw-score tolerance, not a validated clinical difference.
    """
    values = matrix.to_numpy(float)
    pairs = list(combinations(range(values.shape[1]), 2))
    differences = np.column_stack([values[:, a] - values[:, b] for a, b in pairs])
    observed = differences.mean(axis=0)
    counts = np.zeros(len(pairs), dtype=int)
    rng = np.random.default_rng(seed)
    for start in range(0, permutations, 500):
        batch = min(500, permutations - start)
        signs = rng.choice([-1, 1], size=(batch, len(matrix)))
        simulated = signs @ differences / len(matrix)
        counts += np.sum(np.abs(simulated) >= np.abs(observed) - 1e-14, axis=0)
    p_values = (counts + 1) / (permutations + 1)
    adjusted = holm(p_values)
    rows = []
    for i, (a, b) in enumerate(pairs):
        ci = mean_interval(differences[:, i], indices)
        ci90 = mean_interval(differences[:, i], indices, confidence=0.90)
        rows.append(
            dict(
                candidate_a=matrix.columns[a],
                candidate_b=matrix.columns[b],
                **ci,
                p_permutation=float(p_values[i]),
                p_holm=float(adjusted[i]),
                exploratory_margin=margin,
                ci90_low=ci90["bca_low"],
                ci90_high=ci90["bca_high"],
                within_exploratory_margin=bool(
                    ci90["bca_low"] > -margin and ci90["bca_high"] < margin
                ),
                significant_holm=bool(adjusted[i] < 0.05),
            )
        )
    return pd.DataFrame(rows)


def ranking_stability(matrix: pd.DataFrame, indices: np.ndarray) -> pd.DataFrame:
    draws = matrix.to_numpy()[indices].mean(axis=1)
    ranks = rankdata(-draws, axis=1, method="average")
    ties = np.isclose(draws, draws.max(axis=1, keepdims=True), rtol=0, atol=1e-12)
    shares = ties / ties.sum(axis=1, keepdims=True)
    return pd.DataFrame(
        {
            "candidate_id": matrix.columns,
            "mean": matrix.mean().values,
            "mean_rank": ranks.mean(axis=0),
            "rank_p025": np.quantile(ranks, 0.025, axis=0),
            "rank_p975": np.quantile(ranks, 0.975, axis=0),
            "first_place_share": shares.mean(axis=0),
        }
    )
