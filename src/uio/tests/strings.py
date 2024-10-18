import pytest

from uio.utility.strings import extraction
from . import somethingThatDoesntExist


def test_ref_from_full_reference_nasa(
    somethingThatDoesntExist: str
) -> None:
    ref = extraction.refFromFullReferenceNASA(
        "<a refstr=BORSATO_ET_AL__2014 href=https://ui.adsabs.harvard.edu/abs/2014A&A...571A..38B/abstract target=ref>Borsato et al. 2014</a>"
    )
    assert ref == "2014A&A...571A..38B"

    ref = extraction.refFromFullReferenceNASA(
        somethingThatDoesntExist
    )
    assert ref is None, \
        " ".join((
            "There can't be a reference value in",
            f"\"{somethingThatDoesntExist}\" string"
        ))
