from collections.abc import Callable
from contextlib import nullcontext
from typing import Literal

import lightkurve
import pandas
import pytest
import requests
from packaging.version import Version
from pyvo.dal.exceptions import DALFormatError, DALQueryError, DALServiceError

from utils.databases import lightcurves, mirrors, simbad, tap

from . import somethingThatDoesntExist  # noqa: F401


@pytest.fixture
def tapService() -> tuple[str, str]:
    return ("padc", "http://voparis-tap-planeto.obspm.fr/tap")


def test_known_tap_service(tapService: tuple[str, str]) -> None:
    tapServiceEndpoint = tap.getServiceEndpoint(tapService[0])
    assert tapServiceEndpoint
    assert tapServiceEndpoint == tapService[1], (
        f"The \"{tapService[0]}\" TAP service "
        "has a different endpoint registered"
    )


def test_unknown_tap_service(
    somethingThatDoesntExist: str  # noqa: F811
) -> None:
    with pytest.raises(
        ValueError,
        match=r"^There is no TAP service under the name.*$"
    ):
        tapServiceEndpoint = tap.getServiceEndpoint(somethingThatDoesntExist)  # noqa: F841


def test_escape_special_characters_for_adql() -> None:
    rawQuery = (
        "SELECT oid FROM basic "
        "WHERE main_id = 'NAME Teegarden's Star' "
        "AND main_id != 'someone else's star'"
    )
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


@pytest.fixture
def noMainServerFailures(monkeypatch: pytest.MonkeyPatch) -> None:
    # so no main server is skipped because of a failure in another test
    monkeypatch.setattr(mirrors, "_mainServerFailures", {})


def fakeServersAttempt(
    failures: dict[str, Exception],
    calls: list[tuple[str, float | None]]
) -> Callable[[str], str]:
    # records every attempt with its connect timeout and fails
    # for the servers from `failures` with their exception
    def attempt(server: str) -> str:
        calls.append((server, mirrors._attemptConnectTimeout.get()))
        if server in failures:
            raise failures[server]
        return f"results from {server}"
    return attempt


def test_mirrors_fall_back_on_unavailable_servers(
    noMainServerFailures: None
) -> None:
    for failure in (
        DALServiceError("404 Client Error: Not Found", 404),
        DALFormatError(ConnectionError("Connection refused")),
        OSError("Connection timed out")
    ):
        calls: list[tuple[str, float | None]] = []
        result = mirrors.tryMirrors(
            ["main", "mirror1", "mirror2"],
            fakeServersAttempt(
                {"main": failure, "mirror1": OSError("Connection reset")},
                calls
            )
        )
        assert result == "results from mirror2"
        # only the main server has the connect timeout
        assert calls == [
            ("main", mirrors.mainServerConnectTimeout),
            ("mirror1", None),
            ("mirror2", None)
        ]
        assert mirrors._attemptConnectTimeout.get() is None
        mirrors._mainServerFailures.clear()


def test_mirrors_do_not_retry_query_errors(
    noMainServerFailures: None
) -> None:
    calls: list[tuple[str, float | None]] = []
    with pytest.raises(DALQueryError, match=r"^Incorrect ADQL query$"):
        mirrors.tryMirrors(
            ["main", "mirror"],
            fakeServersAttempt(
                {"main": DALQueryError("Incorrect ADQL query")},
                calls
            )
        )
    assert calls == [("main", mirrors.mainServerConnectTimeout)]
    assert mirrors._attemptConnectTimeout.get() is None
    assert "main" not in mirrors._mainServerFailures


def test_mirrors_last_error_propagates(
    noMainServerFailures: None
) -> None:
    lastError = DALServiceError("504 Server Error: Gateway Time-out", 504)
    with pytest.raises(DALServiceError) as ex:
        mirrors.tryMirrors(
            ["main", "mirror"],
            fakeServersAttempt(
                {"main": OSError("Connection timed out"), "mirror": lastError},
                []
            )
        )
    assert ex.value is lastError


def test_mirrors_single_server_is_a_plain_call(
    noMainServerFailures: None
) -> None:
    calls: list[tuple[str, float | None]] = []
    with pytest.raises(OSError):
        mirrors.tryMirrors(
            ["main"],
            fakeServersAttempt({"main": OSError("Connection timed out")}, calls)
        )
    # no connect timeout and no cooldown without mirrors
    assert calls == [("main", None)]
    assert "main" not in mirrors._mainServerFailures
    with pytest.raises(ValueError, match=r"^The list of servers .*$"):
        mirrors.tryMirrors([], fakeServersAttempt({}, calls))


