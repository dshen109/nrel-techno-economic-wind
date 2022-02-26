"""Do statistics."""
import itertools

import numpy as np
from scipy import stats
from scipy import optimize


def hyperbolic(loc, alpha, beta, delta):
    """Return scipy distribution for a hyperbolic distribution.

    Parameters follow Barndorff (1978) (lambda=1).
    """
    a = alpha * delta
    b = beta * delta
    scale = delta
    loc = loc
    return stats.genhyperbolic(p=1, a=a, b=b, loc=loc, scale=scale)


def fit_hyperbolic(mean, percentiles, kurtosis,
                   mean_weight=100, percentile_weight=2, kurtosis_weight=10,
                   x0=None, tol=1e-9, maxiter=1000, method=None):
    """
    Return a hyperbolic distribution fit to the data.

    :param float mean: Expected mean of the hyperbolic distribution.
    :param dict percentiles: Dictionary of percentiles to fit; ex
        {0.1: -1, 0.9: 2}
    :param float kurtosis: Desired kurtosis.
    :param float percentile_weight: Weighting for percentile optimization.
    :param float kurtosis_weight: Weighting for kurtosis optimization.
    :param tuple x0: Starting guess for optimization.
    :param int maxiter: Maximum iteration for scipy solver
    :return: tuple scipy frozen distribution and optimal parameters
    """
    def objective(x):
        """Function to minimize"""
        alpha, beta, delta, loc = x
        distribution = hyperbolic(loc, alpha, beta, delta)
        score = 0
        percentile_scores = []
        for percentile, value in percentiles.items():
            percentile_scores.append(
                100 * np.abs(distribution.cdf(value) - percentile) ** 2 *
                percentile_weight
            )
        # Take the maximum of the score so we don't just fit one side of the
        # distribution
        score += max(percentile_scores)
        mean_dist, kurtosis_dist = distribution.stats(moments='mk')
        score += (
            (1 + np.abs(kurtosis - kurtosis_dist) / kurtosis) ** 2
            * kurtosis_weight)
        score += (1 + np.abs(mean - mean_dist)) ** 2 * mean_weight
        return score
    cons = [{'type': 'ineq', 'fun': lambda x: x[0] - np.abs(x[1]) - 1e-9}]
    bounds = optimize.Bounds(
        [1e-9, -np.inf, 1e-9, -1],
        [np.inf, np.inf, np.inf, 1]
    )
    results = {}
    failed = {}
    best_x = None
    best_score = np.inf
    if x0 is not None:
        result = optimize.minimize(
            objective, x0, constraints=cons, tol=tol,
            options={'maxiter': maxiter, 'disp': True},
            bounds=bounds, method=method)
        if result.success:
            results[x0] = result
            best_x = result.x
            best_score = result.fun
    else:
        # Sample from as many starting points as possible to prevent getting
        # stuck in local minimum
        x0sample = np.logspace(-9, 2, 3)
        x1sample = np.logspace(-2, 2, 2)  # Reflect to negatives
        x1sample = np.concatenate([-x1sample, x1sample])
        x2sample = np.logspace(-9, 2, 3)
        x3sample = np.linspace(0, 1, 2)
        for i, x0 in enumerate(
                itertools.product(x0sample, x1sample, x2sample, x3sample)):
            if np.abs(x0[1]) > x0[0]:
                continue
            result = optimize.minimize(
                objective, x0, constraints=cons, tol=tol,
                options={'maxiter': maxiter, 'disp': False},
                bounds=bounds, method=method)
            if not result.success:
                failed[x0] = result
                continue
            results[x0] = result
            if result.fun < best_score:
                best_score = result.fun
                best_x = result.x
    if best_x is None:
        raise RuntimeError(
            f"Could not successfully fit distribution: {result.message}")
    alpha, beta, delta, loc = best_x
    return hyperbolic(loc, alpha, beta, delta), best_x, results
