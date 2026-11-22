"""
Falling back to mirror servers when the main server of a service is unavailable.

The main server is tried first, and if it is down or unreachable, the mirrors are tried
in turn, until one of them answers. The main server gets only `mainServerConnectTimeout`
to accept the connection, and after a failure it is skipped for `mainServerCooldown`,
after which it is tried first again, so the queries return to it by themselves once it is back.

This is used for SIMBAD, as its main server at CDS has been unavailable since late October 2026,
more details in the Known problems section of `utils.databases`.
"""

import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from contextvars import ContextVar

from pyvo.dal import DALProtocolError
from requests import PreparedRequest, Response, Session
from requests.adapters import HTTPAdapter

from ..logs.log import logger

mainServerConnectTimeout: float = 5
"""
How long (*in seconds*) the main server of a service with mirrors gets to accept the connection
before `tryMirrors` falls back to its mirrors. Neither PyVO nor Astroquery sets a network timeout
of its own, so without it a server that silently drops connections (*as SIMBAD at CDS does since
November 2026*) makes every query wait out the operating system's connect timeout, which can be
over 2 minutes.

It is only a connect timeout: waiting for the response stays unlimited, so a long query on a server
that is up is never cut off. Mirrors get no such limit.
"""

mainServerCooldown: float = 600
"""
For how long (*in seconds*) the main server is skipped after it was found unavailable, so a series
of queries doesn't wait `mainServerConnectTimeout` on every one of them. After that the main server
is tried first again. Set it to `0` to try the main server on every call.
"""

unavailableErrors: tuple[type[Exception], ...] = (DALProtocolError, OSError)
"""
Errors meaning that a server is down or unreachable, so a mirror might still answer. PyVO raises
`DALProtocolError` subclasses for those: HTTP errors (*such as a 404 page*) become `DALServiceError`,
and a connection error or a timeout in a query becomes `DALFormatError`. `OSError` is for a connection
error or a timeout from `requests` that PyVO lets through as it is. Errors in the query itself
(`DALQueryError`) would be the same on every mirror, so those are not retried.
"""

# connect timeout (in seconds) of the current `tryMirrors()` attempt, which `ConnectTimeoutAdapter` applies,
# `None` meaning no timeout
_attemptConnectTimeout: ContextVar[float | None] = ContextVar(
    "attemptConnectTimeout",
    default=None
)

# main server -> `time.monotonic()` of its last failure
_mainServerFailures: dict[str, float] = {}


class ConnectTimeoutAdapter(HTTPAdapter):
    """
    Gives the requests that have no timeout of their own (*and neither PyVO nor Astroquery sets one*)
    the connect timeout of the current `tryMirrors` attempt, if it has one. Waiting for the response
    stays unlimited. It is mounted on a session with `addConnectTimeout`.
    """
    def send(
        self,
        request: PreparedRequest,
        stream: bool = False,
        timeout: None | float | tuple[float | None, float | None] = None,
        verify: bool | str = True,
        cert: None | str | tuple[str, str] = None,
        proxies: dict[str, str] | None = None
    ) -> Response:
        connectTimeout: float | None = _attemptConnectTimeout.get()
        if timeout is None and connectTimeout is not None:
            # a (connect, read) pair, `None` being no limit
            timeout = (connectTimeout, None)
        return super().send(
            request,
            stream=stream,
            timeout=timeout,
            verify=verify,
            cert=cert,
            proxies=proxies
        )


def addConnectTimeout(session: Session) -> Session:
    """
    Mounts `ConnectTimeoutAdapter` on the `session`, so the connect timeout that `tryMirrors`
    gives to the main server applies to its requests. Outside of such attempts it changes nothing.

    Example:

    ``` py
    import pyvo
    from pyvo.utils.http import create_session
    from phab.utils.databases import mirrors

    tapService = pyvo.dal.TAPService(
        "https://simbad.cds.unistra.fr/simbad/sim-tap",
        session=mirrors.addConnectTimeout(create_session())
    )
    ```
    """
    adapter: ConnectTimeoutAdapter = ConnectTimeoutAdapter()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


@contextmanager
def _connectTimeout(seconds: float) -> Generator[None, None, None]:
    token = _attemptConnectTimeout.set(seconds)
    try:
        yield
    finally:
        _attemptConnectTimeout.reset(token)


def tryMirrors[T](servers: list[str], attempt: Callable[[str], T]) -> T:
    """
    Calls `attempt` with each of the `servers` in turn until one of them is available
    (*fails with none of the `unavailableErrors`*).

    The first one is the main server. It gets `mainServerConnectTimeout` to accept
    the connection (*with sessions from `addConnectTimeout`*), and once it has failed,
    it is skipped for `mainServerCooldown`. The mirrors have no such limit. Errors
    from the last server propagate as they are, so with a single server this is the same
    as a plain call.

    Example:

    ``` py
    import pyvo
    from pyvo.utils.http import create_session
    from phab.utils.databases import mirrors

    results = mirrors.tryMirrors(
        [
            "https://simbad.cds.unistra.fr/simbad/sim-tap",
            "https://simbad.cfa.harvard.edu/simbad/sim-tap"
        ],
        lambda url: pyvo.dal.TAPService(
            url,
            session=mirrors.addConnectTimeout(create_session())
        ).search("SELECT TOP 1 oid, main_id FROM basic")
    )
    print(results.to_table().to_pandas())
    ```
    """
    if not servers:
        raise ValueError("The list of servers to try is empty")
    if len(servers) == 1:
        return attempt(servers[0])

    mainServer: str = servers[0]
    skipMainServer: bool = False
    failedAt: float | None = _mainServerFailures.get(mainServer)
    if failedAt is not None:
        sinceFailure: float = time.monotonic() - failedAt
        if sinceFailure < mainServerCooldown:
            skipMainServer = True
            logger.debug(
                f"Skipping [{mainServer}], it was unavailable "
                f"{sinceFailure:.0f} s ago, and it will be tried again "
                f"in {mainServerCooldown - sinceFailure:.0f} s"
            )

    serversToTry: list[str] = servers[1:] if skipMainServer else servers
    # whether some server has failed in this call, so the mirror that answered
    # after it is worth an info message
    fellBack: bool = False
    for i, server in enumerate(serversToTry[:-1]):
        tryingMainServer: bool = i == 0 and not skipMainServer
        logger.debug(f"Trying [{server}]")
        try:
            if tryingMainServer:
                with _connectTimeout(mainServerConnectTimeout):
                    result: T = attempt(server)
            else:
                result = attempt(server)
        except unavailableErrors as ex:
            skipNote: str = ""
            if tryingMainServer:
                _mainServerFailures[mainServer] = time.monotonic()
                if mainServerCooldown > 0:
                    skipNote = (
                        ", it will be skipped for the next "
                        f"{mainServerCooldown:g} s"
                    )
            logger.warning(
                f"[{server}] is unavailable, "
                f"falling back to [{serversToTry[i + 1]}]{skipNote}. "
                f"{type(ex).__name__}: {ex}"
            )
            fellBack = True
            continue
        if tryingMainServer:
            _mainServerFailures.pop(mainServer, None)
        else:
            _logMirrorAnswered(server, fellBack)
        return result

    lastServer: str = serversToTry[-1]
    logger.debug(f"Trying [{lastServer}]")
    result = attempt(lastServer)
    _logMirrorAnswered(lastServer, fellBack)
    return result


def _logMirrorAnswered(mirror: str, fellBack: bool) -> None:
    message: str = f"Got results from the mirror [{mirror}]"
    if fellBack:
        logger.info(message)
    else:  # the main server is being skipped
        logger.debug(message)
