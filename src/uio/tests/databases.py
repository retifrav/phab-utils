import pytest

from uio.utility.databases import tap, lightcurves, simbad
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


def test_find_object_id(somethingThatDoesntExist: str) -> None:
    # an object that does exist
    objectID = simbad.findObjectID("A2 146")
    assert objectID == 3308165
    # an object that does not exist
    objectID = simbad.findObjectID(f"A2 146 {somethingThatDoesntExist}")
    assert objectID is None, \
        " ".join((
            "There shouldn't be a known object that would contain",
            f"\"{somethingThatDoesntExist}\" as a part of its name"
        ))


def test_get_stellar_parameter_from_simbad_by_main_id(
    somethingThatDoesntExist: str
) -> None:
    # parameter of an object that does exist
    val = tap.getStellarParameterFromSimbad(
        None,
        "mesVar",
        "period",
        "CD-29 2360"
    )
    assert val
    # parameter of an object that does not exist
    val = tap.getStellarParameterFromSimbad(
        None,
        "mesVar",
        "period",
        somethingThatDoesntExist
    )
    assert val is None, \
        " ".join((
            "There shouldn't be a known object",
            f"under the name \"{somethingThatDoesntExist}\""
        ))


def test_get_stellar_parameter_from_simbad_by_object_id() -> None:
    # parameter of an object that does exist
    val = tap.getStellarParameterFromSimbad(
        817576,
        "mesVar",
        "period"
    )
    assert val
    # parameter of an object that does not exist
    oidThatDoesNotExist = 123454321
    val = tap.getStellarParameterFromSimbad(
        oidThatDoesNotExist,
        "mesVar",
        "period"
    )
    assert val is None, \
        " ".join((
            "There shouldn't be a known object",
            f"with the object ID \"{oidThatDoesNotExist}\""
        ))


def test_get_stellar_parameter_from_simbad_incorrect_ids() -> None:
    # main ID and object ID are both missing
    with pytest.raises(
        ValueError,
        match=" ".join((
            r"^Either object ID or main ID has to be provided,",
            r"they cannot be missing both$"
        ))
    ):
        val = tap.getStellarParameterFromSimbad(
            None,
            "mesVar",
            "period"
        )
    # main ID and object ID are both provided
    with pytest.raises(
        ValueError,
        match=" ".join((
            r"^Either provide object ID or main ID but not both,",
            r"it is not clear what needs to be done when",
            r"both of them are provided$"
        ))
    ):
        val = tap.getStellarParameterFromSimbad(
            0,
            "mesVar",
            "period",
            "some"
        )
