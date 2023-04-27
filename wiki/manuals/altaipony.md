# AltaiPony

<https://github.com/ekaterinailin/AltaiPony>

## Installing

### From PyPI

``` sh
$ pip install altaipony
```

### From sources

Using `494b3572c1a1af8d34b0882713de42c0350e7198` revision.

``` sh
$ git clone git@github.com:ekaterinailin/AltaiPony.git
$ cd ./AltaiPony
$ pip install cython
$ pip install .
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
$ pip install .
```

## Using

You might get this error trying to use the package:

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

That will help with `MaskedNDArray` issue, but it will now be failing with:

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

If you you'll get some other errors after that too, you might also need to downgrade Pandas to `1.1.4`.

Trying to run now should go fine until this:

``` sh
ValueError: pos must be nonnegative and less than window_length.
```

That will require patching the sources:

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
