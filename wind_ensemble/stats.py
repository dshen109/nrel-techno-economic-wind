"""Do statistics."""
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
                   mean_weight=100, percentile_weight=100, kurtosis_weight=1,
                   x0=(2, 0, 1, 0), tol=1e-8, maxiter=1000):
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
    cons = [{'type': 'ineq', 'fun': lambda x: x[0] - np.abs(x[1]) - 0.000001},
            {'type': 'ineq', 'fun': lambda x: x[2] - 0.000001}]
    result = optimize.minimize(objective, x0, constraints=cons, tol=tol,
                               options={'maxiter': maxiter})
    if not result.success:
        raise RuntimeError(
            f"Could not successfully fit distribution: {result.message}")
    alpha, beta, delta, loc = result.x
    return hyperbolic(loc, alpha, beta, delta), result.x
