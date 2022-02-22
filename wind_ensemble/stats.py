"""Do statistics."""
import numpy as np
from scipy import stats
from scipy import optimize


def hyperbolic(mu, alpha, beta, delta):
    """Return scipy distribution for a hyperbolic distribution.

    Parameters follow Barndorff (1978) (lambda=1).
    """
    a = alpha * delta
    b = beta * delta
    scale = delta
    loc = mu
    return stats.genhyperbolic(p=1, a=a, b=b, loc=loc, scale=scale)


def fit_hyperbolic(mean, percentiles, kurtosis,
                   percentile_weight=100, kurtosis_weight=1, x0=(2, 0, 1),
                   tol=1e-8, maxiter=1000):
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
        alpha, beta, delta = x
        distribution = hyperbolic(mean, alpha, beta, delta)
        score = 0
        for percentile, value in percentiles.items():
            score += (
                np.abs(distribution.cdf(value) - percentile) *
                percentile_weight
            )
        kurtosis_dist = distribution.stats(moments='k')
        score += np.abs(kurtosis - kurtosis_dist) * kurtosis_weight
        return score
    cons = [{'type': 'ineq', 'fun': lambda x: x[0] - np.abs(x[1])}]
    result = optimize.minimize(objective, x0, constraints=cons, tol=tol,
                               options={'maxiter': maxiter})
    if not result.success:
        raise RuntimeError(
            f"Could not successfully fit distribution: {result.message}")
    alpha, beta, delta = result.x
    return hyperbolic(mean, alpha, beta, delta), result.x
