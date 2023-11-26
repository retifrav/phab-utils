import pytest

import tempfile
import pathlib
import pandas
import numpy

from uio.utility.files import pickle
from . import somethingThatDoesntExist


def test_open_pickle_as_pandas_table_fail(
    somethingThatDoesntExist: str
) -> None:
    # openning a non-existent path
    with pytest.raises(ValueError, match=r"^The path \[.*\] does not exist$"):
        pnd = pickle.openPickleAsPandasTable(somethingThatDoesntExist)
    # openning a folder instead of a file
    with pytest.raises(ValueError, match=r"^The path \[.*\] is not a file$"):
        pnd = pickle.openPickleAsPandasTable(".")


def test_open_pickle_as_pandas_table() -> None:
    pnd = pickle.openPickleAsPandasTable("./data/systems-528n.pkl")
    assert pnd.index[0] == "AU Mic b"
    assert pnd.index[3] == "CoRoT-24 c"


def test_save_pandas_table_as_pickle() -> None:
    rng = numpy.random.default_rng()
    pnd = pandas.DataFrame(
        rng.integers(0, 20, size=(3, 5)),
        index=[1, 2, 3],
        columns=["a", "b", "c", "d", "e"]
    )
    with tempfile.TemporaryDirectory() as tempDir:
        tempFilePath = pathlib.Path(tempDir) / "some.pkl"
        pickle.savePandasTableAsPickle(pnd, tempFilePath)
        assert tempFilePath.exists()
        with pytest.raises(
            ValueError, match=r"^The \[.*\] file already exists$"
        ):
            pickle.savePandasTableAsPickle(pnd, tempFilePath)


def test_merge_pickles_return_as_pandas() -> None:
    pnd: pandas.DataFrame = pickle.mergePickles(
        "./data/merge-pickles/",
        None
    )
    assert len(pnd) == 6


def test_merge_pickles_save_to_file() -> None:
    with tempfile.TemporaryDirectory() as tempDir:
        tempFilePath = pathlib.Path(tempDir) / "merged.pkl"
        pickle.mergePickles(
            "./data/merge-pickles/",
            tempFilePath
        )
        assert tempFilePath.exists()
