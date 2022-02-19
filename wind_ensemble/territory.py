"""
Get NREL metadata for a predefined territory.
"""
from pywtk import site_lookup


def metadata(state):
    """
    Return DataFrame of metadata for sites in a state(s).

    :param str_or_list state: U.S. states to query.
    """
    if isinstance(state, str):
        state = [state]

    return site_lookup.sites.loc[site_lookup.sites['state'].isin(state)]
