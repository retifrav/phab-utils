# SIMBAD outage and the mirror fallback

Evidence behind the mirror fallback rules in `CLAUDE.md`. The outage, exception and connect-timeout findings were first gathered on 2026-11-20 and 2026-11-22 for tap-adql-sandbox (the same author's TAP/ADQL GUI, which got the same fallback first) with pyvo 1.10.0 and astroquery 0.4.11. The phab-utils measurements are from 2026-11-22 with pyvo 1.10.0, astroquery 0.4.11, requests 2.34.2 and urllib3 2.8.0 on Python 3.14.7 (what `uv venv` picked), in the x86_64 container on the Arch host.

## The outage

- CDS (Strasbourg) has a cybersecurity incident and took its servers offline on purpose. The announcement on `https://simbad.cds.unistra.fr/` ("Last updated November 09, 2026") and `https://cds.unistra.fr/` ("Last updated November 18, 2026") gives no cause and no restore date. Both pages list the fallbacks.
- Start date: CDS doesn't state one. The earliest public reports found are from 28–30 Oct 2026, for example skyfielders/python-skyfield#1155, opened 2026-10-30 about `cdsarc.cds.unistra.fr` not answering. astropy/astroquery#3701 ("CDS Mirrors") was opened 2026-11-02 and merged 2026-11-12. Its commit `a3a96d5` (2026-11-03) added `simbad.idia.ac.za` to `servers_list`, and that's not in any release yet.
- On 2026-11-20 every path on `simbad.cds.unistra.fr` returned HTTP 404 with a CDS "Page unavailable" HTML page, over both http and https. By 2026-11-22 it no longer accepted connections at all: it still resolves (a CNAME to `www-cds.cds.unistra.fr`, 130.79.129.14, no AAAA record), but a TCP connect on 443 or 80 never completes. Re-checked for phab-utils on 2026-11-22 with `curl --connect-timeout 5`: exit at 5.0 s, `time_connect=0`.
- The mirrors, both official and listed by CDS:
  - CfA Harvard: `https://simbad.cfa.harvard.edu/simbad/sim-tap/`, "data ingested up to 2026-10-14". `simbad.harvard.edu` (astroquery's name for it) serves the same over https directly. Its server is nginx.
  - IDIA (South Africa): `https://simbad.idia.ac.za/simbad/sim-tap/`. Its server is Apache.

  Neither is behind Cloudflare (`Server` headers checked 2026-11-22), and both answered `/capabilities` with 200 (0.7 s and 1.2 s).

## The old endpoint

`tap.services["simbad"]["endpoint"]` was `http://simbad.cds.unistra.fr/simbad/sim-tap/sync`. PyVO's `TAPQuery.queryurl` is `f'{baseurl}/{mode}'`, so the request went to `…/sim-tap/sync/sync`, which CDS used to tolerate. Harvard tolerates it too. The endpoint is now the base `https://simbad.cds.unistra.fr/simbad/sim-tap`, the scheme astroquery ≥ 0.4.8 uses for CDS (`tap_url = f"https://{self.server}/simbad/sim-tap"`).

## Which exceptions mean "server unavailable" (pyvo 1.10.0)

The hierarchy: `DALAccessError` ← `DALProtocolError` ← `DALServiceError` (← `DALRateLimitError`, `DALJobTimeoutError`) and `DALFormatError`. `DALQueryError` is directly under `DALAccessError`. All of them are importable from `pyvo.dal`. Measured outcomes:

- CDS 404 on a TAP query (2026-11-20): `DALServiceError: 404 Client Error: Not Found for url: …/sim-tap/sync`.
- CDS connect timeout on a TAP query: `DALFormatError: ConnectTimeout: HTTPSConnectionPool(host='simbad.cds.unistra.fr', port=443): … (connect timeout=5)`. `execute_stream` calls `submit()` outside its `try`, so the raw `requests` error reaches `execute_votable`, which wraps any non-DAL exception into `DALFormatError`. A fallback catching only `DALServiceError` misses this, which is why it catches `DALProtocolError`.
- CDS connect timeout from astroquery's `query_objectids`: `DALServiceError: Unable to access the capabilities endpoint at: …` (multi-line). astroquery's `query_tap` checks `hardlimit` first, which fetches VOSI capabilities, and pyvo's VOSI code wraps `HTTPError`, `ConnectionError` and `Timeout` into `DALServiceError`. Once a mirror has answered, astroquery caches `_hardlimit` on the instance, so later failures come from `/sync` as `DALFormatError` instead.
- Bad ADQL: SIMBAD answers HTTP 400 with an ERROR VOTable, and pyvo raises `DALQueryError` ("Incorrect ADQL query: …"). `test_escape_special_characters_for_adql` got exactly that from Harvard, so IDIA wasn't tried.
- `requests.RequestException` subclasses `IOError`/`OSError`, so `OSError` catches any raw `requests` error that some other pyvo path lets through.

## astroquery's SIMBAD servers and the private instance

- 0.4.8–0.4.11: `conf.servers_list = ['simbad.cds.unistra.fr', 'simbad.harvard.edu']`. The `server` setter raises `ValueError` for anything not in `conf.servers_list`. `SimbadClass.__init__(self, ROW_LIMIT=None, *, timeout=None)` sets `_tap` and `_hardlimit` to `None` and makes no request. The `tap` property builds a new `TAPService(baseurl=f"https://{self.server}/simbad/sim-tap", session=self._session)` whenever `server` has changed since the last call, so setting `server` per attempt switches the host.
- `conf.server` is a list-option `ConfigItem`, so astropy only accepts values from the list. CDS's fallback page suggests `server = simbad.cfa.harvard.edu` in `astroquery.cfg`, which isn't in the 0.4.11 list.
- Before 0.4.8 astroquery used the sim-script interface and had no `server` property. Setting it is inert there, so there's no real fallback. `_getSimbadServers()` reads `servers_list` with `getattr` in case it is missing there too.
- The private `_simbad = SimbadClass()` was checked: after `getObjectID("A2 146")` and `findIdentificatorFromAnotherCatalogue("TWA 20", …)` fell back, the global `astroquery.simbad.Simbad.server` was still `simbad.cds.unistra.fr`, its `_session` still had two plain `HTTPAdapter`s, and `_simbad.server` was `simbad.harvard.edu`.

## The connect timeout

- Without a timeout, a plain `TAPService(cds).search(…)` raised `DALFormatError: ConnectTimeout` after **136.4 s**. That is the kernel's SYN retransmissions (`net.ipv4.tcp_syn_retries = 6` here). Other OSes give up after a different time.
- Nobody sets a network timeout. pyvo's `TAPQuery.submit` (`session.post(url, data=…, stream=True, files=…)`) and the VOSI GET in `vosi.py` pass none, and requests has no session-level default. astroquery's `Simbad.timeout` / `conf.timeout` (1080) is `execution_duration` for async jobs, a server-side limit, not a network timeout.
- urllib3 applies the connect part of a `(connect, read)` pair to the TCP connect, the TLS handshake and sending the request (`conn.timeout = connect_timeout`, `connectionpool.py` line 465). It switches to the read part only before waiting for the response (line 536). `HTTPAdapter`'s default `max_retries` is 0, so a connect timeout is not retried. DNS resolution is not covered by either part.
- The read side has to stay unlimited: in tap-adql-sandbox a heavy `COUNT(*)` join sent to Harvard with the 5 s limit in force ran until Harvard's own gateway answered `504 Gateway Time-out` at 60.3 s. So Harvard's sync endpoint has a gateway limit of about 60 s, and a 504 is a `DALServiceError` that falls back to the next mirror.
- requests 2.34.2 ships inline annotations (`HTTPAdapter.send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None)`), and mypy rejected a `send(self, request, **kwargs)` override as incompatible with both `HTTPAdapter` and `BaseAdapter`. Hence the spelled-out signature.

## The cool-down

- Why: phab-utils queries SIMBAD in loops. `getObjectID` makes one TAP query for the name, one `query_objectids`, then one TAP query per alias until one is the `main_id`. `lookForParametersInGaia` calls `findIdentificatorFromAnotherCatalogue` once per star. Without the cool-down each of those would wait 5 s while CDS is down. The user chose the cool-down on 2026-11-22 over tap-adql-sandbox's every-call rule.
- Measured with `PHAB_DEBUG=1`, `getObjectID("A2 146")` in a fresh process took 13.7 s and returned 3308165 (the main ID is `TWA 20`):
  - two 5 s timeouts, one for the TAP endpoint key and one for astroquery's `simbad.cds.unistra.fr` key, each with one WARNING and one INFO;
  - then six alias queries that skipped CDS (DEBUG only) at 0.35–0.5 s each at Harvard.
- A following `findIdentificatorFromAnotherCatalogue("TWA 20", "gaia", "dr3")` skipped CDS and took 0.1 s, returning `6132146982868270976`.

## Verification on 2026-11-22

- `python -m mypy ./src/phab` and `ruff check --select E4,E7,E9,F .` pass.
- The offline tests (`-k "mirrors or firewall or range_condition"`, 17 of them) pass. They cover:
  - fallback on `DALServiceError`, `DALFormatError` and `OSError`;
  - no retry on `DALQueryError`;
  - the last error propagating as the same object;
  - a single server being a plain call with no timeout and no cool-down;
  - the ContextVar being set only for the main server;
  - the cool-down's skip, expiry and reset.
- Live `databases.py` before the NASA `CAST` fix: 34 passed, 1 failed (that `CAST` retry), 75 s for the whole file instead of about 12 min. The SIMBAD tests took:
  - `test_get_object_id` 12.4 s;
  - `test_escape_special_characters_for_adql` 6.4 s;
  - `test_get_stellar_parameter` 2.8 s;
  - `…_by_main_id` 0.8 s;
  - `…_by_object_id` 0.7 s.
- Live `databases.py` after all changes: 42 passed in 59 s. `test_get_object_id` took 12.0 s and `test_escape_special_characters_for_adql` 6.4 s, the two 5 s timeouts being most of both.
