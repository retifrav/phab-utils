import pytest

import pandas
import numpy

from uio.utility.datasets import pandas as pnd


def test_merge_pandas() -> None:
    rng = numpy.random.default_rng()
    vals = rng.integers(0, 20, size=(3, 5))
    clmns = ["a", "b", "c", "d", "e"]

    frames = [
        pandas.DataFrame(vals, index=[1, 2, 3], columns=clmns),
        pandas.DataFrame(vals, index=[4, 5, 6], columns=clmns),
        pandas.DataFrame(vals, index=[7, 8, 9], columns=clmns)
    ]

    tbl = pnd.mergeTables(frames)

    assert isinstance(tbl, pandas.DataFrame)
    assert len(tbl) == 9


def test_deduplicate_table() -> None:
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
    assert isinstance(deduplicatedTable, pandas.DataFrame)
    assert len(deduplicatedTable) == 4
    assert deduplicatedTable.at[1, "a"] == 1
    assert deduplicatedTable.at[6, "c"] == 2

    duplicateRows = pnd.deduplicateTable(tbl, False)
    assert isinstance(duplicateRows, pandas.DataFrame)
    assert len(duplicateRows) == 3
    assert duplicateRows.at[7, "b"] == 5
