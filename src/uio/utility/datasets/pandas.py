"""
Data processing with [Pandas](https://pandas.pydata.org) tables.

It is important to import this module with an alias, for example:

``` py
from uio.utility.datasets import pandas as pnd
```

Otherwise it will collide with the `pandas` module itself.
"""

import pandas

from typing import List

from ..logs.log import logger


def mergeTables(frames: List[pandas.DataFrame]) -> pandas.DataFrame:
    """
    Merge (*concatenate*) several tables into one. Sorts the index
    and verifies integrity (*will raise an exception
    on duplicate/overlapping index*).

    Example:

    ``` py
    from uio.utility.datasets import pandas as pnd

    frames = []
    # ...
    # frames.append(someTbl1)
    # frames.append(someTbl2)
    # frames.append(someTbl3)
    # ...
    tbl = pnd.mergeTables(frames)
    #print(tbl.head(15))
    ```
    """

    mergedTable = pandas.concat(
        frames,
        verify_integrity=True
    ).sort_index()

    logger.debug(f"Total records in the resulting table: {len(mergedTable)}")
    # logger.debug("Preview of the first rows:")
    # logger.debug(mergedTable.head(15))

    return mergedTable


def deduplicateTable(
    tbl: pandas.DataFrame,
    returnUniques: bool = True
) -> pandas.DataFrame:
    """
    Find duplicate rows in the table:

    - with `returnUniques` set to `True`, returns a table without duplicate
    rows. The first occurrence is always considered to be unique
    in the resulting table, even if it has duplicates;
    - with `returnUniques` set to `False` returns only duplicate rows.

    Example:

    ``` py
    import pandas
    from uio.utility.datasets import pandas as pnd

    tbl = pandas.DataFrame(
        [
            [1, 2, 3],
            [4, 5, 6],
            [1, 2, 3],
            [7, 8, 9],
            [4, 5, 6],
            [3, 1, 2],
            [4, 5, 6]
        ],
        index=[1, 2, 3, 4, 5, 6, 7],
        columns=["a", "b", "c"]
    )

    deduplicatedTable = pnd.deduplicateTable(tbl, True)
    # print(deduplicatedTable)
    #    a  b  c
    # 1  1  2  3
    # 2  4  5  6
    # 4  7  8  9
    # 6  3  1  2
    # print(deduplicatedTable.index.values)
    # [1 2 4 6]

    duplicateRows = pnd.deduplicateTable(tbl, False)
    # print(duplicateRows)
    #    a  b  c
    # 3  1  2  3
    # 5  4  5  6
    # 7  4  5  6
    # print(duplicateRows.index.values)
    # [3 5 7]
    ```
    """
    duplicateRows = tbl.duplicated()
    duplicateRows = duplicateRows[duplicateRows].index

    logger.debug(f"Unique rows count: {len(tbl) - len(duplicateRows)}")
    logger.debug(f"Duplicate rows count: {len(duplicateRows)}")
    # logger.debug(f"Indexes of duplicate rows: {duplicateRows}")

    duplicatesIndex = tbl.index.isin(duplicateRows)

    return (
        tbl[~duplicatesIndex] if returnUniques
        else tbl[duplicatesIndex]
    )
