"""
File operations with [pickles](https://docs.python.org/3/library/pickle.html).
"""

import pathlib

import pandas

from ..datasets import pandas as pnd
from ..files import file as fl
from ..logs.log import logger


def openPickleAsPandasTable(
    pickleFilePath: str | pathlib.Path
) -> pandas.DataFrame:
    """
    Read [Pandas](https://pandas.pydata.org) table from provided pickle file
    (*after checking that the file exists and that it is actually a file*).
    Raises `ValueError`, if the pickle contains something else than
    a Pandas table.

    Example:

    ``` py
    from phab.utils.files import pickle

    pnd = pickle.openPickleAsPandasTable("/path/to/some.pkl")
    #print(pnd.head(15))
    ```
    """
    pickleFile: pathlib.Path | None = fl.fileExists(pickleFilePath)
    if pickleFile is None:
        raise ValueError(
            f"Provided path to [{pickleFilePath}] seems to be wrong"
        )
    else:
        table = pandas.read_pickle(pickleFile)
        if not isinstance(table, pandas.DataFrame):
            raise ValueError(
                f"Provided pickle [{pickleFile}] contains "
                f"{type(table)} instead of a Pandas table"
            )
        return table


def savePandasTableAsPickle(
    pandasTable: pandas.DataFrame,
    pickleFilePath: str | pathlib.Path
) -> None:
    """
    Save [Pandas](https://pandas.pydata.org) table to a pickle file.

    Example:

    ``` py
    from phab.utils.files import pickle

    savePandasTableAsPickle(pnd, "/path/to/some.pkl")
    ```
    """
    filePath: pathlib.Path = pathlib.Path()
    if isinstance(pickleFilePath, str):
        filePath = pathlib.Path(pickleFilePath)
    else:
        filePath = pickleFilePath
    if filePath.exists():
        raise ValueError(f"The [{filePath}] file already exists")
    pandasTable.to_pickle(filePath)


def mergePickles(
    picklesToMergePath: str | pathlib.Path,
    resultingPicklePath: None | str | pathlib.Path
) -> pandas.DataFrame | None:
    """
    Merge several pickle files into one. Looks for pickle files (*`*.pkl`*)
    in the provided folder, reads them to [Pandas](https://pandas.pydata.org)
    tables (*with `utils.files.pickle.openPickleAsPandasTable`*)
    and concatenates those into one final Pandas table
    (*using `utils.datasets.pandas.mergeTables`*).

    Saves resulting Pandas table to file (*if provided path is not `None`*)
    or just returns it.

    Example:

    ``` py
    from phab.utils.files import pickle

    pickle.mergePickles(
        "/path/to/pickles/to/merge/",
        "/path/to/where/to/save/result.pkl"
    )

    # or

    tbl = pickle.mergePickles(
        "/path/to/pickles/to/merge/",
        None
    )
    #print(tbl.head(15))
    ```
    """
    picklesToMerge = None
    inputPath: pathlib.Path | None = fl.directoryExists(picklesToMergePath)
    if inputPath is None:
        raise ValueError(
            f"Provided path to [{picklesToMergePath}] seems to be wrong"
        )
    else:
        picklesToMerge = list(inputPath.glob("**/*.pkl"))

    frames = []

    filesCount = len(picklesToMerge)
    logger.debug(f"Found files: {filesCount}")
    if filesCount == 0:
        raise ValueError("There are no files in the provided folder")
    # elif filesCount == 1:
    #     raise ValueError(
    #         "[ERROR] There is only one file in the provided folder"
    #     )
    else:
        for p in picklesToMerge:
            logger.info(f"Merging {p}...")
            tbl = openPickleAsPandasTable(p)
            logger.debug(f"Records in this pickle: {len(tbl)}")
            frames.append(tbl)

    mergedTable = pnd.mergeTables(frames)

    if resultingPicklePath:
        savePandasTableAsPickle(mergedTable, resultingPicklePath)
        return None
    else:
        return mergedTable
