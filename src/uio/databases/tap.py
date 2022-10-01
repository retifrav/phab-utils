# __all__ = ["tapServices", "getServiceEndpoint", "queryService"]

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
) -> pandas.DataFrame:
    # print(tapEndpoint, adqlQuery)
    tapService = pyvo.dal.TAPService(tapEndpoint)
    resultingTable = tapService.search(adqlQuery).to_table()
    return resultingTable.to_pandas()

