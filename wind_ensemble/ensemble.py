"""
Create ensemble forecast.
"""
import numpy as np
import pandas as pd
from pywtk.site_lookup import get_3tiersites_from_wkt
from pywtk.wtk_api import get_nc_data, WIND_FCST_DIR
from pywtk import site_lookup

from . import stats


class Ensemble:
    """Creation of ensemble forecasts."""
    _allowable_horizons = (1, 4, 6, 24)
    # 1 and 24 hour values estimated from NREL wind power error report; others
    # are arbitrary
    _default_error_kurtosis = {1: 18, 4: 14, 6: 10, 24: 2.5}

    def __init__(self, coordinates, horizon=24, isclose_distance=10,
                 error_kurtosis=None):
        """
        :param tuple coordinates: lat / long of forecast location (decimal deg)
        :param int_or_list horizon: Forecast horizon(s), hours.
        :param dict error: Forecast errors for each horizon
        :param float isclose_distance: Largest distance [km?] between wind
            toolkit data point and forecast coordinates to be `close`,
            otherwise will take the mean of the three closest points
            TODO: Should really do an inverse-distance mean...
        """
        if isinstance(horizon, int):
            horizon = [horizon]
        for h in horizon:
            assert h in self._allowable_horizons

        self.latitude, self.longitude = coordinates
        self.horizon = horizon
        self.isclose_distance = isclose_distance
        if error_kurtosis is None:
            self.error_kurtosis = self._default_error_kurtosis.copy()
        else:
            self.error_kurtosis = error_kurtosis

    def create_ensemble(self, forecast, n, kurtosis):
        """Create *n* p.u. forecasts from the base pywtk forecast.

        :param DataFrame forecast: pywtk site forecast; should be normalized to
            p.u. power output.
        :param int n: Number of data points to generate.
        :param float kurtosis: Kurtosis for p.u. power prediction error
        """
        # For each timestep, we fit a hyperbolic distribution to the
        # _p90 10th percentile, mean, and _p10 90th percentile to estimate the
        # errors, then generate n power predictions at that point.
        ten_percentile_col = [c for c in forecast.columns if '_p90' in c][0]
        ninety_percentile_col = [c for c in forecast.columns if '_p10' in c][0]
        mean_col = set(forecast.columns) - \
            set((ten_percentile_col, ninety_percentile_col))
        if len(mean_col) > 1:
            raise ValueError("Ambiguous mean column")
        mean_col = list(mean_col)[0]
        forecasts = []
        for i, row in forecast.iterrows():
            percentiles = {0.1: row[ten_percentile_col],
                           0.9: row[ninety_percentile_col]}
            error_dist = stats.fit_hyperbolic(
                row[mean_col], percentiles=percentiles, kurtosis=kurtosis
            )[0]
            forecasts.append(error_dist.rvs(size=n))
        forecasts = np.array(forecasts)
        forecasts = np.around(np.clip(forecasts, 0, 1), 4)
        return pd.DataFrame(forecasts, index=forecast.index)

    def forecast_ensemble(self, start, end, n=100, utc=True):
        """Return an ensemble of *n* forecasts of p.u. power generated using
        the error bounds."""
        site_forecasts = {}
        horizon_ensembles = {}
        for site, distance in self.close_sites:
            site_forecasts[site] = get_nc_data(
                site, start, end, self.forecast_attributes, utc=utc,
                nc_dir=WIND_FCST_DIR
            )
            # Normalize by site capacity to get p.u.
            site_forecasts[site] /= _capacity(site)
            for horizon in self.horizon:
                horizon_ensembles[horizon] = []
                horizon_cols = [c for c in site_forecasts[site].columns
                                if _to_forecast_str(horizon) in c]

                horizon_ensembles[horizon].append(self.create_ensemble(
                    site_forecasts[site][horizon_cols], n,
                    kurtosis=self.error_kurtosis[horizon]))
        # Return mean forecasts across sites
        # TODO: We should do inverse distance weighting.
        result = {}
        for horizon in self.horizon:
            frame = pd.concat(horizon_ensembles[horizon])
            result[horizon] = frame.groupby(frame.index).mean()
        return result

    @property
    def forecast_attributes(self):
        """Forecast attributes based on the horizon(s)."""
        attrs = []
        for horizon in self.horizon:
            attrs.extend(
                [
                    _to_forecast_str(horizon),
                    _to_forecast_str(horizon) + '_p90',
                    _to_forecast_str(horizon) + '_p10',
                ]
            )
        return attrs

    @property
    def point(self):
        """WKT representation of coordinates (NREL convention is long first)"""
        return f"POINT({self.longitude} {self.latitude})"

    @property
    def close_sites(self):
        """Tuple of top 1 or 3 sites that are close and their distances."""
        close = get_3tiersites_from_wkt(self.point)
        if close.iloc[0]['distance'] < self.isclose_distance:
            return ((close.iloc[0]['gid'], close.iloc[0]['distance']),)
        return (
            (close.iloc[0]['gid'], close.iloc[0]['distance']),
            (close.iloc[1]['gid'], close.iloc[1]['distance']),
            (close.iloc[2]['gid'], close.iloc[2]['distance'])
        )


def _capacity(site):
    """Return capacity metadata for a site."""
    return site_lookup.sites.loc[site, 'capacity']


def _to_forecast_str(horizon):
    if horizon == 24:
        return 'day_ahead_power'
    elif horizon in (4, 6):
        return f'{horizon}_hour_ahead_power'
    elif horizon == 1:
        return 'hour_ahead_power'
    else:
        raise ValueError
