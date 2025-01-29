Logging functionality.

To enable debug log messages, set the environment variable `PHAB_DEBUG`. That will set the `phab.utils.logs.debugMode` flag to `True`.

For example, you can set it from command line like this for all the scripts:

``` sh
$ export PHAB_DEBUG=1
$ python ./some.py
$ python ./another.py
```

or like this for just one script:

``` sh
$ PHAB_DEBUG=1 python ./some.py
```

In a Visual Studio Code cell it can be done like this:

``` py
%set_env PHAB_DEBUG 1
```
