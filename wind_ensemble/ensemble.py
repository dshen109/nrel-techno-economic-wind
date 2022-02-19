"""
Create ensemble forecast.
"""
from pywtk.site_lookup import get_3tiersites_from_wkt
from pywtk.wtk_api import get_nc_data, WIND_FCST_DIR, WIND_MET_NC_DIR

class Ensemble:
    """Creation of ensemble forecasts."""
    _allowable_horizons = (1, 4, 6, 24)

    def __init__(self, coordinates, horizon=24, isclose_distance=10):
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

    def create_ensemble(self, forecast, n):
        """Create *n* forecasts from the base pywtk forecast."""
        pass

    def forecast_ensemble(self, start, end, n=100, utc=True):
        """Return an ensemble of *n* forecasts of p.u. power generated using
        the error bounds."""
        site_forecasts = {}
        site_ensembles = {}
        for site, distance in self._close_sites:
            site_forecasts[site] = get_nc_data(
                site, start, end, self.forecast_attributes, utc=utc,
                nc_dir=WIND_FCST_DIR
            )
            site_ensembles[site] = self.create_ensemble(
                site_forecasts[site], n)

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
        return f"POINT({self.long} {self.lat})"

    @property
    def close_sites(self):
        """Tuple of top 1 or 3 sites that are close and their distances."""
        close = get_3tiersites_from_wkt(self.point)
        if close.iloc[0]['Distance'] < self.isclose_distance:
            return ((close.iloc[0]['Site_id'], close.iloc[0]['Distance']),)
        return (
            (close.iloc[0]['Site_id'], close.iloc[0]['Distance']),
            (close.iloc[1]['Site_id'], close.iloc[1]['Distance']),
            (close.iloc[2]['Site_id'], close.iloc[2]['Distance'])
        )


def _to_forecast_str(horizon):
    if horizon == 24:
        return 'day_ahead_power'
    elif horizon in (4, 6):
        return f'{horizon}_hour_ahead_power'
    elif horizon == 1:
        return 'hour_ahead_power'
    else:
        raise ValueError
