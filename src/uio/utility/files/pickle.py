"""
File operations with [pickles](https://docs.python.org/3/library/pickle.html).
"""

import pathlib
import pandas

from typing import Union, List


def openPickleAsPandasTable(f: Union[str, pathlib.Path]) -> pandas.DataFrame:
    """
    Read a [Pandas](https://pandas.pydata.org) table from provided pickle file
    (*after checking that the file exists and that it is actually a file*).

    Example:

    ``` py
    from uio.utility.files import pickle

    pnd = pickle.openPickleAsPandasTable("/path/to/some.pkl")
    #print(pnd.head(15))
    ```
    """
    filePath: pathlib.Path = pathlib.Path()
    if isinstance(f, str):
        filePath = pathlib.Path(f)
    else:
        filePath = f
    if not filePath.exists():
        raise SystemError(f"The path [{filePath}] does not exist")
    if not filePath.is_file():
        raise SystemError(f"The [{filePath}] is not a file")
    return pandas.read_pickle(filePath)


def mergePickles(
    picklesToMergePath: Union[str, pathlib.Path],
    resultingPicklePath: Union[str, pathlib.Path]
) -> None:
    """
    Merge several pickle files into one. Looks for pickle files
    in the provided folder, reads them to Pandas tables
    (*with `uio.utility.files.pickle.openPickleAsPandasTable`*),
    concatenates those into one and saves to resulting pickle.
    Checks for existing files, sorts the index and verifies integrity
    (*will raise an exception on duplicate/overlapping index*).

    Example:

    ``` py
    import pathlib
    from uio.utility.files import pickle

    pickle.mergePickles(
        "/path/to/pickles/to/merge/",
        "/path/to/where/to/save/result.pkl"
    )
    ```
    """
    inputPath: pathlib.Path = pathlib.Path()
    if isinstance(picklesToMergePath, str):
        inputPath = pathlib.Path(picklesToMergePath)
    else:
        inputPath = picklesToMergePath

    if not inputPath.exists():
        raise SystemError(f"The path [{inputPath}] does not exist")
    if not inputPath.is_dir():
        raise SystemError(f"The [{inputPath}] is not a folder")

    picklesToMerge = list(inputPath.glob("**/*.pkl"))

    frames = []

    filesCount = len(picklesToMerge)
    print(f"Found files: {filesCount}\n")
    if filesCount == 0:
        raise ValueError("There are no files in the provided folder")
    # elif filesCount == 1:
    #     raise ValueError("[ERROR] There is only one file in the provided folder")
    else:
        for p in picklesToMerge:
            print(f"Merging {p}...")
            tbl = openPickleAsPandasTable(p)
            print(f"Records in this pickle: {len(tbl)}\n")
            frames.append(tbl)

    mergedTable = pandas.concat(frames, verify_integrity=True).sort_index()
    print(f"Total records in the resulting table: {len(mergedTable)}")
    # print("Preview of the first rows:")
    # print(mergedTable.head(15))

    resultingFilePath: pathlib.Path = pathlib.Path()
    if isinstance(resultingPicklePath, str):
        resultingFilePath = pathlib.Path(resultingPicklePath)
    else:
        resultingFilePath = resultingPicklePath

    if resultingFilePath.exists():
        raise ValueError(f"The [{resultingFilePath}] file already exists")

    mergedTable.to_pickle(resultingFilePath)