def test_mirrors_main_server_cooldown(
    noMainServerFailures: None,
    monkeypatch: pytest.MonkeyPatch
) -> None:
    failures: dict[str, Exception] = {"main": OSError("Connection timed out")}
    calls: list[tuple[str, float | None]] = []
    attempt = fakeServersAttempt(failures, calls)
    servers: list[str] = ["main", "mirror"]

    # the main server fails, so it is skipped on the next call
    assert mirrors.tryMirrors(servers, attempt) == "results from mirror"
    assert "main" in mirrors._mainServerFailures
    assert mirrors.tryMirrors(servers, attempt) == "results from mirror"
    assert [c[0] for c in calls] == ["main", "mirror", "mirror"]

    # once the cooldown is over, the main server is tried first again
    calls.clear()
    monkeypatch.setattr(mirrors, "mainServerCooldown", 0)
    assert mirrors.tryMirrors(servers, attempt) == "results from mirror"
    assert [c[0] for c in calls] == ["main", "mirror"]

    # and once it is back, its failure is forgotten,
    # so it is not skipped even with a cooldown
    calls.clear()
    del failures["main"]
    assert mirrors.tryMirrors(servers, attempt) == "results from main"
    assert "main" not in mirrors._mainServerFailures
    monkeypatch.setattr(mirrors, "mainServerCooldown", 600)
    assert mirrors.tryMirrors(servers, attempt) == "results from main"
    assert calls == [
        ("main", mirrors.mainServerConnectTimeout),
        ("main", mirrors.mainServerConnectTimeout)
    ]


def test_mirrors_of_tap_services() -> None:
    simbadEndpoint = tap.getServiceEndpoint("simbad")
    simbadMirrors = tap.getServiceMirrors(simbadEndpoint)
    assert len(simbadMirrors) > 0
    assert simbadMirrors == tap.services["simbad"]["mirrors"]
    assert tap.getServiceMirrors(f"{simbadEndpoint}/") == simbadMirrors
    # an endpoint that is not from the list is never redirected,
    # and a mirror is not such an endpoint either
    assert tap.getServiceMirrors(simbadMirrors[0]) == []
    assert tap.getServiceMirrors(tap.getServiceEndpoint("nasa")) == []


@pytest.mark.parametrize(
    "server, status, contentType, rayID, expectedHint",
    [
        ("cloudflare", 403, "text/html; charset=UTF-8", "a5e9-OSL", True),
        ("cloudflare", 403, "text/html; charset=UTF-8", None, True),
        ("cloudflare", 403, "application/xml", "a5e9-OSL", False),
        ("nginx", 403, "text/html", None, False),
        ("cloudflare", 404, "text/html; charset=UTF-8", "a5e9-OSL", False)
    ]
)
def test_firewall_block_hint(
    server: str,
    status: int,
    contentType: str,
    rayID: str | None,
    expectedHint: bool
) -> None:
    response = requests.Response()
    response.status_code = status
    response.headers["Server"] = server
    response.headers["Content-Type"] = contentType
    if rayID:
        response.headers["CF-RAY"] = rayID
    response._content = b"<html>Attention Required! | Cloudflare</html>"
    hint = tap.getFirewallBlockHint(
        DALServiceError.from_except(
            requests.HTTPError(f"{status} Client Error", response=response),
            "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
        )
    )
    if expectedHint:
        assert hint.startswith("The request was blocked by Cloudflare")
        assert hint.endswith(f"Ray ID: {rayID if rayID else 'unknown'}.")
    else:
        assert hint == ""
    # the service's own errors are not blocks
    assert tap.getFirewallBlockHint(DALQueryError("Incorrect ADQL query")) == ""


@pytest.mark.parametrize(
    "value, expectedCondition",
    [
        (0.31212, "pl_massj >= 0.3121 AND pl_massj < 0.3122"),
        (-0.31212, "pl_massj > -0.3122 AND pl_massj <= -0.3121"),
        (1.2345, "pl_massj >= 1.234 AND pl_massj < 1.235"),
        (12.5, "pl_massj >= 12 AND pl_massj < 13"),
        (5, "pl_massj >= 5 AND pl_massj < 6"),
        (1e-05, "pl_massj >= 0.0000 AND pl_massj < 0.0001")
    ]
)
def test_range_condition_for_doubles_in_nasa(
    value: float,
    expectedCondition: str
) -> None:
    # the same values as `CAST(pl_massj AS VARCHAR(n)) LIKE '.3121%'`
    # used to match, which Cloudflare's firewall in front of NASA blocks
    assert tap._doubleRangeConditionForADQL(
        "pl_massj",
        value
    ) == expectedCondition


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


def test_getting_double_parameters_from_nasa() -> None:
    # selected as an expression, which NASA does not round
    # according to the column's format
    teff = tap.getStellarParameterFromNASA(
        "Kepler-11",
        "st_teff",
        parameterTypeIsDouble=True
    )
    assert isinstance(teff, float)
    massRounded = tap.getPlanetaryParameterFromNASA(
        "KOI-4777.01",
        "pl_massj"
    )
    mass = tap.getPlanetaryParameterFromNASA(
        "KOI-4777.01",
        "pl_massj",
        parameterTypeIsDouble=True
    )
    assert isinstance(massRounded, float)
    assert isinstance(mass, float)
    assert abs(mass - massRounded) < 1e-7


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


