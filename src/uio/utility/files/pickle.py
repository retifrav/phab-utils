"""
File operations with [pickles](https://docs.python.org/3/library/pickle.html).
"""

import pathlib
import pandas

from typing import Optional, List, Union

from ..datasets import pandas as pnd
from ..logs.log import logger


def openPickleAsPandasTable(
    pickleFilePath: Union[str, pathlib.Path]
) -> pandas.DataFrame:
    """
    Read [Pandas](https://pandas.pydata.org) table from provided pickle file
    (*after checking that the file exists and that it is actually a file*).

    Example:

    ``` py
    from uio.utility.files import pickle

    pnd = pickle.openPickleAsPandasTable("/path/to/some.pkl")
    #print(pnd.head(15))
    ```
    """
    filePath: pathlib.Path = pathlib.Path()
    if isinstance(pickleFilePath, str):
        filePath = pathlib.Path(pickleFilePath)
    else:
        filePath = pickleFilePath
    if not filePath.exists():
        raise ValueError(f"The path [{filePath}] does not exist")
    if not filePath.is_file():
        raise ValueError(f"The path [{filePath}] is not a file")
    return pandas.read_pickle(filePath)


def savePandasTableAsPickle(
    pandasTable: pandas.DataFrame,
    pickleFilePath: Union[str, pathlib.Path]
) -> None:
    """
    Save [Pandas](https://pandas.pydata.org) table to a pickle file.

    Example:

    ``` py
    from uio.utility.files import pickle

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
    picklesToMergePath: Union[str, pathlib.Path],
    resultingPicklePath: Union[None, str, pathlib.Path]
) -> Optional[pandas.DataFrame]:
    """
    Merge several pickle files into one. Looks for pickle files (*`*.pkl`*)
    in the provided folder, reads them to [Pandas](https://pandas.pydata.org)
    tables (*with `uio.utility.files.pickle.openPickleAsPandasTable`*)
    and concatenates those into one final Pandas table
    (*using `uio.utility.datasets.pandas.mergeTables`*).

    Saves resulting Pandas table to file (*if provided path is not `None`*)
    or just returns it.

    Example:

    ``` py
    from uio.utility.files import pickle

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
    inputPath: pathlib.Path = pathlib.Path()
    if isinstance(picklesToMergePath, str):
        inputPath = pathlib.Path(picklesToMergePath)
    else:
        inputPath = picklesToMergePath

    if not inputPath.exists():
        raise ValueError(f"The path [{inputPath}] does not exist")
    if not inputPath.is_dir():
        raise ValueError(f"The [{inputPath}] is not a folder")

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
