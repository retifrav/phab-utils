# uio-exoplanet-group

UIO exoplanet group tools for data processing. Created for [Centre for Earth Evolution and Dynamics](https://www.mn.uio.no/ceed/) and [its successor](https://mn.uio.no/ceed/english/about/news-and-events/research-in-media/new-ceo-centre-phab.html) **Centre for Planetary Habitability**.

<!-- MarkdownTOC -->

- [Installing](#installing)
    - [From sources](#from-sources)
    - [From PyPI](#from-pypi)
- [Modules](#modules)
    - [databases.simbad](#databasessimbad)
        - [getOtherIDfromSimbad](#getotheridfromsimbad)
    - [databases.tap](#databasestap)
        - [getServiceEndpoint](#getserviceendpoint)
        - [queryService](#queryservice)
    - [files.pickle](#filespickle)
        - [openPickleAsPandasTable](#openpickleaspandastable)
    - [tasks](#tasks)
- [Deploying documentation](#deploying-documentation)

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

### From PyPI

Later the package will also be published at PyPI, so it could be installed with pip.

## Modules

### databases.simbad

#### getOtherIDfromSimbad

``` py
from uio.databases import simbad

otherID = simbad.getOtherIDfromSimbad(star, "gaia", "dr3")
print(otherID)
```

### databases.tap

Fetching data from various astronomy databases via [TAP](https://www.ivoa.net/documents/TAP/) interface.

#### getServiceEndpoint

``` py
from uio.databases import tap

tapService = tap.getServiceEndpoint("PADC")
if tapService is None:
    raise SystemError("No endpoint for such TAP service in the list")
print(tapService)
```

#### queryService

``` py
from uio.databases import tap

tbl = tap.queryService(
    "http://voparis-tap-planeto.obspm.fr/tap",
    " ".join((
        "SELECT star_name, granule_uid, mass, radius, period, semi_major_axis",
        "FROM exoplanet.epn_core",
        "WHERE star_name = 'Kepler-107'",
        "ORDER BY granule_uid"
    ))
)
print(tbl)
```

### files.pickle

#### openPickleAsPandasTable

``` py
from uio.files import pickle

pnd = pickle.openPickleAsPandasTable("/path/to/some.pkl")
print(pnd.head(15))
```

### tasks

Code in this module is precisely specific to particular tasks and isn't meant for common use. The purpose and description of each task are provided in in-source as comments for every such function.

## Deploying documentation

The documentation is generated with [pdoc](https://pdoc.dev):

``` sh
$ pip install pdoc

$ cd /path/to/uio-exoplanet-group
$ rm -r ./documentation/_deploy/*
$ pdoc ./src/uio \
    --template-directory ./documentation/_templates/ \
    --edit-url="uio=https://github.com/retifrav/uio-exoplanet-group/blob/master/src/uio/" \
    --output-directory ./documentation/_deploy/
```

For now it's a blunt deployment of generated HTML, but later it probably will be better to rely on GitHub Actions (*if it won't spend too much of free quota*) by customizing [this workflow](https://github.com/mitmproxy/pdoc/blob/main/.github/workflows/docs.yml).
