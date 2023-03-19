UIO exoplanet group tools for data processing. Created for [Centre for Earth Evolution and Dynamics](https://www.mn.uio.no/ceed/) and [its successor](https://mn.uio.no/ceed/english/about/news-and-events/research-in-media/new-ceo-centre-phab.html) **Centre for Planetary Habitability**.

<!-- MarkdownTOC -->

- [Source code](#source-code)
    - [Data](#data)
- [Installing](#installing)
    - [From sources](#from-sources)
    - [From PyPI](#from-pypi)
- [Modules](#modules)

<!-- /MarkdownTOC -->

## Source code

The source code repository is [here](https://github.com/retifrav/uio-exoplanet-group).

### Data

Wherever you see a reference to some data files in documentation, examples, comments or anywhere else, for example some function taking a path like `./data/systems-528n.pkl`, check the [data](https://github.com/retifrav/uio-exoplanet-group/tree/master/data) folder - chances are, that file will be provided there.

## Installing

### From sources

``` sh
$ git clone git@github.com:retifrav/uio-exoplanet-group.git
$ cd ./uio-exoplanet-group
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
    + `uio.tasks` - special module for performing particular tasks.
