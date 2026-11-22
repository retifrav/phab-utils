# NASA Exoplanet Archive: Cloudflare WAF and query checks

Evidence behind the NASA query rules, the double-precision workaround and `getFirewallBlockHint` in `CLAUDE.md`. Gathered on 2026-11-22 with curl POSTs to `https://exoplanetarchive.ipac.caltech.edu/TAP/sync` (`REQUEST=doQuery`, `LANG=ADQL`, `QUERY=…`) and pyvo 1.10.0, in the x86_64 container on the Arch host. The first bisect and the query-check findings were made for tap-adql-sandbox (the same author's TAP/ADQL GUI) earlier the same day, and the `CAST` findings for phab-utils.

## Cloudflare WAF

- Cloudflare proxies the whole host. Every response carries `server: cloudflare` and `cf-ray`, including a 200 (`content-type: application/xml`) and the service's own 400 VOTable errors. PADC (DaCHS), Gaia (Apache) and both SIMBAD mirrors are not behind Cloudflare.
- A block is HTTP 403 with `content-type: text/html` and the "Attention Required! | Cloudflare" page: "Sorry, you have been blocked … submitting a certain word or phrase, a SQL command or malformed data". The page shows the Ray ID, which is the `cf-ray` header.
- PyVO path: `DALQuery.execute_stream` stores `DALServiceError.from_except(HTTPError)` (`code` = 403, `cause` = the `requests.HTTPError`, whose `.response` has the headers). The HTML fails `votableparse` (`E19: File does not appear to be a VOTABLE`), so `execute_votable` calls `raise_if_error`, which raises that `DALServiceError`. `from_except` replaces the message with `response.text` only for `text/plain`, so the message stays `403 Client Error: Forbidden for url: …/TAP/sync`.
- Bisect from tap-adql-sandbox's "Planet parameter by publications" example (`SELECT hostname, pl_name … FROM ps WHERE …`):

  | `WHERE` | status |
  |---|---|
  | `pl_name = 'Kepler-106 e'` | 200 |
  | `pl_radj IS NOT NULL` | 200 |
  | `pl_name = 'Kepler-106 e' AND pl_radj IS NOT NULL` | 403 |
  | `pl_name = 'Kepler-106 e' AND pl_radj IS NULL` | 403 |
  | `pl_name = 'Kepler-106 e' OR pl_radj IS NOT NULL` | 403 |
  | `(pl_name = 'Kepler-106 e') AND pl_radj IS NOT NULL` | 403 |
  | `pl_name = 'Kepler-106 e' AND hostname IS NOT NULL` | 403 |
  | `pl_radj IS NOT NULL AND pl_name = 'Kepler-106 e'` | 200 |
  | `pl_name = 'Kepler-106 e' AND pl_radj > 0` | 200 |
  | `pl_name = 'Kepler-106 e' AND NOT pl_radj IS NULL` | 200 |

- Two correlated subqueries in `WHERE` were blocked too, one of them with no literal before `AND`.
- `CAST` probes for phab-utils:

  | query | status |
  |---|---|
  | `SELECT pl_refname FROM ps WHERE pl_name = 'KOI-4777.01' AND CAST(pl_massj AS VARCHAR(7)) LIKE '.3121%' ORDER BY pl_pubdate DESC` (the old retry, from `test_get_planetary_parameter_reference_from_nasa`) | 403 |
  | the same with the `pl_name` condition last | 403 |
  | `SELECT pl_refname FROM ps WHERE CAST(pl_massj AS VARCHAR(7)) LIKE '.3121%'` | 403 |
  | `SELECT pl_refname FROM ps WHERE pl_name LIKE 'KOI-4777%'` | 200, 5 rows |
  | `SELECT CAST(pl_massj AS REAL) AS pl_massj_real FROM ps WHERE pl_massj IS NOT NULL AND pl_name = 'Kepler-11 b' ORDER BY pl_pubdate DESC` (the old double `SELECT`) | 403 |
  | `SELECT pl_refname, pl_massj FROM ps WHERE pl_massj >= 0.3121 AND pl_massj < 0.3122 AND pl_name = 'KOI-4777.01' ORDER BY pl_pubdate DESC` | 200, 1 row, `2022AJ....163....3C`, `0.31211810` |
  | `SELECT pl_refname FROM ps WHERE pl_letter = 'b' AND pl_name = 'Kepler-11 b' ORDER BY pl_pubdate DESC` (a string comparison after a literal) | 200, 17 rows |

  So `CAST(… AS …)` alone is enough, in `SELECT` or `WHERE`, and the order of the conditions doesn't matter for it.
- The rules aren't published, so these tables only show what was blocked on that day. About a dozen requests were blocked over the tap-adql-sandbox session and 4 in the phab-utils one (the failing test and 3 probes), and the IP was not blocked. Keep probing that light.

## Doubles: rounding and the replacements for `CAST`

- `SELECT pl_massj, pl_massj + 0 AS plus0, pl_massj * 1000000 AS scaled FROM ps WHERE pl_name = 'KOI-4777.01'` returned `0.31211810`, `3.12118104660166e-01` and `3.12118104660166e+05`, all three declared `double`. The column is rounded to its `format`, and an expression isn't. That is what `CAST(… AS REAL)` used to give, minus REAL's single precision.
- NASA declares an expression's VOTable type from its values:
  - `st_teff + 0.0` over Kepler-11's rows (all whole, such as `5657.00`) was declared `int`, and `tap.queryService` returned `np.int32(3396)` for KOI-4777.01;
  - `pl_massj + 0.0` for `1 <= pl_massj < 1.002` (all exactly `1.00000000`) was declared `int`;
  - for `1 <= pl_massj < 1.03` (29 rows, whole first, then `1.002`, `1.003`, …) it was declared `double`.

  So the type comes from all values, not from the first row, and no fractional value gets truncated. The library still converts the `_real` value with `float()`, so the functions keep returning floats.
- The range in `_doubleRangeConditionForADQL` reproduces what the old `LIKE` matched. `floatToStringForADQLcastVarchar(0.31212, dropLeadingZero=True)` is `'.3121%'`, and NASA casts `0.3121181…` to `'.312118'`, so the `LIKE` matched every value whose decimal digits start with `.3121`, which is `[0.3121, 0.3122)`, and `(-0.3122, -0.3121]` for negative values. The value goes through `Decimal(str(value))` with fixed-point formatting, so `1e-05` becomes `0.00001`, and an `int` gets `.0` appended, so `5` becomes `[5, 6)`.

## The archive's own query checks (from tap-adql-sandbox)

- `/TAP/capabilities` declares ADQL 2.0 with only the geometry features. `TAP_SCHEMA.tables` lists `ps` and `pscomppars`.
- An old `SELECT * FROM (WITH latestEntries AS (… ROW_NUMBER() OVER(PARTITION BY pl_name …) …) …)` query now fails with HTTP 400 and `QUERY_STATUS=ERROR`, which PyVO raises as `DALQueryError`: `Table 'latestentries' is not available for querying. Use TAP_SCHEMA.tables to see available tables.` The service checks the table names it finds in the query against a whitelist and doesn't know CTE names.
- Rewrites that failed:
  - a derived table in `FROM`: `Table '(select' is not available for querying.`;
  - a `LEFT JOIN` with three `AND`ed conditions in `ON`: `Table 'b.pl_radj' is not available for querying.`;
  - `FROM ps AS a JOIN ps AS b`: `ORA-00933: SQL command not properly ended`, because the Oracle backend gets `AS` before a table alias as it is;
  - correlated subqueries in `WHERE`: 403 from the WAF.
- What works: `FROM ps a JOIN ps b ON b.pl_name = a.pl_name`, the extra conditions in `WHERE` with the literal last, plus `GROUP BY` and `HAVING a.pl_pubdate = MAX(b.pl_pubdate)`. Window functions run untranslated on their own, so only the service's table-name check stands in the way.
- The backend was Oracle before and still is: `usingTAP.html` has named it since at least November 2021.

## The hint

- Live: in the first phab-utils test run, `queryService` logged `getFirewallBlockHint`'s ERROR for the blocked `CAST` retry, ending in `Ray ID: a5e983d78dbe2efa-OSL.`, and then raised the original `DALServiceError: 403`.
- Synthetic (`test_firewall_block_hint`, `DALServiceError.from_except(HTTPError(response=…))`):
  - hint: a Cloudflare 403 with HTML (`Ray ID: unknown` without `CF-RAY`);
  - no hint: a Cloudflare 403 with `application/xml`, an nginx 403 with HTML, a Cloudflare 404 with HTML, or a `DALQueryError`.

## After the changes

All five live NASA tests passed in 15.5 s: the doubles list, the stellar and planetary parameters, the new `test_getting_double_parameters_from_nasa` and the reference test, whose range retry returned `2022AJ....163....3C`.
