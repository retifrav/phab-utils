import pytest

from uio.utility.databases import tap, lightcurves, simbad
from . import somethingThatDoesntExist

from pyvo.dal.exceptions import DALQueryError

from typing import Tuple


@pytest.fixture
def tapService() -> Tuple[str, str]:
    return ("padc", "http://voparis-tap-planeto.obspm.fr/tap")


def test_known_tap_service(tapService: Tuple[str, str]) -> None:
    tapServiceEndpoint = tap.getServiceEndpoint(tapService[0])
    assert tapServiceEndpoint
    assert tapServiceEndpoint == tapService[1], \
        " ".join((
            f"The \"{tapService[0]}\" TAP service",
            "has a different endpoint registered"
        ))


def test_unknown_tap_service(somethingThatDoesntExist: str) -> None:
    with pytest.raises(
        ValueError,
        match=r"^There is no TAP service under the name.*$"
    ):
        tapServiceEndpoint = tap.getServiceEndpoint(somethingThatDoesntExist)


def test_escape_special_characters_for_adql() -> None:
    rawQuery = " ".join((
        "SELECT oid FROM basic",
        "WHERE main_id = 'NAME Teegarden's Star'",
        "AND main_id != 'someone else's star'"
    ))
    # escaped ADQL query
    tap.queryService(
        tap.getServiceEndpoint("simbad"),
        tap.escapeSpecialCharactersForAdql(rawQuery),
        tryToReExecuteOnFailure=False
    )
    # raw ADQL query that should fail because of unescaped special character
    with pytest.raises(
        DALQueryError,
        match=r"^Incorrect ADQL query.*$"
    ):
        tap.queryService(
            tap.getServiceEndpoint("simbad"),
            rawQuery,
            tryToReExecuteOnFailure=False
        )
    # raw ADQL query, but with enabled re-execution on failure
    tap.queryService(
        tap.getServiceEndpoint("simbad"),
        rawQuery,
        tryToReExecuteOnFailure=True
    )


def test_get_parameters_that_are_double_in_nasa() -> None:
    doubles = tap.getParametersThatAreDoubleInNASA()
    assert len(doubles) > 1


def test_getting_stellar_parameter_from_nasa() -> None:
    starName = "Kepler-11"
    hostname = tap.getStellarParameterFromNASA(starName, "hostname")
    assert hostname == starName


def test_getting_planetary_parameter_from_nasa() -> None:
    planetName = "Kepler-11 b"
    plname = tap.getPlanetaryParameterFromNASA(planetName, "pl_name")
    assert plname == planetName


def test_get_planetary_parameter_reference_from_nasa() -> None:
    # no workarounds required
    ref = tap.getPlanetaryParameterReferenceFromNASA(
        "Kepler-11 b",
        "pl_massj",
        0.0069,
        parameterTypeIsDouble=False,
        tryToReExecuteIfNoResults=False,
        returnOriginalReferenceOnFailureToExtract=False
    )
    assert ref == "2014A&A...571A..38B"

    # no results without applying a workaround for the doubles precision
    ref = tap.getPlanetaryParameterReferenceFromNASA(
        "KOI-4777.01",
        "pl_massj",
        0.31212,
        parameterTypeIsDouble=False,
        tryToReExecuteIfNoResults=False,
        returnOriginalReferenceOnFailureToExtract=False
    )
    assert ref is None

    # applying a workaround for the doubles precision
    doubles = tap.getParametersThatAreDoubleInNASA()
    param = "pl_massj"
    ref = tap.getPlanetaryParameterReferenceFromNASA(
        "KOI-4777.01",
        param,
        0.31212,
        parameterTypeIsDouble=(param in doubles),
        tryToReExecuteIfNoResults=True,
        returnOriginalReferenceOnFailureToExtract=False
    )
    assert ref == "2022AJ....163....3C"


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


def test_get_object_id(somethingThatDoesntExist: str) -> None:
    # an object that does exist
    objectID = simbad.getObjectID("A2 146")
    assert objectID == 3308165
    # an object that does not exist
    with pytest.warns(Warning):  # should be BlankResponseWarning
        objectID = simbad.getObjectID(f"A2 146 {somethingThatDoesntExist}")
        assert objectID is None, \
            " ".join((
                "There shouldn't be a known object that would contain",
                f"\"{somethingThatDoesntExist}\" as a part of its name"
            ))


def test_get_stellar_parameter_from_simbad_by_main_id(
    somethingThatDoesntExist: str
) -> None:
    # parameter of an object that does exist
    rez = tap.getStellarParameterFromSimbadByMainID(
        "CD-29 2360",
        "mesVar",
        "period"
    )
    assert rez
    assert len(rez) == 2
    assert isinstance(rez[1], str)
    # parameter of an object that does not exist
    rez = tap.getStellarParameterFromSimbadByMainID(
        somethingThatDoesntExist,
        "mesVar",
        "period",
    )
    assert rez is None, \
        " ".join((
            "There shouldn't be a known object",
            f"under the name \"{somethingThatDoesntExist}\""
        ))


def test_get_stellar_parameter_from_simbad_by_object_id() -> None:
    # parameter of an object that does exist
    rez = tap.getStellarParameterFromSimbadByObjectID(
        817576,
        "mesVar",
        "period"
    )
    assert rez
    assert len(rez) == 2
    assert isinstance(rez[1], str)
    # parameter of an object that does not exist
    oidThatDoesNotExist = 123454321
    rez = tap.getStellarParameterFromSimbadByObjectID(
        oidThatDoesNotExist,
        "mesVar",
        "period"
    )
    assert rez is None, \
        " ".join((
            "There shouldn't be a known object",
            f"with the object ID \"{oidThatDoesNotExist}\""
        ))


def test_get_stellar_parameter(
    somethingThatDoesntExist: str
) -> None:
    # parameter of an object that does exist
    rez = simbad.getStellarParameter(
        "PPM 725297",
        "mesVar",
        "period"
    )
    assert rez
    assert len(rez) == 2
    assert isinstance(rez[1], str)
    # parameter of an object that does not exist
    with pytest.warns(Warning):  # should be BlankResponseWarning
        rez = simbad.getStellarParameter(
            somethingThatDoesntExist,
            "mesVar",
            "period"
        )
        assert rez is None, \
            " ".join((
                "There shouldn't be a known object",
                f"under the name \"{somethingThatDoesntExist}\""
            ))
