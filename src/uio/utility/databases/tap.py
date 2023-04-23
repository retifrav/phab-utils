"""
Getting data from various databases
via [TAP](https://ivoa.net/documents/TAP/) interface.
"""

# what is available for importing from __init__.py
# __all__ = [
#     "services",
#     "queryService",
#     ...
# ]

import pyvo

from typing import Optional, Dict, List, Tuple, Any

services: Dict[str, Dict] = {
    "NASA":
    {
        # case-sensitive URL
        "endpoint": "https://exoplanetarchive.ipac.caltech.edu/TAP",
        "parameters-that-are-strings":
        [
            "st_metratio",
            "st_spectype"
        ],
        "parameters-that-have-errors":
        [
            "period",
            "pl_massj",
            "pl_orbper",
            "pl_orbsmax",
            "pl_radj",
            "semi_major_axis"
        ]
    },
    "PADC":
    {
        "endpoint": "http://voparis-tap-planeto.obspm.fr/tap"
    },
    "GAIA":
    {
        "endpoint": "https://gea.esac.esa.int/tap-server/tap"
    }
}
"""
Dictionary of the most common TAP services.
"""

mappings: Dict[str, Dict] = {
    "NASA-to-PADC":
    {
        "planets":
        {
            "ima_flag": "ima_flag",
            "pl_massj": "mass",
            "pl_massjerr1": "mass_error_max",
            "pl_massjerr2": "mass_error_min",
            "pl_massjlim": "pl_massjlim",
            "pl_name": "granule_uid",
            "pl_orbeccen": "eccentricity",
            "pl_orbincl": "inclination",
            "pl_orbper": "period",
            "pl_orbpererr1": "period_error_max",
            "pl_orbpererr2": "period_error_min",
            "pl_orbperlim": "pl_orbperlim",
            "pl_orbsmax": "semi_major_axis",
            "pl_orbsmaxerr1": "semi_major_axis_error_max",
            "pl_orbsmaxerr2": "semi_major_axis_error_min",
            "pl_orbsmaxlim": "pl_orbsmaxlim",
            "pl_radj": "radius",
            "pl_radjerr1": "radius_error_max",
            "pl_radjerr2": "radius_error_min",
            "pl_radjlim": "pl_radjlim",
            "rv_flag": "rv_flag",
            "tran_flag": "tran_flag",
            "ttv_flag": "ttv_flag"
        },
        "stars":
        {
            "cb_flag": "cb_flag",
            "hostname": "star_name",
            "ra": "ra",
            "st_age": "star_age",
            "st_lum": "st_lum",
            "st_mass": "star_mass",
            "st_met": "star_metallicity",
            "st_metratio": "st_metratio",
            "st_rad": "star_radius",
            "st_rotp": "st_rotp",
            "st_spectype": "star_spec_type",
            "st_teff": "star_teff",
            "sy_dist": "sy_dist",
            "sy_pnum": "sy_pnum",
            "sy_snum": "sy_snum"
        }
    }
}
"""
Mapping tables columns between different databases.
"""


def getServiceEndpoint(tapServiceName: str) -> Optional[str]:
    """
    Find TAP endpoint by service/database name.

    Example:

    ``` py
    from uio.utility.databases import tap

    tapServiceEndpoint = tap.getServiceEndpoint("PADC")
    if tapServiceEndpoint is None:
        raise SystemError("No endpoint for such TAP service in the list")
    print(tapServiceEndpoint)
    ```
    """
    tapService = services.get(tapServiceName)
    if tapService:
        tapServiceEndpoint = tapService.get("endpoint")
        if tapServiceEndpoint:
            return tapServiceEndpoint
        else:
            f"[ERROR] {tapServiceName} has no registered endpoint"
            return None
    else:
        print(
            f"[ERROR] There is no TAP service under the name {tapServiceName}"
        )
        return None


def queryService(
    tapEndpoint: str,
    adqlQuery: str
) -> Optional[pyvo.dal.tap.TAPResults]:
    """
    Send [ADQL](https://ivoa.net/documents/ADQL/) request to the TAP service
    and return results. Those can be then converted to a Pandas table.

    Example:

    ``` py
    from uio.utility.databases import tap

    tbl = tap.queryService(
        "http://voparis-tap-planeto.obspm.fr/tap",
        " ".join((
            "SELECT star_name, granule_uid, mass, radius, period, semi_major_axis",
            "FROM exoplanet.epn_core",
            "WHERE star_name = 'Kepler-107'",
            "ORDER BY granule_uid"
        ))
    ).to_table().to_pandas()
    #print(tbl)
    ```
    """
    tapService = pyvo.dal.TAPService(tapEndpoint)
    results = tapService.search(adqlQuery)
    if len(results):
        return results
    else:
        return None


