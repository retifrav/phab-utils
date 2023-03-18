# uio-exoplanet-group

UIO exoplanet group tools for data processing. Created for [Centre for Earth Evolution and Dynamics](https://www.mn.uio.no/ceed/) and [its successor](https://mn.uio.no/ceed/english/about/news-and-events/research-in-media/new-ceo-centre-phab.html) **Centre for Planetary Habitability**.

<!-- MarkdownTOC -->

- [Installing](#installing)
    - [From sources](#from-sources)
    - [From PyPI](#from-pypi)
- [Modules](#modules)
- [Data](#data)
- [Documentation](#documentation)
    - [Deployment](#deployment)

<!-- /MarkdownTOC -->

## Installing

### From sources

``` sh
$ cd /path/to/repository/
$ pip install ./
```

Add an `-e` argument, if you intend to modify the original sources.

You can also build a wheel and install/distribute that instead:

``` sh
$ cd /path/to/repository/
$ python -m build
$ pip install ./dist/uio_exoplanet_group-0.1.0-py3-none-any.whl
```

### From PyPI

Later the package will also be published at PyPI, so it could be installed with pip.

## Modules

- utility
    + `uio.databases` - fetching/querying data from various data sources;
    + `uio.files` - working with files;
- tasks
    + `uio.tasks` - special module for performing specific tasks.

## Data

Wherever you see a reference to some data files in documentation, examples, comments or anywhere else, for example some function taking a path like `./data/systems-528n.pkl`, check the [data](https://github.com/retifrav/uio-exoplanet-group/tree/master/data) folder - chances are, that file will be provided there.

## Documentation

The package documentation is published [here](https://uio.decovar.dev/uio.html).

### Deployment

Documentation is generated with [pdoc](https://pdoc.dev):

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
