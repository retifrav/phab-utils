"""
Reconfirming stellar parameters, enriching original datasets
with additional data from various data sources.
"""

from ..utility.files import pickle
from ..utility.databases import tap
from ..utility.databases import simbad

import pandas
import numpy
# import json

from typing import Optional, List, Dict


def lookForParametersInGaia(
    pickleWithOriginalTable: str,
    adqlTable: str,
    adqlParameters: List[str],
    simbadIDversion: Optional[str] = None
) -> pandas.DataFrame:
    """
    Looking for specified parameters in GAIA database:

    1. Opens a pickle file with original Pandas table;
    2. Extracts unique list of star names;
    3. Gets their GAIA IDs from Simbad database;
    4. Queries GAIA database for given parameters;
    5. Adds found parameters to the original table as new columns.

    Example:

    ``` py
    from uio.tasks import reconfirming_stellar_parameters

    tbl = reconfirming_stellar_parameters.lookForParametersInGaia(
        "./data/systems-528n.pkl",
        "gaiadr3.astrophysical_parameters",
        [
            "age_flame",
            "logg_gspphot",
            "mass_flame",
            "mh_gspphot",
            "mh_gspspec",
            "radius_flame",
            "radius_gspphot",
            "teff_esphs",
            "teff_espucd",
            "teff_gspphot",
            "teff_gspspec",
            "teff_msc1",
            "ew_espels_halpha",
            "ew_espels_halpha_model"
        ],
        "dr3"
    )
    ```

    You might need to provide `simbadIDversion` parameter (*the `dr3` value
    here*) if SIMBAD (`uio.utility.databases.simbad.getOtherIDfromSimbad`) returns
    IDs like `DR3 2135237601028549888` and you need to get exactly
    the DR3 ones.

    As a result, your original table `tbl` will be enriched with additional
    columns according to the list of provided astrophysical parameters.
    """

    originalTable = pickle.openPickleAsPandasTable(pickleWithOriginalTable)
    starNames = originalTable["star_name"].unique()

    print("\nGetting GAIA IDs from SIMBAD...\n")

    stars: Dict[str, Optional[str]] = {}
    for star in starNames:
        oid = simbad.getOtherIDfromSimbad(star, "gaia", simbadIDversion)
        if oid is None:
            print(f"- [WARNING] did not GAIA ID for [{star}]")
        else:
            print(f"- found GAIA ID for [{star}]: {oid}")
            stars[star] = oid

    # print(json.dumps(stars, indent=4))

    print("\nLooking for parameters in GAIA...\n")

    for parameter in adqlParameters:
        originalTable[parameter] = numpy.array(numpy.NaN, dtype=float)

    tapService = tap.getServiceEndpoint("GAIA")
    if tapService is None:
        raise SystemError("No endpoint for such TAP service in the list")
    foundCnt = 0
    for star in stars:
        gaiaID = stars[star]
        print(f"- {star} | {gaiaID}...")
        resultsGAIA = tap.queryService(
            tapService,
            " ".join((
                f"SELECT {', '.join(adqlParameters)}",
                f"FROM {adqlTable}",
                f"WHERE source_id = {gaiaID}"
            ))
        )
        if resultsGAIA is None:
            print(f"- [WARNING] did not found anything in GAIA for [{gaiaID}]")
        else:
            tbl = resultsGAIA.to_table().to_pandas()
            foundCnt += 1
            if len(tbl) > 1:
                print(
                    " ".join((
                        "- [WARNING] GAIA has more than one record",
                        f"for ID [{gaiaID}], will take only the first one"
                    ))
                )
            # add found values to the new columns in the original table
            for parameter in adqlParameters:
                originalTable.loc[
                    originalTable["star_name"] == star,
                    parameter
                ] = tbl.head(1)[parameter][0]

    print(f"\nFound parameters for {foundCnt}/{len(stars)} stars\n")

    return originalTable
