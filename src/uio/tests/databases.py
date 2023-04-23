import pytest

from uio.utility.databases import tap

from typing import Tuple


@pytest.fixture
def tapService() -> Tuple[str, str]:
    return ("PADC", "http://voparis-tap-planeto.obspm.fr/tap")


@pytest.fixture
def tapServiceThatDoesntExist() -> str:
    return "Some random value"


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


def test_unknown_tap_service(tapServiceThatDoesntExist: str) -> None:
    tapServiceEndpoint = tap.getServiceEndpoint(tapServiceThatDoesntExist)
    assert tapServiceEndpoint is None, \
        " ".join((
            "There shouldn't be a registered TAP service",
            f"under the name \"{tapServiceThatDoesntExist}\""
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
