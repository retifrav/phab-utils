"""
Getting data from [SIMBAD](https://simbad.u-strasbg.fr/simbad/)
astronomical database.
"""

from astroquery.simbad import Simbad
import re

from typing import Optional

from ..logs.log import logger


def getOtherIDfromSimbad(
    starName: str,
    otherIDname: str,
    otherIDversion: Optional[str] = None,
    withoutIDprefix: bool = True
) -> Optional[str]:
    """
    Finds object identificator from a particular catalogue. SIMBAD returns
    a list of identificators prepended with the catalogue name, and this
    function finds the identificator for the specified catalogue and returns
    just the identificator. In addition to that, some catalogues have versions,
    so it is possible to specify which one if of interest.

    For instance, if you need to find the identificator for `TWA 20` star
    in `Gaia` catalog version `DR3`, then SIMBAD will return
    `Gaia DR3 6132146982868270976` value for it, out of which this function
    will extract `6132146982868270976` as the result.

    Example:

    ``` py
    from uio.utility.databases import simbad

    otherID = simbad.getOtherIDfromSimbad("TWA 20", "gaia", "dr3")
    #print(otherID)
    ```
    """
    otherID = None

    otherIDs = Simbad.query_objectids(starName)
    if otherIDs is None:
        logger.warning(
            " ".join((
                "SIMBAD database doesn't have information",
                f"about [{starName}]"
            ))
        )
    else:
        logger.debug(f"Checking SIMBAD IDs for [{starName}]:")
        for oid in otherIDs:
            logger.debug(f"- {oid["ID"]}")
            if otherIDname.lower() in oid["ID"].lower():
                idToLookFor = (
                    f"{otherIDname} {otherIDversion}"
                    if otherIDversion else otherIDname
                )
                if idToLookFor.lower() in oid["ID"].lower():
                    if withoutIDprefix:
                        prefixRE = re.compile(
                            rf"{idToLookFor}\s?",
                            re.IGNORECASE
                        )
                        otherID = prefixRE.sub("", oid["ID"])
                    else:
                        otherID = oid["ID"]
                    break
    return otherID
