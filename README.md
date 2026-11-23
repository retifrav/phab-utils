# phab-utils

Data processing tools and knowledge base of [Centre for Earth Evolution and Dynamics](https://mn.uio.no/ceed/) and its successor [Centre for Planetary Habitability](https://mn.uio.no/phab/english/).

Original project name was `uio-exoplanet-group`, which later got renamed to `phab-utils` (*on 2025-01-29*).

<!-- MarkdownTOC -->

- [Installing](#installing)
    - [From PyPI](#from-pypi)
    - [From sources](#from-sources)
        - [Building a wheel](#building-a-wheel)
- [Data](#data)
- [Documentation](#documentation)
    - [API](#api)
    - [wiki](#wiki)
- [QA](#qa)
    - [Tests](#tests)
    - [Linting and type checking](#linting-and-type-checking)
- [Donation](#donation)

<!-- /MarkdownTOC -->

## Installing

### From PyPI

``` sh
$ pip install phab-utils
```

If you need an older version from the original `uio-exoplanet-group` package, those are still available [here](https://pypi.org/project/uio-exoplanet-group/#history).

### From sources

``` sh
$ cd /path/to/phab-utils/
$ pip install .
```

Add an `-e` argument, if you'd like to automatically update your locally installed package by pulling from the repository or/and if you intend to modify the sources:

``` sh
$ pip install -e .
```

#### Building a wheel

You can also build a wheel and distribute/install that instead:

``` sh
$ cd /path/to/phab-utils/
$ python -m build
$ pip install ./dist/phab_utils-*.whl
```

## Data

Wherever you see a reference to some data files in documentation, examples, comments or anywhere else, for example some function taking a path like `./data/systems-528n.pkl`, check the [data](https://github.com/retifrav/phab-utils/tree/master/data) folder - chances are, that file will be provided there.

## Documentation

There are two different pieces of documentation.

### API

Located in `documentation`. This is the package API documentation, which is published [here](https://phab.decovar.dev/).

It is generated with [pdoc](https://pdoc.dev):

``` sh
$ pip install pdoc

$ cd /path/to/phab-utils
$ rm -r ./documentation/_deploy/*

$ PHAB_PACKAGE_VERSION=$(git rev-parse --short HEAD) pdoc ./src/phab/utils ./src/phab/tasks \
    --template-directory ./documentation/_templates/ \
    --edit-url="utils=https://github.com/retifrav/phab-utils/blob/master/src/phab/utils/" \
    --edit-url="tasks=https://github.com/retifrav/phab-utils/blob/master/src/phab/tasks/" \
    --output-directory ./documentation/_deploy/
$ cp ./documentation/{favicon.ico,phab.jpg} ./documentation/_deploy/
```

For now it's a blunt deployment of generated HTML, but later it probably will be better to rely on GitHub Actions (*if it won't spend too much of free quota*) by customizing [this workflow](https://github.com/mitmproxy/pdoc/blob/main/.github/workflows/docs.yml).

If you'd like to browse generated documentation locally, you can just open the main `index.html` from `./documentation/_deploy/` in your browser. Alternatively, you can launch a basic Python server:

``` py
$ cd ./documentation/_deploy/
$ python -m http.server 8000
```

and open <http://localhost:8000/>.

### wiki

Located in `wiki`. This is general purpose / technical manuals, articles, notes, etc: how to install/build various tools, dependencies, how to set-up environments and so on.

It is meant to be published somewhere else, but for now it will do being a part of repository. GitHub wikis could've been an option, but those are still quite bad in terms of organizing the content.

## QA

### Tests

To run tests:

``` sh
$ pip install pytest

$ python -m pytest ./src/phab/tests/*[^_*].py
$ python -m pytest ./src/phab/tests/databases.py
$ python -m pytest ./src/phab/tests/databases.py -k "test_get_parameters_that_are_double_in_nasa"
```

### Linting and type checking

The code is checked with [ruff](https://docs.astral.sh/ruff/) (*linting*) and [ty](https://docs.astral.sh/ty/) (*type checking*). Both are configured in `pyproject.toml`, so they need no extra options, but they should be run from the repository root.

`ty` might need a virtual environment (*venv*) with the dependencies installed so it could check how the code uses them. It should run without venv too, but then the dependencies are likely to be unknown to it, so it might miss actual problems. A virtual environment in `.venv` in the repository root is found by `ty` automatically:

``` sh
$ cd /path/to/phab-utils/
$ uv venv --python 3.12 .venv
$ uv pip install --python .venv -e . pytest

$ uvx ruff@0.17.6 check
$ uvx ty@0.0.107 check --error-on-warning

$ rm -r .venv
$ rm -r src/phab_utils.egg-info
```

Some notes:

- the tool versions are pinned on purpose. New `ruff` versions might add new rules to its default set, and `ty` is not stable yet (*it is still `0.0.x`*), so its rules change quite often. Without pinning, the checks might start failing on a new version of the tools for commits that didn't change anything;
- `pytest` is installed for its types, other dependencies are installed from `setup.cfg`;
- `--error-on-warning` makes ty fail on warnings too (*such as deprecations*);
- don't use `ruff format`, as the code isn't formatted with it.

## Donation

You can support this project via [GitHub Sponsors](https://github.com/sponsors/retifrav) or by donating cryptocurrency to either of the following wallets (*[signed variant](https://decovar.dev/donation.txt)*):

- XLM: `GDYB2QGJYWT6VPT7O7INWIGRGJF5ZEAQ7Y73S4T47IOP2QQ554NPN3ZM`
- BTC: `bc1q2kfqwm2kwyw37ay2g4tnguasvp6j4hsmtrgjte`
