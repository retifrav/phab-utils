"""
Getting data from [SIMBAD](https://simbad.u-strasbg.fr/simbad/)
astronomical database.
"""

from astroquery.simbad import Simbad
import re

from typing import Optional


def getOtherIDfromSimbad(
    starName: str,
    otherIDname: str,
    otherIDversion: Optional[str] = None,
    withoutIDprefix: bool = True
) -> Optional[str]:
    """
    Example:

    ``` py
    from uio.utility.databases import simbad

    otherID = simbad.getOtherIDfromSimbad(star, "gaia", "dr3")
    #print(otherID)
    ```
    """
    otherID = None
    otherIDs = Simbad.query_objectids(starName)
    if otherIDs is None:
        print(
            " ".join((
                "- [WARNING] Simbad database doesn't have information",
                f"about [{starName}]"
            ))
        )
    else:
        # print(f"Simbad IDs for {starName}:")
        for oid in otherIDs:
            # print(f"- {oid['ID']}")
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
