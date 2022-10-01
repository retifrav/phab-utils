# uio-exoplanet-group

UIO exoplanet group tools for data processing. Created for [Centre for Earth Evolution and Dynamics](https://www.mn.uio.no/ceed/) and [its successor](https://mn.uio.no/ceed/english/about/news-and-events/research-in-media/new-ceo-centre-phab.html) **Centre for Planetary Habitability**.

<!-- MarkdownTOC -->

- [Installing](#installing)
    - [From sources](#from-sources)
- [Modules](#modules)
    - [tap](#tap)

<!-- /MarkdownTOC -->

## Installing

### From sources

``` sh
$ cd /path/to/repository/
$ pip install ./
```

If you'd like to immediately apply source code changes, add `-e` argument,

You can also build a wheel and install/distribute that instead:

``` sh
$ cd /path/to/repository/
$ python -m build
$ pip install ./dist/uio_exoplanet_group-0.1.0-py3-none-any.whl
```

## Modules

### tap

``` py
from uio.databases import tap

tapService = tap.getServiceEndpoint("PADC")
if not tapService:
    raise SystemError("Unknown service")

tbl = tap.queryService(
    tapService,
    " ".join((
        "SELECT star_name, granule_uid, mass, radius, period, semi_major_axis",
        "FROM exoplanet.epn_core",
        "WHERE star_name = 'Kepler-107'",
        "ORDER BY granule_uid"
    ))
)
print(tbl)
```
