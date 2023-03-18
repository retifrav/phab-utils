"""
Getting data from various databases
via [TAP](https://www.ivoa.net/documents/TAP/) interface.
"""

# what is available for importing from __init__.py
# __all__ = [
#     "tapServices",
#     "getServiceEndpoint",
#     "queryService"
# ]

import pyvo
import pandas

from typing import Optional

tapServices = {
    "NASA": {
        # case-sensitive TAP
        "endpoint": "https://exoplanetarchive.ipac.caltech.edu/TAP"
    },
    "PADC": {
        "endpoint": "http://voparis-tap-planeto.obspm.fr/tap"
    },
    "GAIA": {
        "endpoint": "https://gea.esac.esa.int/tap-server/tap"
    }
}
"""
Dictionary of the most common TAP services.
"""


def getServiceEndpoint(tapServiceName: str) -> Optional[str]:
    """
    Example:

    ``` py
    from uio.databases import tap

    tapService = tap.getServiceEndpoint("PADC")
    if tapService is None:
        raise SystemError("No endpoint for such TAP service in the list")
    #print(tapService)
    ```
    """
    tapService = tapServices.get(tapServiceName)
    if tapService:
        return tapService["endpoint"]
    else:
        return None


def queryService(
    tapEndpoint: str,
    adqlQuery: str
) -> Optional[pandas.DataFrame]:
    """
    Example:

    ``` py
    from uio.databases import tap

    tbl = tap.queryService(
        "http://voparis-tap-planeto.obspm.fr/tap",
        " ".join((
            "SELECT star_name, granule_uid, mass, radius, period, semi_major_axis",
            "FROM exoplanet.epn_core",
            "WHERE star_name = 'Kepler-107'",
            "ORDER BY granule_uid"
        ))
    )
    #print(tbl)
    ```
    """
    tapService = pyvo.dal.TAPService(tapEndpoint)
    results = tapService.search(adqlQuery)
    if len(results):
        return results.to_table().to_pandas()
    else:
        return None
