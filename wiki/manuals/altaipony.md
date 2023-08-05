# AltaiPony

<!-- MarkdownTOC -->

- [About](#about)
- [Installing](#installing)
    - [From PyPI](#from-pypi)
    - [From sources](#from-sources)
        - [Newer versions](#newer-versions)
        - [Older versions](#older-versions)

<!-- /MarkdownTOC -->

## About

<https://github.com/ekaterinailin/AltaiPony>

## Installing

### From PyPI

You should be able to install it from PyPI:

``` sh
$ pip install altaipony
```

But it doesn't always have the latest version published there, so better install it from sources.

### From sources

#### Newer versions

Newer versions (*tested with [aa6ba8d202566d1b69d8b7744eba39617056bbb7](https://github.com/ekaterinailin/AltaiPony/commit/aa6ba8d202566d1b69d8b7744eba39617056bbb7) revision*) seem to install without problems:

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

#### Older versions

Older versions had various problems, but if you really need to install an old version, then it's recommended to do that in a [virtual environment](https://github.com/retifrav/scraps/blob/master/python/index.md#virtual-environment).

The following was tested with [494b3572c1a1af8d34b0882713de42c0350e7198](https://github.com/ekaterinailin/AltaiPony/commit/494b3572c1a1af8d34b0882713de42c0350e7198) revision:

``` sh
$ git clone git@github.com:ekaterinailin/AltaiPony.git
$ cd ./AltaiPony
$ git checkout 494b3572c1a1af8d34b0882713de42c0350e7198
$ pip install cython
$ pip install -e .
```

If it fails with:

``` sh
pandas/_libs/tslibs/src/datetime/np_datetime_strings.c:73:12: error: variable 'numdigits' set but not used [-Werror,-Wunused-but-set-variable]
          int i, numdigits;
                 ^
      1 error generated.
      error: command '/usr/local/opt/llvm/bin/clang' failed with exit code 1
```

then you could try to make compiler not to treat warnings as errors, for example like this:

``` sh
$ CCFLAGS="-Wno-error" CFLAGS="-Wno-error" pip install .
```

but it will likely still fail, as it seems this flag is hardcoded in Pandas sources. Instead you can just remove the Pandas version requirement in `setup.py`: replace `pandas==1.1.4, !=1.1.5` with just `pandas`. Then try installing again (*this time it shouldn't attempt building old Pandas from sources*):

``` sh
$ pip install -e .
```

Then it should install fine, but you might get this error trying to use the package:

``` sh
Traceback (most recent call last):
  File "/path/to/some/some.py", line 314, in <module>
    flcd = flc.detrend("savgol")
           ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/altaipony/flarelc.py", line 342, in detrend
    new_lc =  detrend_savgol(new_lc, **kwargs)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/altaipony/altai.py", line 353, in detrend_savgol
    np.isfinite(lc.detrended_flux.value)]
                ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'MaskedNDArray' object has no attribute 'value'
```

Downgrade Astropy (*[issue](https://github.com/ekaterinailin/AltaiPony/issues/74)*):

``` sh
$ pip uninstall astropy
$ pip install --use-deprecated=legacy-resolver astropy==4.3.1
```

That will probably fail with:

``` sh
ImportError: cannot import name 'soft_unicode' from 'markupsafe' (/tmp/pip-build-env-t9kbjs7v/overlay/lib/python3.10/site-packages/markupsafe/__init__.py)
```

Try to downgrade Jinja2 and MarkupSafe:

``` sh
$ pip uninstall markupsafe
$ pip install markupsafe==2.0.1

$ pip uninstall Jinja2
$ pip install Jinja2==3.0.1
```

but that will likely not help, because these are still installed with their latest versions during the build in its own isolated environment, so try to build it with `--no-build-isolation`:

``` sh
$ pip install wheel extension-helpers
$ pip install --use-deprecated=legacy-resolver --no-build-isolation astropy==4.3.1
```

It will probably output some errors like:

``` sh
ERROR: pip's legacy dependency resolver does not consider dependency conflicts when selecting packages. This behaviour is the source of the following dependency conflicts.
pyvo 1.4.1 requires astropy>=4.1, but you'll have astropy 0.0.0 which is incompatible.
lightkurve 2.4.0 requires astropy>=5.0, but you'll have astropy 0.0.0 which is incompatible.
astroquery 0.4.6 requires astropy>=4.0, but you'll have astropy 0.0.0 which is incompatible.
altaipony 2.0.1 requires astropy>=4.1, but you'll have astropy 0.0.0 which is incompatible.
```

but these doesn't seem to actually affect anything.

Anyway, installing Astropy v4.3.1 will help with `MaskedNDArray` issue, but it will now be failing with:

``` sh
Traceback (most recent call last):
  File "/path/to/some.py", line 1, in <module>
    from altaipony.lcio import from_mast, from_path
  File "/usr/local/lib/python3.11/site-packages/altaipony/lcio.py", line 6, in <module>
    from altaipony.flarelc import FlareLightCurve
  File "/usr/local/lib/python3.11/site-packages/altaipony/flarelc.py", line 11, in <module>
    from lightkurve import KeplerLightCurve, TessLightCurve
  File "/usr/local/lib/python3.11/site-packages/lightkurve/__init__.py", line 105, in <module>
    from . import units  # enable ppt and ppm as units
    ^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/lightkurve/units.py", line 2, in <module>
    from astropy import units as u
  File "/usr/local/lib/python3.11/site-packages/astropy/units/__init__.py", line 17, in <module>
    from .quantity import *
  File "/usr/local/lib/python3.11/site-packages/astropy/units/quantity.py", line 28, in <module>
    from .quantity_helper import (converters_and_unit, can_have_arbitrary_unit,
  File "/usr/local/lib/python3.11/site-packages/astropy/units/quantity_helper/__init__.py", line 10, in <module>
    from . import helpers, function_helpers
  File "/usr/local/lib/python3.11/site-packages/astropy/units/quantity_helper/function_helpers.py", line 119, in <module>
    np.asscalar,
    ^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/numpy/__init__.py", line 320, in __getattr__
    raise AttributeError("module {!r} has no attribute "
AttributeError: module 'numpy' has no attribute 'asscalar'. Did you mean: 'isscalar'?
```

This is because this Astropy version requires a deprecated NumPy function. But trying to downgrade NumPy will also fail:

``` sh
$ pip uninstall numpy
$ pip install numpy==1.15.1

error: legacy-install-failure

× Encountered error while trying to install package.
╰─> numpy
```

and several errors about missing libraries and whatnot. Fortunately, there is a later NumPy version that still works, apparently `asscalar` is still there, even though marked as deprecated:

``` sh
$ pip install numpy==1.19.5
```

If installing/building that one gives you errors like:

``` sh
numpy/core/src/multiarray/scalartypes.c.src:2998:27: error: incompatible type for argument 1 of ‘_Py_HashDouble’
```

then you need to do the whole thing from scratch, but this time with Python version lower than 3.10, so with 3.9 for example. Basically, you'd need to re-created the virtual environment (*hopefully you are using that*) with Python 3.9.

Having installed NumPy v1.19.5 you will get these errors trying to use the package:

``` sh
ImportError: this version of pandas is incompatible with numpy < 1.20.3
your numpy version is 1.19.5.
Please upgrade numpy to >= 1.20.3 to use this pandas version
```

so you also need to still downgrade Pandas to `1.1.4`:

``` sh
$ pip uninstall pandas
$ pip install pandas==1.1.4
```

Trying to use the package now will throw a new error:

``` sh
lib/python3.9/site-packages/scipy/__init__.py:132: UserWarning: A NumPy version >=1.21.6 and <1.28.0 is required for this version of SciPy (detected version 1.19.5)
  warnings.warn(f"A NumPy version >={np_minversion} and <{np_maxversion}"
RuntimeError: module compiled against API version 0xe but this version of numpy is 0xd
...
ImportError: numpy.core.multiarray failed to import
```

so you'll need to downgrade SciPy too:

``` sh
$ pip uninstall scipy
$ pip install scipy==1.6.0
```

Next failing dependency will be Matplotlib:

``` sh
ImportError: Matplotlib requires numpy>=1.20; you have 1.19.5
```

so you'll need to downgrade it too:

``` sh
$ pip uninstall matplotlib
$ pip install matplotlib==3.3.3
```

Trying to run now should fucking finally go fine. Until this:

``` sh
ValueError: pos must be nonnegative and less than window_length.
```

Not sure what is the right way to resolve this, but patching the sources like so does get rid of that error:

``` patch
diff --git a/altaipony/altai.py b/altaipony/altai.py
index 12b862b..5909190 100755
--- a/altaipony/altai.py
+++ b/altaipony/altai.py
@@ -275,6 +275,11 @@ def detrend_savgol(lc, window_length=None, pad=3, printwl=False, **kwargs):
             wl = np.floor(.1 / dt)
             if wl % 2 == 0:
                 wl = wl + 1
+        # don't know what is a proper fallback in this situation,
+        # but since later it takes maximum of this value and 5,
+        # then 0 seems to be okay
+        if np.isnan(wl):
+            wl = 0
         
         # args are flux, window_length, polyorder, mode is 
         wl = max(wl, 5) #wl must be larger than polyorder
```

If you installed the package with `-e`, then this change will have an effect immediately.
