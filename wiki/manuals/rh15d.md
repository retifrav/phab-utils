# RH15D

<https://tiagopereira.space/ast5210/>

<!-- MarkdownTOC -->

- [Configuration](#configuration)
    - [Mac OS](#mac-os)
    - [GNU/Linux](#gnulinux)
- [Build](#build)
- [Run](#run)

<!-- /MarkdownTOC -->

## Configuration

Clone repository:

``` sh
$ git clone git@github.com:ITA-Solar/rh.git
```

### Mac OS

``` sh
$ brew install open-mpi
$ brew install hdf5-mpi
```

Go to the project folder:

``` sh
$ cd /path/to/rh
```

Edit `./Makefile.config`:

``` diff
 CC       = mpicc
 CFLAGS   = -O2 -DHAVE_F90 -Wformat
 
 F90C     = gfortran
 F90FLAGS = -O2
 
 LD       = mpicc
 LDFLAGS  =
 
 AR       = ar
 ARFLAGS  = rs
 RANLIB   = ranlib

-HDF5_DIR = /usr/local
+HDF5_DIR = /usr/local/opt/hdf5-mpi

 # The OS variable should have the operative system name
 # If the command below is unavailable, please edit manually
 OS = $(shell uname -s)
```

### GNU/Linux

Instructions were tested with [8f2bc6199d8e8af9d3f8e20a84ae92173ec564fa](https://github.com/ITA-Solar/rh/tree/8f2bc6199d8e8af9d3f8e20a84ae92173ec564fa) revision on Ubuntu 22.04 (*KDE neon 5.27*). Environment:

``` sh
$ lsb_release -a
Distributor ID:    Neon
Description:    KDE neon 5.27
Release:    22.04
Codename:    jammy

$ gcc --version
gcc (Ubuntu 11.3.0-1ubuntu1~22.04.1) 11.3.0

$ mpicc --version
gcc (Ubuntu 11.3.0-1ubuntu1~22.04.1) 11.3.0

$ gfortran --version
GNU Fortran (Ubuntu 11.3.0-1ubuntu1~22.04.1) 11.3.0
```

Install dependencies:

``` sh
$ sudo apt install libopenmpi-dev openmpi-bin
$ sudo apt install libntirpc-dev
$ sudo apt install libhdf5-mpi-dev
```

It's important to install exactly `libhdf5-mpi-dev` and not `libhdf5-dev`, because the latter isn't parallel, while the former is, and RH requires the parallel one. If you won't install the parallel variant, you'll get the following linking errors trying to build RH15D tools:

```
/usr/bin/ld: hdf5atmos.o: in function `init_hdf5_atmos':
hdf5atmos.c:(.text+0x72): undefined reference to `H5Pset_fapl_mpio'
/usr/bin/ld: writeAux_p.o: in function `init_aux_new':
writeAux_p.c:(.text+0x7c): undefined reference to `H5Pset_fapl_mpio'
/usr/bin/ld: writeAux_p.o: in function `init_aux_existing':
writeAux_p.c:(.text+0x22a2): undefined reference to `H5Pset_fapl_mpio'
/usr/bin/ld: writeRay.o: in function `init_hdf5_ray_new':
writeRay.c:(.text+0x7f): undefined reference to `H5Pset_fapl_mpio'
...
```

Go to the project folder:

``` sh
$ cd /path/to/rh
```

Edit `./Makefile.config`:

``` diff
 CC       = mpicc
-CFLAGS   = -O2 -DHAVE_F90 -Wformat
+CFLAGS   = -O2 -DHAVE_F90 -Wformat -I/usr/include/tirpc

 F90C     = gfortran
 F90FLAGS = -O2
 
 LD       = mpicc
 LDFLAGS  =
 
 AR       = ar
 ARFLAGS  = rs
 RANLIB   = ranlib

-HDF5_DIR = /usr/local
+# on Ubuntu HDF5 package in installed into /usr, not /usr/local, but most importantly
+# it has a different structure, so you'll need to make adjustments in ./rh15d/Makefile instead
+#HDF5_DIR = /usr/local

 # The OS variable should have the operative system name
 # If the command below is unavailable, please edit manually
 OS = $(shell uname -s)
```

and `./rh15d/Makefile`:

``` diff
 include ../Makefile.config

+HDF5_INCLUDE_DIR=/usr/include/hdf5/openmpi
+HDF5_LIB_DIR=/usr/lib/x86_64-linux-gnu/hdf5/openmpi
+
 # Try to get git revision, set preprocessor macros if successful
 REV=$(shell git describe --always)
 ifeq ($(REV), )
-    CFLAGS += -I../ -I$(HDF5_DIR)/include/
+    CFLAGS += -I../ -I$(HDF5_INCLUDE_DIR)
 else
     REV = $(shell git log -1 --pretty=format:"%h  %an  %ai")
-    CFLAGS += -I../ -I$(HDF5_DIR)/include/ -D'REV_ID="$(REV)"'
+    CFLAGS += -I../ -I$(HDF5_INCLUDE_DIR) -D'REV_ID="$(REV)"'
 endif

-LDFLAGS += -L../ -L$(HDF5_DIR)/lib/ -lrh -lrh_f90 -lhdf5 -lhdf5_hl -lm -lpthread
+LDFLAGS += -L../ -L$(HDF5_LIB_DIR) -lrh -lrh_f90 -lhdf5 -lhdf5_hl -lm -lpthread -ltirpc
```

So it's `HDF5_INCLUDE_DIR` and `HDF5_LIB_DIR` variables and their use in `-I` and `-L` flags. Also note the linkage to `-ltirpc`, because without it you'll get these errors trying to build RH15D tools:

```
/usr/bin/ld: writeatom_xdr.c:(.text+0x449): undefined reference to `xdr_double'
/usr/bin/ld: writeatom_xdr.c:(.text+0x491): undefined reference to `xdr_enum'
/usr/bin/ld: writeatom_xdr.c:(.text+0x4af): undefined reference to `xdr_int'
/usr/bin/ld: writeatom_xdr.c:(.text+0x4de): undefined reference to `xdr_double'
/usr/bin/ld: writeatom_xdr.c:(.text+0x578): undefined reference to `xdr_vector'
/usr/bin/ld: ..//librh.a(writeatom_xdr.o): in function `writeAtom':
writeatom_xdr.c:(.text+0x643): undefined reference to `xdrstdio_create'
/usr/bin/ld: ..//librh.a(writeatom_xdr.o): in function `xdr_adamp':
writeatom_xdr.c:(.text+0x760): undefined reference to `xdr_double'
/usr/bin/ld: writeatom_xdr.c:(.text+0x795): undefined reference to `xdr_vector'
...
```

## Build

Main libraries:

``` sh
$ make -j$(nproc --all)
```

Executables:

``` sh
$ cd rh15d
$ make -j$(nproc --all)
```

You should get the following binaries:

- `rh15d_lteray`
- `rh15d_ray`
- `rh15d_ray_pool`

## Run

Do not run the tools directly, you'll get a segmentation fault, such as:

``` sh
$ ./rh15d_lteray --help
[vasya-vmlinux:09251] *** Process received signal ***
[vasya-vmlinux:09251] Signal: Segmentation fault (11)
[vasya-vmlinux:09251] Signal code: Address not mapped (1)
[vasya-vmlinux:09251] Failing at address: 0xc0
[vasya-vmlinux:09251] [ 0] /lib/x86_64-linux-gnu/libc.so.6(+0x42520)[0x7fa817242520]
[vasya-vmlinux:09251] [ 1] /lib/x86_64-linux-gnu/libc.so.6(+0x750f8)[0x7fa8172750f8]
[vasya-vmlinux:09251] [ 2] /lib/x86_64-linux-gnu/libc.so.6(__fprintf_chk+0xa3)[0x7fa817334ec3]
[vasya-vmlinux:09251] [ 3] ./rh15d_lteray(+0x14563)[0x55a39895d563]
[vasya-vmlinux:09251] [ 4] ./rh15d_lteray(+0x1476a)[0x55a39895d76a]
[vasya-vmlinux:09251] [ 5] ./rh15d_lteray(+0x5987)[0x55a39894e987]
[vasya-vmlinux:09251] [ 6] /lib/x86_64-linux-gnu/libc.so.6(+0x29d90)[0x7fa817229d90]
[vasya-vmlinux:09251] [ 7] /lib/x86_64-linux-gnu/libc.so.6(__libc_start_main+0x80)[0x7fa817229e40]
[vasya-vmlinux:09251] [ 8] ./rh15d_lteray(+0x5e65)[0x55a39894ee65]
[vasya-vmlinux:09251] *** End of error message ***
Segmentation fault 
```

The tools are supposed to be run with `mpiexec` like this:

``` sh
$ cd run_example
$ mpiexec -np 4 ../rh15d_ray_pool
```

Results will be written to `output` folder.
