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
