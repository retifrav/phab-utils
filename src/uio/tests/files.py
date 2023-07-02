import pytest

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
