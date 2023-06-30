# uio-exoplanet-group

UiO exoplanet group tools for data processing. Created for [Centre for Earth Evolution and Dynamics](https://www.mn.uio.no/ceed/) and its successor [Center for Planetary Habitability](https://planetaryhabitability.org/).

<!-- MarkdownTOC -->

- [Installing](#installing)
    - [From sources](#from-sources)
    - [From PyPI](#from-pypi)
- [Modules](#modules)
- [Data](#data)
- [Documentation](#documentation)
    - [API](#api)
    - [wiki](#wiki)
- [Tests](#tests)

<!-- /MarkdownTOC -->

## Installing

### From sources

``` sh
$ cd /path/to/uio-exoplanet-group/
$ pip install ./
```

Add an `-e` argument, if you intend to modify the original sources.

You can also build a wheel and install/distribute that instead:

``` sh
$ cd /path/to/uio-exoplanet-group/
$ python -m build
$ pip install ./dist/uio_exoplanet_group-0.1.0-py3-none-any.whl
```

### From PyPI

Later the package will also be published at PyPI, so it could be installed with pip.

## Modules

- utility - reusable/common utility modules;
- tasks - special module for performing particular tasks.

## Data

Wherever you see a reference to some data files in documentation, examples, comments or anywhere else, for example some function taking a path like `./data/systems-528n.pkl`, check the [data](https://github.com/retifrav/uio-exoplanet-group/tree/master/data) folder - chances are, that file will be provided there.

## Documentation

There are two different pieces of documentation.

### API

Located in `documentation`. This is the package API documentation, which is published [here](https://uio.decovar.dev/).

It is generated with [pdoc](https://pdoc.dev):

``` sh
$ pip install pdoc

$ cd /path/to/uio-exoplanet-group
$ rm -r ./documentation/_deploy/*

$ UIO_PACKAGE_VERSION=$(git rev-parse --short HEAD) pdoc ./src/uio/utility ./src/uio/tasks \
    --template-directory ./documentation/_templates/ \
    --edit-url="uio=https://github.com/retifrav/uio-exoplanet-group/blob/master/src/uio/" \
    --output-directory ./documentation/_deploy/
$ cp ./documentation/{favicon.ico,phab.jpg} ./documentation/_deploy/
```

For now it's a blunt deployment of generated HTML, but later it probably will be better to rely on GitHub Actions (*if it won't spend too much of free quota*) by customizing [this workflow](https://github.com/mitmproxy/pdoc/blob/main/.github/workflows/docs.yml).

### wiki

Located in `wiki`. This is general purpose / technical manuals, articles, notes, etc: how to install/build various tools, dependencies, how to set-up environments and so on.

It is meant to be published somewhere else, but for now it will do being a part of repository. GitHub wikis could've been an option, but those are still quite bad in terms of organizing the content.

## Tests

To run tests:

``` sh
$ pip install pytest
$ python -m pytest ./src/uio/tests/*[^_*].py
```
