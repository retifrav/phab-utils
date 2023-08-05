# AltaiPony

<https://github.com/ekaterinailin/AltaiPony>

## Installing

### From PyPI

You should be able to install it from PyPI:

``` sh
$ pip install altaipony
```

But it doesn't always have the latest version published there, so better install it from sources.

### From sources

Older versions had various problems, you can find instructions for those in [cec1bd33dbcc3d9bd1823a5b6cdb40b20843c9be](https://github.com/retifrav/uio-exoplanet-group/blob/cec1bd33dbcc3d9bd1823a5b6cdb40b20843c9be/wiki/manuals/altaipony.md#from-sources), if you really need to install exactly those.

Newer versions (*tested with [aa6ba8d202566d1b69d8b7744eba39617056bbb7](https://github.com/ekaterinailin/AltaiPony/commit/aa6ba8d202566d1b69d8b7744eba39617056bbb7)*) seem to install without problems:

``` sh
$ git clone git@github.com:ekaterinailin/AltaiPony.git
$ cd ./AltaiPony
$ pip install cython
$ pip install .
```

If you plan to modify sources, then install with `-e` instead:

``` sh
$ pip install -e .
```
