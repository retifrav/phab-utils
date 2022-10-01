from astroquery.simbad import Simbad
import re

from typing import Optional


def getOtherIDfromSimbad(
    starName: str,
    otherIDname: str,
    otherIDversion: Optional[str],
    withoutIDprefix: bool = True
) -> Optional[str]:
    otherID = None
    otherIDs = Simbad.query_objectids(starName)
    for oid in otherIDs:
        if otherIDname in oid["ID"].lower():
            idToLookFor = (
                f"{otherIDname} {otherIDversion}"
                if otherIDversion else otherIDname
            )
            if idToLookFor in oid["ID"].lower():
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
