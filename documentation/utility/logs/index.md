Logging functionality.

To enable debug log messages, set the environment variable `UIO_EXOPLANET_GROUP_DEBUG`. For example:

``` sh
$ export UIO_EXOPLANET_GROUP_DEBUG=1
```

or:

``` sh
$ UIO_EXOPLANET_GROUP_DEBUG=1 python ./some.py
```

Doing so will set the `uio.utility.logs.debugMode` flag to `True`.
