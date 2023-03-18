UIO exoplanet group tools for data processing. Created for [Centre for Earth Evolution and Dynamics](https://www.mn.uio.no/ceed/) and [its successor](https://mn.uio.no/ceed/english/about/news-and-events/research-in-media/new-ceo-centre-phab.html) **Centre for Planetary Habitability**.

<!-- MarkdownTOC -->

- [Installing](#installing)
    - [From sources](#from-sources)
    - [From PyPI](#from-pypi)

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
