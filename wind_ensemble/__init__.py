import os
# Late setting of env so pywtk loads correctly
pywtk_cache = os.path.join(os.environ['HOME'], 'dropbox', 'pywtk-data')
os.environ['PYWTK_CACHE_DIR'] = pywtk_cache

import pandas
from pywtk.site_lookup import get_3tiersites_from_wkt
from pywtk.wtk_api import get_nc_data, WIND_FCST_DIR, WIND_MET_NC_DIR


if __name__ == '__main__':
    pywtk_cache = os.path.join(
        os.environ['HOME'], 'dropbox', 'pywtk-data')

    os.environ['PYWTK_CACHE_DIR'] = pywtk_cache
    site_id = '0'
    start = pandas.Timestamp('2013-01-01', tz='utc')
    end = pandas.Timestamp('2013-01-07', tz='utc')
    utc = True
    attributes = ["power", "wind_direction", "wind_speed", "temperature", "pressure", "density"]
    met_data = get_nc_data(
        site_id, start, end, attributes, utc=utc, nc_dir=WIND_MET_NC_DIR)
    attributes_hour = [
        "hour_ahead_power", "hour_ahead_power_p90",
        "hour_ahead_power_p10"]
    attributes_4_hour = [
        "4_hour_ahead_power", "4_hour_ahead_power_p90",
        "4_hour_ahead_power_p10"]
    attributes_6_hour = [
        "6_hour_ahead_power", "6_hour_ahead_power_p90",
        "6_hour_ahead_power_p10"]
    attributes_day = [
        "day_ahead_power", "day_ahead_power_p90", "day_ahead_power_p10"]
    fcst_attributes = attributes_hour + attributes_4_hour + attributes_6_hour + attributes_day
    fcst_data = get_nc_data(
        site_id, start, end, fcst_attributes, utc=utc, nc_dir=WIND_FCST_DIR)

    # Longitude first
    sites = get_3tiersites_from_wkt('POINT(23.8000 -68.33000)')
    assert 0
