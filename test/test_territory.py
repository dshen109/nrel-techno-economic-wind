import os
from wind_ensemble import territory
from unittest import TestCase

if "PYWTK_CACHE_DIR" not in os.environ:
    raise RuntimeError("Must specify PYWTK_CACHE_DIR env var")


class TestTerritory(TestCase):

    def test_site_meta(self):
        states = ['New York', 'Rhode Island']
        metadata = territory.metadata(states)
        self.assertListEqual(
            metadata.state.unique().tolist(),
            ['New York', 'Rhode Island'])
