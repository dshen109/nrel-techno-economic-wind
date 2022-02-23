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
            mean, percentiles, kurtosis, percentile_weight=100,
            mean_weight=1, kurtosis_weight=1)
        self.assertAlmostEqual(hyperbolic.cdf(-1), 0.1, places=2)
        self.assertAlmostEqual(hyperbolic.cdf(4), 0.9, places=2)
        self.assertAlmostEqual(hyperbolic.stats('k'), kurtosis, places=2)

    def test_another_fit(self):
        mean = 0.010283576
        percentiles = {0.1: 0.0, 0.9: 0.1240082}
        kurtosis = 18
        x0 = (3, 0, 1, 0)
        hyperbolic, _ = stats.fit_hyperbolic(
            mean, percentiles, kurtosis, percentile_weight=100, x0=x0)
        self.assertAlmostEqual(hyperbolic.cdf(0), 0.1, places=2)
        self.assertAlmostEqual(hyperbolic.cdf(0.12401), 0.9, places=2)
        self.assertAlmostEqual(hyperbolic.stats('k'), kurtosis, places=2)

        # mean
        # 0.010283576
        # hyperbolic(mean, alpha, beta, delta).stats()
        # (array(0.06196856), array(0.00348014))
        # alpha
        # 261.0398055858605
        # beta
        # 14.900258500382094
