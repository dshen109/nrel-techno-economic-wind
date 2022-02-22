from wind_ensemble import stats

from unittest import TestCase


class TestHyperbolic(TestCase):

    def test_non_skewed_fit(self):
        mean = 0
        percentiles = {0.1: -1, 0.9: 1}
        kurtosis = 1
        hyperbolic, _ = stats.fit_hyperbolic(mean, percentiles, kurtosis)
        self.assertAlmostEqual(hyperbolic.cdf(-1), 0.1, places=2)
        self.assertAlmostEqual(hyperbolic.cdf(1), 0.9, places=2)
        self.assertAlmostEqual(hyperbolic.stats('k'), kurtosis, places=2)

    def test_skewed_fit(self):
        mean = 0
        percentiles = {0.1: -1, 0.9: 4}
        kurtosis = 2
        hyperbolic, _ = stats.fit_hyperbolic(
            mean, percentiles, kurtosis, percentile_weight=100)
        self.assertAlmostEqual(hyperbolic.cdf(-1), 0.1, places=2)
        self.assertAlmostEqual(hyperbolic.cdf(4), 0.9, places=2)
        self.assertAlmostEqual(hyperbolic.stats('k'), kurtosis, places=2)