def test_get_light_curve_stats_fail(
    somethingThatDoesntExist: str  # noqa: F811
) -> None:
    stats = lightcurves.getLightCurveStats(somethingThatDoesntExist)
    assert not stats


def test_get_light_curve_ids() -> None:
    ids = lightcurves.getLightCurveIDs("LTT 1445 A")
    assert ids
    assert len(ids) > 0


def test_get_light_curve_ids_fail(
    somethingThatDoesntExist: str  # noqa: F811
) -> None:
    with pytest.raises(
        ValueError,
        match=r"^Didn't find any results for this star$"
    ):
        stats = lightcurves.getLightCurveIDs(somethingThatDoesntExist)  # noqa: F841


@pytest.mark.parametrize(
    "downloadLC",
    [
        True,
        False
    ]
)
@pytest.mark.parametrize(
    "qualityMask",
    [
        "none",
        "default",
        "hard",
        "hardest"
    ]
)
def test_fits_to_pandas_and_light_curve_tess_to_pandas(
    downloadLC: bool,
    qualityMask: Literal["none", "default", "hard", "hardest"]
) -> None:
    lc = None
    if downloadLC:
        search_result = lightkurve.search_lightcurve(
            "Karmn J07446+035",
            author="SPOC",
            cadence="short"
        )
        lc = search_result[0].download(
            quality_bitmask=qualityMask
        )
    else:
        lc = lightkurve.TessLightCurve.read(
            "./data/tess2019006130736-s0007-0000000266744225-0131-s_lc.fits",
            quality_bitmask=qualityMask
        )
    pnd1 = lc.to_pandas()

    pnd2 = lightcurves.fitsToPandas(
        "./data/tess2019006130736-s0007-0000000266744225-0131-s_lc.fits",
        fitsType="tess",
        qualityBitmask=qualityMask,
        dropNanTimes=True,
        convertTimesToSeconds=False
    )
    assert isinstance(pnd2, pandas.DataFrame)
    assert len(pnd2) == len(pnd1)
    assert pnd2.iloc[0, 0] == pnd1.index[0]

    pnd3 = lightcurves.lightCurveTessToPandas(lc, convertTimesToSeconds=False)
    assert isinstance(pnd3, pandas.DataFrame)
    assert len(pnd3) == len(pnd2)
    assert pnd3.iloc[0, 0] == pnd2.iloc[0, 0]


def test_get_object_id(
    somethingThatDoesntExist: str  # noqa: F811
) -> None:
    # an object that does exist and has no problems with its identifier
    objectID = simbad.getObjectID(
        "A2 146",
        fallbackToLikeInsteadOfEqual=False
    )
    assert objectID == 3308165

    # an object that does not exist
    #
    # from version 0.4.8 astroquery no longer outputs BlankResponseWarning
    with (
        nullcontext()
        if Version(simbad.astroqueryVersion) > Version("0.4.7")
        else pytest.warns(Warning)  # should be BlankResponseWarning
    ):
        objectID = simbad.getObjectID(f"A2 146 {somethingThatDoesntExist}")
        assert objectID is None, (
            "There shouldn't be a known object that would contain "
            f"\"{somethingThatDoesntExist}\" as a part of its name"
        )

        # an object that does exist but has a problematic identifier
        # (no longer a problem, apparently)
        # objectID = simbad.getObjectID(
        #     "2MASS J15392828-3446180",  # its `main_id` is `SZ  66`
        #     fallbackToLikeInsteadOfEqual=False
        # )
        # assert objectID is None, \
        #     " ".join((
        #         "There is an object with this identifier, but without LIKE",
        #         "in WHERE clause it should have not been found (unless they",
        #         "have finally fixed that by now)"
        #     ))

    # an object that does exist but has a problematic identifier,
    # but this time with a fallback to LIKE
    objectID = simbad.getObjectID(
        "2MASS J15392828-3446180",  # its `main_id` is `SZ  66`
        fallbackToLikeInsteadOfEqual=True,
        problematicIdentifiersPrefixes=["SZ"]
    )
    assert objectID == 2325762


def test_get_stellar_parameter_from_simbad_by_main_id(
    somethingThatDoesntExist: str  # noqa: F811
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
    assert rez is None, (
        "There shouldn't be a known object "
        f"under the name \"{somethingThatDoesntExist}\""
    )


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
    assert rez is None, (
        "There shouldn't be a known object "
        f"with the object ID \"{oidThatDoesNotExist}\""
    )


def test_get_stellar_parameter(
    somethingThatDoesntExist: str  # noqa: F811
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
    with (
        nullcontext()
        if Version(simbad.astroqueryVersion) > Version("0.4.7")
        else pytest.warns(Warning)  # should be BlankResponseWarning
    ):
        rez = simbad.getStellarParameter(
            somethingThatDoesntExist,
            "mesVar",
            "period"
        )
        assert rez is None, (
            "There shouldn't be a known object "
            f"under the name \"{somethingThatDoesntExist}\""
        )
