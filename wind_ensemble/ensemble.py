"""
Create ensemble forecast.
"""

class Ensemble:
    """Creation of ensemble forecasts."""
    _allowable_horizons = (1, 4, 6, 24)

    def __init__(self, horizon=24, err=None):
        """
        :param int horizon: Forecast horizon, hours.
        :param dict error: Forecast errors for each horizon
        :param 
        """
        assert horizon in self._allowable_horizons

