import pytest

from uio.utility.databases import tap, lightcurves
from . import somethingThatDoesntExist

from typing import Tuple


@pytest.fixture
def tapService() -> Tuple[str, str]:
    return ("padc", "http://voparis-tap-planeto.obspm.fr/tap")


def test_known_tap_service(tapService: Tuple[str, str]) -> None:
    tapServiceEndpoint = tap.getServiceEndpoint(tapService[0])
    assert tapServiceEndpoint is not None, \
        " ".join((
            "There is no TAP service registered",
            f"under the name \"{tapService[0]}\""
        ))
    assert tapServiceEndpoint == tapService[1], \
        " ".join((
            f"The \"{tapService[0]}\" TAP service",
            "has a different endpoint registered"
        ))


def test_unknown_tap_service(somethingThatDoesntExist: str) -> None:
    tapServiceEndpoint = tap.getServiceEndpoint(somethingThatDoesntExist)
    assert tapServiceEndpoint is None, \
        " ".join((
            "There shouldn't be a registered TAP service",
            f"under the name \"{somethingThatDoesntExist}\""
        ))


def test_getting_stellar_parameter_from_nasa() -> None:
    starName = "Kepler-11"
    hostname = tap.getStellarParameterFromNASA(starName, "hostname")
    assert hostname == starName


def test_getting_planetary_parameter_from_nasa() -> None:
    planetName = "Kepler-11 b"
    plname = tap.getPlanetaryParameterFromNASA(planetName, "pl_name")
    assert plname == planetName


def test_getting_parameter_from_padc() -> None:
    planetName = "Kepler-11 b"
    granuleUID = tap.getParameterFromPADC(planetName, "granule_uid")
    assert granuleUID == planetName


def test_get_light_curve_stats() -> None:
    stats = lightcurves.getLightCurveStats("LTT 1445 A", detailed=False)
    assert stats
    assert len(stats) > 0


def test_get_light_curve_stats_fail(somethingThatDoesntExist: str) -> None:
    stats = lightcurves.getLightCurveStats(somethingThatDoesntExist)
    assert not stats


def test_get_light_curve_ids() -> None:
    ids = lightcurves.getLightCurveIDs("LTT 1445 A")
    assert ids
    assert len(ids) > 0


def test_get_light_curve_ids_fail(somethingThatDoesntExist: str) -> None:
    with pytest.raises(
            ValueError,
            match=r"^Didn't find any results for this star$"
    ):
        stats = lightcurves.getLightCurveIDs(somethingThatDoesntExist)
