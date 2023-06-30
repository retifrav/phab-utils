"""
Getting light curves data.
"""

import lightkurve
import re

from typing import Optional, Dict, Pattern

# apparently, one cannot set long/short threshold,
# hence this dictionary
#
# there are actually more authors available,
# but we are only interested in these
#
authors: Dict[str, Dict] = {
    "Kepler":
    {
        "mission": "Kepler",
        "cadence":
        {
            "long": 1800,
            "short": 60
        }
    },
    "K2":
    {
        "mission": "K2",
        "cadence":
        {
            "long": 1800,
            "short": 60
        }
    },
    "SPOC":
    {
        "mission": "TESS",
        "cadence":
        {
            "long": 600,
            "short": 120,
            "fast": 20
        }
    },
    "TESS-SPOC":
    {
        "mission": "TESS",
        "cadence":
        {
            "long": 600
        }
    }
}
"""
Dictionary of authors, their cadence values and mapping to missions.
"""

missionSectorRegExes: Dict[str, Pattern] = {
    "Kepler": re.compile(
        r"^Kepler\s\w+\s(\d+)$"  # Kepler Quarter 15
    ),
    "K2": re.compile(
        r"^K2\s\w+\s(\d+)$"  # K2 Campaign 12
    ),
    "TESS": re.compile(
        r"^TESS\s\w+\s(\d+)$"  # TESS Sector 40
    )
}
"""
Dictionary of regular expressions for extracting sectors.
"""


def getLightCurveStats(
    starName: str,
    detailed: bool = True
) -> Optional[Dict[str, Dict]]:
    """
    Gather statistics about available cadence values for a given star.

    If `detailed` is set to `False`, then function will skip collecting
    cadence values count by sectors, so resulting statistics will only
    contain total count of values.

    Example:

    ``` py
    from uio.utility.databases import lightcurves

    stats = lightcurves.getLightCurveStats("Kepler-114")
    if stats is None:
        raise ValueError("Didn't find any results for this star")
    #print(stats)
    ```
    """
    stats: Dict[str, Dict] = {}

    lghtcrvs = lightkurve.search_lightcurve(
        starName,
        author=tuple(authors.keys())
    )
    lghtcrvsCnt = len(lghtcrvs)
    if lghtcrvsCnt == 0:
        return None

    tbl = lghtcrvs.table.to_pandas()[["author", "exptime", "mission"]]
    # print(tbl)

    for author, group in (tbl.groupby("author")):
        if author not in authors:
            raise ValueError(f"Unknown author: {author}")
        mission = authors[author]["mission"]
        if not stats.get(mission):
            stats[mission] = {}
        for cadence in ["long", "short", "fast"]:
            if cadence in authors[author]["cadence"]:
                stats[mission][cadence] = {}
                cadenceValue = authors[author]["cadence"][cadence]
                # perhaps both of these should be normalized to int first
                cadences = group.query("exptime == @cadenceValue")

                # total count
                stats[mission][cadence]["total"] = len(cadences)

                if detailed:
                    # count by sectors
                    stats[mission][cadence]["by-sectors"] = {}
                    for m in cadences["mission"]:
                        sectorMatch = re.search(missionSectorRegExes[mission], m)
                        if not sectorMatch:
                            raise ValueError(
                                " ".join((
                                    "Couldn't extract sector from",
                                    f"this mission value: {m}"
                                ))
                            )
                        sector = sectorMatch.group(1)
                        try:
                            stats[mission][cadence]["by-sectors"][sector] += 1
                        except KeyError:
                            stats[mission][cadence]["by-sectors"][sector] = 1
    return stats