def getStellarParameterFromNASA(
    systemName: str,
    param: str
) -> Optional[Any]:
    """
    Get the latest (*the newest*) published stellar parameter
    from NASA database.

    Example:

    ``` py
    from uio.utility.databases import tap

    val = tap.getStellarParameterFromNASA("Kepler-11", "st_teff")
    #print(val)
    ```
    """
    serviceEndpoint = getServiceEndpoint("NASA")
    if not serviceEndpoint:
        raise ValueError("Couldn't get TAP service endpoint for NASA")
    results = queryService(
        serviceEndpoint,
        " ".join((
            f"SELECT {param}",
            f"FROM ps",
            f"WHERE hostname = '{systemName}' AND {param} IS NOT NULL",
            "ORDER BY pl_pubdate DESC"
        ))
    )
    if results:
        # print(f"All results for this parameter: {results}")
        val = results[0].get(param)
        return val
    else:
        return None


def getPlanetaryParameterFromNASA(
    planetName: str,
    param: str
) -> Optional[Any]:
    """
    Get the latest (*the newest*) published planetary parameter
    from NASA database.

    Example:

    ``` py
    from uio.utility.databases import tap

    val = tap.getPlanetaryParameterFromNASA("Kepler-11 b", "pl_massj")
    #print(val)
    ```
    """
    serviceEndpoint = getServiceEndpoint("NASA")
    if not serviceEndpoint:
        raise ValueError("Couldn't get TAP service endpoint for NASA")
    results = queryService(
        serviceEndpoint,
        " ".join((
            f"SELECT {param}",
            f"FROM ps",
            f"WHERE pl_name = '{planetName}' AND {param} IS NOT NULL",
            "ORDER BY pl_pubdate DESC"
        ))
    )
    if results:
        # print(f"All results for this parameter: {results}")
        return results[0].get(param)
    else:
        return None


def getParameterFromNASA(
    systemName: str,
    planetName: str,
    param: str
) -> Optional[Any]:
    """
    Get the latest (*the newest*) published parameter from NASA database.
    The parameter kind (*stellar or planetary*) is determined
    based on the `uio.utility.databases.tap.mappings` list. This might be
    convenient when one only has a list of parameters names
    without specifying which one is of which kind.

    Example:

    ``` py
    from uio.utility.databases import tap

    systemName = "Kepler-11"
    planetName = "Kepler-11 b"
    params = ["st_teff", "pl_massj"]
    for p in params:
        val = tap.getParameterFromNASA(systemName, planetName, p)
        #print(val)
    ```
    """
    result = None
    if param in mappings["NASA-to-PADC"]["stars"]:  # get stellar parameter
        result = getStellarParameterFromNASA(systemName, param)
    else:  # get planet parameter
        result = getPlanetaryParameterFromNASA(planetName, param)
    return result


def getParameterErrorsFromNASA(
    systemName: str,
    planetName: str,
    param: str
) -> Tuple[Optional[float], Optional[float]]:
    """
    Get the latest (*the newest*) published stellar or planetary
    parameter errors from NASA database. This is a convenience function
    that uses `uio.utility.databases.tap.getParameterFromNASA`
    to get `PARAMerr2` (*minimum error*) and `PARAMerr1` (*maximum error*).

    Example:

    ``` py
    from uio.utility.databases import tap

    systemName = "Kepler-11"
    planetName = "Kepler-11 b"
    params = ["st_teff", "pl_massj"]
    for p in params:
        errMin, errMax = tap.getParameterErrorsFromNASA(systemName, planetName, p)
        #print(errMin, errMax)
    ```
    """
    errMin = getParameterFromNASA(systemName, planetName, f"{param}err2")
    errMax = getParameterFromNASA(systemName, planetName, f"{param}err1")
    return errMin, errMax


def getParameterFromPADC(
    planetName: str,
    param: str
) -> Optional[Any]:
    """
    Get stellar or planetary parameter from PADC database.

    Example:

    ``` py
    from uio.utility.databases import tap

    val = tap.getParameterFromPADC("Kepler-11 b", "mass")
    #print(val)
    ```
    """
    serviceEndpoint = getServiceEndpoint("PADC")
    if not serviceEndpoint:
        raise ValueError("Couldn't get TAP service endpoint for PADC")
    results = queryService(
        serviceEndpoint,
        " ".join((
            f"SELECT {param}",
            f"FROM exoplanet.epn_core",
            f"WHERE granule_uid = '{planetName}' AND {param} IS NOT NULL"
        ))
    )
    if results:
        return results[0].get(param)
    else:
        return None


def getParameterErrorsFromPADC(
    planetName: str,
    param: str
) -> Tuple[Optional[float], Optional[float]]:
    """
    Get stellar or planetary parameter errors from PADC database.
    This is a convenience function that uses
    `uio.utility.databases.tap.getParameterFromPADC` to get `PARAM_error_min`
    and `PARAM_error_max`.

    Example:

    ``` py
    from uio.utility.databases import tap

    errMin, errMax = tap.getParameterErrorsFromPADC("Kepler-11 b", "mass")
    #print(errMin, errMax)
    ```
    """
    errMin = getParameterFromPADC(planetName, f"{param}_error_min")
    errMax = getParameterFromPADC(planetName, f"{param}_error_max")
    return errMin, errMax
