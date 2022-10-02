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


def getServiceEndpoint(tapServiceName: str) -> Optional[str]:
    tapService = tapServices.get(tapServiceName)
    if tapService:
        return tapService["endpoint"]
    else:
        return None


def queryService(
    tapEndpoint: str,
    adqlQuery: str
) -> Optional[pandas.DataFrame]:
    #
    tapService = pyvo.dal.TAPService(tapEndpoint)
    results = tapService.search(adqlQuery)
    if len(results):
        return results.to_table().to_pandas()
    else:
        return None
