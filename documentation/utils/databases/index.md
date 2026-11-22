Fetching/querying data from various data sources.

## Known problems

### SIMBAD at CDS is unavailable since October 2026

Since late October 2026 (*the first reports are from 28-30 October*) [CDS](https://cds.unistra.fr/) in Strasbourg has been dealing with a cybersecurity incident, and as part of that it took its servers offline, SIMBAD included. As of 2026-11-22 they are still down, and `simbad.cds.unistra.fr` doesn't even accept connections anymore (*until 2026-11-20 it was at least answering with a 404 page*), so a query to it hangs until the operating system gives up on connecting (*over 2 minutes on GNU/Linux*), and then fails with:

``` sh
DALFormatError: ConnectTimeout: HTTPSConnectionPool(host='simbad.cds.unistra.fr', port=443): Max retries exceeded with url: /simbad/sim-tap/sync
```

SIMBAD hasn't moved anywhere, it is just temporarily unavailable, and in the meantime CDS [suggests](https://cds.unistra.fr/) using its official mirrors:

- [CfA Harvard](https://simbad.cfa.harvard.edu/simbad/), TAP service at `https://simbad.cfa.harvard.edu/simbad/sim-tap` (*contains data ingested up to 2026-10-14*);
- [IDIA](https://simbad.idia.ac.za/) (*South Africa*), TAP service at `https://simbad.idia.ac.za/simbad/sim-tap`.

So SIMBAD queries still try the main server first (*in case it is back*), giving it `utils.databases.mirrors.mainServerConnectTimeout` (*5 seconds*) to accept the connection, and if that fails, they fall back to the mirrors, logging that:

``` sh
[WARNING] [https://simbad.cds.unistra.fr/simbad/sim-tap] is unavailable, falling back to [https://simbad.cfa.harvard.edu/simbad/sim-tap], it will be skipped for the next 600 s. DALFormatError: ConnectTimeout: HTTPSConnectionPool(host='simbad.cds.unistra.fr', port=443): Max retries exceeded with url: /simbad/sim-tap/sync (Caused by ConnectTimeoutError(<HTTPSConnection(host='simbad.cds.unistra.fr', port=443) at 0x7fa43284a120>, 'Connection to simbad.cds.unistra.fr timed out. (connect timeout=5)'))
[INFO] Got results from the mirror [https://simbad.cfa.harvard.edu/simbad/sim-tap]
```

After such a failure the main server is skipped for `utils.databases.mirrors.mainServerCooldown` (*10 minutes*), so a series of queries (*such as `utils.databases.simbad.getObjectID` checking every identificator of an object*) doesn't wait those 5 seconds for every query. Those queries go straight to the mirrors, which is only mentioned in the debug log. After that period the main server is tried first again, so the queries return to it by themselves once it is back. Both values can be changed:

``` py
from phab.utils.databases import mirrors

mirrors.mainServerConnectTimeout = 10
mirrors.mainServerCooldown = 0  # try the main server first on every query
```

Those 5 seconds are only for connecting, waiting for the results is not limited, so a long query still runs to the end once the main server is back. The mirrors aren't limited at all.

That applies to:

- `utils.databases.tap.queryService`, but only when the endpoint is exactly the one from `utils.databases.tap.services` (*`getServiceEndpoint("simbad")`, a trailing `/` doesn't matter*), as any other endpoint is queried as it is. To query a particular mirror, pass its URL as the endpoint;
- looking up object identificators in `utils.databases.simbad`, which first tries the server configured in Astroquery (*the CDS one by default*), and then the mirrors that Astroquery knows about. With Astroquery `0.4.11` that is only CfA Harvard, the IDIA mirror comes in its next release. This requires Astroquery `0.4.8` or later, older versions will just fail as before. These lookups use their own instance of Astroquery's SIMBAD class, so the `Simbad` object in your own code is not affected.

Keep in mind that the results from a mirror might differ from what the main server would return, as the mirror's data might be older.

### Queries to NASA Exoplanet Archive might be blocked with 403 Forbidden

[NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/) has [Cloudflare](https://cloudflare.com/) in front of its servers, and Cloudflare's firewall blocks some perfectly valid ADQL queries, because to the firewall they look like an SQL injection attack. Such a query fails with:

``` sh
DALServiceError: 403 Client Error: Forbidden for url: https://exoplanetarchive.ipac.caltech.edu/TAP/sync
```

The request never reaches the TAP service, so it is neither an error in the query nor in this package. As of 2026-11-22, the firewall blocks a string literal followed by `AND` or `OR` and then an `IS NULL` or `IS NOT NULL` condition, for example:

``` sql
WHERE pl_name = 'Kepler-106 e' AND pl_radj IS NOT NULL
```

That is what `utils.databases.tap.getStellarParameterFromNASA` and `utils.databases.tap.getPlanetaryParameterFromNASA` used to send, so now they put the condition with the string literal last:

``` sql
WHERE pl_radj IS NOT NULL AND pl_name = 'Kepler-106 e'
```

The firewall also blocks any query with `CAST(… AS …)`, wherever it is in the query and whatever the type. That broke the workarounds for NASA returning doubles rounded (*`parameterTypeIsDouble`*), so they no longer use `CAST`:

- `utils.databases.tap.getStellarParameterFromNASA` and `utils.databases.tap.getPlanetaryParameterFromNASA` select `pl_massj + 0` instead of `CAST(pl_massj AS REAL)`. An expression isn't rounded the way a column is, and it is even a bit more precise, as it is a double, while `REAL` is a single-precision float;
- `utils.databases.tap.getPlanetaryParameterReferenceFromNASA` compares with a range of values, such as `pl_massj >= 0.3121 AND pl_massj < 0.3122`, instead of `CAST(pl_massj AS VARCHAR(7)) LIKE '.3121%'`, and that is the same set of values.

Queries with a subquery in `WHERE` were blocked as well, and there are probably other such patterns. If you compose your own queries, rephrasing them without changing their meaning usually gets them through, for example by reordering the conditions like above, or by writing `AND NOT pl_radj IS NULL` instead of `AND pl_radj IS NOT NULL`.

`utils.databases.tap.queryService` recognizes Cloudflare's block page and logs an explanation (*from `utils.databases.tap.getFirewallBlockHint`*) along with the Cloudflare Ray ID of the blocked request, before raising the exception as usual. If rephrasing doesn't help, you can try reporting the block to the archive and refer to that Ray ID in your report.

### NASA Exoplanet Archive no longer accepts WITH and subqueries in FROM

Before passing a query to its database, the archive's TAP service checks every table name in the query against `TAP_SCHEMA.tables`, and as of 2026-11-22 that check rejects queries that used to work. So if you compose your own queries, avoid:

- `WITH`, because the name of a common table expression (*CTE*) fails as an unknown table: `Table 'latestentries' is not available for querying`;
- subqueries in `FROM`, which fail the same way: `Table '(select' is not available for querying`;
- more than one condition in the `ON` clause of a `JOIN`, as the service takes some of them for table names too (*`Table 'b.pl_radj' is not available for querying`*), so put the extra conditions into `WHERE`;
- `AS` before a table alias. That is valid ADQL, but the service passes the query to its database (*Oracle*) as it is, and Oracle fails with `ORA-00933: SQL command not properly ended`, so write `FROM ps a` instead of `FROM ps AS a`.

The database itself still supports what these constructs do, so a self-join with `GROUP BY` and `HAVING` can often replace a `WITH` or a subquery.
