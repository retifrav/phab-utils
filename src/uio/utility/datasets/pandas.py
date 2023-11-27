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
    Merge (*concatenate*) several Pandas tables into one. Sorts the index
    and verifies integrity (*will raise an exception on duplicate/overlapping
    index*).

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
