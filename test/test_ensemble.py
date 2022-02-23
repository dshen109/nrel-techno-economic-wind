from wind_ensemble import ensemble

import pandas as pd

from unittest import TestCase


class TestEnsemble(TestCase):
    forecaster = ensemble.Ensemble(coordinates=(None, None))
    pywtk_forecast = pd.DataFrame(
        {'hour_ahead_power': [0.5, 0.6, 0.7],
         'hour_ahead_power_p90': [0.4, 0.55, 0.69],
         'hour_ahead_power_p10': [0.6, 0.7, 0.8]}
    )

    def test_forecast_basic(self):
        predictions = self.forecaster.create_ensemble(
            self.pywtk_forecast, 10, kurtosis=20)
        self.assertEqual(predictions.shape, (3, 10))

    def test_forecast_percentiles_respected(self):
        n = 1000
        predictions = self.forecaster.create_ensemble(
            self.pywtk_forecast, n=n, kurtosis=20)
        self.assertEqual(predictions.shape, (3, n))
        above = (predictions >=
                 self.pywtk_forecast['hour_ahead_power_p10']).sum(axis=1)
        below = (predictions <=
                 self.pywtk_forecast['hour_ahead_power_p90']).sum(axis=1)
        for i in range(len(self.pywtk_forecast)):
            self.assertLessEqual(above.iloc[i], n / 10)
            self.assertLessEqual(below.iloc[i], n / 10)


class TestEnsembleRealData(TestCase):
    coordinates = 39.740223, -105.168885  # NREL
    horizon = (1, 24)

    def setUp(self):
        self.ensemble = ensemble.Ensemble(
            self.coordinates, horizon=self.horizon)

    def test_forecast_ensemble(self):
        forecasts = self.ensemble.forecast_ensemble(
            pd.to_datetime('2013-01-01 00:00', utc=True),
            pd.to_datetime('2013-01-01 23:59', utc=True), n=100,
            utc=True)
        self.assertEqual(sorted(forecasts.keys()), [1, 24])
