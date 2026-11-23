"""
Getting light curves data.
"""

import pathlib
import re
from re import Pattern
from typing import Literal

import lightkurve
import numpy
import pandas
from astropy.table import Table
from pandera import pandas as pandera

from ..files import file as fl
from ..logs.log import logger

# apparently, one cannot set long/short threshold,
# hence this dictionary
#
# there are actually more authors available,
# but we are only interested in these
#
authors: dict[str, dict] = {
    "Kepler":
    {
        "mission": "Kepler",
        "cadence":
        {
            "long": [1800],
            "short": [60]
        }
    },
    "K2":
    {
        "mission": "K2",
        "cadence":
        {
            "long": [1800],
            "short": [60]
        }
    },
    "SPOC":
    {
        "mission": "TESS",
        "cadence":
        {
            "long": [600],
            "short": [120],
            "fast": [20]
        }
    },
    "TESS-SPOC":
    {
        "mission": "TESS",
        "cadence":
        {
            "long": []  # any cadence is long
        }
    }
}
"""
Dictionary of authors, their cadence values and mapping to missions.
"""

missionSectorRegExes: dict[str, Pattern] = {
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

lightCurveFluxTableSchema = pandera.DataFrameSchema(
    {
        "time": pandera.Column(numpy.float64),
        "flux": pandera.Column(numpy.float32, nullable=True),
        "fluxError": pandera.Column(numpy.float32, nullable=True)
    },
    index=pandera.Index(int, unique=True),
    strict=True,  # only specified columns are allowed
    coerce=False  # do not cast other types to the specified one
)
"""
Table schema for light curve fluxes.
"""


def getLightCurveStats(
    starName: str,
    detailed: bool = True
) -> dict[str, dict]:
    """
    Gather statistics about available cadence values for a given star.

    If `detailed` is set to `False`, then function will skip collecting
    cadence values count by sectors, so resulting statistics will only
    contain total count of values.

    Example:

    ``` py
    from phab.utils.databases import lightcurves

    stats = lightcurves.getLightCurveStats("Kepler-114")
    if not stats:
        print("Didn't find any results for this star")
    else:
        missionName = "Kepler"
        cadenceType = "long"
        sectors = stats.get(
            missionName,
            {}
        ).get(cadenceType)
        if sectors is None:
            print(
                " ".join((
                    "There doesn't seem to be any sectors",
                    f"with [{cadenceType}] cadence by [{missionName}]"
                ))
            )
        else:
            totalProperty = "total"
            sectorsCount = sectors.get(totalProperty)
            if sectorsCount is None:
                print(
                    " ".join((
                        f"For some reason, the [{totalProperty}] property",
                        f"is missing from the [{cadenceType}] cadence",
                        f"collection by [{missionName}]"
                    ))
                )
            else:
                print(
                    " ".join((
                        f"Total amount of sectors with [{cadenceType}]",
                        f"cadence by [{missionName}]: {sectorsCount}",
                    ))
                )
                bySectors = sectors.get("by-sectors")
                if bySectors is None:
                    print(
                        " ".join((
                            "For some reason, the [total] property is missing",
                            f"from the [{cadenceType}] cadence collection",
                            f"by [{missionName}]"
                        ))
                    )
                else:
                    for s in bySectors:
                        print(f"- {s}: {bySectors[s]}")
    ```
    """
    stats: dict[str, dict] = {}

    lghtcrvs = lightkurve.search_lightcurve(
        starName,
        author=tuple(authors.keys())
    )
    if len(lghtcrvs) != 0:
        tbl: pandas.DataFrame = lghtcrvs.table.to_pandas()[
            ["author", "exptime", "mission"]
        ]
        logger.debug(tbl)

        for author, group in tbl.groupby("author"):
            # the `isinstance()` narrows the `Hashable` group key down to `str`
            if not isinstance(author, str) or author not in authors:
                raise ValueError(f"Unknown author: {author}")
            mission = authors[author]["mission"]
            if not stats.get(mission):
                stats[mission] = {}
            for cadence in ["long", "short", "fast"]:
                if cadence in authors[author]["cadence"]:
                    stats[mission][cadence] = {}
                    cadenceValues: list[int] = (
                        authors[author]["cadence"][cadence]
                    )
                    cadences: pandas.DataFrame
                    if len(cadenceValues) > 0:  # take only specified values
                        # perhaps both of these should be normalized to int
                        cadences = group.query("exptime == @cadenceValues")
                    else:  # any value is good
                        cadences = group

                    # total count
                    stats[mission][cadence]["total"] = len(cadences)

                    if detailed:
                        # count by sectors
                        stats[mission][cadence]["by-sectors"] = {}
                        for m in cadences["mission"]:
                            # logger.debug(cadences.query("mission == @m")[
                            #     "exptime"
                            # ].values)
                            sectorMatch = re.search(
                                missionSectorRegExes[mission],
                                m
                            )
                            if not sectorMatch:
                                raise ValueError(
                                    "Couldn't extract sector from "
                                    f"this mission value: {m}"
                                )
                            sector = sectorMatch.group(1)
                            if not stats[mission][cadence]["by-sectors"].get(
                                sector
                            ):  # this sector hasn't been added yet
                                stats[mission][cadence]["by-sectors"][
                                    sector
                                ] = {}
                                # save the cadence/exptime too (assuming
                                # that it is the same for every sector entry)
                                stats[mission][cadence]["by-sectors"][sector][
                                    "exptime"
                                ] = cadences.query("mission == @m")[
                                    "exptime"
                                ].values[0]  # there must be a better way
                            try:
                                stats[mission][cadence][
                                    "by-sectors"
                                ][sector]["count"] += 1
                            except KeyError:
                                stats[mission][cadence][
                                    "by-sectors"
                                ][sector]["count"] = 1
    return stats


def getLightCurveIDs(
    starName: str
) -> dict[str, list[str]]:
    """
    Based on available cadence values statistics for a given star,
    get names of missions and cadences. For instance, in order to pass
    them to `altaipony.lcio.from_mast()`.

    Example:

    ``` py
    from phab.utils.databases import lightcurves
    from altaipony.lcio import from_mast

    starName = "LTT 1445 A"
    lightCurveIDs = {}

    try:
        lightCurveIDs = lightcurves.getLightCurveIDs(starName)
    except ValueError as ex:
        print(f"Failed to get light curves missons and cadences. {ex}")
        raise
    if not lightCurveIDs:
        raise ValueError("Didn't find any results for this star")
    #print(lightCurveIDs)

    for m in lightCurveIDs.keys():
        #print(f"Mission: {m}")
        for c in lightCurveIDs[m]:
            #print(f"- {c}")
            flc = from_mast(
                starName,
                mode="LC",
                cadence=c,
                mission=m
            )
            #print(flc)
    ```
    """
    lightCurveIDs: dict[str, list[str]] = {}

    stats: dict[str, dict] = getLightCurveStats(
        starName,
        detailed=False
    )
    if not stats:
        raise ValueError("Didn't find any results for this star")

    # the order matters, it goes from most important to least important,
    # and in fact long cadence is so not important that it is discarded
    # if there is fast or short cadence available
    cadencePriority = ["fast", "short", "long"]

    for m, missionStats in stats.items():
        lightCurveIDs[m] = []
        for priorityThreshold, cp in enumerate(cadencePriority):
            # if there is already fast or short cadence in the list,
            # don't take long cadence (except for mission K2, because
            # its long cadence is what's most important even if
            # there are also fast and short ones)
            if any(lightCurveIDs[m]) and priorityThreshold > 1 and m != "K2":
                break
            if cp in missionStats:
                # print(f"Count [{cp}]: {missionStats[cp]['total']}")
                totalCnt = missionStats[cp].get("total")
                if totalCnt and totalCnt != 0:
                    lightCurveIDs[m].append(cp)
                # else:
                #     print(
                #         " ".join((
                #             f"[WARNING] The [{cp}] cadence count",
                #             f"in [{m}] is 0 (or missing)"
                #         ))
                #     )

    return lightCurveIDs


def fitsToPandas(
    fitsFilePath: str,
    fitsType: Literal["tess", "kepler"] | None = None,
    qualityBitmask: Literal["none", "default", "hard", "hardest"] = "default",
    dropNanTimes: bool = True,
    convertTimesToSeconds: bool = False
) -> pandas.DataFrame:
    """
    Open a generic light curves [FITS](https://en.wikipedia.org/wiki/FITS) file
    and create a Pandas table from it. Only the fluxes, their times
    and errors columns are taken.

    FITS stores data in big-endian byte order, but the resulting table
    has its columns in the native byte order of the system, as Astropy
    converts them already.

    Example:

    ``` py
    from phab.utils.databases import lightcurves

    pnd = lightcurves.fitsToPandas(
        "./data/tess2019006130736-s0007-0000000266744225-0131-s_lc.fits",
        fitsType="tess",
        qualityBitmask="default",
        dropNanTimes=True,
        convertTimesToSeconds=True
    )

    #print(pnd)
    ```
    """
    lc = None
    fitsFile: pathlib.Path | None = fl.fileExists(fitsFilePath)
    if fitsFile is None:
        raise ValueError(
            f"Provided path to [{fitsFilePath}] seems to be wrong"
        )
    else:
        # light curve files from the archives have unit strings that are not in the FITS standard
        # (TESS files have `BJD - 2457000, days`, `e-/s` and `pixels`), and Astropy warns about
        # every such column on every read. The units are not needed here, because `numpy.array()`
        # below drops them, so they are left unrecognized without warnings, just like Lightkurve
        # ignores these warnings too (its issue #1216)
        lc = Table.read(fitsFile, unit_parse_strict="silent")

    # exclude values which do not satisfy the required quality
    if fitsType is not None:
        msk = None
        if fitsType == "tess":
            msk = lightkurve.utils.TessQualityFlags.create_quality_mask(
                quality_array=lc["QUALITY"],
                bitmask=qualityBitmask
            )
        elif fitsType == "kepler":
            msk = lightkurve.utils.KeplerQualityFlags.create_quality_mask(
                quality_array=lc["QUALITY"],
                bitmask=qualityBitmask
            )
        else:
            print(
                "[WARNING] Unknown FITS type, don't know "
                "which quality mask to use"
            )
        lc = lc[msk]

    # FITS stores data in big-endian byte order, and so do the columns
    # of `lc`, but this array is already in the native byte order of the system,
    # because `Table.as_array()` (which is what `numpy.array()` gets) converts
    # all columns to native since Astropy 1.1, so there is nothing to swap
    narr = numpy.array(lc)

    # astropy.time does not(?) support NaN
    if dropNanTimes:
        nantimes = numpy.isnan(narr["TIME"].data)
        if numpy.any(nantimes):
            print(
                f"[DEBUG] {numpy.sum(nantimes)} rows were excluded, "
                "because their time values are NaN"
            )
        narr = narr[~nantimes]

    # apparently, one cannot just take columns from `lc`/`narr` directly,
    # hence this intermediate table
    pndraw = pandas.DataFrame(narr)
    logger.debug(f"Light curve table columns: {pndraw.columns}")

    flux = pandas.DataFrame(
        columns=[
            "time",
            "flux",
            "fluxError"
        ]
    )
    flux["time"] = pndraw["TIME"]
    flux["flux"] = pndraw["PDCSAP_FLUX"]
    flux["fluxError"] = pndraw["PDCSAP_FLUX_ERR"]

    # in case excluding NaN times right after `Table.read()` is less efficient
    # if dropNanTimes:
    #     flux = flux.dropna(subset=["time"])

    if convertTimesToSeconds:
        flux["time"] = flux["time"] * 24 * 60 * 60

    if dropNanTimes:
        lightCurveFluxTableSchema.validate(flux)
    else:
        lightCurveFluxTableSchema.update_column(
            "time",
            dtype=numpy.float64,
            nullable=True
        ).validate(flux)

    return flux


def lightCurveTessToPandas(
    lightKurve: lightkurve.lightcurve.TessLightCurve,
    convertTimesToSeconds: bool = False
) -> pandas.DataFrame:
    """
    Converting a TESS light curve object to a Pandas table. In general,
    it does almost the same thing as
    `utils.databases.lightcurves.fitsToPandas()`,
    but here there it uses a TESS-specific reading function, and also
    there is no need to drop NaN times "manually".

    Example:

    ``` py
    from phab.utils.databases import lightcurves
    import lightkurve

    downloadLC: bool = False
    lc = None
    if downloadLC:
        search_result = lightkurve.search_lightcurve(
            "Karmn J07446+035",
            author="SPOC",
            cadence="short"
        )
        lc = search_result[0].download(
            quality_bitmask="default"
        )
    else:
        lc = lightkurve.TessLightCurve.read(
            "./data/tess2019006130736-s0007-0000000266744225-0131-s_lc.fits",
            quality_bitmask="default"
        )

    pnd = lightcurves.lightCurveTessToPandas(lc, convertTimesToSeconds=True)

    #print(pnd)
    ```
    """
    pndraw = lightKurve.to_pandas()
    logger.debug(f"Light curve table columns: {pndraw.columns}")

    flux = pandas.DataFrame(
        columns=[
            "time",
            "flux",
            "fluxError"
        ]
    )

    flux["time"] = pndraw.index
    flux["flux"] = pndraw["pdcsap_flux"].values
    flux["fluxError"] = pndraw["pdcsap_flux_err"].values

    if convertTimesToSeconds:
        flux["time"] = flux["time"] * 24 * 60 * 60

    lightCurveFluxTableSchema.validate(flux)

    return flux
