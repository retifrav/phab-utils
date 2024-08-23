"""
Getting data from [SIMBAD](https://simbad.u-strasbg.fr/simbad/)
astronomical database.
"""

from astroquery.simbad import Simbad
import re

from typing import Optional

from ..logs.log import logger
from ..databases import tap


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
            idCandidate: str = oid["ID"]
            logger.debug(f"- {idCandidate}")
            if otherIDname.lower() in idCandidate.lower():
                idToLookFor = (
                    f"{otherIDname} {otherIDversion}"
                    if otherIDversion else otherIDname
                )
                if idToLookFor.lower() in idCandidate.lower():
                    if withoutIDprefix:
                        prefixRE = re.compile(
                            rf"{idToLookFor}\s?",
                            re.IGNORECASE
                        )
                        otherID = prefixRE.sub("", idCandidate)
                    else:
                        otherID = idCandidate
                    break
    return otherID


def findObjectID(starName: str) -> Optional[int]:
    """
    Finds object identificator for
    [SIMBAD tables](http://simbad.cds.unistra.fr/simbad/tap/tapsearch.html).
    It is stored in the `oid` field of the `basic` table.

    The discovery process is to compare all the known object identificators
    with the `main_id` field value (*also from the `basic` table*). It is
    not clear, how exactly SIMBAD maintainers choose the main ID for an object,
    so one has to iterate through all the identificators known to SIMBAD.

    Example:

    ``` py
    from uio.utility.databases import simbad

    oid = simbad.findObjectID("A2 146")
    #print(oid)
    ```
    """
    oid: Optional[int] = None

    ids = Simbad.query_objectids(starName)
    if ids is None:
        logger.warning(
            " ".join((
                "SIMBAD database doesn't have information",
                f"about [{starName}]"
            ))
        )
    else:
        logger.debug(f"Checking SIMBAD IDs for [{starName}]:")
        for id in ids:
            idValue = id["ID"]
            logger.debug(f"- {idValue}")
            serviceEndpoint = tap.getServiceEndpoint("simbad")
            if not serviceEndpoint:
                raise ValueError("Couldn't get TAP service endpoint for SIMBAD")
            rez = tap.queryService(
                serviceEndpoint,
                " ".join((
                    "SELECT oid",
                    "FROM basic",
                    f"WHERE main_id = '{idValue}'"
                ))
            )
            if rez:
                oid = rez[0]["oid"]
                logger.debug(
                    " ".join((
                        f"The [{idValue}] is the main ID for [{starName}],",
                        f"SIMBAD object ID is: {oid}"
                    ))
                )
                break
    return oid
