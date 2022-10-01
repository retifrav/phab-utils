import pathlib
import pandas


def openPickleAsPandasTable(f: str) -> pandas.DataFrame:
    filePath = pathlib.Path(f)
    if not filePath.exists():
        raise SystemError(f"The path [{filePath}] does not exist")
    if not filePath.is_file():
        raise SystemError(f"The [{filePath}] is not a file")
    return pandas.read_pickle(filePath)
