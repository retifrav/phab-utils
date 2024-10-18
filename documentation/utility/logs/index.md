Logging functionality.

To enable debug log messages, set the environment variable `UIO_EXOPLANET_GROUP_DEBUG`. That will set the `uio.utility.logs.debugMode` flag to `True`.

For example, you can set it from command line like this for all the scripts:

``` sh
$ export UIO_EXOPLANET_GROUP_DEBUG=1
$ python ./some.py
$ python ./another.py
```

or like this for just one script:

``` sh
$ UIO_EXOPLANET_GROUP_DEBUG=1 python ./some.py
```

In a Visual Studio Code cell it can be done like this:

``` py
%set_env UIO_EXOPLANET_GROUP_DEBUG 1
```
